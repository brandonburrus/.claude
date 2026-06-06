---
name: write-post-mortem
description: Use this skill when writing a post-mortem, postmortem, RCA, or root
  cause analysis for a fixed and validated bug. Use when the user says "write the
  post-mortem", "document this fix", "write up the root cause", "close out this bug
  with a writeup", or when a debugging session has landed a validated fix worth
  recording. Do not use for customer-facing incident reports (timeline, blast
  radius, and comms scope), for bugs not yet fixed and validated, or for trivial
  one-line fixes where the PR description is the record.
---

## Purpose

Write the canonical engineering record of a fixed bug: root cause, mechanism, fix, validation, and how it slipped through. The audience is engineers and future-you, who will have forgotten everything in six months; code identifiers are first-class content because they are what lets the next person grep their way back. Do not draft until all four required inputs exist: a post-mortem of a hypothesis is worse than no post-mortem, because it records a guess with the authority of a conclusion.

## Required inputs

Confirm all four before writing a single line. If any is missing, list what is missing and stop:

- [ ] **Reliable repro**: deterministic or high-rate, runnable by the next person; "happens sometimes" does not qualify
- [ ] **Root cause known**: the mechanism is identified, not a hypothesis that survived
- [ ] **Fix identified**: a PR, commit, or branch pointer
- [ ] **Fix validated**: the original repro now passes; the failing test or workload now succeeds

If the debugging ran under the fix skill, its ledger is the raw material: the reproduction command, the hypotheses tried and rejected, the instrumentation tags, and the confirming experiment are already recorded. Mine it before asking the user anything.

## Workflow

1. **Confirm the gate.** All four required inputs, explicitly.
2. **Confirm the destination.** Default is a draft in chat; offer to save to `docs/postmortems/<short-slug>.md` in the project. The shape is identical either way.
3. **Mine before asking.** The conversation, the fix ledger, `git log`, and the PR carry most sections. Ask the user only for what none of those contain (typically the owner, the tracking ticket, and whether other configurations were tested).
4. **Draft using the structure below.**
5. **Review pass.** Check every claim against the rules in Tone before presenting; strip any hedge words or unverifiable statements you cannot replace with facts.

## Structure

Summary, Root cause, Fix, and Validation are mandatory. The rest are conditional but usually present. Keep this order:

| Section | Content |
|---|---|
| Summary (mandatory) | One paragraph: what broke in user or workload terms, what fixed it in one sentence, ticket, PR, owner. A reader who stops here has the right answer |
| Symptom | What was actually observed: exact test output, error message, log line, perf number. Never paraphrase the failure mode |
| Root cause (mandatory) | The actual mechanism, walked end-to-end with function names, file paths, fields, branch conditions, offending commit SHAs. The most expensive section and the reason the document exists |
| Why it produced the symptom | The chain from cause to observed failure, which is often non-obvious; the bug lives frames away from where the failure surfaces |
| Fix | What changed and why it addresses the root cause rather than hiding the symptom. Link the PR. If a prior fix attempt papered over the symptom, name it and what was wrong with it; that history is part of the cause |
| How it was found | The repro that made it deterministic, the tools that cracked it, hypotheses tried and rejected with the one-line reason each died, and the single experiment that confirmed the cause. Written for the next debugger |
| Why it slipped through | The real gap: CI gap, latent code broken by a later change, workload gap, incomplete prior fix, or review miss. If the honest answer is "no good reason, we should have caught it", write that |
| Validation (mandatory) | Concrete evidence the fix works: test names and links, workload runs, before/after numbers, soak duration. State coverage honestly; "validated on config X, not retested on Y" is information, not a hole |
| Action items | What + owner + tracking artifact for each follow-up not in the fix PR. "None; the fix is sufficient" is a valid entry. Never manufacture items to look thorough |

## Tone

- **Code identifiers are first-class.** Function names, paths, fields, SHAs, line numbers stay in. Stripping them to "a synchronization issue" destroys the document's value as an index.
- **Mechanism over narrative.** Say which function skipped which check under which condition, not the story of the afternoon.
- **No hedging.** "We believe", "appears to", "may have": drop them. State it or do not write it. A validated fix means the mechanism is known.
- **Blameless.** Describe the bug, the gap, and the fix. The CI gap is the failure mode, never the person. No "X should have caught this".
- **No advocacy.** The post-mortem records what happened and what is next. An argument for a refactor is a separate proposal, linked from the action items.
- Active voice, concrete subjects, short paragraphs.

## Gotchas

- **The gate is the skill.** Everything else is formatting. A confident writeup of an unvalidated fix will be trusted, cited, and wrong; refusing to draft is the correct behavior, not an inconvenience.
- **Prior failed fixes belong in the record.** A reverted or symptom-hiding earlier attempt is exactly what the next debugger needs to know not to retry; omitting it out of politeness deletes the most useful history.
- **Validation honesty breeds trust; implied coverage breeds regressions.** If only one configuration was tested, saying so is what lets the next engineer know where the dragons still live.
- **Incident reports are a different document.** A customer-visible outage needs a timeline, blast radius, paging history, and communications record; flag the mismatch and confirm scope before producing the wrong artifact.
- **Action items without owners are wishes.** Each one needs a name and a tracking artifact, or it will be rediscovered in the next post-mortem.
