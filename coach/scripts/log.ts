/**
 * log.ts — the only way data enters the repo. Everything is zod-validated.
 *
 *   npx tsx scripts/log.ts weight 209.4
 *   npx tsx scripts/log.ts meal "chipotle bowl double chicken" 700 68
 *   npx tsx scripts/log.ts checkin --sleep 6 --stress 4 --energy 3 --back tight --time 50 --note "..."
 *   npx tsx scripts/log.ts set "Incline DB Press" 70 10 8
 *   npx tsx scripts/log.ts session-done --feel Flat --rpe 8
 *   npx tsx scripts/log.ts cardio "Zone 2" 25
 *   npx tsx scripts/log.ts steps 9200
 *   npx tsx scripts/log.ts waist 35.5
 *   npx tsx scripts/log.ts adjust --kind steps --from 8000 --to 10000 --reason "R3 rung 1"
 *   npx tsx scripts/log.ts remember "Hates seated cable rows"
 *   npx tsx scripts/log.ts forget "Chipotle bowl is the default"
 */
import fs from 'node:fs';
import { z } from 'zod';
import {
  AdjustmentRow, CardioRow, CheckinRow, ExerciseLibrary, FoodEntry, MealRow, MeasurementRow,
  PrEntry, Profile, SessionRow, SetRow, StepsRow, WeightRow, parseOrThrow,
} from './schema.js';
import { appendJsonl, paths, readJson, readJsonl, writeJson, writeJsonl } from './io.js';
import { ISODate, dowOf, localISODate, toDayNum } from './dates.js';

/* ---------------------------------------------------------------- parsing */

export interface Args {
  cmd: string;
  positional: string[];
  flags: Record<string, string | boolean>;
}

export function parseArgs(argv: string[]): Args {
  const [cmd = '', ...rest] = argv;
  const positional: string[] = [];
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = rest[i + 1];
      if (next === undefined || next.startsWith('--')) flags[key] = true;
      else {
        flags[key] = next;
        i++;
      }
    } else positional.push(a);
  }
  return { cmd, positional, flags };
}

const num = (v: unknown, what: string): number => {
  const n = Number(v);
  if (v === undefined || v === '' || Number.isNaN(n)) throw new Error(`${what} must be a number, got ${JSON.stringify(v)}`);
  return n;
};
const str = (v: unknown, fallback = ''): string => (typeof v === 'string' ? v : fallback);
const canonical = (s: string) => s.trim().toLowerCase().replace(/\s+/g, ' ');

function nowClock(now: Date): string {
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

const FoodsFile = z.record(FoodEntry);
const PrsFile = z.record(PrEntry);

function e1rm(w: number, r: number): number {
  return Math.round(w * (1 + r / 30) * 10) / 10;
}

/* ------------------------------------------------------------- the writes */

export function run(argv: string[], now: Date = new Date()): string {
  const { cmd, positional, flags } = parseArgs(argv);
  const d: ISODate = str(flags.date, localISODate(now));
  const profile = readJson(paths.profile(), Profile, null as unknown as Profile);

  switch (cmd) {
    /* ----------------------------------------------------------- weight */
    case 'weight': {
      const row = parseOrThrow(WeightRow, { d, lb: num(positional[0], 'weight (lb)') }, 'weight');
      appendJsonl(paths.weights(), row);
      return `weight ${row.lb} lb logged for ${row.d}`;
    }

    /* ------------------------------------------------------------- meal */
    case 'meal': {
      const name = positional[0];
      if (!name) throw new Error('meal needs a name: log.ts meal "<name>" <kcal> <protein>');
      const known = readJson(paths.foods(), FoodsFile, {});
      const hit = known[canonical(name)];
      const row = parseOrThrow(
        MealRow,
        {
          d,
          t: str(flags.time, nowClock(now)),
          name,
          kcal: positional[1] !== undefined ? num(positional[1], 'kcal') : hit?.kcal ?? num(undefined, 'kcal'),
          p: positional[2] !== undefined ? num(positional[2], 'protein') : hit?.p ?? num(undefined, 'protein'),
          fat: flags.fat !== undefined ? num(flags.fat, 'fat') : hit?.fat ?? 0,
          carb: flags.carb !== undefined ? num(flags.carb, 'carb') : hit?.carb ?? 0,
          fiber: flags.fiber !== undefined ? num(flags.fiber, 'fiber') : hit?.fiber ?? 0,
          fodmap: flags.fodmap === true || flags.fodmap === 'true' || (hit?.fodmap ?? false),
          restaurant: flags.restaurant === true || flags.restaurant === 'true',
          raw: str(flags.raw, name),
        },
        'meal',
      );
      appendJsonl(paths.meals(), row);

      const key = canonical(name);
      known[key] = parseOrThrow(
        FoodEntry,
        {
          name: hit?.name ?? name,
          kcal: row.kcal, p: row.p, fat: row.fat, carb: row.carb, fiber: row.fiber,
          fodmap: row.fodmap,
          zeroCook: hit?.zeroCook ?? true,
          count: (hit?.count ?? 0) + 1,
          last: d,
        },
        'food library entry',
      );
      writeJson(paths.foods(), known);
      const today = readJsonl(paths.meals(), MealRow).filter((m) => m.d === d);
      const kcal = today.reduce((a, m) => a + m.kcal, 0);
      const p = today.reduce((a, m) => a + m.p, 0);
      const target = profile.targets;
      return `${row.name} logged: ${row.kcal} kcal / ${row.p}p${row.fodmap ? ' (FODMAP flag)' : ''} — day at ${kcal}/${target.kcal} kcal, ${p}/${target.proteinG}p`;
    }

    /* ---------------------------------------------------------- checkin */
    case 'checkin': {
      const row = parseOrThrow(
        CheckinRow,
        {
          d,
          sleep: num(flags.sleep, '--sleep'),
          stress: num(flags.stress, '--stress'),
          energy: num(flags.energy, '--energy'),
          back: str(flags.back, 'fine'),
          time_min: num(flags.time ?? 60, '--time'),
          note: str(flags.note),
        },
        'checkin',
      );
      const rows = readJsonl(paths.checkins(), CheckinRow).filter((c) => c.d !== d);
      writeJsonl(paths.checkins(), [...rows, row].sort((a, b) => toDayNum(a.d) - toDayNum(b.d)));
      return `checkin ${row.d}: sleep ${row.sleep}h, stress ${row.stress}, energy ${row.energy}, back ${row.back}, ${row.time_min} min`;
    }

    /* -------------------------------------------------------------- set */
    case 'set': {
      const name = positional[0];
      if (!name) throw new Error('set needs an exercise: log.ts set "<exercise>" <w> <r> <rpe>');
      const lib = readJson(paths.exercises(), ExerciseLibrary, { trackedLifts: [], exercises: [] });
      const known = lib.exercises.find((e) => canonical(e.name) === canonical(name));
      if (known?.contraindicated.includes('QL')) {
        throw new Error(`${known.name} is contraindicated (QL). It does not get logged and it does not get programmed.`);
      }
      const set = parseOrThrow(
        SetRow,
        {
          w: num(positional[1], 'weight'),
          r: num(positional[2], 'reps'),
          rpe: num(positional[3], 'rpe'),
          done: !(flags.missed === true || flags.missed === 'true'),
        },
        'set',
      );

      const sessions = readJsonl(paths.sessions(), SessionRow);
      let session = sessions.find((s) => s.d === d);
      if (!session) {
        session = parseOrThrow(
          SessionRow,
          { d, type: str(flags.type, profile.split[String(dowOf(d))] ?? 'Session'), ex: [], done: false },
          'session',
        );
        sessions.push(session);
      }
      const exName = known?.name ?? name;
      let ex = session.ex.find((e) => canonical(e.name) === canonical(exName));
      if (!ex) {
        ex = { name: exName, sets: [] };
        session.ex.push(ex);
      }
      ex.sets.push(set);
      writeJsonl(paths.sessions(), sessions.sort((a, b) => toDayNum(a.d) - toDayNum(b.d)));

      let prLine = '';
      if (set.done && set.r > 0) {
        const prs = readJson(paths.prs(), PrsFile, {});
        const e = e1rm(set.w, set.r);
        const cur = prs[exName];
        if (!cur || e > cur.e1rm) {
          prs[exName] = parseOrThrow(PrEntry, { w: set.w, r: set.r, e1rm: e, d }, 'pr');
          writeJson(paths.prs(), prs);
          prLine = cur ? ` — PR, e1RM ${cur.e1rm} → ${e}` : ` — first entry, e1RM ${e}`;
        }
      }
      return `${exName} set ${ex.sets.length}: ${set.w} x ${set.r} @ RPE ${set.rpe}${set.done ? '' : ' (missed)'}${prLine}`;
    }

    /* ----------------------------------------------------- session-done */
    case 'session-done': {
      const sessions = readJsonl(paths.sessions(), SessionRow);
      const session = sessions.find((s) => s.d === d);
      if (!session) throw new Error(`no session logged for ${d} — log a set first`);
      session.done = true;
      session.feel = str(flags.feel, session.feel);
      session.rpe = flags.rpe !== undefined ? num(flags.rpe, '--rpe') : session.rpe;
      session.notes = str(flags.notes, session.notes);
      parseOrThrow(SessionRow, session, 'session');
      writeJsonl(paths.sessions(), sessions);
      const sets = session.ex.reduce((a, e) => a + e.sets.length, 0);
      return `session ${d} closed: ${session.type}, ${session.ex.length} exercises, ${sets} sets, feel ${session.feel || 'n/a'}, RPE ${session.rpe ?? 'n/a'}`;
    }

    /* ------------------------------------------------------------ cardio */
    case 'cardio': {
      const row = parseOrThrow(
        CardioRow,
        { d, type: positional[0] ?? '', min: num(positional[1], 'minutes'), note: str(flags.note) },
        'cardio',
      );
      appendJsonl(paths.cardio(), row);
      return `cardio logged: ${row.type} ${row.min} min on ${row.d}`;
    }

    /* ------------------------------------------------------------- steps */
    case 'steps': {
      const row = parseOrThrow(StepsRow, { d, steps: num(positional[0], 'steps') }, 'steps');
      const rows = readJsonl(paths.steps(), StepsRow).filter((s) => s.d !== d);
      writeJsonl(paths.steps(), [...rows, row].sort((a, b) => toDayNum(a.d) - toDayNum(b.d)));
      return `${row.steps} steps logged for ${row.d}`;
    }

    /* ------------------------------------------------------ measurements */
    case 'waist':
    case 'chest':
    case 'arm':
    case 'thigh':
    case 'hips': {
      const rows = readJsonl(paths.measurements(), MeasurementRow);
      const existing = rows.find((m) => m.d === d);
      const merged = { ...(existing ?? { d }), [cmd]: num(positional[0], cmd) };
      const row = parseOrThrow(MeasurementRow, merged, 'measurement');
      writeJsonl(
        paths.measurements(),
        [...rows.filter((m) => m.d !== d), row].sort((a, b) => toDayNum(a.d) - toDayNum(b.d)),
      );
      return `${cmd} ${row[cmd as 'waist']} in logged for ${row.d}`;
    }

    /* ------------------------------------------------------- adjustments */
    case 'adjust': {
      const row = parseOrThrow(
        AdjustmentRow,
        {
          d,
          kind: str(flags.kind),
          from: num(flags.from, '--from'),
          to: num(flags.to, '--to'),
          reason: str(flags.reason),
          locked_until: str(flags['locked-until'], addDaysISO(d, 14)),
        },
        'adjustment',
      );
      appendJsonl(paths.adjustments(), row);
      return `adjustment ${row.kind}: ${row.from} → ${row.to}, locked until ${row.locked_until}`;
    }

    /* ------------------------------------------------------------ memory */
    case 'remember': {
      const fact = positional[0];
      if (!fact || !fact.trim()) throw new Error('remember needs a fact');
      const category = str(flags.category, 'note');
      const line = `- [${category}] ${fact.trim()} (${d})`;
      const existing = fs.existsSync(paths.facts()) ? fs.readFileSync(paths.facts(), 'utf8') : '';
      if (existing.split('\n').some((l) => canonical(l) === canonical(line))) return `already known: ${line}`;
      fs.appendFileSync(paths.facts(), (existing.endsWith('\n') || !existing ? '' : '\n') + line + '\n', 'utf8');
      return `remembered: ${line}`;
    }

    case 'forget': {
      const needle = positional[0];
      if (!needle || !needle.trim()) throw new Error('forget needs a substring to match');
      const lines = fs.existsSync(paths.facts()) ? fs.readFileSync(paths.facts(), 'utf8').split('\n') : [];
      const hit = lines.filter((l) => l.toLowerCase().includes(needle.trim().toLowerCase()) && l.trim());
      if (!hit.length) throw new Error(`no fact matches "${needle}"`);
      const kept = lines.filter((l) => !hit.includes(l));
      fs.writeFileSync(paths.facts(), kept.join('\n').replace(/\n{3,}/g, '\n\n'), 'utf8');
      const stamp = hit.map((l) => `${l}  <- superseded ${d}`).join('\n');
      fs.appendFileSync(paths.superseded(), stamp + '\n', 'utf8');
      return `superseded ${hit.length} fact(s):\n${hit.join('\n')}`;
    }

    default:
      throw new Error(
        `unknown command "${cmd}". Try: weight | meal | checkin | set | session-done | cardio | steps | waist | adjust | remember | forget`,
      );
  }
}

function addDaysISO(d: ISODate, n: number): ISODate {
  const t = new Date(`${d}T12:00:00Z`);
  t.setUTCDate(t.getUTCDate() + n);
  return t.toISOString().slice(0, 10);
}

const isMain = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  try {
    console.log(run(process.argv.slice(2)));
  } catch (err) {
    console.error(`error: ${(err as Error).message}`);
    process.exit(1);
  }
}
