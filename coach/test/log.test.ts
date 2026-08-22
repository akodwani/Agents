import fs from 'node:fs';
import path from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { z } from 'zod';
import { parseArgs, run } from '../scripts/log.js';
import { DEFAULT_ROOT, paths, readJson, readJsonl, setRoot } from '../scripts/io.js';
import {
  AdjustmentRow, CardioRow, CheckinRow, FoodEntry, MealRow, MeasurementRow, PrEntry,
  SessionRow, StepsRow, WeightRow,
} from '../scripts/schema.js';
import { scratchRoot } from './helpers.js';

const NOW = new Date('2026-08-22T10:30:00');
const TODAY = '2026-08-22';

let root: string;
beforeEach(() => {
  root = scratchRoot('log');
  setRoot(root);
});
afterEach(() => {
  setRoot(DEFAULT_ROOT);
  fs.rmSync(root, { recursive: true, force: true });
});

const foods = () => readJson(paths.foods(), z.record(FoodEntry), {});
const prs = () => readJson(paths.prs(), z.record(PrEntry), {});

describe('argument parsing', () => {
  it('splits positionals from flags and handles bare flags', () => {
    expect(parseArgs(['meal', 'chipotle bowl', '700', '68', '--fodmap', '--raw', 'ate a bowl'])).toEqual({
      cmd: 'meal',
      positional: ['chipotle bowl', '700', '68'],
      flags: { fodmap: true, raw: 'ate a bowl' },
    });
  });
});

describe('weight', () => {
  it('appends a validated row', () => {
    const msg = run(['weight', '209.4'], NOW);
    expect(msg).toContain('209.4');
    const rows = readJsonl(paths.weights(), WeightRow);
    expect(rows[rows.length - 1]).toEqual({ d: TODAY, lb: 209.4 });
  });

  it('honours an explicit date', () => {
    run(['weight', '208.8', '--date', '2026-08-23'], NOW);
    expect(readJsonl(paths.weights(), WeightRow).at(-1)!.d).toBe('2026-08-23');
  });

  it('rejects a non-number', () => {
    expect(() => run(['weight', 'heavy'], NOW)).toThrow(/must be a number/);
  });

  it('rejects an out-of-range weight', () => {
    expect(() => run(['weight', '900'], NOW)).toThrow(/invalid weight/);
  });

  it('rejects a malformed date', () => {
    expect(() => run(['weight', '209', '--date', '08/22/2026'], NOW)).toThrow(/YYYY-MM-DD/);
  });
});

describe('meal', () => {
  it('appends the meal and grows the food library', () => {
    const before = foods()['chipotle bowl double chicken rice no beans'].count;
    run(['meal', 'Chipotle bowl double chicken rice no beans', '700', '68'], NOW);
    const after = foods()['chipotle bowl double chicken rice no beans'];
    expect(after.count).toBe(before + 1);
    expect(after.last).toBe(TODAY);
    const meal = readJsonl(paths.meals(), MealRow).at(-1)!;
    expect(meal).toMatchObject({ d: TODAY, t: '10:30', kcal: 700, p: 68 });
  });

  it('learns a brand-new food', () => {
    run(['meal', 'Halal cart chicken over rice', '850', '55', '--fodmap', '--restaurant', '--raw', 'halal cart'], NOW);
    const f = foods()['halal cart chicken over rice'];
    expect(f).toMatchObject({ name: 'Halal cart chicken over rice', kcal: 850, p: 55, fodmap: true, count: 1, last: TODAY });
    expect(readJsonl(paths.meals(), MealRow).at(-1)).toMatchObject({ restaurant: true, fodmap: true, raw: 'halal cart' });
  });

  it('reuses known macros when they are omitted', () => {
    run(['meal', 'Whey shake 2 scoops water'], NOW);
    expect(readJsonl(paths.meals(), MealRow).at(-1)).toMatchObject({ kcal: 240, p: 48 });
  });

  it('rejects an unknown food with no macros', () => {
    expect(() => run(['meal', 'mystery plate'], NOW)).toThrow(/must be a number/);
  });

  it('rejects a meal with no name', () => {
    expect(() => run(['meal'], NOW)).toThrow(/needs a name/);
  });

  it('rejects impossible macros', () => {
    expect(() => run(['meal', 'x', '700', '900'], NOW)).toThrow(/invalid meal/);
  });

  it('reports the day total in one line', () => {
    const msg = run(['meal', 'Whey shake 2 scoops water'], NOW);
    expect(msg).toMatch(/day at \d+\/1800 kcal, \d+\/180p/);
  });
});

describe('checkin', () => {
  it('writes one row per day and replaces a same-day re-log', () => {
    run(['checkin', '--sleep', '6', '--stress', '4', '--energy', '3', '--back', 'tight', '--time', '50', '--note', 'quarter close'], NOW);
    run(['checkin', '--sleep', '7', '--stress', '2', '--energy', '4', '--back', 'fine', '--time', '60'], NOW);
    const rows = readJsonl(paths.checkins(), CheckinRow).filter((c) => c.d === TODAY);
    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({ sleep: 7, stress: 2, back: 'fine' });
  });

  it('rejects an unknown back state', () => {
    expect(() => run(['checkin', '--sleep', '7', '--stress', '2', '--energy', '4', '--back', 'wrecked'], NOW)).toThrow(/invalid checkin/);
  });

  it('rejects an out-of-scale stress value', () => {
    expect(() => run(['checkin', '--sleep', '7', '--stress', '9', '--energy', '4', '--back', 'fine'], NOW)).toThrow(/invalid checkin/);
  });

  it('rejects a missing required field', () => {
    expect(() => run(['checkin', '--sleep', '7'], NOW)).toThrow(/--stress must be a number/);
  });
});

describe('set and session-done', () => {
  it('creates today\'s session, appends sets and records the PR', () => {
    run(['set', 'Incline DB Press', '75', '10', '8'], NOW);
    run(['set', 'Incline DB Press', '75', '9', '9'], NOW);
    const s = readJsonl(paths.sessions(), SessionRow).find((x) => x.d === TODAY)!;
    expect(s.type).toBe('Legs'); // 2026-08-22 is a Saturday
    expect(s.done).toBe(false);
    expect(s.ex).toHaveLength(1);
    expect(s.ex[0].sets).toHaveLength(2);
    expect(prs()['Incline DB Press']).toMatchObject({ w: 75, r: 10, e1rm: 100, d: TODAY });
  });

  it('leaves the PR alone when the set is weaker', () => {
    const before = prs()['Incline DB Press'];
    run(['set', 'Incline DB Press', '50', '5', '7'], NOW);
    expect(prs()['Incline DB Press']).toEqual(before);
  });

  it('records a missed set without crediting a PR', () => {
    run(['set', 'Hack Squat', '400', '10', '10', '--missed'], NOW);
    const s = readJsonl(paths.sessions(), SessionRow).find((x) => x.d === TODAY)!;
    expect(s.ex[0].sets[0].done).toBe(false);
    expect(prs()['Hack Squat'].w).not.toBe(400);
  });

  it('normalises the exercise name to the library spelling', () => {
    run(['set', 'incline db press', '60', '10', '8'], NOW);
    const s = readJsonl(paths.sessions(), SessionRow).find((x) => x.d === TODAY)!;
    expect(s.ex[0].name).toBe('Incline DB Press');
  });

  it('refuses to log a QL-contraindicated lift', () => {
    expect(() => run(['set', 'Conventional Deadlift', '315', '5', '8'], NOW)).toThrow(/contraindicated/i);
  });

  it('rejects a bad RPE', () => {
    expect(() => run(['set', 'Hack Squat', '180', '10', '14'], NOW)).toThrow(/invalid set/);
  });

  it('closes the session with feel and RPE', () => {
    run(['set', 'Hack Squat', '185', '10', '8'], NOW);
    const msg = run(['session-done', '--feel', 'Flat', '--rpe', '8'], NOW);
    const s = readJsonl(paths.sessions(), SessionRow).find((x) => x.d === TODAY)!;
    expect(s).toMatchObject({ done: true, feel: 'Flat', rpe: 8 });
    expect(msg).toContain('closed');
  });

  it('refuses to close a session that was never started', () => {
    expect(() => run(['session-done', '--feel', 'Flat', '--rpe', '8'], NOW)).toThrow(/no session logged/);
  });
});

describe('cardio, steps and measurements', () => {
  it('appends cardio', () => {
    run(['cardio', 'Zone 2', '25'], NOW);
    expect(readJsonl(paths.cardio(), CardioRow).at(-1)).toMatchObject({ d: TODAY, type: 'Zone 2', min: 25 });
  });

  it('keeps one steps row per day', () => {
    run(['steps', '9200'], NOW);
    run(['steps', '11400'], NOW);
    const rows = readJsonl(paths.steps(), StepsRow).filter((s) => s.d === TODAY);
    expect(rows).toEqual([{ d: TODAY, steps: 11400 }]);
  });

  it('merges measurements taken on the same day', () => {
    run(['waist', '35.5'], NOW);
    run(['chest', '41'], NOW);
    const row = readJsonl(paths.measurements(), MeasurementRow).find((m) => m.d === TODAY)!;
    expect(row).toMatchObject({ waist: 35.5, chest: 41 });
  });

  it('rejects an absurd measurement', () => {
    expect(() => run(['waist', '350'], NOW)).toThrow(/invalid measurement/);
  });
});

describe('adjust', () => {
  it('records a ladder rung with a 14-day lock by default', () => {
    run(['adjust', '--kind', 'steps', '--from', '8000', '--to', '10000', '--reason', 'R3 rung 1'], NOW);
    expect(readJsonl(paths.adjustments(), AdjustmentRow).at(-1)).toEqual({
      d: TODAY, kind: 'steps', from: 8000, to: 10000, reason: 'R3 rung 1', locked_until: '2026-09-05',
    });
  });

  it('rejects an unknown rung kind', () => {
    expect(() => run(['adjust', '--kind', 'vibes', '--from', '1', '--to', '2'], NOW)).toThrow(/invalid adjustment/);
  });
});

describe('memory', () => {
  const facts = () => fs.readFileSync(paths.facts(), 'utf8');

  it('appends one categorised, dated line', () => {
    run(['remember', 'Trains at 6am on weekdays', '--category', 'schedule'], NOW);
    expect(facts()).toContain(`- [schedule] Trains at 6am on weekdays (${TODAY})`);
  });

  it('does not duplicate a fact it already holds', () => {
    run(['remember', 'Trains at 6am on weekdays', '--category', 'schedule'], NOW);
    const msg = run(['remember', 'Trains at 6am on weekdays', '--category', 'schedule'], NOW);
    expect(msg).toMatch(/already known/);
    expect(facts().split('Trains at 6am').length - 1).toBe(1);
  });

  it('moves a retired fact to superseded.md instead of deleting it', () => {
    run(['forget', 'Chipotle bowl is the default'], NOW);
    expect(facts()).not.toContain('Chipotle bowl is the default');
    const gone = fs.readFileSync(paths.superseded(), 'utf8');
    expect(gone).toContain('Chipotle bowl is the default');
    expect(gone).toContain(`superseded ${TODAY}`);
  });

  it('refuses to forget something it does not know', () => {
    expect(() => run(['forget', 'never said this'], NOW)).toThrow(/no fact matches/);
  });

  it('rejects an empty fact', () => {
    expect(() => run(['remember', '   '], NOW)).toThrow(/needs a fact/);
  });
});

describe('unknown commands', () => {
  it('lists what it does understand', () => {
    expect(() => run(['yell'], NOW)).toThrow(/unknown command "yell"/);
  });
});

describe('what log.ts writes stays readable by derive', () => {
  it('a full day of logging round-trips through loadDataset', async () => {
    run(['weight', '208.6'], NOW);
    run(['checkin', '--sleep', '6.5', '--stress', '4', '--energy', '3', '--back', 'tight', '--time', '55'], NOW);
    run(['meal', 'Chipotle bowl double chicken rice no beans'], NOW);
    run(['set', 'Hack Squat', '185', '10', '8'], NOW);
    run(['session-done', '--feel', 'Solid', '--rpe', '8'], NOW);
    run(['cardio', 'Zone 2', '20'], NOW);
    run(['steps', '10400'], NOW);

    const { loadDataset } = await import('../scripts/io.js');
    const { derive } = await import('../scripts/derive.js');
    const { runRules } = await import('../scripts/rules.js');
    const d = loadDataset();
    const f = derive(d, TODAY);
    expect(f.weight.latest).toEqual({ d: TODAY, lb: 208.6 });
    expect(f.checkins.latest?.back).toBe('tight');
    expect(f.training.sessionsDone7).toBeGreaterThan(0);
    const out = runRules(f, d);
    expect(out.decisions.find((x) => x.rule === 'R6')!.verdict).toBe('QL_TIGHT');
    expect(out.allowedExercises.list.every((e) => e.spinalLoad !== 'high')).toBe(true);
  });

  it('writes into the scratch root, never the real repo', () => {
    run(['weight', '123.4'], NOW);
    expect(fs.readFileSync(path.join(root, 'data/weights.jsonl'), 'utf8')).toContain('123.4');
    expect(fs.readFileSync(path.join(DEFAULT_ROOT, 'data/weights.jsonl'), 'utf8')).not.toContain('123.4');
  });
});
