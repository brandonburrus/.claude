---
name: research-solutions
description: >-
  This skill should be used to research and decide among technical solutions, from the approach
  down to the specific tool. It applies when deciding the technical approach or mechanism ("what
  are the options", "which approach should we take", "sync vs async", "monolith vs service") and
  when selecting the named dev tool that implements it ("compare X vs Y", "Postgres vs Mongo",
  "which database/library/framework/service should we use", "shortlist tools for", "pick a tool
  for", "which auth provider"). The deliverable is a decision: an evaluation table for the
  approach, an evidence-grounded comparison matrix for the tool, each with a recommendation and
  trade-offs. It should not be used for the strategic build-vs-buy of a whole capability or buying
  a business app like a CRM (use research-build-vs-buy), digesting docs of a chosen tool (use
  ground-in-docs), assessing a product's market (use research-market), or general fact-finding
  (use deep-research).
---

## Purpose

Research and decide among technical solutions, at two altitudes that often run in sequence:

- **Decide the approach** (when the mechanism is open): architecture, sync versus async, monolith versus service, which pattern, where the work runs. The deliverable is a decision and its reasoning, not code.
- **Select the tool** (when the approach is fixed and the open question is which named thing implements it): a library, framework, database, managed service, or developer-facing SaaS such as an auth provider, chosen by a requirements-first, evidence-based comparison.

Do both in order when both are open: settle the shape, then pick the tool that fills the slot. The shared discipline is refusing to let the favorite pick itself: force real divergence (or a real candidate set) before converging, draw the criteria from the problem before scoring, and name why each rejected option lost.

A developer-integrated service measured against a build-it baseline (for example "WorkOS vs Auth0 vs build it") belongs here, as a candidate row in the matrix. The strategic build-versus-buy of a whole capability or product, or buying a business application like a CRM, goes to research-build-vs-buy.

## Decide the approach

Use this altitude when the mechanism itself is the open question. The method is diverge, define axes, evaluate, converge.

### Frame the decision

State the problem, the goal, and the hard constraints in a few lines. Name what actually makes this a fork: why the one obvious answer does not simply win. If after framing only one approach is viable, say so and stop; manufacturing alternatives to look thorough wastes everyone's time.

### Diverge across genuinely distinct approaches

Generate at least three approaches that differ in mechanism, layer, or trade-off posture, not one idea with a parameter changed. The test: if swapping any two would not change the trade-off conversation, you have not actually diverged. Generators that produce real distance:

- Do nothing, or defer: is the problem load-bearing right now? The boring option is often the existing approach scaled one notch (a bigger instance, an index, a cache), not a new architecture.
- Reuse or buy what exists versus build new.
- A different layer: configuration, application code, infrastructure, or the data model. The lowest layer that solves it is usually cheapest to own.
- A different posture on a core axis: sync versus async, strong versus eventual consistency, simple-now versus flexible-later.

Include the cheap, boring option explicitly; omitting it inflates every comparison against it.

For the deep mechanism divergence generators (coupling posture, boundary, consistency model, state placement) and the technical axes and pitfalls, read references/technical-approaches.md.

### Define the axes from the problem

Before scoring anything, name the three to six criteria that actually decide this case: time to ship, operational cost, blast radius and reversibility, fit with existing patterns, scaling headroom, team familiarity. Axes invented after scoring are just the winner's features written as criteria. Weight them to the situation: a throwaway prototype and a payments system rank reversibility very differently.

### Evaluate in a table

Score each approach against the axes honestly, including the real costs of the one you expect to win. Lay it out so the trade-offs are visible at a glance, and mark where a hard constraint disqualifies an approach (different from merely scoring lower).

| Approach | Axis A | Axis B | Axis C | Notes |
|---|---|---|---|---|
| Do the simple thing | ... | ... | ... | ... |
| Build it properly | ... | ... | ... | ... |
| Buy / reuse | ... | ... | ... | ... |

### Converge

Recommend one approach with the single biggest reason it wins. Name the strongest rejected alternative and why it lost; if the runner-up has a piece worth grafting in, say so. State the condition that would change the decision, so the reader knows the assumption it rests on. If two approaches are genuinely close and the tie-breaker is empirical (does it perform, does the API actually work that way), recommend a time-boxed spike rather than deliberating further on paper.

## Select the tool

Use this altitude when the approach is settled and the open question is which named library, framework, database, or service fills the slot. Copy this checklist and track progress:

```text
Select the tool:
- [ ] 1. Define requirements and weighted criteria first
- [ ] 2. Identify the candidate set, including the build-it / self-host baseline
- [ ] 3. Disqualify on hard constraints
- [ ] 4. Evaluate survivors on evidence, not marketing
- [ ] 5. Spike the riskiest assumption
- [ ] 6. Recommend with the matrix and the trade-offs
```

### 1. Define requirements and weighted criteria first

Before looking at any product, write the criteria: must-haves (hard constraints that disqualify), should-haves (weighted by importance), and deal-breakers. Criteria defined after browsing reverse-engineer to fit the tool you already liked. Include the adoption criteria a feature list omits: license terms, lock-in and exit cost, maturity and release cadence, support and SLA, security and compliance, total cost at your scale, integration fit, and community size and longevity.

### 2. Identify the candidate set

List the realistic options, usually three to five, including the boring incumbent and the build-it or self-host baseline. Cast wide enough not to miss the obvious leader, narrow enough to evaluate each seriously; a list of ten you cannot research properly is worse than four you can.

### 3. Disqualify on hard constraints

Apply the must-haves and drop any candidate that cannot meet one (incompatible license, no required compliance, will not run on your platform, wrong pricing model). Do not spend evaluation budget scoring a candidate a deal-breaker already eliminated; record why it was cut so the decision is auditable.

### 4. Evaluate survivors on evidence, not marketing

For each criterion, find the real signal, never the vendor's own claim:

- **Docs**: read them for depth and gaps; thin or stale docs predict the support experience.
- **Pricing**: at your actual volume, not the headline tier; "starting at" rarely survives contact with scale. Use estimate-at-scale.
- **Maturity**: changelog cadence, open-issue age, and breaking-change history; a comparison page is sales, the issue tracker is truth.
- **Community and longevity**: size, recency of activity, and whether one company can sunset it.
- **Benchmarks**: third-party over first-party, and note their bias and conditions.
- **License and lock-in**: the exact terms and the cost of leaving later.

### 5. Spike the riskiest assumption

Where the decision hinges on something a feature table cannot answer (does the API actually do X, does it hold up at our load, does the migration path work), a time-boxed proof-of-concept beats more reading. The goal is evidence, not a product. Skip the spike only when the decision does not rest on an untested claim.

### 6. Recommend with the matrix and the trade-offs

Present the comparison table (candidates against weighted criteria, disqualified options and their reason noted), then the recommendation: the single biggest reason it wins, the strongest runner-up and why it lost, the key risk you are accepting, and the assumption that, if it changes, would change the call.

## Output shape

For the approach: a framing, an evaluation table, and a recommendation block (pick, why, runner-up, revisit-if). For the tool: a matrix of candidates by weighted criterion (with disqualified options and their reason), then a recommendation block (pick, why, runner-up, accepted risk, revisit-if).

## Gotchas

- **The boring option is a real option.** Leaving "do the simple thing" or the build-it baseline off the board makes every alternative look better than it is. Put it on the table even when you expect it to lose.
- **Criteria written after browsing bend to the favorite.** Requirements and axes first, then products; otherwise the matrix is a rationalization of a choice already made.
- **Fake divergence is one option, not three.** Three tunings of one design do not diverge. Force distance in mechanism, layer, or posture.
- **Marketing is not evidence.** The comparison page, the conference demo, and the first-party benchmark are sales. Read the docs, the issues, the license, and the third-party numbers.
- **Headline pricing lies at scale.** The free tier and "starting at" price rarely hold at your real volume; price it with estimate-at-scale before trusting it.
- **A genuine tie means spike, not deliberate.** When two options are close and the deciding question is empirical, more paper analysis is procrastination; a time-boxed prototype settles it.
- **This precedes the plan and the spec.** Once decided, hand the winner to create-code-plan or spec. Re-opening the decision there reruns work already done.

## Example

Choosing an auth provider for a B2B SaaS (the approach, build versus buy, is already settled as buy):

```text
Requirements first (before looking at products):
- Must: SAML/SSO and SOC2. Deal-breaker: no SCIM provisioning.
- Should (weighted): low cost at 50k MAU (3), docs/DX (2), exit cost (2).

Candidates: Auth0, Clerk, Cognito, WorkOS, and the build-it baseline.

Disqualify on hard constraints:
- Clerk: no SCIM at evaluation time. Out.
- Build-it: SOC2 + SAML is months the team will not staff. Out.

| Criterion (weight) | Auth0 | Cognito | WorkOS |
|---|---|---|---|
| SAML + SCIM (must) | yes | partial | yes |
| Cost at 50k MAU (3) | high | low | mid |
| Docs / DX (2) | good | weak | good |
| Lock-in / exit (2) | high | high (AWS) | mid |

Spike: confirmed WorkOS SCIM actually syncs against a test IdP in an
afternoon (the decision hinged on that untested claim).

Recommend: WorkOS. Reason: SSO/SCIM is its core product with a clean
exit. Runner-up Auth0 lost on cost and lock-in. Accepted risk: smaller
company. Revisit if: MAU pricing shifts or we need non-auth features.
```
