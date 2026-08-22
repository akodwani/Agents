/**
 * derive.ts — turns data/ into Facts. Pure arithmetic, no judgement.
 * COACH never does math in its head; it reads this output.
 *
 *   npx tsx scripts/derive.ts            # today
 *   npx tsx scripts/derive.ts 2026-09-14 # as of a given date
 */
import { Dataset, loadDataset } from './io.js';
import {
  ISODate, addDays, dateRange, daysBetween, dowOf, localHour, localISODate, toDayNum,
} from './dates.js';
import { BackState, MealRow, SessionRow } from './schema.js';

/* ------------------------------------------------------------------ types */

export interface LiftFact {
  name: string;
  currentE1rm: number | null;
  priorE1rm: number | null;
  deltaPct: number | null;
}

export interface DayIntake {
  d: ISODate;
  kcal: number;
  protein: number;
  logged: boolean;
  target: number;
  ok: boolean;
}

export interface EmergencyPlan {
  items: string[];
  kcal: number;
  protein: number;
  pctOfTarget: number;
  /** true when the combo also clears the protein target minus 10 g. */
  meetsProtein: boolean;
}

export interface Facts {
  asOf: ISODate;
  hour: number;
  daysIn: number;
  weight: {
    latest: { d: ISODate; lb: number } | null;
    avg7: number | null;
    avg7prev: number | null;
    avg7Delta: number | null;
    rateLbWk: number | null;
    rateLbWkPrev: number | null;
    weeksLeft: number;
    goalWeightLb: number;
    deadline: ISODate;
    projectedDec1: number | null;
    projectedGap: number | null;
    stallStreakDays: number;
    points14: number;
  };
  targets: {
    kcal: number;
    kcalRestDay: number;
    proteinG: number;
    fatG: number;
    fiberG: number;
    stepsPerDay: number;
    cardioMinPerWk: number;
    kcalToday: number;
  };
  floors: { kcal: number; proteinG: number };
  adherence7: number | null;
  adherenceDays: DayIntake[];
  adherenceFailDays: ISODate[];
  today: {
    kcal: number; protein: number; fat: number; carb: number; fiber: number;
    kcalRemaining: number; proteinRemaining: number; proteinPctOfTarget: number;
    meals: { t: string; name: string; kcal: number; p: number }[];
  };
  checkins: {
    sleep5: number | null; stress5: number | null; energy5: number | null;
    backLast3: BackState[];
    latest: { d: ISODate; sleep: number; stress: number; energy: number; back: BackState; time_min: number; note: string } | null;
    stressNoteHit: boolean;
    painStreak: number;
  };
  training: {
    sessionsDone7: number; sessionsPlanned7: number; meanRpe7: number | null;
    cardioMin7: number; steps7: number | null; stepsTotal7: number;
    lastSession: { d: ISODate; type: string; rpe: number | null; feel: string } | null;
    todayType: string; nextSplitDay: { d: ISODate; type: string };
  };
  lifts: LiftFact[];
  daysSinceMeasurement: number | null;
  indulgenceDays: { d: ISODate; restaurantMeals: number; kcal: number }[];
  ladder: {
    rungsApplied: string[];
    nextRung: string | null;
    lockedUntil: ISODate | null;
    locked: boolean;
    lastAdjustment: { d: ISODate; kind: string; from: number; to: number } | null;
  };
  emergencyPlans: EmergencyPlan[];
}

/* ---------------------------------------------------------------- helpers */

const r1 = (n: number) => Math.round(n * 10) / 10;
const r2 = (n: number) => Math.round(n * 100) / 100;
const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0);
const mean = (xs: number[]) => (xs.length ? sum(xs) / xs.length : null);

/** Ordinary least squares slope of y over x. null when it cannot be fit. */
export function olsSlope(points: { x: number; y: number }[]): number | null {
  if (points.length < 3) return null;
  const mx = sum(points.map((p) => p.x)) / points.length;
  const my = sum(points.map((p) => p.y)) / points.length;
  let num = 0;
  let den = 0;
  for (const p of points) {
    num += (p.x - mx) * (p.y - my);
    den += (p.x - mx) ** 2;
  }
  if (den === 0) return null;
  return num / den;
}

function isRestDay(label: string): boolean {
  return /rest/i.test(label);
}

/** Mean weight over the 7 days ending on `end` (inclusive). Needs >= 5 points. */
export function avgWindow(
  weights: { d: ISODate; lb: number }[],
  end: ISODate,
  days = 7,
  minPoints = 5,
): number | null {
  const hi = toDayNum(end);
  const lo = hi - (days - 1);
  const pts = weights.filter((w) => {
    const n = toDayNum(w.d);
    return n >= lo && n <= hi;
  });
  if (pts.length < minPoints) return null;
  return sum(pts.map((w) => w.lb)) / pts.length;
}

/** Loss rate in lb/week (positive = losing) from the last 14 weigh-ins up to `end`. */
export function rateFrom(weights: { d: ISODate; lb: number }[], end: ISODate): number | null {
  const upTo = weights.filter((w) => toDayNum(w.d) <= toDayNum(end)).slice(-14);
  const slope = olsSlope(upTo.map((w) => ({ x: toDayNum(w.d), y: w.lb })));
  if (slope === null) return null;
  return -slope * 7;
}

/** Consecutive days on which avg7 has not dropped >= 0.5 lb vs 7 days earlier. */
export function stallStreak(weights: { d: ISODate; lb: number }[], asOf: ISODate, cap = 120): number {
  let streak = 0;
  for (let i = 0; i < cap; i++) {
    const day = addDays(asOf, -i);
    const now = avgWindow(weights, day);
    const then = avgWindow(weights, addDays(day, -7));
    if (now === null || then === null) break;
    if (then - now >= 0.5) break;
    streak++;
  }
  return streak;
}

function e1rmOf(w: number, r: number): number {
  return w * (1 + r / 30);
}

/** Best e1rm for one lift across done sessions inside [from, to]. */
export function bestE1rm(sessions: SessionRow[], lift: string, from: ISODate, to: ISODate): number | null {
  let best: number | null = null;
  const lo = toDayNum(from);
  const hi = toDayNum(to);
  for (const s of sessions) {
    const n = toDayNum(s.d);
    if (n < lo || n > hi || !s.done) continue;
    for (const ex of s.ex) {
      if (ex.name.toLowerCase() !== lift.toLowerCase()) continue;
      for (const st of ex.sets) {
        if (!st.done || st.r === 0) continue;
        const e = e1rmOf(st.w, st.r);
        if (best === null || e > best) best = e;
      }
    }
  }
  return best;
}

const STRESS_WORDS = /stress|work|deadline|boss|swamped|slammed|overtime|crunch|anxious|burn(ed|t)?[- ]?out/i;
/**
 * Deliberately narrow. The `restaurant` flag on the meal row is the source of
 * truth (log.ts --restaurant); these words only catch an obvious miss. Staple
 * names like "Chipotle bowl" are NOT here — that meal has known macros and is
 * part of the plan, not an untracked one.
 */
const RESTAURANT_WORDS = /restaurant|take-?out|\bdelivery\b|\bate out\b|\bdinner out\b|\bbrunch\b|halal cart|\bbuffet\b|\bbar tab\b/i;

export function isRestaurantMeal(m: MealRow): boolean {
  return m.restaurant || RESTAURANT_WORDS.test(`${m.name} ${m.raw}`);
}

/* ------------------------------------------------ effective target ladder */

const LADDER_ORDER = ['steps', 'cardio', 'kcal_rest', 'kcal_all'] as const;
export type LadderRung = (typeof LADDER_ORDER)[number];
export { LADDER_ORDER };

export function effectiveTargets(ds: Dataset, asOf: ISODate) {
  const p = ds.profile;
  let kcal = p.targets.kcal;
  let kcalRestDay = p.targets.kcal;
  let stepsPerDay = p.baseline.stepsPerDay;
  let cardioMinPerWk = p.baseline.cardioMinPerWk;
  const applied: string[] = [];
  let lockedUntil: ISODate | null = null;
  let last: { d: ISODate; kind: string; from: number; to: number } | null = null;

  const rows = [...ds.adjustments]
    .filter((a) => toDayNum(a.d) <= toDayNum(asOf))
    .sort((a, b) => toDayNum(a.d) - toDayNum(b.d));

  for (const a of rows) {
    switch (a.kind) {
      case 'steps':
        stepsPerDay = a.to;
        applied.push('steps');
        break;
      case 'cardio':
        cardioMinPerWk = a.to;
        applied.push('cardio');
        break;
      case 'kcal_rest':
        kcalRestDay += a.to - a.from;
        applied.push('kcal_rest');
        break;
      case 'kcal_all': {
        const delta = a.to - a.from;
        kcal += delta;
        kcalRestDay += delta;
        applied.push('kcal_all');
        break;
      }
      case 'governor_kcal': {
        const delta = a.to - a.from;
        kcal += delta;
        kcalRestDay += delta;
        break;
      }
      case 'diet_break':
        kcal = a.to;
        kcalRestDay = a.to;
        applied.length = 0; // ladder resets
        break;
    }
    last = { d: a.d, kind: a.kind, from: a.from, to: a.to };
    if (lockedUntil === null || toDayNum(a.locked_until) > toDayNum(lockedUntil)) lockedUntil = a.locked_until;
  }

  const nextRung = LADDER_ORDER.find((k) => !applied.includes(k)) ?? null;
  return {
    kcal: Math.round(kcal),
    kcalRestDay: Math.round(kcalRestDay),
    proteinG: p.targets.proteinG,
    fatG: p.targets.fatG,
    fiberG: p.targets.fiberG,
    stepsPerDay,
    cardioMinPerWk,
    ladder: {
      rungsApplied: applied,
      nextRung,
      lockedUntil,
      locked: lockedUntil !== null && toDayNum(asOf) < toDayNum(lockedUntil),
      lastAdjustment: last,
    },
  };
}

/* ------------------------------------------------------- emergency plans */

/** Small bounded knapsack: zero-cook combos landing within +/-5% of the day's kcal. */
export function emergencyPlans(ds: Dataset, targetKcal: number, proteinG = 0, limit = 3): EmergencyPlan[] {
  type Item = { name: string; kcal: number; p: number };
  const seen = new Set<string>();
  const items: Item[] = [];
  const push = (it: Item) => {
    const key = it.name.toLowerCase();
    if (seen.has(key) || it.kcal <= 0) return;
    seen.add(key);
    items.push(it);
  };
  for (const m of ds.profile.diet.readyToEat) push(m);
  for (const m of ds.profile.diet.fixedMeals) push(m);
  for (const f of Object.values(ds.foods)) if (f.zeroCook) push({ name: f.name, kcal: f.kcal, p: f.p });

  const lo = targetKcal * 0.95;
  const hi = targetKcal * 1.05;
  const out: EmergencyPlan[] = [];
  const combos: number[][] = [];
  const n = items.length;
  // combinations with repetition, up to 2 of the same item, 1..4 items
  const walk = (start: number, picked: number[]) => {
    if (picked.length >= 2) combos.push([...picked]);
    if (picked.length === 4) return;
    for (let i = start; i < n; i++) {
      const used = picked.filter((x) => x === i).length;
      if (used >= 2) continue;
      picked.push(i);
      walk(i, picked);
      picked.pop();
    }
  };
  walk(0, []);

  const keyed = new Map<string, EmergencyPlan>();
  for (const c of combos) {
    const kcal = sum(c.map((i) => items[i].kcal));
    if (kcal < lo || kcal > hi) continue;
    const protein = sum(c.map((i) => items[i].p));
    const names = c.map((i) => items[i].name).sort();
    const key = names.join(' + ');
    if (keyed.has(key)) continue;
    keyed.set(key, {
      items: c.map((i) => items[i].name),
      kcal: Math.round(kcal),
      protein: Math.round(protein),
      pctOfTarget: r1((kcal / targetKcal) * 100),
      meetsProtein: protein >= proteinG - 10,
    });
  }
  out.push(...keyed.values());
  out.sort(
    (a, b) =>
      Number(b.meetsProtein) - Number(a.meetsProtein) ||
      b.protein - a.protein ||
      a.items.length - b.items.length,
  );
  return out.slice(0, limit);
}

/* ------------------------------------------------------------------ main */

export function derive(ds: Dataset, now: Date | ISODate = new Date()): Facts {
  const asOf: ISODate = typeof now === 'string' ? now : localISODate(now);
  const hour = typeof now === 'string' ? 12 : localHour(now);
  const p = ds.profile;

  const weights = [...ds.weights].sort((a, b) => toDayNum(a.d) - toDayNum(b.d));
  const upToToday = weights.filter((w) => toDayNum(w.d) <= toDayNum(asOf));

  const avg7 = avgWindow(upToToday, asOf);
  const avg7prev = avgWindow(upToToday, addDays(asOf, -7));
  const rateLbWk = rateFrom(upToToday, asOf);
  const rateLbWkPrev = rateFrom(upToToday, addDays(asOf, -7));
  const weeksLeft = Math.max(0, daysBetween(asOf, p.deadline) / 7);
  const projected = avg7 !== null && rateLbWk !== null ? avg7 - rateLbWk * weeksLeft : null;

  const t = effectiveTargets(ds, asOf);
  const { ladder: _ladder, ...targetsOnly } = t;
  const todayType = p.split[String(dowOf(asOf))] ?? 'Rest/Cardio';
  const kcalToday = isRestDay(todayType) ? t.kcalRestDay : t.kcal;

  /* ---- intake by day -------------------------------------------------- */
  const mealsBy = new Map<ISODate, MealRow[]>();
  for (const m of ds.meals) {
    if (!mealsBy.has(m.d)) mealsBy.set(m.d, []);
    mealsBy.get(m.d)!.push(m);
  }
  const dayTarget = (d: ISODate) =>
    isRestDay(p.split[String(dowOf(d))] ?? 'Rest/Cardio') ? t.kcalRestDay : t.kcal;

  const firstLog = ds.meals.length ? ds.meals.map((m) => m.d).sort()[0] : null;
  const window7 = dateRange(addDays(asOf, -7), addDays(asOf, -1)); // complete days only
  const adherenceDays: DayIntake[] = window7
    .filter((d) => firstLog !== null && toDayNum(d) >= toDayNum(firstLog))
    .map((d) => {
      const ms = mealsBy.get(d) ?? [];
      const kcal = sum(ms.map((m) => m.kcal));
      const protein = sum(ms.map((m) => m.p));
      const target = dayTarget(d);
      const logged = ms.length > 0;
      const ok = logged && Math.abs(kcal - target) <= target * 0.1 && protein >= t.proteinG - 10;
      return { d, kcal: Math.round(kcal), protein: Math.round(protein), logged, target, ok };
    });
  const adherence7 = adherenceDays.length
    ? r2(adherenceDays.filter((x) => x.ok).length / adherenceDays.length)
    : null;

  const todayMeals = mealsBy.get(asOf) ?? [];
  const todayKcal = sum(todayMeals.map((m) => m.kcal));
  const todayP = sum(todayMeals.map((m) => m.p));

  /* ---- check-ins ------------------------------------------------------ */
  const chk = [...ds.checkins]
    .filter((c) => toDayNum(c.d) <= toDayNum(asOf))
    .sort((a, b) => toDayNum(a.d) - toDayNum(b.d));
  const last5 = chk.slice(-5);
  const latestChk = chk.length ? chk[chk.length - 1] : null;
  const backLast3 = chk.slice(-3).reverse().map((c) => c.back);
  let painStreak = 0;
  for (let i = chk.length - 1; i >= 0; i--) {
    if (chk[i].back === 'pain') painStreak++;
    else break;
  }

  /* ---- training ------------------------------------------------------- */
  const win7 = dateRange(addDays(asOf, -6), asOf);
  const inWin = (d: ISODate) => toDayNum(d) >= toDayNum(addDays(asOf, -6)) && toDayNum(d) <= toDayNum(asOf);
  const done7 = ds.sessions.filter((s) => s.done && inWin(s.d));
  const planned7 = win7.filter((d) => !isRestDay(p.split[String(dowOf(d))] ?? 'Rest/Cardio')).length;
  const rpes = done7.map((s) => s.rpe).filter((x): x is number => x !== null);
  const cardioMin7 = sum(ds.cardio.filter((c) => inWin(c.d)).map((c) => c.min));
  const stepRows = ds.steps.filter((s) => inWin(s.d));
  const doneSessions = [...ds.sessions].filter((s) => s.done).sort((a, b) => toDayNum(a.d) - toDayNum(b.d));
  const lastSession = doneSessions.length ? doneSessions[doneSessions.length - 1] : null;

  const doneToday = ds.sessions.some((s) => s.d === asOf && s.done);
  const nextDay = doneToday ? addDays(asOf, 1) : asOf;

  const lifts: LiftFact[] = ds.library.trackedLifts.map((name) => {
    const cur = bestE1rm(ds.sessions, name, addDays(asOf, -13), asOf);
    const prior = bestE1rm(ds.sessions, name, addDays(asOf, -27), addDays(asOf, -14));
    return {
      name,
      currentE1rm: cur === null ? null : r1(cur),
      priorE1rm: prior === null ? null : r1(prior),
      deltaPct: cur !== null && prior !== null && prior > 0 ? r1(((cur - prior) / prior) * 100) : null,
    };
  });

  const measurements = [...ds.measurements].sort((a, b) => toDayNum(a.d) - toDayNum(b.d));
  const lastMeas = measurements.length ? measurements[measurements.length - 1] : null;

  /* ---- R2 check 2 evidence -------------------------------------------- */
  const indulgenceDays = dateRange(addDays(asOf, -3), asOf)
    .map((d) => {
      const ms = mealsBy.get(d) ?? [];
      return {
        d,
        restaurantMeals: ms.filter(isRestaurantMeal).length,
        kcal: Math.round(sum(ms.map((m) => m.kcal))),
      };
    })
    .filter((x) => x.restaurantMeals >= 2 || x.kcal > dayTarget(x.d) + 400);

  return {
    asOf,
    hour: r2(hour),
    daysIn: daysBetween(p.startDate, asOf),
    weight: {
      latest: upToToday.length ? { d: upToToday[upToToday.length - 1].d, lb: upToToday[upToToday.length - 1].lb } : null,
      avg7: avg7 === null ? null : r2(avg7),
      avg7prev: avg7prev === null ? null : r2(avg7prev),
      avg7Delta: avg7 !== null && avg7prev !== null ? r2(avg7prev - avg7) : null,
      rateLbWk: rateLbWk === null ? null : r2(rateLbWk),
      rateLbWkPrev: rateLbWkPrev === null ? null : r2(rateLbWkPrev),
      weeksLeft: r2(weeksLeft),
      goalWeightLb: p.goalWeightLb,
      deadline: p.deadline,
      projectedDec1: projected === null ? null : r1(projected),
      projectedGap: projected === null ? null : r1(projected - p.goalWeightLb),
      stallStreakDays: stallStreak(upToToday, asOf),
      points14: upToToday.slice(-14).length,
    },
    targets: { ...targetsOnly, kcalToday },
    floors: p.floors,
    adherence7,
    adherenceDays,
    adherenceFailDays: adherenceDays.filter((x) => !x.ok).map((x) => x.d),
    today: {
      kcal: Math.round(todayKcal),
      protein: Math.round(todayP),
      fat: Math.round(sum(todayMeals.map((m) => m.fat))),
      carb: Math.round(sum(todayMeals.map((m) => m.carb))),
      fiber: Math.round(sum(todayMeals.map((m) => m.fiber))),
      kcalRemaining: Math.round(kcalToday - todayKcal),
      proteinRemaining: Math.round(t.proteinG - todayP),
      proteinPctOfTarget: r2(todayP / t.proteinG),
      meals: todayMeals.map((m) => ({ t: m.t, name: m.name, kcal: m.kcal, p: m.p })),
    },
    checkins: {
      sleep5: last5.length ? r2(mean(last5.map((c) => c.sleep))!) : null,
      stress5: last5.length ? r2(mean(last5.map((c) => c.stress))!) : null,
      energy5: last5.length ? r2(mean(last5.map((c) => c.energy))!) : null,
      backLast3,
      latest: latestChk,
      stressNoteHit: latestChk ? STRESS_WORDS.test(latestChk.note) : false,
      painStreak,
    },
    training: {
      sessionsDone7: done7.length,
      sessionsPlanned7: planned7,
      meanRpe7: rpes.length ? r2(mean(rpes)!) : null,
      cardioMin7,
      steps7: stepRows.length ? Math.round(mean(stepRows.map((s) => s.steps))!) : null,
      stepsTotal7: sum(stepRows.map((s) => s.steps)),
      lastSession: lastSession
        ? { d: lastSession.d, type: lastSession.type, rpe: lastSession.rpe, feel: lastSession.feel }
        : null,
      todayType,
      nextSplitDay: { d: nextDay, type: p.split[String(dowOf(nextDay))] ?? 'Rest/Cardio' },
    },
    lifts,
    daysSinceMeasurement: lastMeas ? daysBetween(lastMeas.d, asOf) : null,
    indulgenceDays,
    ladder: t.ladder,
    emergencyPlans: emergencyPlans(ds, kcalToday, t.proteinG),
  };
}

/* ------------------------------------------------------------------- cli */

const isMain = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const arg = process.argv[2];
  const ds = loadDataset();
  const facts = derive(ds, arg && /^\d{4}-\d{2}-\d{2}$/.test(arg) ? arg : new Date());
  console.log(JSON.stringify(facts, null, 2));
}
