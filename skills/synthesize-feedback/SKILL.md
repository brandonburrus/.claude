---
name: synthesize-feedback
description: >-
  Use this skill to turn raw product feedback into themes, the pain behind each,
  and the opportunities they point to. Use for user interviews, support tickets,
  app reviews, survey free-text, sales notes, or churn comments, and when the
  user says "synthesize the feedback", "what are users saying", "themes in this
  feedback", "go through these support tickets", "what are the top pain points",
  "make sense of these reviews", or "cluster this feedback". The deliverable is
  signal-ranked themes grounded in quoted evidence. Do not use for quantitative
  analysis of a dataset (use analyze-data), for code-review feedback on your own
  PR (use triage-review-feedback), for writing the spec a theme leads to (use
  write-product-spec), or for deciding build order across themes (use
  prioritize-roadmap).
---

## Purpose

Turn a pile of raw product feedback into a small set of themes, the underlying pain behind each, and the opportunity each points to, all grounded in quoted evidence. The deliverable is a synthesis, not a feature list. The discipline is refusing to react to the loudest or most recent item: cluster by underlying problem rather than requested feature, weight by signal rather than raw count, and separate what users said from what they actually need. The synthesis names problems and opportunities; it does not design the solution, that is downstream.

## Workflow

Copy this checklist and track progress:

```text
Synthesize:
- [ ] 1. Gather and tag the corpus
- [ ] 2. Cluster by problem, not by requested feature
- [ ] 3. Separate the said from the needed
- [ ] 4. Weight by signal, not volume
- [ ] 5. Quote the evidence
- [ ] 6. Name the bias the corpus carries
```

### 1. Gather and tag the corpus

Pull the feedback into one place and tag each item with its source and segment: a churned enterprise account and a free-tier tweet are not equal signal. The source shapes the weight in step 4 and the bias in step 6, so capture it now.

### 2. Cluster by problem, not by requested feature

Users propose solutions ("add a dark-mode toggle"); the job is the problem underneath ("the UI is painful at night", "I work in a dark room"). Group items by the shared pain, because three different feature requests often share one root problem, and the problem is what becomes an opportunity. Clustering by the literal request fragments one real need into three shallow ones.

### 3. Separate the said from the needed

"I want X" is a request; the need is the job behind it. Each theme states the need and the evidence, never the requested feature as if it were the goal. Conflating them ships the literal ask and misses the actual opportunity, the classic faster-horse trap.

### 4. Weight by signal, not volume

A theme's strength is frequency times severity times segment value, not a raw count. One churned key account naming a blocker outweighs fifty low-stakes nice-to-haves. State the weighting so the user can challenge it; a silent tally of votes hides the judgment that a dealbreaker beats a preference.

### 5. Quote the evidence

Every theme carries one or two verbatim quotes, each tagged with its source and segment. A theme without a quote is your hypothesis wearing a user's hat; the quote is what keeps the synthesis honest and lets the reader feel the pain rather than take your word for it.

### 6. Name the bias the corpus carries

State what this corpus cannot tell you, because every feedback channel is a skewed sample:

- **Recency**: the last loud ticket feels like a trend; check whether it predates this week.
- **Vocal minority**: the power users in the forum are the most available, not the most representative.
- **Sampling**: support tickets over-represent the frustrated; churn surveys miss the people who stayed happy; reviews skew to the extremes.
- **Confirmation**: the theme you already believed is the one you will find first; look for the disconfirming item on purpose.

## Output shape

| Theme (the need) | Signal (freq / severity / segment) | Evidence (quoted) | Opportunity |
|---|---|---|---|

Close with **What this corpus cannot tell us**: the gaps and skews from step 6, so the reader knows where the synthesis is blind.

## Gotchas

- **Clustering by feature buries the problem.** Group by the requested solution and you ship the literal ask; group by the pain and three requests resolve into one opportunity worth prioritizing.
- **Counting votes is not weighting signal.** Raw frequency ranks a loud nice-to-have above a quiet dealbreaker. Severity and segment value are the other two axes, and they often dominate.
- **A theme without a quote is a bias.** Verbatim evidence is what separates what users said from what you wanted them to say; if you cannot quote it, you have not found it yet.
- **The corpus is not the population.** Tickets, reviews, and churn surveys are all skewed samples, never the silent majority. Naming the skew is part of the deliverable, not a disclaimer.
- **Solutioning hides the problem.** Designing the feature inside the synthesis collapses the problem into one answer; leave the opportunity open and hand it to write-product-spec or prioritize-roadmap.

## Example

Three raw items that read like three different feature requests:

```text
- Enterprise admin (churned): "We need SSO or we can't roll this out company-wide."
- Free user (tweet): "why a separate login, just let me use Google"
- Mid-market trial: "IT won't approve us without SAML."
```

Clustered by problem, not by feature, all three are one job: "I cannot adopt this without my organization's identity system." The requested solutions differ (SSO, Google login, SAML); the need is single.

| Theme (the need) | Signal | Evidence | Opportunity |
|---|---|---|---|
| Adoption blocked without org identity | high: a churned enterprise plus a blocked mid-market trial, both revenue-bearing; the free tweet weights low | "IT won't approve us without SAML"; "can't roll this out company-wide" | unblock team and enterprise adoption with identity-provider login |

What this corpus cannot tell us: it samples people who spoke at the buying boundary, so it says nothing about why activated users stay or churn, and the free-tier voice here is one tweet, not a measured segment.
