---
name: write-eval
description: >-
  Use this skill when writing evaluations for an LLM-powered feature, agent,
  or prompt: building eval datasets, choosing graders (code checks, pattern
  matching, LLM-as-judge, human review), setting pass thresholds, and wiring
  evals into the development loop. Use when the user says "write evals",
  "add evals for this", "how do I know the agent actually works", "test my
  prompt", "the agent feels unreliable, measure it", or before changing a
  prompt that has no eval coverage. Do not use for designing the agent
  itself (use design-llm-agent), for testing conventional code (use
  follow-tdd), or for Claude API mechanics (use the bundled claude-api
  reference).
---

## Purpose

Build evals: the unit tests of AI work. design-llm-agent makes eval-first non-negotiable at the design level; this skill is the implementation side, producing the dataset, the graders, the thresholds, and the loop integration. Evals exist before the prompt is tuned, because without a measured baseline every prompt change is a vibes-based bet, and "the output looks good" is not a regression suite. Deliverable: versioned eval definitions, a recorded baseline, and a defined place in the dev loop.

## Workflow

### 1. Define the eval before building the thing it measures

Split into two kinds with different jobs: capability evals (does the new behavior work) and regression evals (does everything that worked still work). Write the success criteria as gradeable statements now, while they are still requirements rather than rationalizations of whatever the prompt currently produces.

### 2. Build the dataset

- Each case is input, plus either a golden answer (deterministic tasks) or a written rubric (open-ended tasks). A rubric describes what makes an answer correct; a single example answer is not a rubric.
- Volume beats polish: 10 to 20 diverse cases minimum before anything ships, and 50 noisy-but-varied cases outperform 5 hand-polished ones, because diversity is where systematic failures surface.
- Source cases from real inputs first, then synthesize variations seeded by the real ones (matching length, format, and tone of production data). Every production failure becomes a new case permanently.
- Pin everything the case depends on (input files, repo commits, fixtures) so results stay comparable across months.
- Hold out a subset that prompt-tuning never sees; it is the only honest measure once the visible set has shaped the prompt.
- Beyond representative cases, plant trap cases: inputs engineered so a known LLM failure mode produces a plausible-looking-but-wrong output, with the grader checking for the specific tell rather than surface plausibility. Representative cases answer "does the output look right"; trap cases answer "does the output reveal the failure", which is the question that catches the failures that ship. Each trap case names the mode it targets and the tell, so a regression is diagnosable, not just a red cell.

| Failure mode | Example trap case | What the grader checks |
|---|---|---|
| Plausible-but-wrong answer | Question whose confident-sounding common answer is incorrect | Output matches the verified answer, not the popular wrong one |
| Hallucinated fact or citation | Prompt inviting a specific source, figure, or quote the model lacks | Every named source or figure resolves against ground truth; no invented specifics |
| Buggy work passed off as correct | Task whose naive solution has a subtle defect (off-by-one, wrong edge case) | Output handles the seeded edge input correctly, not just the happy path |
| Shortcut that beats a naive check | Input where a spurious cue (keyword, format) predicts the naive-graded answer | Output stays correct when the cue is flipped or removed in a paired variant |
| Unsupported claim stated as fact | Prompt that rewards asserting beyond the given evidence | Claims trace to provided context; the model hedges or declines when evidence is absent |

### 3. Choose the cheapest grader that grades truthfully

| Grader | Use for | Failure mode |
|---|---|---|
| Code (assertions, tests, exact match) | Deterministic outputs, structure, format, behavior under test | Cannot grade nuance |
| Pattern (regex, contains) | Format checks, required mentions | Fragile to paraphrase; false positives |
| LLM-as-judge with rubric | Tone, reasoning quality, open-ended correctness | Bias, drift, cost, nondeterminism |
| Human | High-stakes ambiguity, safety calls | Slow, expensive, inconsistent |

- Reformat before reaching for a judge: often all that lies between you and a code-gradeable eval is clever design (multiple choice instead of free text, structured output instead of prose). A code grader is deterministic ground truth; a judge is a second model guessing.
- Judge rules when a judge is genuinely needed: the rubric is written, frozen, and versioned (a quietly edited rubric makes every historical score incomparable); validate the judge on 5 to 10 graded samples and read its reasoning before trusting it; prefer a different model family than the one under test, because self-family grading inflates scores; the judge critiques and never proposes fixes, since a judge grading its own suggestions is biased by construction.
- Make the rubric ruthlessly strict. If everything passes the first run, the rubric is measuring nothing; tighten until real failures appear.

### 4. Set thresholds in pass@k terms

- LLM systems are nondeterministic, so single runs are noise: run 3+ trials per case. pass@k means at least one success in k attempts (practical reliability with retries); pass^k means all k succeed (consistency).
- Calibrate by criticality: capability evals around pass@3 at 90 percent; regression and anything user-facing-critical at pass^3 at 100 percent.
- Track cost and latency next to pass rate; a prompt change that buys 2 points of accuracy for 10x token spend is a regression wearing a win's clothes.

### 5. Wire evals into the loop

- Baseline before any prompt change, re-run after; the delta is the review artifact for the change. A prompt edit without an eval run is an untested code change.
- Evals are code: versioned with the prompts they test (prompts are first-class code per design-llm-agent), reviewed, and runnable by one command. Slow evals stop getting run, so speed is a feature: parallelize, use cheaper models for judges, trim cases that never discriminate.
- Release gates use deterministic graders only; a probabilistic judge in a deploy gate produces flaky releases. Judges inform trends, code graders gate.
- Log every run's results and keep the history; a slow downward trend across ten changes is invisible without it.

## Gotchas

- **Overfitting to the eval set is the default failure.** Once the cases are known, prompt tuning quietly optimizes for them specifically. The hold-out set and a habit of synthesizing fresh cases after each tuning round are the countermeasures.
- **Never let eval cases leak into the prompt.** Examples embedded in the system prompt must not double as eval cases; the eval then measures memorization of itself.
- **A tiny eval suite is worse than it looks.** Three cases passing reads as "it works" while hiding entire failure classes; the confidence is the damage.
- **Judge drift is silent.** The same rubric scored by the same judge can shift across model updates; re-grade a frozen sample periodically and treat a shift as a broken instrument, not a real trend.
- **Agent evals need the variance treatment most.** Multi-step agents compound nondeterminism; budget more trials per case there, and grade end states (files, test results) over transcripts, because transcripts are long and judges get lost in them.
