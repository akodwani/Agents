import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';
import {
  AdjustmentRow, CardioRow, CheckinRow, DecisionRow, Exercise, ExerciseLibrary, FoodEntry,
  MealRow, MeasurementRow, PrEntry, Profile, SessionRow, StepsRow, WeightRow, zodMessage,
} from './schema.js';

export const DEFAULT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let ROOT = DEFAULT_ROOT;

/** Point the whole IO layer at another directory. Tests use this; the CLI never does. */
export function setRoot(dir: string): void {
  ROOT = path.resolve(dir);
}
export function getRoot(): string {
  return ROOT;
}

export const paths = {
  profile: () => path.join(ROOT, 'data/profile.json'),
  weights: () => path.join(ROOT, 'data/weights.jsonl'),
  meals: () => path.join(ROOT, 'data/meals.jsonl'),
  foods: () => path.join(ROOT, 'data/foods.json'),
  checkins: () => path.join(ROOT, 'data/checkins.jsonl'),
  sessions: () => path.join(ROOT, 'data/sessions.jsonl'),
  prs: () => path.join(ROOT, 'data/prs.json'),
  cardio: () => path.join(ROOT, 'data/cardio.jsonl'),
  steps: () => path.join(ROOT, 'data/steps.jsonl'),
  measurements: () => path.join(ROOT, 'data/measurements.jsonl'),
  adjustments: () => path.join(ROOT, 'data/adjustments.jsonl'),
  decisions: () => path.join(ROOT, 'data/decisions.jsonl'),
  exercises: () => path.join(ROOT, 'lib/exercises.json'),
  facts: () => path.join(ROOT, 'memory/facts.md'),
  superseded: () => path.join(ROOT, 'memory/superseded.md'),
  weekReviews: () => path.join(ROOT, 'memory/week-reviews'),
};

export function readJsonl<S extends z.ZodTypeAny>(file: string, schema: S): z.infer<S>[] {
  if (!fs.existsSync(file)) return [];
  const out: z.infer<S>[] = [];
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    let raw: unknown;
    try {
      raw = JSON.parse(trimmed);
    } catch {
      throw new Error(`${path.basename(file)}:${i + 1} is not valid JSON`);
    }
    const r = schema.safeParse(raw);
    if (!r.success) throw new Error(`${path.basename(file)}:${i + 1} — ${zodMessage(r.error)}`);
    out.push(r.data);
  });
  return out;
}

export function appendJsonl(file: string, row: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, JSON.stringify(row) + '\n', 'utf8');
}

export function writeJsonl(file: string, rows: unknown[]): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, rows.map((r) => JSON.stringify(r)).join('\n') + (rows.length ? '\n' : ''), 'utf8');
}

export function readJson<S extends z.ZodTypeAny>(file: string, schema: S, fallback: z.infer<S>): z.infer<S> {
  if (!fs.existsSync(file)) return fallback;
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  const r = schema.safeParse(raw);
  if (!r.success) throw new Error(`${path.basename(file)} — ${zodMessage(r.error)}`);
  return r.data;
}

export function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

/** Everything derive() and rules() need, loaded once. */
export interface Dataset {
  profile: Profile;
  library: ExerciseLibrary;
  weights: WeightRow[];
  meals: MealRow[];
  foods: Record<string, FoodEntry>;
  checkins: CheckinRow[];
  sessions: SessionRow[];
  prs: Record<string, PrEntry>;
  cardio: CardioRow[];
  steps: StepsRow[];
  measurements: MeasurementRow[];
  adjustments: AdjustmentRow[];
}

const FoodsFile = z.record(FoodEntry);
const PrsFile = z.record(PrEntry);

export function loadDataset(): Dataset {
  return {
    profile: readJson(paths.profile(), Profile, null as unknown as Profile),
    library: readJson(paths.exercises(), ExerciseLibrary, { trackedLifts: [], exercises: [] }),
    weights: readJsonl(paths.weights(), WeightRow),
    meals: readJsonl(paths.meals(), MealRow),
    foods: readJson(paths.foods(), FoodsFile, {}),
    checkins: readJsonl(paths.checkins(), CheckinRow),
    sessions: readJsonl(paths.sessions(), SessionRow),
    prs: readJson(paths.prs(), PrsFile, {}),
    cardio: readJsonl(paths.cardio(), CardioRow),
    steps: readJsonl(paths.steps(), StepsRow),
    measurements: readJsonl(paths.measurements(), MeasurementRow),
    adjustments: readJsonl(paths.adjustments(), AdjustmentRow),
  };
}

/** Build a Dataset for tests without touching disk (library defaults to the real one). */
export function makeDataset(partial: Partial<Dataset> & { profile: Profile }): Dataset {
  return {
    library: { trackedLifts: [], exercises: [] },
    weights: [], meals: [], foods: {}, checkins: [], sessions: [], prs: {},
    cardio: [], steps: [], measurements: [], adjustments: [],
    ...partial,
  };
}

export function appendDecisions(rows: DecisionRow[]): void {
  for (const r of rows) appendJsonl(paths.decisions(), r);
}

export { Exercise };
