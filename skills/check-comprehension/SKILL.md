---
name: check-comprehension
description: Use this skill when the user wants to deeply understand something and have
  that understanding verified rather than just receive an explanation, typically after a
  change, fix, or feature was just built, or for a concept they are studying. Triggers
  include 'make sure I understand this', 'check my understanding', 'quiz me on this',
  'teach me what we just did', 'do I actually get this', and 'walk me through until it
  clicks'. It opens an interactive teaching mode that builds a comprehension checklist,
  has the learner restate first, drills the whys, quizzes with AskUserQuestion, and
  refuses to advance until each item is mastered. Do not use for a one-off explanation the
  user only wants to read (answer directly), or for producing written teaching material
  (use teach-through-writing).
---

## Purpose

Enter an interactive teaching mode whose only goal is for the learner to deeply understand the work or concept at hand, verified rather than assumed. Build a comprehension checklist, work it one stage at a time, and confirm mastery of each stage before moving to the next. Do not lecture, do not race to the end, and do not declare understanding on the learner's behalf. The session is not done until every checklist item is mastered, or the learner explicitly stops with the remaining gaps named.

## Workflow

Track this loop; the verification step is the one you will be tempted to skip, so do not:

- [ ] Build the comprehension checklist across the three tiers
- [ ] Restate-first: have the learner explain before you teach
- [ ] Teach to the revealed gap; drill the whys
- [ ] Verify mastery (restate + quiz + follow-up) before advancing
- [ ] Gate the ending until every item is mastered

### 1. Build the comprehension checklist

Enumerate what the learner needs to understand, grouped into three tiers and worked in this order because understanding the problem is the foundation every later tier rests on:

1. **Problem** - what it was, why it existed, what alternatives or branches were considered.
2. **Solution** - what was done, why this way, the design decisions, the edge cases.
3. **Broader context** - why it matters, what the change impacts downstream.

Keep the checklist inline in the conversation and re-post it each turn with a status per item (unverified / in progress / mastered), so progress stays visible even after a long back-and-forth. No file is written; the checklist lives in the chat, which means re-posting it is the only thing keeping it from drifting out of view.

### 2. Restate first

Before explaining anything, have the learner restate their current understanding of the item in their own words. This is the hardest instruction to follow and the most important. The instinct is to explain immediately, but leading with the explanation hides the gap you are here to find and denies the learner the retrieval that actually builds understanding. Ask, listen, then teach to what is missing.

### 3. Teach to the gap

Fill only the specific gap the restatement revealed; do not re-explain what they already have. Drill the whys: when they answer one "why", ask the next one down until you hit bedrock. Use the real material - show the actual code, walk the diff, or have them step through the debugger when a concept is easier seen than told. Offer the ELI ladder on request (see below). One stage at a time; never dump the whole checklist as a lecture.

### 4. Verify mastery before advancing

An item is mastered only when the learner can do all three:

1. Restate it in their own words, unprompted.
2. Answer a quiz question that tests the reasoning correctly.
3. Handle at least one follow-up "why" or edge-case probe.

A single correct multiple-choice click is not mastery; it could be a guess. "That makes sense" is not mastery; agreement is not understanding. Require them to produce the explanation. Do not start the next tier until the current tier's items are all mastered.

### 5. Gate the ending

Do not end the session while any item is unverified. If the learner explicitly asks to stop or move on, honor it, but first state plainly which items remain unmastered and mark them in the checklist so the gap is on the record. Absent an explicit stop, keep going.

## Quizzing rules

Quiz with the AskUserQuestion tool. These are what make the quiz a real check rather than a tell:

- **Never reveal or hint the answer before submission.** Not in the question, not in the option wording. Reveal and explain only after they answer.
- **Vary the position of the correct option across questions.** Do not habitually place it first; a predictable slot lets the learner pattern-match instead of reason.
- **Test reasoning, not trivia.** Good: "why would approach B deadlock here?" Bad: "what is the function named?"
- **Mix formats.** Open-ended (have them type the explanation) catches gaps that multiple choice hides; multiple choice is faster for discrete checks. Use both.
- **On a wrong answer, teach the misconception, then re-quiz with a different question.** Do not just supply the right answer and move on; the miss located a gap, so close it and re-verify.

## The ELI ladder

Offer these depths on request; each assumes less prior knowledge than the last:

| Trigger | Audience | Assume |
|---|---|---|
| ELI5 | Total beginner | No technical background; reach for analogy. |
| ELI15 | Curious teenager | Basic logic, no domain knowledge. |
| ELI-intern | New engineer | CS fundamentals, but new to this codebase and domain. |

## Gotchas

- **Restate-first is the whole game and the easiest to skip.** The reflex is to explain. If you explain before they restate, you teach to an imagined gap instead of the real one.
- **A correct click is not comprehension.** Mastery requires the learner to generate the explanation, not recognize it. Always pair a quiz with a "walk me through why."
- **Agreement is not mastery.** "Yeah, that makes sense" verifies nothing. Push back: "great, so explain it back to me."
- **Do not advance to be polite.** The urge to keep things moving is the exact failure mode this skill exists to resist. A half-understood problem tier poisons every tier after it.
- **Do not quiz on memorization.** Names, line numbers, and syntax are not understanding. Every question should probe a why or a what-if.

## Example

After merging a change that replaced a global lock with per-account locks in a payments service, the learner runs `/check-comprehension`.

Checklist posted inline:

```markdown
Problem
- [ ] Why the global lock hurt throughput under concurrent charges
- [ ] What the contention looked like in production
Solution
- [ ] Why per-account locks fix it without losing safety
- [ ] Edge case: two charges on the same account still serialize
Broader context
- [ ] What changes for unrelated accounts (now parallel)
```

Restate-first prompt: "Before I explain anything, tell me in your own words why the global lock was hurting us."

After they answer, a quiz with the correct option in a varied slot and no tell:

```text
AskUserQuestion: "Two charges hit DIFFERENT accounts at the same time. Under per-account locks, what happens?"
- They serialize; one waits for the other   (incorrect - that was the old global-lock behavior)
- They run in parallel                        (correct)
- One is rejected as a conflict               (incorrect)
```

The answer is revealed and explained only after submission. A wrong pick routes back to teaching lock granularity, then a fresh question, before the item is marked mastered.
