import { describe, expect, it } from 'vitest';
import { avgWindow, derive, emergencyPlans, olsSlope, rateFrom, stallStreak } from '../scripts/derive.js';
import { addDays } from '../scripts/dates.js';
import { loadDataset } from '../scripts/io.js';
import { checkin, compliantMeals, ds, session, weightSeries } from './helpers.js';

const TODAY = '2026-10-15';

describe('rolling averages', () => {
  it('needs 5 points in the window', () => {
    const four = weightSeries(TODAY, 4, 200, -0.2);
    expect(avgWindow(four, TODAY)).toBeNull();
    const five = weightSeries(TODAY, 5, 200, -0.2);
    expect(avgWindow(five, TODAY)).toBeCloseTo(199.6, 5);
  });

  it('tolerates gaps as long as 5 points land inside the window', () => {
    // 5 weigh-ins spread over the 7-day window, two days skipped
    const gappy = [
      { d: addDays(TODAY, -6), lb: 210 },
      { d: addDays(TODAY, -5), lb: 209.8 },
      { d: addDays(TODAY, -3), lb: 209.4 },
      { d: addDays(TODAY, -1), lb: 209.0 },
      { d: TODAY, lb: 208.8 },
    ];
    expect(avgWindow(gappy, TODAY)).toBeCloseTo(209.4, 5);
  });

  it('ignores points outside the window', () => {
    const s = [{ d: addDays(TODAY, -7), lb: 300 }, ...weightSeries(TODAY, 5, 200, 0)];
    expect(avgWindow(s, TODAY)).toBe(200);
  });

  it('drops the whole window to null when a gap leaves fewer than 5 points', () => {
    const gappy = [
      { d: addDays(TODAY, -6), lb: 210 },
      { d: addDays(TODAY, -4), lb: 209.6 },
      { d: addDays(TODAY, -2), lb: 209.2 },
      { d: TODAY, lb: 208.9 },
    ];
    expect(avgWindow(gappy, TODAY)).toBeNull();
  });
});

describe('OLS rate', () => {
  it('returns null below 3 points', () => {
    expect(olsSlope([{ x: 0, y: 1 }, { x: 1, y: 2 }])).toBeNull();
    expect(rateFrom(weightSeries(TODAY, 2, 210, -0.2), TODAY)).toBeNull();
  });

  it('recovers a known slope with 5 points', () => {
    // -0.2 lb/day => 1.4 lb/wk of loss
    expect(rateFrom(weightSeries(TODAY, 5, 211, -0.2), TODAY)).toBeCloseTo(1.4, 6);
  });

  it('recovers a known slope with 14 points', () => {
    expect(rateFrom(weightSeries(TODAY, 14, 215, -0.25), TODAY)).toBeCloseTo(1.75, 6);
  });

  it('uses only the last 14 of 30 points', () => {
    // 16 flat days then 14 falling days: the rate must reflect the recent 14 only
    const flat = weightSeries(addDays(TODAY, -14), 16, 220, 0);
    const falling = weightSeries(TODAY, 14, 215, -0.3);
    expect(rateFrom([...flat, ...falling], TODAY)).toBeCloseTo(2.1, 6);
  });

  it('reports a gain as a negative rate', () => {
    expect(rateFrom(weightSeries(TODAY, 7, 200, 0.1), TODAY)).toBeCloseTo(-0.7, 6);
  });

  it('returns null when every point sits on the same day', () => {
    expect(olsSlope([{ x: 5, y: 1 }, { x: 5, y: 2 }, { x: 5, y: 3 }])).toBeNull();
  });
});

describe('projection', () => {
  it('projects the deadline from avg7 and the rate', () => {
    const d = ds({ weights: weightSeries(TODAY, 14, 200, -0.2) });
    const f = derive(d, TODAY);
    expect(f.weight.avg7).not.toBeNull();
    const expected = f.weight.avg7! - f.weight.rateLbWk! * f.weight.weeksLeft;
    expect(f.weight.projectedDec1).toBeCloseTo(Math.round(expected * 10) / 10, 5);
    expect(f.weight.projectedGap).toBeCloseTo(Math.round((expected - 170) * 10) / 10, 5);
  });

  it('is null without enough weigh-ins', () => {
    const f = derive(ds({ weights: weightSeries(TODAY, 3, 200, -0.2) }), TODAY);
    expect(f.weight.projectedDec1).toBeNull();
  });
});

describe('stall streak', () => {
  it('is zero while the average is still dropping', () => {
    expect(stallStreak(weightSeries(TODAY, 30, 215, -0.2), TODAY)).toBe(0);
  });

  it('counts every flat day once the average stops moving', () => {
    expect(stallStreak(weightSeries(TODAY, 40, 205, 0), TODAY)).toBeGreaterThanOrEqual(14);
  });

  it('stops counting where the data runs out', () => {
    expect(stallStreak(weightSeries(TODAY, 10, 205, 0), TODAY)).toBeLessThan(10);
  });
});

describe('adherence', () => {
  it('counts a zero-log day as a failure, not as an absence', () => {
    const meals = compliantMeals(addDays(TODAY, -1), 7).filter((m) => m.d !== addDays(TODAY, -3));
    const f = derive(ds({ meals }), TODAY);
    expect(f.adherenceDays).toHaveLength(7);
    const blank = f.adherenceDays.find((x) => x.d === addDays(TODAY, -3))!;
    expect(blank.logged).toBe(false);
    expect(blank.ok).toBe(false);
    expect(f.adherence7).toBeCloseTo(6 / 7, 2);
    expect(f.adherenceFailDays).toEqual([addDays(TODAY, -3)]);
  });

  it('is 1 on a perfect week and excludes today', () => {
    const f = derive(ds({ meals: compliantMeals(TODAY, 8) }), TODAY);
    expect(f.adherence7).toBe(1);
    expect(f.adherenceDays.some((x) => x.d === TODAY)).toBe(false);
  });

  it('fails a day more than 10% off target', () => {
    const meals = compliantMeals(addDays(TODAY, -1), 7).map((m) =>
      m.d === addDays(TODAY, -2) ? { ...m, kcal: 2100 } : m,
    );
    const f = derive(ds({ meals }), TODAY);
    expect(f.adherenceFailDays).toEqual([addDays(TODAY, -2)]);
  });

  it('fails a day more than 10 g under the protein target', () => {
    const meals = compliantMeals(addDays(TODAY, -1), 7).map((m) =>
      m.d === addDays(TODAY, -2) ? { ...m, p: 169 } : m,
    );
    const f = derive(ds({ meals }), TODAY);
    expect(f.adherenceFailDays).toEqual([addDays(TODAY, -2)]);
    // 170 exactly is still a pass
    const edge = compliantMeals(addDays(TODAY, -1), 7).map((m) =>
      m.d === addDays(TODAY, -2) ? { ...m, p: 170 } : m,
    );
    expect(derive(ds({ meals: edge }), TODAY).adherence7).toBe(1);
  });

  it('is null before anything has been logged', () => {
    expect(derive(ds(), TODAY).adherence7).toBeNull();
  });

  it('only counts days on or after the first ever log', () => {
    const meals = compliantMeals(addDays(TODAY, -1), 3); // logging started 3 days ago
    const f = derive(ds({ meals }), TODAY);
    expect(f.adherenceDays).toHaveLength(3);
    expect(f.adherence7).toBe(1);
  });
});

describe('emergency plans', () => {
  const d = ds({
    foods: {
      'whey shake': { name: 'Whey shake', kcal: 240, p: 48, fat: 3, carb: 6, fiber: 1, fodmap: false, zeroCook: true, count: 5, last: TODAY },
      'rotisserie chicken 6 oz': { name: 'Rotisserie chicken 6 oz', kcal: 280, p: 54, fat: 7, carb: 0, fiber: 0, fodmap: false, zeroCook: true, count: 2, last: TODAY },
      'greek yogurt': { name: 'Greek yogurt', kcal: 200, p: 20, fat: 5, carb: 12, fiber: 0, fodmap: false, zeroCook: true, count: 4, last: TODAY },
      'must not appear': { name: 'Must not appear', kcal: 900, p: 60, fat: 40, carb: 60, fiber: 4, fodmap: false, zeroCook: false, count: 1, last: TODAY },
    },
  });

  it('returns three combos, every one inside +/-5% of target', () => {
    const plans = emergencyPlans(d, 1800, 180);
    expect(plans).toHaveLength(3);
    for (const p of plans) {
      expect(p.kcal).toBeGreaterThanOrEqual(1800 * 0.95);
      expect(p.kcal).toBeLessThanOrEqual(1800 * 1.05);
      expect(p.pctOfTarget).toBeGreaterThanOrEqual(95);
      expect(p.pctOfTarget).toBeLessThanOrEqual(105);
      expect(p.kcal).toBe(p.items.reduce((a, n) => a + itemKcal(d, n), 0));
    }
  });

  it('ranks protein-complete combos first', () => {
    const plans = emergencyPlans(d, 1800, 180);
    expect(plans[0].meetsProtein).toBe(true);
    expect(plans[0].protein).toBeGreaterThanOrEqual(170);
  });

  it('never proposes a food that needs cooking', () => {
    for (const p of emergencyPlans(d, 1800, 180)) {
      expect(p.items).not.toContain('Must not appear');
    }
  });

  it('returns nothing when no combo can land in the band', () => {
    expect(emergencyPlans(d, 120, 180)).toEqual([]);
  });

  function itemKcal(dataset: typeof d, name: string): number {
    const all = [
      ...dataset.profile.diet.readyToEat,
      ...dataset.profile.diet.fixedMeals,
      ...Object.values(dataset.foods).map((f) => ({ name: f.name, kcal: f.kcal })),
    ];
    return all.find((x) => x.name === name)!.kcal;
  }
});

describe('training and lift facts', () => {
  it('counts sessions against the planned week and averages RPE', () => {
    const f = derive(
      ds({
        sessions: [
          session(addDays(TODAY, -1), 'Pull', [{ name: 'Weighted Pull-up', sets: [{ w: 25, r: 8, rpe: 8 }] }], { rpe: 8 }),
          session(addDays(TODAY, -2), 'Legs', [{ name: 'Hack Squat', sets: [{ w: 180, r: 10, rpe: 9 }] }], { rpe: 9 }),
          session(addDays(TODAY, -20), 'Legs', [{ name: 'Hack Squat', sets: [{ w: 180, r: 10, rpe: 8 }] }], { rpe: 8 }),
        ],
      }),
      TODAY,
    );
    expect(f.training.sessionsDone7).toBe(2);
    expect(f.training.sessionsPlanned7).toBe(6);
    expect(f.training.meanRpe7).toBe(8.5);
    expect(f.training.lastSession?.d).toBe(addDays(TODAY, -1));
  });

  it('ignores planned-but-not-done sessions', () => {
    const f = derive(
      ds({ sessions: [session(TODAY, 'Legs', [{ name: 'Hack Squat', sets: [{ w: 180, r: 10, rpe: 8 }] }], { done: false })] }),
      TODAY,
    );
    expect(f.training.sessionsDone7).toBe(0);
    expect(f.lifts.find((l) => l.name === 'Hack Squat')?.currentE1rm).toBeNull();
  });

  it('computes e1RM deltas across the 14-day boundary', () => {
    const f = derive(
      ds({
        sessions: [
          session(addDays(TODAY, -20), 'Legs', [{ name: 'Hack Squat', sets: [{ w: 200, r: 10, rpe: 8 }] }]),
          session(addDays(TODAY, -2), 'Legs', [{ name: 'Hack Squat', sets: [{ w: 180, r: 10, rpe: 8 }] }]),
        ],
      }),
      TODAY,
    );
    const hack = f.lifts.find((l) => l.name === 'Hack Squat')!;
    expect(hack.priorE1rm).toBeCloseTo(266.7, 1);
    expect(hack.currentE1rm).toBeCloseTo(240, 1);
    expect(hack.deltaPct).toBeCloseTo(-10, 1);
  });

  it('rolls the next split day forward once today is done', () => {
    const saturday = '2026-08-22';
    const before = derive(ds(), saturday);
    expect(before.training.nextSplitDay).toEqual({ d: saturday, type: 'Legs' });
    const after = derive(ds({ sessions: [session(saturday, 'Legs', [])] }), saturday);
    expect(after.training.nextSplitDay).toEqual({ d: '2026-08-23', type: 'Rest/Cardio' });
  });
});

describe('effective targets and the ladder', () => {
  it('starts at the profile targets with nothing applied', () => {
    const f = derive(ds(), TODAY);
    expect(f.targets.kcal).toBe(1800);
    expect(f.targets.kcalRestDay).toBe(1800);
    expect(f.ladder.rungsApplied).toEqual([]);
    expect(f.ladder.nextRung).toBe('steps');
    expect(f.ladder.locked).toBe(false);
  });

  it('applies rungs in order and reports the lock', () => {
    const f = derive(
      ds({
        adjustments: [
          { d: addDays(TODAY, -30), kind: 'steps', from: 8000, to: 10000, reason: 'R3', locked_until: addDays(TODAY, -16) },
          { d: addDays(TODAY, -5), kind: 'kcal_rest', from: 1800, to: 1700, reason: 'R3', locked_until: addDays(TODAY, 9) },
        ],
      }),
      TODAY,
    );
    expect(f.targets.stepsPerDay).toBe(10000);
    expect(f.targets.kcalRestDay).toBe(1700);
    expect(f.targets.kcal).toBe(1800);
    expect(f.ladder.rungsApplied).toEqual(['steps', 'kcal_rest']);
    expect(f.ladder.nextRung).toBe('cardio');
    expect(f.ladder.locked).toBe(true);
  });

  it('an all-day cut moves the rest-day target too', () => {
    const f = derive(
      ds({
        adjustments: [
          { d: addDays(TODAY, -20), kind: 'kcal_rest', from: 1800, to: 1700, reason: '', locked_until: addDays(TODAY, -6) },
          { d: addDays(TODAY, -2), kind: 'kcal_all', from: 1800, to: 1700, reason: '', locked_until: addDays(TODAY, 12) },
        ],
      }),
      TODAY,
    );
    expect(f.targets.kcal).toBe(1700);
    expect(f.targets.kcalRestDay).toBe(1600);
  });

  it('a diet break resets the ladder and sets both targets', () => {
    const f = derive(
      ds({
        adjustments: [
          { d: addDays(TODAY, -40), kind: 'steps', from: 8000, to: 10000, reason: '', locked_until: addDays(TODAY, -26) },
          { d: addDays(TODAY, -3), kind: 'diet_break', from: 1600, to: 2400, reason: '', locked_until: addDays(TODAY, 7) },
        ],
      }),
      TODAY,
    );
    expect(f.targets.kcal).toBe(2400);
    expect(f.targets.kcalRestDay).toBe(2400);
    expect(f.ladder.rungsApplied).toEqual([]);
    expect(f.ladder.nextRung).toBe('steps');
  });
});

describe('check-ins and QL history', () => {
  it('averages the last five check-ins and keeps back history newest-first', () => {
    const f = derive(
      ds({
        checkins: [
          checkin(addDays(TODAY, -5), { sleep: 8, stress: 1, energy: 5, back: 'fine' }),
          checkin(addDays(TODAY, -4), { sleep: 6, stress: 4, energy: 3, back: 'fine' }),
          checkin(addDays(TODAY, -3), { sleep: 6, stress: 4, energy: 3, back: 'tight' }),
          checkin(addDays(TODAY, -2), { sleep: 6, stress: 4, energy: 2, back: 'sore' }),
          checkin(addDays(TODAY, -1), { sleep: 6, stress: 5, energy: 2, back: 'pain' }),
        ],
      }),
      TODAY,
    );
    expect(f.checkins.sleep5).toBe(6.4);
    expect(f.checkins.stress5).toBe(3.6);
    expect(f.checkins.backLast3).toEqual(['pain', 'sore', 'tight']);
    expect(f.checkins.painStreak).toBe(1);
  });

  it('counts consecutive pain days', () => {
    const f = derive(
      ds({
        checkins: [
          checkin(addDays(TODAY, -2), { back: 'pain' }),
          checkin(addDays(TODAY, -1), { back: 'pain' }),
        ],
      }),
      TODAY,
    );
    expect(f.checkins.painStreak).toBe(2);
  });

  it('detects a stress note', () => {
    const yes = derive(ds({ checkins: [checkin(TODAY, { note: 'quarter close, slammed at work' })] }), TODAY);
    expect(yes.checkins.stressNoteHit).toBe(true);
    const no = derive(ds({ checkins: [checkin(TODAY, { note: 'felt good' })] }), TODAY);
    expect(no.checkins.stressNoteHit).toBe(false);
  });
});

describe('today and indulgence days', () => {
  it('sums only today and computes what is left', () => {
    const f = derive(
      ds({
        meals: [
          ...compliantMeals(addDays(TODAY, -1), 3),
          { d: TODAY, t: '08:00', name: 'shake', kcal: 240, p: 48, fat: 3, carb: 6, fiber: 1, fodmap: false, restaurant: false, raw: 'shake' },
        ],
      }),
      TODAY,
    );
    expect(f.today.kcal).toBe(240);
    expect(f.today.protein).toBe(48);
    expect(f.today.kcalRemaining).toBe(1560);
    expect(f.today.proteinRemaining).toBe(132);
    expect(f.today.proteinPctOfTarget).toBeCloseTo(0.27, 2);
  });

  it('flags a day with two restaurant meals and a day 400 kcal over', () => {
    const out = { d: addDays(TODAY, -1), t: '19:00', name: 'dinner', kcal: 700, p: 40, fat: 30, carb: 60, fiber: 4, fodmap: false, restaurant: true, raw: 'dinner' };
    const f = derive(
      ds({
        meals: [
          out,
          { ...out, t: '13:00' },
          { d: addDays(TODAY, -2), t: '20:00', name: 'huge', kcal: 2400, p: 120, fat: 90, carb: 220, fiber: 10, fodmap: false, restaurant: false, raw: 'huge' },
          { d: addDays(TODAY, -3), t: '12:00', name: 'fine', kcal: 1800, p: 185, fat: 55, carb: 150, fiber: 30, fodmap: false, restaurant: false, raw: 'fine' },
        ],
      }),
      TODAY,
    );
    expect(f.indulgenceDays.map((x) => x.d).sort()).toEqual([addDays(TODAY, -2), addDays(TODAY, -1)].sort());
  });
});

describe('derive on the seeded repo', () => {
  it('produces a complete Facts object', () => {
    const f = derive(loadDataset(), '2026-08-22');
    expect(f.asOf).toBe('2026-08-22');
    expect(f.weight.avg7).toBe(210);
    expect(f.targets.kcal).toBe(1800);
    expect(f.training.todayType).toBe('Legs');
    expect(f.emergencyPlans.length).toBe(3);
  });
});
