---
name: audit-skill-efficacy
description: >-
  Use this skill to find which skills in the library actually change behavior
  versus which are dead weight, by running the create-skill Phase 5 baseline-vs-
  with-skill test across many skills at once and flagging the ones a no-skill
  baseline already matches. Use when the user says "audit my skills", "which
  skills are dead weight", "do my skills actually work", "test the skill library",
  "find redundant skills", "are these skills earning their place", or "skill
  efficacy". Do not use for authoring or fixing one skill (use create-skill, whose
  Phase 5 this scales up), for auditing AGENTS.md documentation coverage (use
  audit-agent-context), or for mining transcripts to see which skills ever fire in
  real use (use audit-harness-usage).
---

## Purpose

Measure whether skills earn their place. A skill that produces the same output a no-skill baseline would is dead weight: it loads, consumes context, and changes nothing. The deliverable is a per-skill verdict, keep / sharpen / cut, each backed by a side-by-side baseline-vs-with-skill comparison. This scales `create-skill` Phase 5 (which verifies one new skill) across the existing library.

The rule the skill defends: **the test is not "is the with-skill output good," it is "did the skill change behavior the baseline would not have produced."** A strong base model already does much of what a skill describes; only the delta justifies the skill's existence.

## Workflow

- [ ] 1. Select the skills to audit
- [ ] 2. Derive realistic prompts from each skill's triggers
- [ ] 3. Run baseline and with-skill in parallel per prompt
- [ ] 4. Score the delta, not the quality
- [ ] 5. Report keep / sharpen / cut with the evidence

### 1. Select the skills to audit

Auditing all 70+ at once is expensive; scope deliberately. Good cohorts: skills changed since the last audit, skills covering domains a strong base model likely already knows (general engineering, common product frameworks) since those are the likeliest dead weight, or a random sample for a periodic health check. State the cohort and why.

### 2. Derive realistic prompts

For each skill, write 2-3 prompts a real user would actually type, drawn from the skill's description triggers: concrete, with specifics and casual phrasing, not "use skill X to do Y." The prompt must be answerable without the skill (so the baseline has a fair shot); a prompt that names the skill's own method contaminates the test.

### 3. Run baseline and with-skill in parallel

For each prompt, spawn two subagents in the same dispatch: one given only the task, one told to read the skill's SKILL.md first and then do the task. Parallel dispatch matters; running them serially tempts skipping the baseline, which is the whole control. Cap output length equally so the comparison is fair.

### 4. Score the delta, not the quality

Compare each pair on one question: did the skill change behavior in the way it claims to? Classify:

| Verdict | Signal |
|---|---|
| Keep | With-skill is materially better or more reliable; baseline misses the skill's core move |
| Sharpen | The delta exists but is small or inconsistent; the redundant-with-baseline content dilutes a smaller real contribution |
| Cut | Baseline output is equivalent across prompts; the skill adds nothing it claims to |

A skill can be low-delta on output yet still earn its place through **routing** (it fires on tasks where the user did not name it) or a **reference/script** the model cannot reproduce from memory. Note that explicitly before cutting; the audit measures behavior change, and routing is a behavior change the single-prompt test underweights.

### 5. Report

Per skill: the verdict, the prompts used, a one-line characterization of the delta, and the specific fix for Sharpen (which redundant sections to trim, what to keep). For Cut, name what unique value, if any, would have to be added to justify keeping it. Apply fixes only with the user's go; the report is the deliverable.

## Gotchas

- **A fair baseline is the entire experiment.** If the prompt leaks the skill's method or names the skill, the baseline "knows" the answer and every skill looks redundant. Write prompts as a naive user would.
- **Low output-delta is not automatically Cut.** Routing and bundled references/scripts are real value the single-prompt comparison does not capture. Check both before cutting.
- **Discipline skills resist this test.** A skill whose job is to make the agent comply under pressure (a rule it is tempted to bypass) needs the pressure-scenario method in `create-skill`'s `references/testing-skills.md`, not a plain baseline comparison.
- **Subjective-output skills need human review.** For writing-style or design-taste skills, there is no objective delta to score; surface the paired outputs for the user to judge rather than asserting a verdict.

## Example

Auditing the product-discovery cohort. For `validate-idea`, prompts like "I want to build a Chrome extension that summarizes Slack threads, how do I know if it's worth building?" The baseline already produces a strong Mom-Test-style answer (riskiest assumption, cheapest test, go/pivot/kill), so the output delta is small. Verdict: **Keep, but note the basis** is routing (firing on "build me X" phrasings where the user did not ask to validate) and the bundled experiment-library reference, not raw output superiority. The report flags that the body's general-knowledge sections could be trimmed if context budget ever demands it, but the routing value justifies the skill.
