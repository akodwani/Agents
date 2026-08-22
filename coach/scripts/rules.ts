/**
 * rules.ts — the decision engine. Reads Facts, emits Decision[].
 * Decisions printed here are final; COACH explains them, never overrides them.
 *
 *   npx tsx scripts/rules.ts             # today, appends to data/decisions.jsonl
 *   npx tsx scripts/rules.ts 2026-09-14  # as of a date
 *   npx tsx scripts/rules.ts --dry       # do not write decisions.jsonl
 */
import { Dataset, loadDataset, appendDecisions, paths, readJsonl } from './io.js';
import { derive, Facts, LADDER_ORDER } from './derive.js';
import { ISODate, addDays, isSunday, localISODate, toDayNum } from './dates.js';
import { BackState, DecisionRow, Exercise, SessionRow } from './schema.js';

export interface Decision {
  rule: string;
  verdict: string;
  data: Record<string, unknown>;
  action: string;
  rationale: string;
}

export interface LoadSuggestion {
  name: string;
  lastTopSet: { d: ISODate; w: number; r: number; rpe: number } | null;
  suggestedLoad: number | null;
  reason: string;
}

export interface SessionInputs {
  d: ISODate;
  type: string;
  timeMin: number;
  exerciseCount: number;
  volumeMultiplier: number;
  multiplierReasons: string[];
  restSeconds: { compound: number; isolation: number };
  loads: LoadSuggestion[];
}

export interface AllowedExercises {
  type: string;
  back: BackState;
  warmup: { name: string; cue: string }[];
  list: Exercise[];
  byPattern: Record<string, Exercise[]>;
  excluded: { name: string; reason: string }[];
}

export interface RulesOutput {
  asOf: ISODate;
  decisions: Decision[];
  allowedExercises: AllowedExercises;
  sessionInputs: SessionInputs;
}

const round25 = (n: number) => Math.round(n / 2.5) * 2.5;

/** Round to the gym's 2.5 lb granularity without swallowing a small step. */
function stepLoad(base: number, pct: number): number {
  const raw = base * pct;
  let v = round25(raw);
  if (pct > 1 && v <= base) v = base + 2.5;
  if (pct < 1 && v >= base) v = Math.max(0, base - 2.5);
  return v;
}
const r1 = (n: number) => Math.round(n * 10) / 10;
const r2 = (n: number) => Math.round(n * 100) / 100;

/* ------------------------------------------------------- R6: exercise filter */

const PATTERNS_BY_TYPE: { test: RegExp; patterns: string[] }[] = [
  { test: /push/i, patterns: ['horizontal_push', 'vertical_push', 'chest_iso', 'delt_lat', 'triceps'] },
  { test: /pull/i, patterns: ['vertical_pull', 'horizontal_pull', 'delt_rear', 'biceps', 'forearm'] },
  { test: /leg/i, patterns: ['squat', 'hinge', 'lunge', 'quad_iso', 'ham_iso', 'glute', 'calf'] },
  { test: /abs|core/i, patterns: ['core_anti_ext', 'core_anti_rot', 'core_flex'] },
  { test: /rest|cardio/i, patterns: ['conditioning', 'core_anti_ext', 'core_anti_rot', 'core_flex', 'carry'] },
];

export function patternsForType(type: string): string[] {
  const out = new Set<string>();
  for (const p of PATTERNS_BY_TYPE) if (p.test.test(type)) p.patterns.forEach((x) => out.add(x));
  if (out.size === 0) PATTERNS_BY_TYPE.forEach((p) => p.patterns.forEach((x) => out.add(x)));
  return [...out];
}

/**
 * The QL filter. Contraindicated movements are removed in code — there is no
 * path by which COACH can prescribe one.
 */
export function allowedExercisesFor(ds: Dataset, type: string, back: BackState): AllowedExercises {
  const excluded: { name: string; reason: string }[] = [];
  const patterns = patternsForType(type);
  const list: Exercise[] = [];

  for (const ex of ds.library.exercises) {
    if (ex.contraindicated.includes('QL')) {
      excluded.push({ name: ex.name, reason: 'contraindicated: QL' });
      continue;
    }
    if (back === 'tight' && ex.spinalLoad === 'high') {
      excluded.push({ name: ex.name, reason: 'back tight: high spinal load, supported variants only for 7d' });
      continue;
    }
    if ((back === 'sore' || back === 'pain') && ex.spinalLoad !== 'none') {
      excluded.push({ name: ex.name, reason: `back ${back}: no loaded spinal work` });
      continue;
    }
    if (!patterns.includes(ex.pattern)) continue;
    list.push(ex);
  }

  const byPattern: Record<string, Exercise[]> = {};
  for (const ex of list) (byPattern[ex.pattern] ||= []).push(ex);

  const warmup =
    back === 'fine'
      ? []
      : ds.library.exercises.filter((e) => e.mcgill).map((e) => ({ name: e.name, cue: e.cue }));

  return { type, back, warmup, list, byPattern, excluded };
}

/* --------------------------------------------------------- R8: load ladder */

export function suggestLoad(ds: Dataset, name: string, asOf: ISODate): LoadSuggestion {
  const ex = ds.library.exercises.find((e) => e.name.toLowerCase() === name.toLowerCase());
  const range = ex?.repRange ?? [8, 12];
  const hist = ds.sessions
    .filter((s) => s.done && toDayNum(s.d) <= toDayNum(asOf) && s.ex.some((e) => e.name.toLowerCase() === name.toLowerCase()))
    .sort((a, b) => toDayNum(a.d) - toDayNum(b.d));

  if (hist.length === 0) {
    return { name, lastTopSet: null, suggestedLoad: null, reason: 'no history — pick a load you stop at RPE 7 and log it' };
  }

  const topOf = (s: SessionRow) => {
    const sets = s.ex.find((e) => e.name.toLowerCase() === name.toLowerCase())!.sets.filter((x) => x.done);
    if (!sets.length) return null;
    return sets.reduce((a, b) => (b.w > a.w || (b.w === a.w && b.r > a.r) ? b : a));
  };

  const last = hist[hist.length - 1];
  const lastTop = topOf(last);
  if (!lastTop) return { name, lastTopSet: null, suggestedLoad: null, reason: 'last session logged no completed sets' };

  const lastSets = last.ex.find((e) => e.name.toLowerCase() === name.toLowerCase())!.sets;
  const missedReps = lastSets.some((s) => !s.done || s.r < range[0]);
  const base = lastTop.w;
  const stamp = { d: last.d, w: lastTop.w, r: lastTop.r, rpe: lastTop.rpe };

  if (lastTop.rpe >= 9.5 || missedReps) {
    return {
      name,
      lastTopSet: stamp,
      suggestedLoad: stepLoad(base, 0.95),
      reason: missedReps ? `missed reps below ${range[0]} last time — back off 5%` : 'last top set RPE >= 9.5 — back off 5%',
    };
  }

  const prev = hist.length >= 2 ? topOf(hist[hist.length - 2]) : null;
  const bothToppedOut = prev !== null && lastTop.r >= range[1] && prev.r >= range[1];
  if (bothToppedOut) {
    const easy = lastTop.rpe <= 8 && prev!.rpe <= 8;
    const pct = easy ? 1.05 : 1.025;
    return {
      name,
      lastTopSet: stamp,
      suggestedLoad: stepLoad(base, pct),
      reason: `hit ${range[1]} reps two sessions running — up ${easy ? '5' : '2.5'}%`,
    };
  }

  return { name, lastTopSet: stamp, suggestedLoad: round25(base), reason: `hold ${base} and add reps toward ${range[1]}` };
}

export function sessionInputsFor(ds: Dataset, f: Facts): SessionInputs {
  const chk = f.checkins.latest;
  const noteType = chk?.note.match(/push|pull|legs?|rest|cardio/i)?.[0];
  const type = noteType ? normaliseType(noteType, ds) : f.training.todayType;
  const timeMin = chk?.d === f.asOf ? chk.time_min : 60;

  const reasons: string[] = [];
  let mult = 1;
  if (chk && chk.d === f.asOf) {
    if (chk.sleep < 6) { mult *= 0.7; reasons.push(`sleep ${chk.sleep}h < 6 → x0.7`); }
    if (chk.stress >= 4) { mult *= 0.8; reasons.push(`stress ${chk.stress} >= 4 → x0.8`); }
    if (chk.energy <= 2) { mult *= 0.75; reasons.push(`energy ${chk.energy} <= 2 → x0.75`); }
  }
  mult = Math.max(0.6, r2(mult));
  if (!reasons.length) reasons.push('inputs clean — full volume');

  const exerciseCount = timeMin <= 45 ? 4 : timeMin <= 60 ? 5 : timeMin <= 75 ? 6 : 7;

  const back = f.checkins.backLast3[0] ?? 'fine';
  const allowed = allowedExercisesFor(ds, type, back);
  const allowedNames = new Set(allowed.list.map((e) => e.name.toLowerCase()));
  const recent = new Set(
    ds.sessions
      .filter((s) => s.done && toDayNum(s.d) >= toDayNum(addDays(f.asOf, -21)))
      .flatMap((s) => s.ex.map((e) => e.name)),
  );
  const candidates = [
    ...ds.library.trackedLifts.filter((n) => allowedNames.has(n.toLowerCase())),
    ...[...recent].filter((n) => allowedNames.has(n.toLowerCase())),
  ];
  const loads = [...new Set(candidates)].map((n) => suggestLoad(ds, n, f.asOf));

  return {
    d: f.asOf,
    type,
    timeMin,
    exerciseCount,
    volumeMultiplier: mult,
    multiplierReasons: reasons,
    restSeconds: { compound: 150, isolation: 75 },
    loads,
  };
}

function normaliseType(word: string, ds: Dataset): string {
  const labels = Object.values(ds.profile.split);
  const hit = labels.find((l) => new RegExp(word, 'i').test(l));
  return hit ?? word;
}

/* -------------------------------------------------------------- the rules */

function r1Trend(f: Facts): Decision {
  const d = {
    avg7: f.weight.avg7, avg7prev: f.weight.avg7prev, drop: f.weight.avg7Delta,
    rateLbWk: f.weight.rateLbWk, stallStreakDays: f.weight.stallStreakDays,
    adherence7: f.adherence7, projectedDec1: f.weight.projectedDec1,
  };
  if (f.weight.avg7 === null || f.weight.avg7prev === null) {
    return {
      rule: 'R1', verdict: 'INSUFFICIENT_DATA', data: d,
      action: 'Weigh in daily. Need 5 weigh-ins in each of the last two 7-day windows.',
      rationale: 'Rolling averages need >= 5 points per window; one of them is short.',
    };
  }
  const drop = f.weight.avg7prev - f.weight.avg7;
  if (drop >= 0.5) {
    return {
      rule: 'R1', verdict: 'ON_PACE', data: d,
      action: 'Change nothing. Keep the current targets.',
      rationale: `7-day average fell ${r1(drop)} lb week over week — that is real movement.`,
    };
  }
  if (f.weight.stallStreakDays < 14) {
    return {
      rule: 'R1', verdict: 'NOISE', data: d,
      action: 'Change nothing. Keep logging.',
      rationale: `Average moved ${r1(drop)} lb and the flat run is ${f.weight.stallStreakDays} days — under the 14-day bar for a stall.`,
    };
  }
  if (f.adherence7 === null) {
    return {
      rule: 'R1', verdict: 'INSUFFICIENT_DATA', data: d,
      action: 'Log meals for 7 straight days before any diet change.',
      rationale: '14 flat days, but there is no intake record to judge adherence against.',
    };
  }
  if (f.adherence7 >= 0.9) {
    return {
      rule: 'R1', verdict: 'STALL', data: d,
      action: 'Run the stress protocol, then the ladder.',
      rationale: `${f.weight.stallStreakDays} flat days at ${Math.round(f.adherence7 * 100)}% adherence — the plan, not the execution, is the problem.`,
    };
  }
  return {
    rule: 'R1', verdict: 'UNDER_ADHERENCE', data: d,
    action: 'Fix execution before touching the plan. No calorie cut.',
    rationale: `${f.weight.stallStreakDays} flat days at ${Math.round(f.adherence7 * 100)}% adherence — the plan has not actually been run yet.`,
  };
}

export function r2Stress(f: Facts): Decision {
  const base = {
    stress5: f.checkins.stress5, sleep5: f.checkins.sleep5, adherence7: f.adherence7,
    sessionsDone7: f.training.sessionsDone7, sessionsPlanned7: f.training.sessionsPlanned7,
    meanRpe7: f.training.meanRpe7,
  };
  // 1. sleep
  if (f.checkins.sleep5 !== null && f.checkins.sleep5 < 6.5) {
    return {
      rule: 'R2', verdict: 'SLEEP_DEFICIT', data: { ...base, check: 1 },
      action: '8h in bed for 5 nights. No diet change. Recheck in 5 days.',
      rationale: `Sleeping ${f.checkins.sleep5}h on average. Under-slept scale weight is water and cortisol, not fat.`,
    };
  }
  // 2. water retention
  if (f.indulgenceDays.length > 0) {
    return {
      rule: 'R2', verdict: 'WATER_RETENTION_LIKELY', data: { ...base, check: 2, days: f.indulgenceDays },
      action: 'No change. Expect a whoosh in 3-7 days.',
      rationale: `${f.indulgenceDays.map((x) => x.d).join(', ')} carried restaurant food or a big sodium/carb load. The scale is holding water.`,
    };
  }
  // 3. adherence
  if (f.adherence7 !== null && f.adherence7 < 0.9) {
    return {
      rule: 'R2', verdict: 'ADHERENCE_GAP', data: { ...base, check: 3, failDays: f.adherenceFailDays },
      action: 'No change to the plan. Close these days first.',
      rationale: `Missed on ${f.adherenceFailDays.join(', ')}. That is the variable to fix before anything else moves.`,
    };
  }
  // 4. training
  const sessionsShort = f.training.sessionsDone7 < f.training.sessionsPlanned7 - 1;
  const softSessions = f.training.meanRpe7 !== null && f.training.meanRpe7 < 6;
  if (sessionsShort || softSessions) {
    return {
      rule: 'R2', verdict: 'TRAINING_DROP', data: { ...base, check: 4 },
      action: 'Rebuild the training week before cutting food.',
      rationale: sessionsShort
        ? `${f.training.sessionsDone7} of ${f.training.sessionsPlanned7} sessions done. Missing stimulus reads as a stall.`
        : `Mean session RPE ${f.training.meanRpe7} — the sessions happened but nothing was asked of you.`,
    };
  }
  // 5. clear
  return {
    rule: 'R2', verdict: 'CORTISOL_LOAD', data: { ...base, check: 5, lockUntil: addDays(f.asOf, 7) },
    action: '48h de-stress: 30-min outdoor walk daily, 8h sleep, carbs held where they are, no extra cardio. Diet changes locked 7 days.',
    rationale: 'Sleep, intake, adherence and training all check out. What is left is stress load, and cutting food into it makes it worse.',
  };
}

export function r3Ladder(f: Facts): Decision {
  const nextRung = f.ladder.nextRung as (typeof LADDER_ORDER)[number] | null;
  const base = { rungsApplied: f.ladder.rungsApplied, nextRung, lockedUntil: f.ladder.lockedUntil };

  if (f.ladder.locked) {
    return {
      rule: 'R3', verdict: 'LADDER_LOCKED', data: base,
      action: `Hold. Next rung unlocks ${f.ladder.lockedUntil}.`,
      rationale: 'One rung per 14 days. Stacking changes makes the next stall unreadable.',
    };
  }

  const dietBreak = (why: string): Decision => {
    const kcal = f.weight.avg7 !== null ? Math.round(f.weight.avg7 * 11.5) : null;
    return {
      rule: 'R3', verdict: 'DIET_BREAK', data: { ...base, kcal, days: '7-10', why },
      action: kcal
        ? `Diet break 7-10 days at ${kcal} kcal, protein held at ${f.targets.proteinG}g. Ladder resets after.`
        : 'Diet break 7-10 days at maintenance. Need a 7-day average to set the number.',
      rationale: why,
    };
  };

  if (nextRung === null) return dietBreak('Every rung is spent. Nothing left to take away.');

  if (nextRung === 'steps') {
    const to = f.targets.stepsPerDay + 2000;
    return {
      rule: 'R3', verdict: 'RUNG_STEPS', data: { ...base, kind: 'steps', from: f.targets.stepsPerDay, to, lockUntil: addDays(f.asOf, 14) },
      action: `Steps target ${f.targets.stepsPerDay} → ${to}/day. Locked 14 days.`,
      rationale: 'Cheapest rung first: more NEAT costs nothing in recovery and nothing in food.',
    };
  }
  if (nextRung === 'cardio') {
    const to = f.targets.cardioMinPerWk + 60;
    return {
      rule: 'R3', verdict: 'RUNG_CARDIO', data: { ...base, kind: 'cardio', from: f.targets.cardioMinPerWk, to, lockUntil: addDays(f.asOf, 14) },
      action: `Add 20 min Zone 2 three times a week: ${f.targets.cardioMinPerWk} → ${to} min/wk. Locked 14 days.`,
      rationale: 'Steps are already spent. Zone 2 adds deficit without touching recovery or food.',
    };
  }
  if (nextRung === 'kcal_rest') {
    const to = f.targets.kcalRestDay - 100;
    if (to < f.floors.kcal) return dietBreak(`Rest-day cut would land at ${to}, under the ${f.floors.kcal} floor.`);
    return {
      rule: 'R3', verdict: 'RUNG_KCAL_REST', data: { ...base, kind: 'kcal_rest', from: f.targets.kcalRestDay, to, lockUntil: addDays(f.asOf, 14) },
      action: `Rest days ${f.targets.kcalRestDay} → ${to} kcal, off carbs. Training days unchanged. Locked 14 days.`,
      rationale: 'First food cut goes where it costs the least: the days you are not training.',
    };
  }
  const to = f.targets.kcal - 100;
  if (to < f.floors.kcal) return dietBreak(`All-day cut would land at ${to}, under the ${f.floors.kcal} floor.`);
  return {
    rule: 'R3', verdict: 'RUNG_KCAL_ALL', data: { ...base, kind: 'kcal_all', from: f.targets.kcal, to, lockUntil: addDays(f.asOf, 14) },
    action: `All days ${f.targets.kcal} → ${to} kcal, off carbs. Protein stays ${f.targets.proteinG}g. Locked 14 days.`,
    rationale: 'Last rung on the ladder. After this it is a diet break, not a deeper cut.',
  };
}

function r4Governor(f: Facts): Decision[] {
  const out: Decision[] = [];
  const rate = f.weight.rateLbWk;
  const prev = f.weight.rateLbWkPrev;
  const base = { rateLbWk: rate, rateLbWkPrev: prev, projectedDec1: f.weight.projectedDec1, goal: f.weight.goalWeightLb };

  if (rate === null || prev === null) {
    out.push({
      rule: 'R4a', verdict: 'INSUFFICIENT_DATA', data: base,
      action: 'Need two consecutive weeks of rate before the governor can rule.',
      rationale: 'Fewer than three weigh-ins in one of the two windows.',
    });
  } else if (rate > 2.5 && prev > 2.5) {
    const to = f.targets.kcal + 125;
    out.push({
      rule: 'R4a', verdict: 'TOO_FAST', data: { ...base, kind: 'governor_kcal', from: f.targets.kcal, to, lockUntil: addDays(f.asOf, 14) },
      action: `Add 125 kcal of carbs: ${f.targets.kcal} → ${to}. Locked 14 days.`,
      rationale: `Losing ${rate} lb/wk two weeks running. Past 2.5 you are spending muscle, and this is a lean-look goal.`,
    });
  } else if (rate < 1.0 && prev < 1.0) {
    out.push({
      rule: 'R4a', verdict: 'TOO_SLOW', data: base,
      action: 'Run the stress protocol, then the ladder.',
      rationale: `Rate is ${rate} lb/wk two weeks running — under the 1.0 lb/wk floor for this deadline.`,
    });
  } else {
    out.push({
      rule: 'R4a', verdict: 'PACE_OK', data: base,
      action: 'Nothing to change on pace.',
      rationale: `${rate} lb/wk sits inside the 1.0-2.5 lb/wk governor band.`,
    });
  }

  if (f.weight.projectedDec1 !== null && f.weight.avg7 !== null && f.weight.projectedDec1 > f.weight.goalWeightLb + 3) {
    const needed = f.weight.weeksLeft > 0 ? r2((f.weight.avg7 - f.weight.goalWeightLb) / f.weight.weeksLeft) : null;
    const weeksAtRate = rate && rate > 0 ? (f.weight.avg7 - f.weight.goalWeightLb) / rate : null;
    out.push({
      rule: 'R4b', verdict: 'OFF_TRACK', data: {
        projectedDec1: f.weight.projectedDec1, goal: f.weight.goalWeightLb, gap: f.weight.projectedGap,
        requiredRateLbWk: needed, governorCap: 2.5,
        options: [
          { id: 'keep_pace', label: `Keep this pace and accept ${f.weight.projectedDec1} lb on Dec 1`, cost: `${f.weight.projectedGap} lb over goal, no extra stress` },
          { id: 'go_faster', label: needed !== null ? `Push to ${Math.min(needed, 2.5)} lb/wk (governor caps at 2.5)` : 'Push toward the governor cap of 2.5 lb/wk', cost: needed !== null && needed > 2.5 ? `Even at the cap you land short — ${needed} lb/wk would be required` : 'More cardio, tighter weekends, higher stress load' },
          { id: 'move_date', label: weeksAtRate !== null ? `Move the date out ~${Math.ceil(weeksAtRate)} weeks from today at the current rate` : 'Move the date out', cost: 'Same body, later. No extra risk to strength.' },
        ],
      },
      action: 'Present these three options. Avi picks. Do not choose for him.',
      rationale: `Projection puts Dec 1 at ${f.weight.projectedDec1} lb against a ${f.weight.goalWeightLb} lb goal — more than 3 lb off.`,
    });
  } else if (f.weight.projectedDec1 !== null) {
    out.push({
      rule: 'R4b', verdict: 'PROJECTION_OK', data: { projectedDec1: f.weight.projectedDec1, goal: f.weight.goalWeightLb },
      action: 'Hold the line.',
      rationale: `Current rate lands Dec 1 at ${f.weight.projectedDec1} lb.`,
    });
  }
  return out;
}

function r5Strength(f: Facts): Decision[] {
  const out: Decision[] = [];
  const rated = f.lifts.filter((l) => l.deltaPct !== null);
  const down10 = rated.filter((l) => l.deltaPct! < -10);
  const anyDown = rated.filter((l) => l.deltaPct! < 0);

  if (down10.length >= 2) {
    out.push({
      rule: 'R5a', verdict: 'UNDER_RECOVERY',
      data: { lifts: down10, cardioMin7: f.training.cardioMin7, cardioTo: Math.round(f.training.cardioMin7 * 0.7) },
      action: `Cut cardio 30%: ${f.training.cardioMin7} → ${Math.round(f.training.cardioMin7 * 0.7)} min this week. No food change until strength comes back.`,
      rationale: `${down10.map((l) => `${l.name} ${l.deltaPct}%`).join(', ')} vs 14 days ago. Strength going backwards on a cut means recovery, not effort.`,
    });
  } else {
    out.push({
      rule: 'R5a', verdict: rated.length ? 'STRENGTH_HOLDING' : 'INSUFFICIENT_DATA',
      data: { lifts: f.lifts },
      action: rated.length ? 'Keep the loads climbing where they can.' : 'Log tracked lifts so e1RM can be compared across 14 days.',
      rationale: rated.length ? 'Fewer than two tracked lifts are down more than 10%.' : 'No tracked lift has both a current and a 14-day-prior e1RM.',
    });
  }

  if (f.training.cardioMin7 > 240 && anyDown.length >= 1) {
    out.push({
      rule: 'R5b', verdict: 'CARDIO_CAP',
      data: { cardioMin7: f.training.cardioMin7, cap: 240, lifts: anyDown },
      action: `Cap cardio at 240 min/wk. You are at ${f.training.cardioMin7}.`,
      rationale: `Over 4 hours of cardio a week with ${anyDown.map((l) => l.name).join(', ')} trending down. The cardio is eating the lifting.`,
    });
  }
  return out;
}

function r6QL(f: Facts): Decision {
  const back = f.checkins.backLast3[0] ?? 'fine';
  const base = { back, backLast3: f.checkins.backLast3, painStreak: f.checkins.painStreak };

  if (f.checkins.painStreak >= 2) {
    return {
      rule: 'R6', verdict: 'QL_PAIN_CLINICIAN', data: base,
      action: 'No loaded spinal work. See a clinician this week — two straight days of pain is not something to train through.',
      rationale: 'Back reported as pain on two consecutive check-ins. That is outside what a training plan should manage.',
    };
  }
  if (back === 'pain' || back === 'sore') {
    return {
      rule: 'R6', verdict: back === 'pain' ? 'QL_PAIN' : 'QL_SORE', data: base,
      action: 'No loaded spinal work today. Machines with full back support, McGill big-3 in the warm-up.',
      rationale: `Back reported ${back}. Loading a spine that is already complaining is how the last flare started.`,
    };
  }
  if (back === 'tight') {
    return {
      rule: 'R6', verdict: 'QL_TIGHT', data: { ...base, until: addDays(f.asOf, 7) },
      action: `Supported and machine variants for 7 days (through ${addDays(f.asOf, 7)}). McGill big-3 in every warm-up.`,
      rationale: 'Tight is the warning shot before a flare. Take the free-weight spinal load out for a week.',
    };
  }
  return {
    rule: 'R6', verdict: 'QL_CLEAR', data: base,
    action: 'Normal exercise selection, minus the permanent contraindications.',
    rationale: 'Back reported fine. Deadlifts, good mornings and loaded rotation stay off the list regardless.',
  };
}

function r7Protein(f: Facts, ds: Dataset): Decision {
  const pct = f.today.proteinPctOfTarget;
  const remaining = f.today.kcalRemaining;
  const gap = f.today.proteinRemaining;
  const socialBudget = remaining + 200;
  const base = {
    hour: f.hour, proteinPctOfTarget: pct, proteinRemaining: gap,
    kcalRemaining: remaining,
    socialMeal: { budgetKcal: socialBudget, borrowedFromTomorrowCarbs: 200 },
  };

  if (f.hour < 14) {
    return {
      rule: 'R7', verdict: 'PROTEIN_EARLY', data: base,
      action: `${f.today.protein}g in, ${gap}g to go on ${remaining} kcal.`,
      rationale: 'Before 14:00 the protein-first gate does not apply yet.',
    };
  }
  if (pct >= 0.45) {
    return {
      rule: 'R7', verdict: 'PROTEIN_ON_TRACK', data: base,
      action: `${f.today.protein}g in (${Math.round(pct * 100)}% of target), ${gap}g on ${remaining} kcal.`,
      rationale: 'Past 14:00 and protein is above 45% of target.',
    };
  }

  const candidates = [
    ...ds.profile.diet.readyToEat,
    ...Object.values(ds.foods).filter((x) => x.zeroCook).map((x) => ({ name: x.name, kcal: x.kcal, p: x.p })),
  ].filter((c) => c.p > 0);
  const fits = candidates.filter((c) => c.kcal <= remaining).sort((a, b) => b.p - a.p);
  const best = fits[0] ?? [...candidates].sort((a, b) => b.p / Math.max(b.kcal, 1) - a.p / Math.max(a.kcal, 1))[0] ?? null;

  return {
    rule: 'R7', verdict: 'PROTEIN_BEHIND', data: { ...base, pick: best, fitsInRemaining: fits.length > 0 },
    action: best
      ? `Eat now: ${best.name} — ${best.kcal} kcal, ${best.p}g protein.${fits.length ? '' : ' It does not fit the remaining budget; it is still the right call — take the kcal overage, not the protein miss.'}`
      : `${gap}g of protein left and nothing in the food library to close it. Name what is nearby.`,
    rationale: `${Math.round(pct * 100)}% of protein at ${Math.floor(f.hour)}:00. Protein missed at 14:00 does not get made up at 21:00.`,
  };
}

function r8Session(inputs: SessionInputs): Decision {
  return {
    rule: 'R8', verdict: inputs.volumeMultiplier < 1 ? 'SESSION_SCALED' : 'SESSION_FULL',
    data: {
      type: inputs.type, timeMin: inputs.timeMin, exerciseCount: inputs.exerciseCount,
      volumeMultiplier: inputs.volumeMultiplier, reasons: inputs.multiplierReasons,
    },
    action: `${inputs.type}: ${inputs.exerciseCount} exercises, working sets x${inputs.volumeMultiplier}, rest 150s compound / 75s isolation.`,
    rationale: inputs.multiplierReasons.join('; '),
  };
}

/* ------------------------------------------------------------------ main */

export function runRules(f: Facts, ds: Dataset): RulesOutput {
  const decisions: Decision[] = [];

  const trend = r1Trend(f);
  decisions.push(trend);

  const sunday = isSunday(f.asOf);
  const governor = sunday ? r4Governor(f) : [];
  const tooSlow = governor.some((g) => g.verdict === 'TOO_SLOW');
  const tooFast = governor.some((g) => g.verdict === 'TOO_FAST');

  const stressTriggered =
    (f.checkins.stress5 !== null && f.checkins.stress5 >= 3.5) || f.checkins.stressNoteHit;
  const r2Applies =
    (trend.verdict === 'NOISE' || trend.verdict === 'STALL' || tooSlow) && stressTriggered;
  const stress = r2Applies ? r2Stress(f) : null;
  if (stress) decisions.push(stress);

  // R3 runs only on a stall (or a governor TOO_SLOW routing into it) with R2 clear,
  // and never while TOO_FAST is asking for calories back.
  const r3Applies = (trend.verdict === 'STALL' || tooSlow) && stress === null && !tooFast;
  if (r3Applies) decisions.push(r3Ladder(f));

  decisions.push(...governor);
  decisions.push(...r5Strength(f));
  decisions.push(r6QL(f));
  decisions.push(r7Protein(f, ds));

  const back = f.checkins.backLast3[0] ?? 'fine';
  const sessionInputs = sessionInputsFor(ds, f);
  const allowedExercises = allowedExercisesFor(ds, sessionInputs.type, back);
  decisions.push(r8Session(sessionInputs));

  return { asOf: f.asOf, decisions, allowedExercises, sessionInputs };
}

const isMain = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const args = process.argv.slice(2);
  const dry = args.includes('--dry');
  const dateArg = args.find((a) => /^\d{4}-\d{2}-\d{2}$/.test(a));
  const ds = loadDataset();
  const facts = derive(ds, dateArg ?? new Date());
  const out = runRules(facts, ds);
  console.log(JSON.stringify(out, null, 2));

  if (!dry) {
    const asOf = dateArg ?? localISODate();
    const already = new Set(
      readJsonl(paths.decisions(), DecisionRow)
        .filter((r) => r.d === asOf)
        .map((r) => `${r.rule}|${r.verdict}|${r.action}`),
    );
    const fresh = out.decisions
      .map((d) => ({ d: asOf, ...d }))
      .filter((r) => !already.has(`${r.rule}|${r.verdict}|${r.action}`));
    appendDecisions(fresh);
  }
}
