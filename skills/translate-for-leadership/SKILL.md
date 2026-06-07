---
name: translate-for-leadership
description: >-
  Use this skill when rewriting engineering content for engineering-org
  leadership (VPs, directors, PMs, release managers) and shaping it for its
  channel: ticket comment, Slack post, async standup line, email, or meeting
  talking points. Use when the user says "write this up for management",
  "exec summary", "leadership update", "status update", "make this less
  technical", or asks for a slack/email/standup version of engineering work.
  Do not use for marketing or customer-facing copy, true ELI5 audiences
  (different rewrite, flag it), or the engineering record itself (use
  write-post-mortem).
---

## Purpose

Reframe engineer-to-engineer content for people who read product names and ticket keys but not code, shaped for the channel it will land in. The audience wants four things: what is the state, what does it mean for customers, who owns it, what happens next. The channel decides length and structure. The deliverable is always print-only: a draft the user posts themselves, never something posted on their behalf.

## The translation rules

| Move | What |
|---|---|
| Keep | Product, framework, and component names; ticket keys; PR numbers; customer and workload identifiers. These are the bridge to leadership's own tracking; stripping them breaks cross-referencing |
| Strip | Function names, file paths, struct fields, commit SHAs, line numbers, env vars. Not actionable to this audience |
| Translate | Mechanism into one or two sentences of plain cause and effect: not "the kernel reads scratchBuf as NULL" but "the GPUs read an uninitialized buffer and wait forever for a signal that never arrives". Translate without lying; a race stays a race, a regression stays a regression |

**Do not over-strip.** This audience reads concept-level vocabulary fluently: race condition, synchronization, fast-path, rollback, queue. The line runs between "the concept matters here" (keep) and "here is the function and SHA" (strip); replacing "race condition" with "timing issue" patronizes.

**Avoid**: fake hedging ("we believe", "appears to": state it or do not); re-explaining the obvious; telling leadership what to prioritize (facts, not directives; they decide); engineering-process play-by-play (bisects, debugger sessions; they care that you found it, not how, unless the process itself is the one-sentence lesson).

Active voice, concrete subjects, short paragraphs: "We found the bug. Alex's fix is in review." beats "The root cause has been identified and a fix has been authored."

## Channel shapes

Same content, different shell. Confirm the channel first if unstated ("Ticket, Slack, standup, or email?") and stop until answered.

| Channel | Shape |
|---|---|
| Ticket comment / status report | Full structured block, bolded labels, ordered by what matters for this item: Status/TLDR (one line; a reader stopping here has the right answer), Impact (customer and workload terms, not test-suite terms), What broke (plain mechanism, one level of why), Why now (only when leadership will ask anyway), Owner (person + one link), Next steps (concrete, ordered), Workaround (if customers hit it today), Risk (real ones only) |
| Slack post | One bolded TLDR line, then 2-4 short bullets: impact, owner+link, next step. One inline link, no link walls, no greeting or signoff, under ~80 words. Thread replies lose the TLDR and lead with the answer, under ~40 words |
| Async standup | 1-3 lines, verb first, no bullets or labels: "Fixed the Tada hang on LLM-7B (PROJ-12345). PR in review. Backport next." The reader scans ten of these in thirty seconds |
| Email | The subject line is half the value: the TLDR as a noun phrase ("Checkout latency regression: fix in review (PROJ-12345)"). Body is the ticket shape as two or three flowing paragraphs, no bolded labels. Sign off with the decision the recipient owns, if any |
| Meeting talking points | Bullets in speaking order, one short clause each, with the numbers and keys you want to say out loud baked into the bullet so there is no fumbling |

## Source material

In order of preference: the current conversation (when the user says "now make that a Slack update", reuse what is in context), pasted technical text, or a ticket reference to fetch. The most recent substantive state is what gets reframed, not the full thread history. Ambiguous source: one question, then stop.

## Output flow

1. Confirm the channel.
2. Produce the draft as a single block formatted as the channel would render it.
3. Hand it over. Never post to Slack, email, or any channel on the user's behalf; the user owns the send.
4. One revision is normal; a third means a framing assumption is wrong, so ask what it is instead of tweaking blindly.

## Rules

- **Never invent facts for narrative tidiness.** "Root cause unknown" stays "root cause unknown"; promoting a speculation to a finding because it reads better is the cardinal sin of status updates.
- **Never invent owners.** No name in the source means asking, not guessing from git blame.
- **Never strip a ticket key, PR number, or customer name** while de-jargoning; they are the tracking bridge.
- **Status, not advocacy.** This skill reports state; a recommendation memo is write-proposal's job, and sliding from one into the other without the user choosing it misrepresents them.

## Gotchas

- **This skill composes with write-post-mortem, in one direction.** The post-mortem owns the engineering truth with every identifier intact; this skill derives the leadership version from it. Deriving the post-mortem from the leadership version reverses the information flow and loses the record.
- **The TLDR line carries the entire update.** Most readers stop there; if it says "investigating" when the fix is in review, the update failed regardless of the paragraphs below.
- **Impact in their units.** "The test fails on CI" means nothing upstream; "fine-tuning runs hang for any customer using dumbModel" is the same fact in units leadership can act on.
- **Channel mismatch reads as tone-deafness.** A five-block JIRA structure pasted into Slack says "I escaped from a ticket"; forty words in a ticket comment says "nothing happened". The shell is part of the message.
