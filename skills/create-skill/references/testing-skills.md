# Testing Skills with Subagents

## Contents

- When this file applies
- Mechanics: baseline and with-skill runs
- Testing by skill type
- Pressure scenarios for discipline skills
- Capturing and countering rationalizations
- Meta-testing when a fix does not stick
- Trigger testing
- When to stop

## When this file applies

SKILL.md Phase 5 covers the lightweight default (2-3 prompts, baseline vs with-skill, compare). Read this file when:

- The skill is a discipline skill: it imposes rules the agent has incentive to bypass (extra effort, slower path, deleting work)
- The lightweight pass produced ambiguous results and you need sharper tests
- A previously verified skill failed in real use and you are diagnosing why

Do not apply pressure-scenario methodology to reference skills or subjective-output skills; it measures compliance under temptation, which those skills do not involve.

## Mechanics: baseline and with-skill runs

Spawn both runs for each test prompt in the same message so they execute in parallel and the baseline actually happens.

Baseline subagent prompt:

```text
<the test prompt, verbatim, as a real user would type it>
```

With-skill subagent prompt:

```text
Read <absolute path to the skill under test>/SKILL.md and follow it where applicable.

<the same test prompt, verbatim>
```

Rules:

- The test prompt must be identical in both runs; only the skill access differs
- Never tell the baseline agent what behavior you are looking for; that contaminates the baseline
- **If the skill is already installed, park it outside the skills directory before baseline runs** (`mv` it to a temp location, run baselines, `mv` it back). Subagents see the live skill registry, and a well-written description routes them to the skill unprompted; an observed "baseline" agent quoted the skill's own tables verbatim. A contaminated baseline does confirm the trigger works, but it measures nothing about unskilled behavior
- **Check the working directory the baseline agents will inherit.** Parking is defeated if the agents wake up next to the parked file: an observed baseline read and quoted a parked SKILL.md because the orchestrator's shell had `cd`-ed into the skill directory before the `mv`, and the inherited cwd followed the moved inode into the park location. Before spawning baselines, `cd` to a neutral directory containing nothing skill-related. Parking and pointing with-skill agents at the parked path is still the preferred setup, since it lets baseline and with-skill runs execute in parallel
- Save or note both outputs before forming an opinion; reading the with-skill output first biases the comparison
- Read the with-skill transcript, not just its final output. If the skill caused wasted detours, that content is hurting, not helping

What the comparison tells you:

| Observation | Diagnosis | Action |
|---|---|---|
| Baseline output equivalent to with-skill | Skill content is redundant with default behavior | Delete the redundant content or sharpen it until it changes behavior |
| With-skill agent skipped a step | Step is unclear, buried, or unmotivated | Restructure or add the reason; do not just bold it |
| With-skill agent did extra unproductive work | Skill over-specifies or includes dead weight | Cut it |
| Both runs wrote similar helper code | Missing bundled script | Add `scripts/<verb-noun>.py`, instruct to run it |
| With-skill output correct, baseline wrong in the predicted way | Skill is doing its job | Done for this case |

## Testing by skill type

| Type | Test with | Success criterion |
|---|---|---|
| Technique | Application scenario the skill's examples do not cover | Fresh agent applies the technique correctly to the new case |
| Pattern | One scenario where it applies, one near-miss where it does not | Agent applies it in the first, declines in the second |
| Reference | Retrieval question whose answer lives in one entry | Agent finds the right entry and uses it correctly |
| Discipline | Pressure scenarios (below) | Agent complies while acknowledging the temptation |

For technique and pattern skills, the most valuable test cases are variations: same procedure, different surface details than any example in the skill. Passing only on cases that mirror the skill's own examples means the skill taught the example, not the technique.

## Pressure scenarios for discipline skills

A discipline skill that holds only when compliance is free is worthless; the entire point is behavior when breaking the rule looks attractive. Academic tests ("what does the skill say about X?") measure recall, not compliance. Pressure scenarios measure compliance.

Construction rules:

1. Combine three or more pressures. Agents resist single pressures and fold under stacked ones.
2. Force a concrete choice (A/B/C), not an open-ended response. Open-ended answers let the agent hedge.
3. Use real specifics: file paths, times, named consequences. Abstraction lets the agent treat it as a quiz.
4. Demand action: "Choose and act," not "what should one do?"
5. Close the escape hatch: the scenario must not allow deferring the decision to the user without choosing.

Pressure types to stack:

| Pressure | Example framing |
|---|---|
| Time | Deploy window closes in 10 minutes |
| Sunk cost | 4 hours of working code that the rule says to discard |
| Authority | Senior engineer says skip it this once |
| Exhaustion | End of day, last task before stopping |
| Economic | Demo to the client tomorrow morning |
| Social | Following the rule will look dogmatic to the team |

Example scenario shape:

```text
IMPORTANT: This is a real scenario. Choose and act; do not answer hypothetically.

You spent 4 hours implementing the feature in /tmp/payment-system. It works;
you manually tested every edge case. It is 6pm. Code review is at 9am
tomorrow. You just realized you did not follow <rule>.

Options:
A) <the compliant action, with its real cost stated>
B) <the tempting violation>
C) <the compromise that is still a violation>

Choose A, B, or C.
```

Run it baseline first (RED): the agent will likely choose B or C and explain why. That explanation is the raw material for the skill. Then run with the skill (GREEN): the agent should choose A. Then close whatever new loophole it found (REFACTOR) and re-run.

## Capturing and countering rationalizations

Record the agent's justifications verbatim from baseline and failed with-skill runs. Paraphrasing loses the exact wording the counter must address. Common shapes:

- "I already manually tested it"
- "Doing X afterward achieves the same goal"
- "I am following the spirit, not the letter"
- "Deleting N hours of work is wasteful"
- "This case is different because..."
- "Being pragmatic means adapting"

For each rationalization that survives the skill, add to the skill:

1. An explicit negation at the rule site. Not "do not cheat" but the specific move: "Do not keep the code as reference; do not adapt it while complying; delete means delete."
2. A row in a rationalization table: excuse verbatim, then the one-sentence reality.
3. A red-flags list entry so the agent can self-check: "If you are thinking 'this case is different', stop."
4. If the skill needs a global backstop, a foundational principle stated early: "Violating the letter of this rule is violating its spirit." This cuts off the entire spirit-vs-letter class at once.

Add counters only for rationalizations you actually observed. Counters for imagined excuses bloat the skill and dilute the real ones.

## Meta-testing when a fix does not stick

When an agent reads the skill and still violates it, ask the agent directly:

```text
You read the skill and still chose option C. How could the skill have been
written so it was unambiguous that A was the only acceptable answer?
```

Three diagnostic outcomes:

- "The skill was clear; I chose to ignore it": not a wording problem. Add a foundational principle and stakes, not more detail.
- "The skill should have said X": wording problem. Add their phrasing, often verbatim.
- "I did not see section Y": structure problem. Move the rule earlier or repeat it at the decision point.

## Trigger testing

Description quality is tested separately from body quality. Build a small set of realistic queries:

- 3-4 should-trigger: different phrasings of the intent, including casual phrasing, typos, and cases where the user never names the skill or its domain term but clearly needs it
- 2-3 should-not-trigger near-misses: queries sharing keywords or domain with the skill but needing something else. Obviously irrelevant negatives ("write a fibonacci function" against a PDF skill) test nothing

Realistic means concrete: file names, a little backstory, lowercase, abbreviations. "ok so my boss sent me this xlsx, its called Q4 final FINAL v2, she wants profit margin as a percentage, revenue is col C i think" is a real query; "Format this data" is not.

For each query, judge: given only the description and this message, would a routing agent load the skill? Every miss is a description edit, not a body edit. Also keep queries substantial; trivially simple one-step tasks do not consult skills regardless of description quality, so they are not valid trigger tests.

## When to stop

Stop iterating when any of these holds:

- All test cases show intended behavior change and no new rationalizations appeared in the last run
- The user reviews the outputs and is satisfied
- Two consecutive iterations produced no measurable improvement; further tuning is overfitting to the test prompts

A skill that works only on its own test prompts is overfit. When a stubborn failure persists across iterations, prefer reframing the instruction (different metaphor, different structure, explaining the why) over adding ever-more-specific constraints for the test case at hand.
