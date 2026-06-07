---
name: research-solutioning
description: >-
  Use this skill to research and compare specific external technical solutions
  (libraries, frameworks, SaaS, databases, managed services, or commercial
  vendors) against your requirements and choose one. Use when the user says
  "compare X vs Y", "evaluate these tools", "which database, library, framework,
  or service should we use", "vendor comparison", "which auth provider",
  "Postgres vs Mongo", "shortlist tools for", or "pick a tool for". The
  deliverable is an evidence-grounded comparison matrix and a recommendation
  with trade-offs. Do not use for deciding the overall approach or whether to
  build versus buy at all (use explore-solutions), for digesting the docs of a
  tool already chosen (use ground-in-docs), for assessing a product's market
  (use research-market), or for general fact-finding (use deep-research).
---

## Purpose

Research and compare specific external technical solutions against your requirements, and recommend one. The deliverable is a comparison matrix of candidates against weighted criteria, grounded in real evidence (docs, pricing, release history, community, license, benchmarks), with a recommendation and the trade-offs named. The discipline is refusing to let the favorite pick itself: define requirements before looking at products, evaluate on adoption realities rather than feature checklists, test the riskiest assumption hands-on where it matters, and state why each rejected option lost.

This runs after `explore-solutions` has settled the approach (including build versus buy); this skill picks which external solution to adopt. Lean on `deep-research` for breadth, `estimate-at-scale` for pricing at your real volume, and `vibe-code` for the proof-of-concept spike.

## Workflow

Copy this checklist and track progress:

```text
Evaluate solutions:
- [ ] 1. Define requirements and weighted criteria first
- [ ] 2. Identify the candidate set
- [ ] 3. Disqualify on hard constraints
- [ ] 4. Evaluate survivors on evidence, not marketing
- [ ] 5. Spike the riskiest assumption
- [ ] 6. Recommend with the matrix and the trade-offs
```

### 1. Define requirements and weighted criteria first

Before looking at any product, write the criteria: must-haves (hard constraints that disqualify), should-haves (weighted by importance), and deal-breakers. Defining criteria after browsing products reverse-engineers them to fit the tool you already liked. Include the adoption criteria a feature list omits: license terms, lock-in and exit cost, maturity and release cadence, support and SLA, security and compliance, total cost at your scale, integration fit, and community size and longevity.

### 2. Identify the candidate set

List the realistic options, usually three to five, including the boring incumbent and the build-it or self-host baseline. Cast wide enough not to miss the obvious leader, narrow enough to evaluate each seriously; a list of ten you cannot research properly is worse than four you can.

### 3. Disqualify on hard constraints

Apply the must-haves and drop any candidate that cannot meet one (incompatible license, no required compliance, will not run on your platform, wrong pricing model). Do not spend evaluation budget scoring a candidate a deal-breaker already eliminated; record why it was cut so the decision is auditable.

### 4. Evaluate survivors on evidence, not marketing

For each criterion, find the real signal, never the vendor's own claim:

- **Docs**: read them for depth and gaps; thin or stale docs predict the support experience.
- **Pricing**: at your actual volume, not the headline tier; the "starting at" price rarely survives contact with scale. Use `estimate-at-scale`.
- **Maturity**: changelog cadence, open-issue age, and breaking-change history; a vendor comparison page is sales, the issue tracker is truth.
- **Community and longevity**: size, recency of activity, and whether one company can sunset it.
- **Benchmarks**: third-party over first-party, and note their bias and conditions.
- **License and lock-in**: the exact terms and the cost of leaving later.

### 5. Spike the riskiest assumption

Where the decision hinges on something a feature table cannot answer (does the API actually do X, does it hold up at our load, does the migration path work), a time-boxed proof-of-concept beats more reading. Hand the build to `vibe-code`; the goal is evidence, not a product. Skip the spike only when the decision does not rest on an untested claim.

### 6. Recommend with the matrix and the trade-offs

Present the comparison table (candidates against weighted criteria), then the recommendation: the single biggest reason it wins, the strongest runner-up and why it lost, the key risk you are accepting, and the assumption that, if it changes, would change the call.

## Output shape

A matrix of candidates by weighted criterion (with disqualified options and their reason noted), then a recommendation block: pick, why, runner-up, accepted risk, and revisit-if.

## Gotchas

- **Criteria written after browsing bend to the favorite.** Requirements first, then products; otherwise the matrix is a rationalization of a choice already made.
- **Feature checklists miss what hurts later.** Counts of features do not capture lock-in, license, maturity, support, or total cost at scale, which are usually what you regret. Weight adoption criteria above feature parity.
- **Marketing is not evidence.** The comparison page, the conference demo, and the first-party benchmark are sales. Read the docs, the issues, the license, and the third-party numbers.
- **Headline pricing lies at scale.** The free tier and "starting at" price rarely hold at your real volume; price it with `estimate-at-scale` before trusting it.
- **Omitting the build or self-host baseline hides the trade-off.** Comparing only managed options buries the build-versus-buy reality; include the boring baseline even when you expect it to lose.
- **A spreadsheet cannot answer "does it actually work for us".** When the decision rests on an untested claim, a two-hour spike beats two more days of reading; analysis is not evidence.

## Example

Choosing an auth provider for a B2B SaaS:

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
