# COACH

No API. No dashboard. No server. Claude Code *is* the coach; this repo is its brain and its memory.

```bash
cd coach
npm install
npm test
claude
```

Then talk:

```
> slept 6.5, stress 4, back fine, 55 min          # → today's session
> at the gym                                        # → walkthrough, reply "70 10 8" per set
> ate chipotle bowl double chicken no beans         # → logged, remaining shown
> 208.6                                             # → weight logged, trend updated
> sunday                                            # → weekly review + prep list
```

## How it works

`CLAUDE.md` is loaded automatically every session. It tells Claude to run two scripts before it says anything:

- **`scripts/derive.ts`** turns `data/` into `Facts` — rolling averages, OLS trend, projection, adherence,
  strength deltas, session inputs. Pure arithmetic.
- **`scripts/rules.ts`** runs eight decision rules over those Facts and prints verdicts with actions and
  rationales, plus the exercises allowed today.

Claude reasons only from that output. It never does the math itself, and it never invents a verdict.
`scripts/log.ts` is the only way data gets in — every write is zod-validated.

Read `NOTES.md` for every assumption behind the numbers, and `CLAUDE.md` for the operating manual.

## Layout

```
CLAUDE.md          the brain — behaviour, hard rules, modes
NOTES.md           every assumption, numbered
data/              the record: weights, meals, check-ins, sessions, PRs, adjustments, decisions
memory/            facts.md, superseded.md, week-reviews/
lib/exercises.json 116 movements with cues, substitutes and contraindications
scripts/           derive.ts (math) · rules.ts (decisions) · log.ts (writes)
test/              160 tests — one fixture per verdict
```
