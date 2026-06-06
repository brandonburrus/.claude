---
name: humanize
description: >-
  Use this skill when editing text to remove signs of AI-generated writing and
  make it read as natural and human-written. Use when the user says "humanize
  this", "make this sound less like AI", "remove the AI-isms", "this reads like
  ChatGPT", "de-slop this", or "make this sound natural", and as a final pass
  over prose the user will publish under their own name. Do not use for
  drafting new content from scratch (use the writing skills), for code, or for
  detecting whether a third party used AI (this skill edits, it does not
  accuse).
---

## Purpose

Edit text to remove the specific, documented tells of AI-generated writing while preserving its meaning, coverage, and the author's voice. The tells are not vibes; they are catalogued patterns (grounded in Wikipedia's "Signs of AI writing", maintained by WikiProject AI Cleanup) that arise because models gravitate toward the most statistically likely phrasing that fits the widest variety of cases. The deliverable is a final rewrite produced through a draft, self-audit, final loop, never a single pass.

## Hard rules

- **Rewrite, do not delete.** Every substantive point in the original survives into the rewrite; losing content is not humanizing, it is shrinking. Pure ceremony is the exception: chatbot framing, signposting, heading warm-ups, and passages that carry no content beyond their own rhetoric get cut, not rewritten, so some shrinkage from removing ceremony is expected. The test is "did any actual information disappear?", not paragraph count.
- **Never invent specifics.** Concrete details make text feel human, which makes fabricating them tempting; a made-up interviewee, study, or statistic is worse than any AI-ism. Use only specifics present in the source text or supplied by the user. When the text needs a concrete detail it does not have, ask for one or leave the sentence general.
- **The final rewrite contains no em dashes or en dashes.** They are among the most reliable tells; replace each with a period, comma, colon, parentheses, or a restructured sentence. Scan the final text for them before returning; any hit means it is not done.
- **No emojis, no curly quotes, no mechanical boldface** in the final rewrite.
- **Match the register.** For encyclopedic, technical, legal, or reference text, neutral and plain is the correct human voice; injecting opinions or first person there makes it worse, not warmer.

## Workflow

1. **Calibrate voice.** If the user provides a writing sample (inline or a file path), read it first and note sentence-length habits, word register, punctuation tics, and how transitions are handled; the rewrite should replace AI patterns with that writer's patterns, not generic polish. Without a sample, default to a natural, varied voice fitting the content's register.
2. **Load the catalog.** Read [references/ai-patterns.md](references/ai-patterns.md) and check the text against every pattern in it. The catalog is the skill; working from memory of it produces partial passes.
3. **Judge before flagging.** Apply the cluster rule below; confirm each flagged instance is a real tell and not legitimate prose.
4. **Draft rewrite.** Fix every confirmed instance. Read it aloud mentally: varied sentence length, simple copulas (is, are, has), specific over abstract.
5. **Self-audit.** Ask: what makes this draft still obviously AI-generated? List the remaining tells honestly; an even, mid-length cadence and too-tidy contrasts survive most first drafts.
6. **Final rewrite.** Address the audit findings, then run the hard-rule scans (dashes, emojis, curly quotes).
7. **Deliver** the final rewrite plus a short summary of the pattern groups removed. Show the intermediate draft and audit only when the user asks to see the work.

## Detection judgment

**The cluster rule.** A single tell means nothing; clusters are the signal. One em dash is a punctuation choice; em dashes plus rule-of-three plus "vibrant tapestry" plus a generic upbeat conclusion is a confession. Weigh accordingly before rewriting a passage.

These are not reliable indicators on their own, so do not flatten them:

- Perfect grammar, consistent style, or correct complex formatting (professionals and templates exist)
- Formal or academic vocabulary in general; the catalog lists the specific overused words, and "ostensibly" is not one of them
- Common transition words in isolation; one "however" is not a tell, a pileup is
- Curly quotes alone (most editors auto-curl) or em dashes alone (journalists love them); both count only alongside other tells
- Bland prose without specific tells, mixed registers, or unsourced claims

**Preserve signs of human writing.** Over-editing destroys exactly what makes prose sound human. When you see these, lean toward leaving the passage alone:

- Specific, unusual, hard-to-fabricate detail; humans hoard specifics, models round them off
- Mixed feelings and unresolved tension instead of clean takes
- Era-bound slang, memes, or in-jokes; genuine asides, parentheticals, and self-corrections
- Varied sentence length, including fragments
- First-person choices the writer could defend

## Voice and soul

Removing AI patterns is half the job; sterile, voiceless writing is just as obviously machine-made. When the content calls for a human voice (blog posts, essays, opinion, personal writing), check the draft for soullessness: every sentence the same length, no opinions, no uncertainty, no first person where it belongs, reads like a press release. The fixes:

- **Have reactions, not just facts.** "I genuinely don't know how to feel about this" is more human than a neutral pro/con list, when the author's voice supports it.
- **Vary the rhythm.** Short punchy sentences. Then longer ones that take their time getting where they are going.
- **Let some mess in.** Tangents, asides, and half-formed thoughts read as a person; perfect structure reads as an algorithm.

This section applies only where opinion belongs; see the register rule above.

## Gotchas

- **The self-audit step is load-bearing.** Single-pass rewrites reliably keep the even cadence and tidy paragraphing that mark AI text even after the vocabulary is fixed; the "what is still obviously AI here?" question is what catches them.
- **Voice matching beats voice improving.** If the user's sample says "stuff" and "things", the rewrite says "stuff" and "things"; upgrading their vocabulary reintroduces the polish you were asked to remove.
- **Hyphation has position rules.** Keep compound hyphens before the noun (a high-quality report) and drop them after it (the report is high quality); uniform hyphenation everywhere is the machine pattern.
- **Documentation should not narrate its own diff.** Text that explains what the code used to do before a change (outside changelogs and migration guides) is a tell; describe the thing as it is.
