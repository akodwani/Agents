import { describe, expect, it } from 'vitest';
import { derive, Facts } from '../scripts/derive.js';
import { allowedExercisesFor, r2Stress, r3Ladder, runRules, sessionInputsFor, suggestLoad } from '../scripts/rules.js';
import { addDays } from '../scripts/dates.js';
import { Dataset } from '../scripts/io.js';
import { checkin, compliantMeals, ds, session, weightSeries } from './helpers.js';

const SAT = '2026-10-17'; // Saturday
const SUN = '2026-10-18'; // Sunday — the governor only runs today

function verdictOf(out: { decisions: { rule: string; verdict: string }[] }, rule: string): string | undefined {
  return out.decisions.find((d) => d.rule === rule)?.verdict;
}
function decisionOf(out: { decisions: any[] }, rule: string) {
  return out.decisions.find((d) => d.rule === rule);
}

/** A dataset that is losing weight cleanly, fully adherent, calm, training on plan. */
function healthy(over: Partial<Dataset> = {}, asOf = SAT): Dataset {
  return ds({
    weights: weightSeries(asOf, 30, 220, -0.15),
    meals: compliantMeals(asOf, 10),
    checkins: [1, 2, 3, 4, 5].map((i) => checkin(addDays(asOf, -i))),
    sessions: [1, 2, 3, 4, 5].map((i) =>
      session(addDays(asOf, -i), 'Pull', [{ name: 'Weighted Pull-up', sets: [{ w: 25, r: 8, rpe: 8 }] }], { rpe: 8 }),
    ),
    ...over,
  });
}

/** Falling, then 18 flat days: both 7-day averages are flat but the streak is still under 14. */
function noisy(over: Partial<Dataset> = {}, asOf = SAT): Dataset {
  return healthy(
    { weights: [...weightSeries(addDays(asOf, -18), 22, 215, -0.3), ...weightSeries(asOf, 18, 208, 0)], ...over },
    asOf,
  );
}

/** 30 days of flat weight: guarantees stallStreakDays >= 14. */
function flat(over: Partial<Dataset> = {}, asOf = SAT): Dataset {
  return healthy({ weights: weightSeries(asOf, 40, 205, 0), ...over }, asOf);
}

function run(d: Dataset, asOf = SAT) {
  return runRules(derive(d, asOf), d);
}

/* ------------------------------------------------------------------- R1 */

describe('R1 Trend', () => {
  it('INSUFFICIENT_DATA when a window is short', () => {
    expect(verdictOf(run(ds({ weights: weightSeries(SAT, 4, 210, -0.2) })), 'R1')).toBe('INSUFFICIENT_DATA');
  });

  it('ON_PACE when the 7-day average dropped at least 0.5 lb', () => {
    const out = run(healthy());
    expect(verdictOf(out, 'R1')).toBe('ON_PACE');
    expect(decisionOf(out, 'R1').data.drop).toBeGreaterThanOrEqual(0.5);
  });

  it('NOISE when the drop is small but the flat run is under 14 days', () => {
    const out = run(noisy());
    expect(verdictOf(out, 'R1')).toBe('NOISE');
    expect(decisionOf(out, 'R1').data.stallStreakDays).toBeLessThan(14);
  });

  it('STALL at 14+ flat days with adherence >= 0.9', () => {
    const out = run(flat());
    expect(verdictOf(out, 'R1')).toBe('STALL');
    expect(decisionOf(out, 'R1').data.adherence7).toBeGreaterThanOrEqual(0.9);
  });

  it('UNDER_ADHERENCE at 14+ flat days with adherence < 0.9', () => {
    const sloppy = compliantMeals(addDays(SAT, -1), 7).map((m, i) => (i < 3 ? { ...m, kcal: 2600 } : m));
    const out = run(flat({ meals: sloppy }));
    expect(verdictOf(out, 'R1')).toBe('UNDER_ADHERENCE');
    expect(decisionOf(out, 'R1').action).toMatch(/No calorie cut/i);
  });

  it('INSUFFICIENT_DATA at 14+ flat days with no intake logged at all', () => {
    const out = run(flat({ meals: [] }));
    expect(verdictOf(out, 'R1')).toBe('INSUFFICIENT_DATA');
  });
});

/* ------------------------------------------------------------------- R2 */

describe('R2 Stress protocol', () => {
  const stressCheckins = (over: Record<string, unknown> = {}) =>
    [1, 2, 3, 4, 5].map((i) => checkin(addDays(SAT, -i), { stress: 4, ...over }));

  /** Stalled (14+ flat days) and stressed. Adherence stays clean unless overridden. */
  const stressed = (over: Partial<Dataset> = {}) => flat({ checkins: stressCheckins(), ...over });

  /** Noise (streak < 14) and stressed — the only route to a verdict that needs poor adherence. */
  const stressedNoise = (over: Partial<Dataset> = {}) => noisy({ checkins: stressCheckins(), ...over });

  it('does not fire on ON_PACE even under stress', () => {
    const out = run(healthy({ checkins: [1, 2, 3, 4, 5].map((i) => checkin(addDays(SAT, -i), { stress: 5 })) }));
    expect(verdictOf(out, 'R1')).toBe('ON_PACE');
    expect(decisionOf(out, 'R2')).toBeUndefined();
  });

  it('does not fire on a stall with calm inputs and no stress note', () => {
    const out = run(flat());
    expect(decisionOf(out, 'R2')).toBeUndefined();
    expect(decisionOf(out, 'R3')).toBeDefined();
  });

  it('fires on a stress note even when stress5 is below 3.5', () => {
    const out = run(
      flat({ checkins: [1, 2, 3, 4, 5].map((i) => checkin(addDays(SAT, -i), { stress: 2, note: i === 1 ? 'brutal week at work' : '' })) }),
    );
    expect(decisionOf(out, 'R2')).toBeDefined();
  });

  it('check 1 — SLEEP_DEFICIT stops the protocol first', () => {
    // every later check is also failing; sleep must still win
    const bad = compliantMeals(addDays(SAT, -1), 7).map((m, i) => (i < 4 ? { ...m, kcal: 2600, restaurant: true } : m));
    const out = run(
      stressedNoise({ checkins: stressCheckins({ sleep: 5 }), meals: bad, sessions: [] }),
    );
    const d = decisionOf(out, 'R2');
    expect(d.verdict).toBe('SLEEP_DEFICIT');
    expect(d.data.check).toBe(1);
    expect(d.action).toMatch(/No diet change/i);
  });

  it('check 2 — WATER_RETENTION_LIKELY once sleep is fine', () => {
    // the same compliant day, eaten out across two meals: adherence is still perfect
    const meals = compliantMeals(addDays(SAT, -1), 7).flatMap((m) =>
      m.d === addDays(SAT, -1)
        ? [
            { ...m, t: '13:00', kcal: m.kcal / 2, p: m.p / 2, restaurant: true },
            { ...m, t: '20:00', kcal: m.kcal / 2, p: m.p / 2, restaurant: true },
          ]
        : [m],
    );
    const out = run(stressed({ meals }));
    const d = decisionOf(out, 'R2');
    expect(d.verdict).toBe('WATER_RETENTION_LIKELY');
    expect(d.data.check).toBe(2);
    expect(d.action).toMatch(/whoosh/i);
  });

  it('check 3 — ADHERENCE_GAP names the days', () => {
    const meals = compliantMeals(addDays(SAT, -1), 7).map((m, i) => (i < 3 ? { ...m, p: 100 } : m));
    const out = run(stressedNoise({ meals }));
    const d = decisionOf(out, 'R2');
    expect(d.verdict).toBe('ADHERENCE_GAP');
    expect(d.data.check).toBe(3);
    expect((d.data.failDays as string[]).length).toBe(3);
    for (const day of d.data.failDays as string[]) expect(d.rationale).toContain(day);
  });

  it('check 4 — TRAINING_DROP on missed sessions', () => {
    const out = run(stressed({ sessions: [session(addDays(SAT, -1), 'Pull', [], { rpe: 8 })] }));
    const d = decisionOf(out, 'R2');
    expect(d.verdict).toBe('TRAINING_DROP');
    expect(d.data.check).toBe(4);
  });

  it('check 4 — TRAINING_DROP on soft sessions', () => {
    const out = run(
      stressed({
        sessions: [1, 2, 3, 4, 5].map((i) =>
          session(addDays(SAT, -i), 'Pull', [{ name: 'Weighted Pull-up', sets: [{ w: 25, r: 8, rpe: 5 }] }], { rpe: 5 }),
        ),
      }),
    );
    expect(decisionOf(out, 'R2').verdict).toBe('TRAINING_DROP');
  });

  it('check 5 — CORTISOL_LOAD when everything else is clean, and it holds carbs', () => {
    const out = run(stressed());
    const d = decisionOf(out, 'R2');
    expect(d.verdict).toBe('CORTISOL_LOAD');
    expect(d.data.check).toBe(5);
    expect(d.action).toMatch(/carbs held/i);
    expect(d.action).toMatch(/no extra cardio/i);
    expect(d.data.lockUntil).toBe(addDays(SAT, 7));
  });

  it('blocks the ladder whenever it fires', () => {
    const out = run(stressed());
    expect(decisionOf(out, 'R2')).toBeDefined();
    expect(decisionOf(out, 'R3')).toBeUndefined();
  });
});

/* ------------------------------------------------------------------- R3 */

describe('R3 Ladder', () => {
  it('only runs on a stall', () => {
    expect(decisionOf(run(healthy()), 'R3')).toBeUndefined();
  });

  it('rung 1 is steps, +2000, locked 14 days', () => {
    const d = decisionOf(run(flat()), 'R3');
    expect(d.verdict).toBe('RUNG_STEPS');
    expect(d.data.from).toBe(8000);
    expect(d.data.to).toBe(10000);
    expect(d.data.lockUntil).toBe(addDays(SAT, 14));
  });

  it('rung 2 is Zone 2 cardio', () => {
    const d = decisionOf(
      run(flat({ adjustments: [{ d: addDays(SAT, -20), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -6) }] })),
      'R3',
    );
    expect(d.verdict).toBe('RUNG_CARDIO');
    expect(d.data.to).toBe(120);
  });

  it('rung 3 cuts rest days only', () => {
    const d = decisionOf(
      run(
        flat({
          adjustments: [
            { d: addDays(SAT, -40), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -26) },
            { d: addDays(SAT, -20), kind: 'cardio', from: 60, to: 120, reason: '', locked_until: addDays(SAT, -6) },
          ],
        }),
      ),
      'R3',
    );
    expect(d.verdict).toBe('RUNG_KCAL_REST');
    expect(d.data.from).toBe(1800);
    expect(d.data.to).toBe(1700);
    expect(d.action).toMatch(/Training days unchanged/i);
  });

  it('rung 4 cuts every day', () => {
    const d = decisionOf(
      run(
        flat({
          adjustments: [
            { d: addDays(SAT, -60), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -46) },
            { d: addDays(SAT, -40), kind: 'cardio', from: 60, to: 120, reason: '', locked_until: addDays(SAT, -26) },
            { d: addDays(SAT, -20), kind: 'kcal_rest', from: 1800, to: 1700, reason: '', locked_until: addDays(SAT, -6) },
          ],
        }),
      ),
      'R3',
    );
    expect(d.verdict).toBe('RUNG_KCAL_ALL');
    expect(d.data.to).toBe(1700);
  });

  it('is blocked inside the 14-day lock', () => {
    const d = decisionOf(
      run(flat({ adjustments: [{ d: addDays(SAT, -3), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, 11) }] })),
      'R3',
    );
    expect(d.verdict).toBe('LADDER_LOCKED');
    expect(d.action).toContain(addDays(SAT, 11));
  });

  it('unlocks on the day the lock expires', () => {
    const d = decisionOf(
      run(flat({ adjustments: [{ d: addDays(SAT, -14), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: SAT }] })),
      'R3',
    );
    expect(d.verdict).toBe('RUNG_CARDIO');
  });

  it('the kcal floor blocks a cut and calls a diet break instead', () => {
    const f = derive(
      flat({
        adjustments: [
          { d: addDays(SAT, -60), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -46) },
          { d: addDays(SAT, -50), kind: 'cardio', from: 60, to: 120, reason: '', locked_until: addDays(SAT, -36) },
          { d: addDays(SAT, -30), kind: 'kcal_rest', from: 1800, to: 1700, reason: '', locked_until: addDays(SAT, -16) },
          { d: addDays(SAT, -20), kind: 'kcal_all', from: 1800, to: 1650, reason: '', locked_until: addDays(SAT, -6) },
          { d: addDays(SAT, -19), kind: 'kcal_all', from: 1650, to: 1650, reason: 'noop', locked_until: addDays(SAT, -6) },
        ],
      }),
      SAT,
    ) as Facts;
    // targets are at 1650; every rung is spent, so the next move is a diet break
    expect(f.targets.kcal).toBe(1650);
    const d = r3Ladder(f);
    expect(d.verdict).toBe('DIET_BREAK');
    expect(d.data.kcal).toBe(Math.round(f.weight.avg7! * 11.5));
  });

  it('never proposes a target under the floor', () => {
    const f = derive(
      flat({
        adjustments: [
          { d: addDays(SAT, -60), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -46) },
          { d: addDays(SAT, -50), kind: 'cardio', from: 60, to: 120, reason: '', locked_until: addDays(SAT, -36) },
          { d: addDays(SAT, -30), kind: 'kcal_rest', from: 1800, to: 1650, reason: '', locked_until: addDays(SAT, -16) },
        ],
      }),
      SAT,
    ) as Facts;
    // rest days are at 1650; the next rung (all days, -100) would land at 1700 -> fine,
    // but the rest-day target would fall to 1550, under the 1600 floor.
    const d = r3Ladder(f);
    if (d.verdict.startsWith('RUNG')) {
      expect(d.data.to as number).toBeGreaterThanOrEqual(f.floors.kcal);
    } else {
      expect(d.verdict).toBe('DIET_BREAK');
    }
  });
});

/* ------------------------------------------------------------------- R4 */

describe('R4 Governor', () => {
  it('does not run on a weekday', () => {
    expect(decisionOf(run(healthy()), 'R4a')).toBeUndefined();
  });

  it('TOO_FAST adds 125 kcal and locks 14 days', () => {
    const d = decisionOf(run(healthy({ weights: weightSeries(SUN, 30, 230, -0.45) }, SUN), SUN), 'R4a');
    expect(d.verdict).toBe('TOO_FAST');
    expect(d.data.to).toBe(1925);
    expect(d.data.lockUntil).toBe(addDays(SUN, 14));
  });

  it('TOO_SLOW routes into the stress protocol and the ladder', () => {
    const slow = healthy({ weights: weightSeries(SUN, 30, 205, -0.05) }, SUN);
    const out = run(slow, SUN);
    expect(verdictOf(out, 'R4a')).toBe('TOO_SLOW');
    // no stress trigger here, so it lands on the ladder directly
    expect(decisionOf(out, 'R3')).toBeDefined();
  });

  it('TOO_SLOW with stress routes into R2, not the ladder', () => {
    const slow = healthy(
      {
        weights: weightSeries(SUN, 30, 205, -0.05),
        checkins: [1, 2, 3, 4, 5].map((i) => checkin(addDays(SUN, -i), { stress: 4, sleep: 5 })),
      },
      SUN,
    );
    const out = run(slow, SUN);
    expect(verdictOf(out, 'R4a')).toBe('TOO_SLOW');
    expect(decisionOf(out, 'R2').verdict).toBe('SLEEP_DEFICIT');
    expect(decisionOf(out, 'R3')).toBeUndefined();
  });

  it('PACE_OK inside the 1.0-2.5 lb/wk band', () => {
    expect(verdictOf(run(healthy({ weights: weightSeries(SUN, 30, 220, -0.2) }, SUN), SUN), 'R4a')).toBe('PACE_OK');
  });

  it('OFF_TRACK presents exactly three options and refuses to pick', () => {
    const d = decisionOf(run(healthy({ weights: weightSeries(SUN, 30, 205, -0.02) }, SUN), SUN), 'R4b');
    expect(d.verdict).toBe('OFF_TRACK');
    const options = d.data.options as { id: string; label: string; cost: string }[];
    expect(options).toHaveLength(3);
    expect(options.map((o) => o.id)).toEqual(['keep_pace', 'go_faster', 'move_date']);
    for (const o of options) {
      expect(o.label.length).toBeGreaterThan(0);
      expect(o.cost.length).toBeGreaterThan(0);
    }
    expect(d.action).toMatch(/Do not choose for him/i);
    expect(d.data.governorCap).toBe(2.5);
  });

  it('never lets go_faster exceed the governor cap', () => {
    const d = decisionOf(run(healthy({ weights: weightSeries(SUN, 30, 205, -0.02) }, SUN), SUN), 'R4b');
    const faster = (d.data.options as any[]).find((o) => o.id === 'go_faster');
    const claimed = Number(faster.label.match(/([\d.]+) lb\/wk/)?.[1] ?? 0);
    expect(claimed).toBeLessThanOrEqual(2.5);
  });

  it('PROJECTION_OK when the projection lands on goal', () => {
    // dropping fast enough to reach 170 by the deadline
    expect(verdictOf(run(healthy({ weights: weightSeries(SUN, 30, 180, -0.2) }, SUN), SUN), 'R4b')).toBe('PROJECTION_OK');
  });

  it('TOO_FAST suppresses the ladder', () => {
    const d = healthy({ weights: weightSeries(SUN, 40, 235, -0.45) }, SUN);
    const out = run(d, SUN);
    expect(verdictOf(out, 'R4a')).toBe('TOO_FAST');
    expect(decisionOf(out, 'R3')).toBeUndefined();
  });
});

/* ------------------------------------------------------------------- R5 */

describe('R5 Strength', () => {
  const drop = (name: string, pct: number) => [
    session(addDays(SAT, -20), 'X', [{ name, sets: [{ w: 200, r: 10, rpe: 8 }] }]),
    session(addDays(SAT, -2), 'X', [{ name, sets: [{ w: Math.round(200 * (1 + pct / 100)), r: 10, rpe: 8 }] }]),
  ];

  it('UNDER_RECOVERY when two tracked lifts are down more than 10%', () => {
    const out = run(healthy({ sessions: [...drop('Hack Squat', -15), ...drop('Chest-Supported Row', -14)], cardio: [{ d: addDays(SAT, -1), type: 'Zone 2', min: 100, note: '' }] }));
    const d = decisionOf(out, 'R5a');
    expect(d.verdict).toBe('UNDER_RECOVERY');
    expect(d.data.cardioTo).toBe(70);
    expect(d.action).toMatch(/No food change/i);
  });

  it('STRENGTH_HOLDING when only one lift is down', () => {
    expect(verdictOf(run(healthy({ sessions: drop('Hack Squat', -15) })), 'R5a')).toBe('STRENGTH_HOLDING');
  });

  it('INSUFFICIENT_DATA with no 14-day comparison', () => {
    expect(verdictOf(run(healthy()), 'R5a')).toBe('INSUFFICIENT_DATA');
  });

  it('CARDIO_CAP over 240 min/wk with any lift down', () => {
    const out = run(
      healthy({
        sessions: drop('Hack Squat', -3),
        cardio: [1, 2, 3].map((i) => ({ d: addDays(SAT, -i), type: 'Zone 2', min: 90, note: '' })),
      }),
    );
    const d = decisionOf(out, 'R5b');
    expect(d.verdict).toBe('CARDIO_CAP');
    expect(d.data.cardioMin7).toBe(270);
  });

  it('no CARDIO_CAP when every lift is holding', () => {
    const out = run(
      healthy({
        sessions: drop('Hack Squat', +3),
        cardio: [1, 2, 3].map((i) => ({ d: addDays(SAT, -i), type: 'Zone 2', min: 90, note: '' })),
      }),
    );
    expect(decisionOf(out, 'R5b')).toBeUndefined();
  });
});

/* ------------------------------------------------------------------- R6 */

describe('R6 QL', () => {
  const CONTRA = ['Conventional Deadlift', 'Sumo Deadlift', 'Romanian Deadlift', 'Good Morning', 'Barbell Row from Floor', 'Russian Twist', 'Loaded Side Bend', 'Hanging Windshield Wiper', 'Landmine Rotation'];

  it('filters every QL-contraindicated movement out of the allowed list, on every split day and back state', () => {
    for (const type of ['Push+Abs', 'Pull', 'Legs', 'Rest/Cardio']) {
      for (const back of ['fine', 'tight', 'sore', 'pain'] as const) {
        const a = allowedExercisesFor(ds(), type, back);
        const names = a.list.map((e) => e.name);
        for (const bad of CONTRA) expect(names).not.toContain(bad);
        for (const e of a.list) expect(e.contraindicated).not.toContain('QL');
      }
    }
  });

  it('names the QL exclusions with a reason', () => {
    const a = allowedExercisesFor(ds(), 'Legs', 'fine');
    const ql = a.excluded.filter((x) => x.reason.includes('QL'));
    expect(ql.map((x) => x.name)).toEqual(expect.arrayContaining(['Conventional Deadlift', 'Good Morning', 'Romanian Deadlift']));
  });

  it('keeps the allowed hinge set available on leg day', () => {
    const names = allowedExercisesFor(ds(), 'Legs', 'fine').list.map((e) => e.name);
    expect(names).toEqual(expect.arrayContaining(['Barbell Hip Thrust', '45-Degree Back Extension', 'Lying Leg Curl', 'Cable Pull-Through', 'Glute Bridge']));
  });

  it('QL_CLEAR on a fine back, with no forced warm-up', () => {
    const out = run(healthy({ checkins: [checkin(SAT, { back: 'fine' })] }));
    expect(verdictOf(out, 'R6')).toBe('QL_CLEAR');
    expect(out.allowedExercises.warmup).toEqual([]);
  });

  it('QL_TIGHT drops high-spinal-load work for 7 days and adds the McGill big-3', () => {
    const out = run(healthy({ checkins: [checkin(SAT, { back: 'tight' })] }));
    const d = decisionOf(out, 'R6');
    expect(d.verdict).toBe('QL_TIGHT');
    expect(d.data.until).toBe(addDays(SAT, 7));
    expect(out.allowedExercises.warmup.map((w) => w.name).sort()).toEqual(['Bird Dog', 'Dead Bug', 'Side Plank']);
    expect(out.allowedExercises.list.every((e) => e.spinalLoad !== 'high')).toBe(true);
  });

  it('QL_SORE removes all loaded spinal work', () => {
    const out = run(healthy({ checkins: [checkin(SAT, { back: 'sore' })] }));
    expect(verdictOf(out, 'R6')).toBe('QL_SORE');
    expect(out.allowedExercises.list.every((e) => e.spinalLoad === 'none')).toBe(true);
  });

  it('QL_PAIN on one day, clinician referral on two', () => {
    const one = run(healthy({ checkins: [checkin(addDays(SAT, -1), { back: 'fine' }), checkin(SAT, { back: 'pain' })] }));
    expect(verdictOf(one, 'R6')).toBe('QL_PAIN');
    const two = run(healthy({ checkins: [checkin(addDays(SAT, -1), { back: 'pain' }), checkin(SAT, { back: 'pain' })] }));
    const d = decisionOf(two, 'R6');
    expect(d.verdict).toBe('QL_PAIN_CLINICIAN');
    expect(d.action).toMatch(/clinician/i);
  });
});

/* ------------------------------------------------------------------- R7 */

describe('R7 Protein-first', () => {
  const withMeals = (kcal: number, p: number) =>
    healthy({
      meals: [
        ...compliantMeals(addDays(SAT, -1), 7),
        { d: SAT, t: '09:00', name: 'breakfast', kcal, p, fat: 5, carb: 10, fiber: 1, fodmap: false, restaurant: false, raw: 'breakfast' },
      ],
    });

  const at = (hour: number, asOf = SAT) => new Date(`${asOf}T${String(hour).padStart(2, '0')}:00:00`);

  it('PROTEIN_EARLY before 14:00 regardless of protein', () => {
    const d = withMeals(300, 10);
    expect(verdictOf(runRules(derive(d, at(9)), d), 'R7')).toBe('PROTEIN_EARLY');
  });

  it('PROTEIN_BEHIND after 14:00 under 45% of target, with one concrete pick', () => {
    const d = withMeals(300, 10);
    const dec = decisionOf(runRules(derive(d, at(15)), d), 'R7');
    expect(dec.verdict).toBe('PROTEIN_BEHIND');
    expect(dec.data.pick).not.toBeNull();
    expect((dec.data.pick as any).p).toBeGreaterThan(0);
    expect(dec.action).toContain((dec.data.pick as any).name);
  });

  it('PROTEIN_ON_TRACK at or above 45%', () => {
    const d = withMeals(600, 81); // 81/180 = 45%
    expect(verdictOf(runRules(derive(d, at(15)), d), 'R7')).toBe('PROTEIN_ON_TRACK');
  });

  it('the pick fits the remaining kcal when anything does', () => {
    const d = withMeals(300, 10);
    const dec = decisionOf(runRules(derive(d, at(15)), d), 'R7');
    expect(dec.data.fitsInRemaining).toBe(true);
    expect((dec.data.pick as any).kcal).toBeLessThanOrEqual(dec.data.kcalRemaining as number);
  });

  it('still names a pick and owns the overage when nothing fits', () => {
    const d = withMeals(1750, 10);
    const dec = decisionOf(runRules(derive(d, at(15)), d), 'R7');
    expect(dec.verdict).toBe('PROTEIN_BEHIND');
    expect(dec.data.fitsInRemaining).toBe(false);
    expect(dec.action).toMatch(/take the kcal overage, not the protein miss/i);
  });

  it('offers a social-meal budget of remaining + 200 borrowed, never a refusal', () => {
    const d = withMeals(600, 81);
    const dec = decisionOf(runRules(derive(d, at(15)), d), 'R7');
    const social = dec.data.socialMeal as { budgetKcal: number; borrowedFromTomorrowCarbs: number };
    expect(social.borrowedFromTomorrowCarbs).toBe(200);
    expect(social.budgetKcal).toBe((dec.data.kcalRemaining as number) + 200);
  });
});

/* ------------------------------------------------------------------- R8 */

describe('R8 Session inputs', () => {
  const withCheckin = (over: Record<string, unknown>) => healthy({ checkins: [checkin(SAT, over)] });

  it('takes the type from the split', () => {
    expect(sessionInputsFor(healthy(), derive(healthy(), SAT)).type).toBe('Legs'); // 2026-10-17 is a Saturday
  });

  it('lets a check-in note override the split', () => {
    const d = withCheckin({ note: 'shoulder day, doing push instead' });
    expect(sessionInputsFor(d, derive(d, SAT)).type).toBe('Push+Abs');
  });

  it('scales volume by sleep, stress and energy, and never below 0.6', () => {
    const cases: [Record<string, unknown>, number][] = [
      [{}, 1],
      [{ sleep: 5 }, 0.7],
      [{ stress: 4 }, 0.8],
      [{ energy: 2 }, 0.75],
      [{ sleep: 5, stress: 4 }, 0.56],
      [{ sleep: 5, stress: 5, energy: 1 }, 0.42],
    ];
    for (const [over, raw] of cases) {
      const d = withCheckin(over);
      const got = sessionInputsFor(d, derive(d, SAT)).volumeMultiplier;
      expect(got).toBe(Math.max(0.6, Math.round(raw * 100) / 100));
    }
  });

  it('sets exercise count from available time', () => {
    for (const [time, count] of [[30, 4], [45, 4], [50, 5], [60, 5], [70, 6], [90, 7]] as [number, number][]) {
      const d = withCheckin({ time_min: time });
      expect(sessionInputsFor(d, derive(d, SAT)).exerciseCount).toBe(count);
    }
  });

  it('prescribes 150s compound / 75s isolation rest', () => {
    expect(sessionInputsFor(healthy(), derive(healthy(), SAT)).restSeconds).toEqual({ compound: 150, isolation: 75 });
  });

  it('never suggests a load for a QL-contraindicated lift', () => {
    const d = healthy({
      sessions: [session(addDays(SAT, -2), 'Legs', [{ name: 'Conventional Deadlift', sets: [{ w: 315, r: 5, rpe: 8 }] }])],
    });
    expect(sessionInputsFor(d, derive(d, SAT)).loads.map((l) => l.name)).not.toContain('Conventional Deadlift');
  });
});

describe('load progression', () => {
  const lift = 'Hack Squat'; // repRange [8, 12]
  const s = (d: string, w: number, r: number, rpe: number, done = true) =>
    session(d, 'Legs', [{ name: lift, sets: [{ w, r, rpe, done }] }]);

  it('starts conservative with no history', () => {
    const out = suggestLoad(ds(), lift, SAT);
    expect(out.suggestedLoad).toBeNull();
    expect(out.reason).toMatch(/RPE 7/);
  });

  it('holds the load while reps are still climbing', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -3), 180, 9, 8)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(180);
    expect(out.reason).toMatch(/add reps/);
  });

  it('adds 2.5% after two sessions at the top of the range', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -7), 180, 12, 9), s(addDays(SAT, -3), 180, 12, 9)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(185);
    expect(out.reason).toMatch(/2\.5%/);
  });

  it('adds 5% when those two sessions were easy', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -7), 180, 12, 8), s(addDays(SAT, -3), 180, 12, 8)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(190);
    expect(out.reason).toMatch(/5%/);
  });

  it('backs off 5% after an RPE 9.5+ top set', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -3), 180, 10, 9.5)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(170);
    expect(out.reason).toMatch(/RPE >= 9\.5/);
  });

  it('backs off 5% after missed reps', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -3), 180, 6, 9)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(170);
    expect(out.reason).toMatch(/missed reps/);
  });

  it('still moves the bar on light loads where 2.5% rounds to nothing', () => {
    const out = suggestLoad(ds({ sessions: [s(addDays(SAT, -7), 25, 12, 9), s(addDays(SAT, -3), 25, 12, 9)] }), lift, SAT);
    expect(out.suggestedLoad).toBe(27.5);
  });
});

/* -------------------------------------------------------------- integration */

describe('the whole engine', () => {
  it('always returns a verdict for R1, R6, R7 and R8', () => {
    const out = run(healthy());
    for (const rule of ['R1', 'R5a', 'R6', 'R7', 'R8']) expect(decisionOf(out, rule)).toBeDefined();
  });

  it('every decision carries an action and a rationale', () => {
    for (const dataset of [healthy(), flat(), healthy({ weights: weightSeries(SUN, 30, 205, -0.02) }, SUN)]) {
      for (const d of runRules(derive(dataset, SUN), dataset).decisions) {
        expect(d.action.trim().length).toBeGreaterThan(0);
        expect(d.rationale.trim().length).toBeGreaterThan(0);
        expect(d.rule).toMatch(/^R[1-8][ab]?$/);
      }
    }
  });

  it('never proposes a kcal target below the floor, at any rung', () => {
    const rungs = [
      { d: addDays(SAT, -60), kind: 'steps' as const, from: 8000, to: 10000, reason: '', locked_until: addDays(SAT, -46) },
      { d: addDays(SAT, -50), kind: 'cardio' as const, from: 60, to: 120, reason: '', locked_until: addDays(SAT, -36) },
      { d: addDays(SAT, -40), kind: 'kcal_rest' as const, from: 1800, to: 1700, reason: '', locked_until: addDays(SAT, -26) },
      { d: addDays(SAT, -30), kind: 'kcal_all' as const, from: 1800, to: 1700, reason: '', locked_until: addDays(SAT, -16) },
    ];
    for (let n = 0; n <= rungs.length; n++) {
      // r3Ladder directly: runRules gates it on the trend verdict, which is not what is under test
      const d = r3Ladder(derive(flat({ adjustments: rungs.slice(0, n) }), SAT));
      expect(d).toBeDefined();
      if (typeof d.data.to === 'number' && String(d.verdict).includes('KCAL')) {
        expect(d.data.to).toBeGreaterThanOrEqual(1600);
      }
      if (d.verdict === 'DIET_BREAK') expect(d.data.kcal).toBeGreaterThan(1600);
    }
  });
});
