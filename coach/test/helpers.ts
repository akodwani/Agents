import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { DEFAULT_ROOT, Dataset, makeDataset } from '../scripts/io.js';
import { ExerciseLibrary, Profile } from '../scripts/schema.js';
import { ISODate, addDays } from '../scripts/dates.js';

/** The real seeded profile, parsed through zod so defaults apply. */
export function baseProfile(over: Partial<Profile> = {}): Profile {
  const raw = JSON.parse(fs.readFileSync(path.join(DEFAULT_ROOT, 'data/profile.json'), 'utf8'));
  return { ...Profile.parse(raw), ...over };
}

export function realLibrary(): ExerciseLibrary {
  return ExerciseLibrary.parse(JSON.parse(fs.readFileSync(path.join(DEFAULT_ROOT, 'lib/exercises.json'), 'utf8')));
}

export function ds(partial: Partial<Dataset> = {}): Dataset {
  return makeDataset({ profile: baseProfile(), library: realLibrary(), ...partial });
}

/** n daily weigh-ins ending on `end`, starting at `start` lb and moving by `perDay`. */
export function weightSeries(end: ISODate, n: number, start: number, perDay: number) {
  return Array.from({ length: n }, (_, i) => ({
    d: addDays(end, -(n - 1 - i)),
    lb: Math.round((start + perDay * i) * 100) / 100,
  }));
}

/** Perfectly compliant meal days across [end-n+1, end]. */
export function compliantMeals(end: ISODate, n: number, kcal = 1800, p = 185) {
  return Array.from({ length: n }, (_, i) => ({
    d: addDays(end, -(n - 1 - i)),
    t: '12:00',
    name: 'compliant day',
    kcal,
    p,
    fat: 55,
    carb: 150,
    fiber: 30,
    fodmap: false,
    restaurant: false,
    raw: 'compliant day',
  }));
}

export function checkin(d: ISODate, over: Partial<{ sleep: number; stress: number; energy: number; back: string; time_min: number; note: string }> = {}) {
  return {
    d, sleep: 7.5, stress: 2, energy: 4, back: 'fine' as const, time_min: 60, note: '',
    ...over,
  } as any;
}

export function session(d: ISODate, type: string, ex: { name: string; sets: { w: number; r: number; rpe: number; done?: boolean }[] }[], over: Partial<{ rpe: number; feel: string; done: boolean }> = {}) {
  return {
    d, type,
    ex: ex.map((e) => ({ name: e.name, sets: e.sets.map((s) => ({ done: true, ...s })) })),
    feel: 'ok', rpe: 8, notes: '', done: true,
    ...over,
  } as any;
}

/** Copy the real repo (data, lib, memory) into a scratch dir for log.ts tests. */
export function scratchRoot(tag: string): string {
  const dir = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), `coach-${tag}-`));
  for (const sub of ['data', 'lib', 'memory']) {
    fs.cpSync(path.join(DEFAULT_ROOT, sub), path.join(dir, sub), { recursive: true });
  }
  return dir;
}
