# NOTES — assumptions and interpretations

The brief left some things underspecified. Every judgement call is listed here with what was chosen and why.
Anything marked **CHANGE ME** is a one-line edit if the intent was different.

## Structure

1. **`coach/` is a self-contained subproject.** The repo root already held an unrelated Electron/Python
   workspace, so `coach/` has its own `package.json`, `node_modules`, `tsconfig.json` and test runner. Run
   everything from inside `coach/`.
2. **Dependencies.** Runtime: `zod` only. Dev: `tsx`, `vitest`, and `@types/node` (a types-only package needed
   for `fs`/`process` under `strict`; nothing ships from it). `vitest` is pinned to v4 — v2 pulled a `vite`
   with open advisories.
3. **Shared modules beyond the three named scripts.** `scripts/dates.ts`, `scripts/schema.ts` and
   `scripts/io.ts` exist so the three CLIs and the tests share one date implementation, one set of zod schemas
   and one IO layer. `derive`/`rules` are exported as pure functions over an in-memory `Dataset`; the CLI
   wrapper at the bottom of each file is the only part that touches disk.

## Dates

4. **All dates are `YYYY-MM-DD` strings**, converted through UTC-noon so DST never moves a day boundary.
   "Today" is the machine's local calendar date. Both `derive.ts` and `rules.ts` accept a date argument for
   backfill and review.
5. **The 14:00 gate in R7 uses local clock time.** Passing a date string instead of a `Date` pins the hour to
   12:00, which keeps tests deterministic.

## profile.json

6. **Seeded byte-for-byte as specified.** The ladder needs baselines the brief did not give, so
   `Profile.baseline` defaults in the schema to `{ stepsPerDay: 8000, cardioMinPerWk: 60 }` rather than being
   written into the seed file. Add a `baseline` key to `profile.json` to override. **CHANGE ME** if Avi's real
   baseline differs — rung 1 and rung 2 move off these numbers.

## derive.ts

7. **`avg7` / `avg7prev` windows** are `[asOf-6, asOf]` and `[asOf-13, asOf-7]`, each needing ≥5 weigh-ins.
   Fewer than 5 → `null`, and the whole downstream chain reports `INSUFFICIENT_DATA` rather than guessing.
8. **`rateLbWk` is positive when losing.** The brief's `projectedDec1 = avg7 − rate × weeksLeft` only works
   with that sign, and R4's `rate > 2.5` reads naturally. A gain shows as a negative rate.
9. **The OLS fit needs ≥3 points** (2 points is a line through 2 points, not a trend) and uses the last 14
   weigh-ins on or before the date. `rateLbWkPrev` is the same fit ending 7 days earlier — that is what makes
   R4's "two weeks running" testable.
10. **`stallStreakDays`** walks back day by day comparing `avg7(d)` against `avg7(d-7)` and stops at the first
    day with a ≥0.5 lb drop, or where either window is short. Capped at 120 iterations.
11. **`adherence7` uses the last seven *complete* days, `[asOf-7, asOf-1]`.** Today is excluded: judging
    adherence at 08:00 against a full-day target would fail every morning. The denominator is the days in that
    window on or after the first ever meal log, so a zero-log day inside the tracked span counts as a
    **failure**, while days before Avi started logging are not counted at all. No logs ever → `null`.
12. **A day passes** when kcal is within ±10% of that day's target *and* protein ≥ target − 10 g. Rest days
    use the rest-day target once rung 3 is applied.
13. **`sleep5` / `stress5` / `energy5` are means over the last five check-ins**, not the last five calendar
    days — a skipped check-in shouldn't dilute the average toward zero.
14. **`sessionsPlanned7`** counts the days in the last 7 whose split label is not a rest day (6/week on the
    seeded split). `sessionsDone7` counts sessions with `done: true`; a session written as a plan does not
    count until it is closed with `session-done`.
15. **e1RM = `w × (1 + r/30)`** (Epley), max over completed sets. `currentE1rm` is the best in the last 14
    days; `priorE1rm` is the best in the 14 days before that. `deltaPct` is `null` unless both exist — R5 never
    fires on a comparison it cannot make.
16. **`steps7` is the mean of logged days** (the useful number against a per-day target); `stepsTotal7` is
    also exposed.
17. **"Restaurant/untracked meal" is the explicit `restaurant` flag on the meal row**, set by
    `log.ts --restaurant`. A deliberately narrow keyword fallback catches an obvious miss
    (`restaurant`, `takeout`, `delivery`, `ate out`, `brunch`, `halal cart`, `buffet`, `bar tab`). Staple names
    are **not** in that list — the Chipotle bowl has known macros and is part of the plan, not an untracked meal.
18. **`emergencyPlans`** enumerates 2–4 zero-cook items (max 2 of any one item) from `readyToEat` + `fixedMeals`
    + `zeroCook` entries in `foods.json`, keeps combos within ±5% of the day's kcal, and ranks
    protein-complete first, then protein, then fewest items. Returns up to 3; returns `[]` honestly when
    nothing lands in the band.
19. **Effective targets are replayed from `adjustments.jsonl` chronologically.** `kcal_rest` moves rest days
    only; `kcal_all` and `governor_kcal` move both; `diet_break` sets both absolutely and resets the ladder.
    That composes correctly when rungs stack.

## rules.ts

20. **Rule ids are `R1`–`R8`**, with `R4a`/`R4b` (pace vs projection) and `R5a`/`R5b` (under-recovery vs cardio
    cap) split because each can fire independently.
21. **Output shape is `{ asOf, decisions, allowedExercises, sessionInputs }`.** The brief asks for
    `Decision[]` plus `allowedExercises` and `sessionInputs`; this is those three, addressable.
22. **R2's trigger** is `stress5 ≥ 3.5` **or** a stress word in the latest check-in note
    (`stress|work|deadline|boss|swamped|slammed|overtime|crunch|anxious|burned out`).
23. **R2 only reaches `ADHERENCE_GAP` on a `NOISE` trend.** On a stall, adherence < 0.9 already routes R1 to
    `UNDER_ADHERENCE`, which is a stronger statement than R2 check 3. Both paths refuse to change the plan.
24. **R3 requires R2 to have not fired at all.** A `CORTISOL_LOAD` verdict locks diet changes for 7 days, so
    every R2 outcome blocks the ladder. R3 also stands down while R4a says `TOO_FAST` — the governor is
    asking for calories back, and the two must not fight.
25. **Rung 2 adds 60 min/wk** ("+20 min Z2 3×/wk"). Rungs 3 and 4 cut 100 kcal, described as coming off carbs.
26. **The floor blocks the cut, not the rung.** If the next kcal rung would land under `floors.kcal` (1600),
    R3 returns `DIET_BREAK` at `avg7 × 11.5` for 7–10 days, and `diet_break` in the adjustment log resets the
    ladder to rung 1.
27. **R4 runs on Sundays only.** `TOO_FAST` and `TOO_SLOW` each need the condition true in both the current
    and the prior week's rate. `OFF_TRACK` returns exactly three options with ids `keep_pace`, `go_faster`,
    `move_date`, each with a stated cost, `go_faster` capped at the 2.5 lb/wk governor, and an action line that
    says not to choose. The engine never picks.
28. **R5's cardio cut is 30% of the last 7 days' actual cardio minutes**, since there is no prescribed weekly
    cardio number before rung 2 is applied.
29. **R6 filters in three layers**: QL-contraindicated movements are removed always; `back: tight` also removes
    `spinalLoad: "high"`; `back: sore|pain` removes anything with any spinal load. `exercises.json` therefore
    carries two fields beyond the brief's list — `spinalLoad` (`none|low|high`) and `supported` — because
    "supported/machine variants" has to be a property of the data, not a judgement at reply time. `mcgill: true`
    marks Dead Bug, Side Plank and Bird Dog, which are returned as `allowedExercises.warmup` whenever the back
    is anything but fine.
30. **R7's pick** is the highest-protein ready-to-eat or zero-cook item that fits the remaining kcal. If
    nothing fits, it still names the best protein-per-kcal option and says to take the overage rather than the
    protein miss. `socialMeal.budgetKcal` is `remaining + 200` and is present on **every** R7 verdict, so the
    answer to a dinner invitation is always a number.
31. **R8 exercise count**: ≤45 → 4, ≤60 → 5, ≤75 → 6, else 7. The volume multiplier uses *today's* check-in
    only (an old check-in shouldn't scale today's session) and floors at 0.6. Session type comes from the split
    unless the check-in note names one.
32. **Load progression** needs a rep range, so `exercises.json` carries `repRange` per movement. Back off 5% on
    an RPE ≥ 9.5 top set or any set below the bottom of the range; add 5% after two sessions that hit the top of
    the range at RPE ≤ 8, 2.5% otherwise; hold and add reps in every other case. Rounded to 2.5 lb, and a step
    that would round away to nothing becomes a single 2.5 lb increment instead.
33. **`decisions.jsonl` is deduplicated per day** on `rule|verdict|action`, so running `rules.ts` several times
    in a day does not spam the audit log. `--dry` skips the write entirely.

## log.ts

34. **`checkin`, `steps` and measurements are one row per day** — re-logging replaces. `weight`, `meal`,
    `cardio` and `adjust` append. `sessions.jsonl` is rewritten in place when a set lands on an existing day,
    since a session is built up across a workout.
35. **`set` refuses a QL-contraindicated lift** rather than recording it. It also normalises the exercise name
    to the library spelling so e1RM comparisons don't split across "hack squat" and "Hack Squat".
36. **`meal` with no macros reuses `foods.json`** and errors if the food is unknown — better than inventing a
    number.
37. **`forget` moves the line to `superseded.md` with a date stamp**; nothing is ever deleted.
38. **`adjust` is the write side of R3/R4.** Rules propose; nothing is locked until this is run. Default lock
    is 14 days.

## Testing

39. **160 tests across `dates`, `derive`, `rules`, `log` and `exercises`**, one fixture per verdict named in
    §3 of the brief, plus the ordering, lock, floor, QL-filter and governor-options cases it calls out.
40. **`log.ts` tests run against a scratch copy of the repo** via `setRoot()`, and assert the real `data/` is
    untouched.

## Seed data

41. **The seed is a realistic first week** (2026-08-15 → 2026-08-21), with no weigh-in for 2026-08-22 so COACH
    opens by asking for it. Consequence: `avg7prev` is `null`, so R1 correctly reports `INSUFFICIENT_DATA` on
    day one. That is the honest state of a week-old cut, not a bug.
42. **`lib/exercises.json` holds 116 movements**, more than the ~80 asked for, so every split day has real
    depth after the QL and back-state filters run.
