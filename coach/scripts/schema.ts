import { z } from 'zod';

const iso = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'date must be YYYY-MM-DD');
const clock = z.string().regex(/^\d{2}:\d{2}$/, 'time must be HH:MM');

export const BackState = z.enum(['fine', 'tight', 'sore', 'pain']);
export type BackState = z.infer<typeof BackState>;

export const WeightRow = z.object({
  d: iso,
  lb: z.number().min(80).max(500),
});
export type WeightRow = z.infer<typeof WeightRow>;

export const MealRow = z.object({
  d: iso,
  t: clock,
  name: z.string().min(1),
  kcal: z.number().min(0).max(6000),
  p: z.number().min(0).max(400),
  fat: z.number().min(0).max(400).default(0),
  carb: z.number().min(0).max(800).default(0),
  fiber: z.number().min(0).max(200).default(0),
  fodmap: z.boolean().default(false),
  /** true when eaten out — feeds R2 check 2 (water retention). */
  restaurant: z.boolean().default(false),
  raw: z.string().default(''),
});
export type MealRow = z.infer<typeof MealRow>;

export const FoodEntry = z.object({
  name: z.string().min(1),
  kcal: z.number().min(0),
  p: z.number().min(0),
  fat: z.number().min(0).default(0),
  carb: z.number().min(0).default(0),
  fiber: z.number().min(0).default(0),
  fodmap: z.boolean().default(false),
  zeroCook: z.boolean().default(true),
  count: z.number().int().min(0).default(1),
  last: iso,
});
export type FoodEntry = z.infer<typeof FoodEntry>;

export const CheckinRow = z.object({
  d: iso,
  sleep: z.number().min(0).max(14),
  stress: z.number().int().min(1).max(5),
  energy: z.number().int().min(1).max(5),
  back: BackState,
  time_min: z.number().int().min(0).max(240),
  note: z.string().default(''),
});
export type CheckinRow = z.infer<typeof CheckinRow>;

export const SetRow = z.object({
  w: z.number().min(0).max(1000),
  r: z.number().int().min(0).max(100),
  rpe: z.number().min(1).max(10),
  done: z.boolean().default(true),
});
export type SetRow = z.infer<typeof SetRow>;

export const ExerciseLog = z.object({
  name: z.string().min(1),
  sets: z.array(SetRow).default([]),
});
export type ExerciseLog = z.infer<typeof ExerciseLog>;

export const SessionRow = z.object({
  d: iso,
  type: z.string().min(1),
  ex: z.array(ExerciseLog).default([]),
  feel: z.string().default(''),
  rpe: z.number().min(1).max(10).nullable().default(null),
  notes: z.string().default(''),
  /** false while the session is only planned. */
  done: z.boolean().default(false),
});
export type SessionRow = z.infer<typeof SessionRow>;

export const PrEntry = z.object({
  w: z.number().min(0),
  r: z.number().int().min(0),
  e1rm: z.number().min(0),
  d: iso,
});
export type PrEntry = z.infer<typeof PrEntry>;

export const CardioRow = z.object({
  d: iso,
  type: z.string().min(1),
  min: z.number().min(0).max(600),
  note: z.string().default(''),
});
export type CardioRow = z.infer<typeof CardioRow>;

export const StepsRow = z.object({ d: iso, steps: z.number().int().min(0).max(120000) });
export type StepsRow = z.infer<typeof StepsRow>;

export const MeasurementRow = z.object({
  d: iso,
  waist: z.number().min(10).max(80).nullable().default(null),
  chest: z.number().min(10).max(80).nullable().default(null),
  arm: z.number().min(5).max(40).nullable().default(null),
  thigh: z.number().min(10).max(50).nullable().default(null),
  hips: z.number().min(10).max(80).nullable().default(null),
});
export type MeasurementRow = z.infer<typeof MeasurementRow>;

/** Ladder / governor rungs. `from`/`to` are numbers in the rung's own unit. */
export const AdjustmentKind = z.enum([
  'steps',
  'cardio',
  'kcal_rest',
  'kcal_all',
  'diet_break',
  'governor_kcal',
]);
export type AdjustmentKind = z.infer<typeof AdjustmentKind>;

export const AdjustmentRow = z.object({
  d: iso,
  kind: AdjustmentKind,
  from: z.number(),
  to: z.number(),
  reason: z.string().default(''),
  locked_until: iso,
});
export type AdjustmentRow = z.infer<typeof AdjustmentRow>;

export const DecisionRow = z.object({
  d: iso,
  rule: z.string(),
  verdict: z.string(),
  data: z.record(z.any()).default({}),
  action: z.string(),
  rationale: z.string(),
});
export type DecisionRow = z.infer<typeof DecisionRow>;

export const Profile = z.object({
  name: z.string(),
  age: z.number(),
  heightIn: z.number(),
  sex: z.string(),
  startWeightLb: z.number(),
  startDate: iso,
  goalWeightLb: z.number(),
  goalBodyFatPct: z.number(),
  deadline: iso,
  aesthetic: z.string(),
  targets: z.object({ kcal: z.number(), proteinG: z.number(), fatG: z.number(), fiberG: z.number() }),
  floors: z.object({ kcal: z.number(), proteinG: z.number() }),
  split: z.record(z.string()),
  gym: z.string(),
  cardioMenu: z.array(z.string()),
  injuries: z.array(z.object({ site: z.string(), rule: z.string() })),
  diet: z.object({
    style: z.string(),
    avoid: z.array(z.string()),
    fixedMeals: z.array(z.object({ name: z.string(), kcal: z.number(), p: z.number() })),
    readyToEat: z.array(z.object({ name: z.string(), kcal: z.number(), p: z.number() })),
    rule: z.string(),
  }),
  supplements: z.array(z.string()),
  life: z.string(),
  /** Baselines the R3 ladder moves off. Optional so the seed file stays as specified. */
  baseline: z
    .object({ stepsPerDay: z.number(), cardioMinPerWk: z.number() })
    .default({ stepsPerDay: 8000, cardioMinPerWk: 60 }),
});
export type Profile = z.infer<typeof Profile>;

export const Exercise = z.object({
  name: z.string(),
  pattern: z.string(),
  equipment: z.string(),
  contraindicated: z.array(z.string()).default([]),
  substitutes: z.array(z.string()).default([]),
  cue: z.string(),
  /** How much the movement loads the spine — drives the R6 back-state filter. */
  spinalLoad: z.enum(['none', 'low', 'high']).default('low'),
  supported: z.boolean().default(false),
  repRange: z.tuple([z.number(), z.number()]).default([8, 12]),
  mcgill: z.boolean().default(false),
});
export type Exercise = z.infer<typeof Exercise>;

export const ExerciseLibrary = z.object({
  trackedLifts: z.array(z.string()),
  exercises: z.array(Exercise),
});
export type ExerciseLibrary = z.infer<typeof ExerciseLibrary>;

/** Formats a zod failure as one terminal line. */
export function zodMessage(err: z.ZodError): string {
  return err.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ');
}

export function parseOrThrow<S extends z.ZodTypeAny>(schema: S, value: unknown, what: string): z.infer<S> {
  const r = schema.safeParse(value);
  if (!r.success) throw new Error(`invalid ${what} — ${zodMessage(r.error)}`);
  return r.data;
}
