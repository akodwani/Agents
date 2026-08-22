import { describe, expect, it } from 'vitest';
import { realLibrary } from './helpers.js';
import { patternsForType } from '../scripts/rules.js';

const lib = realLibrary();

describe('lib/exercises.json', () => {
  it('holds a full library with unique names', () => {
    expect(lib.exercises.length).toBeGreaterThanOrEqual(80);
    const names = lib.exercises.map((e) => e.name);
    expect(new Set(names).size).toBe(names.length);
  });

  it('gives every movement 2-3 real substitutes that are not itself', () => {
    const names = new Set(lib.exercises.map((e) => e.name));
    for (const e of lib.exercises) {
      expect(e.substitutes.length, e.name).toBeGreaterThanOrEqual(2);
      expect(e.substitutes.length, e.name).toBeLessThanOrEqual(3);
      expect(e.substitutes, e.name).not.toContain(e.name);
      for (const s of e.substitutes) expect(names.has(s), `${e.name} -> ${s}`).toBe(true);
    }
  });

  it('gives every movement a coach cue of at most two sentences', () => {
    for (const e of lib.exercises) {
      expect(e.cue.trim().length, e.name).toBeGreaterThan(20);
      const sentences = e.cue.split(/[.!?]+\s/).filter(Boolean);
      expect(sentences.length, `${e.name}: ${e.cue}`).toBeLessThanOrEqual(2);
    }
  });

  it('flags exactly the movements the injury rule forbids', () => {
    const flagged = lib.exercises.filter((e) => e.contraindicated.includes('QL')).map((e) => e.name).sort();
    expect(flagged).toEqual([
      'Barbell Row from Floor', 'Conventional Deadlift', 'Good Morning', 'Hanging Windshield Wiper',
      'Landmine Rotation', 'Loaded Side Bend', 'Meadows Row', 'Romanian Deadlift', 'Russian Twist',
      'Sumo Deadlift',
    ]);
  });

  it('keeps the client\'s allowed hinge set unflagged', () => {
    for (const name of ['Barbell Hip Thrust', 'Machine Hip Thrust', '45-Degree Back Extension', 'Lying Leg Curl', 'Seated Leg Curl', 'Cable Pull-Through', 'Glute Bridge']) {
      const e = lib.exercises.find((x) => x.name === name)!;
      expect(e, name).toBeDefined();
      expect(e.contraindicated, name).not.toContain('QL');
    }
  });

  it('tracks the six R5 lifts and they all exist', () => {
    expect(lib.trackedLifts).toEqual([
      'Incline DB Press', 'Weighted Pull-up', 'Chest-Supported Row', 'Hack Squat', 'Barbell Hip Thrust', 'Seated DB OHP',
    ]);
    for (const n of lib.trackedLifts) expect(lib.exercises.some((e) => e.name === n), n).toBe(true);
  });

  it('carries the McGill big-3', () => {
    expect(lib.exercises.filter((e) => e.mcgill).map((e) => e.name).sort()).toEqual(['Bird Dog', 'Dead Bug', 'Side Plank']);
  });

  it('covers every split day with enough movements to build a session', () => {
    for (const type of ['Push+Abs', 'Pull', 'Legs', 'Rest/Cardio']) {
      const pats = patternsForType(type);
      const available = lib.exercises.filter((e) => pats.includes(e.pattern) && !e.contraindicated.includes('QL'));
      expect(available.length, type).toBeGreaterThanOrEqual(7);
    }
  });

  it('has a sane rep range on every movement', () => {
    for (const e of lib.exercises) {
      expect(e.repRange[0], e.name).toBeGreaterThan(0);
      expect(e.repRange[1], e.name).toBeGreaterThan(e.repRange[0]);
    }
  });
});
