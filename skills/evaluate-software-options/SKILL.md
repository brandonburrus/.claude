---
name: evaluate-software-options
description: >-
  Use this skill when finding, comparing, or choosing a commercial or
  open-source software application to adopt for a business or team need,
  including CRM, ITSM, project management, document management, data
  visualization, HR, helpdesk, analytics, and similar product categories. Use
  when the user says "what CRM/tool should we buy", "find software for X",
  "compare these apps", "evaluate options for", "which platform should we use",
  "what's the best tool for", or does not yet know which products exist in a
  category. Do not use for selecting engineering building blocks a developer
  integrates such as libraries, frameworks, databases, or managed services (use
  research-solutioning), for deciding the overall approach or whether to build
  versus buy (use explore-solutions), or for assessing a product's own market
  opportunity (use research-market).
---

## Purpose

Discover which software applications exist for a stated need, rank them by how well they fit the user's confirmed requirements, and present a structured comparison. The deliverable is a two-layer output: a summary ranking table, then a detailed per-product profile for each candidate with grouped strengths and cautions. The discipline is the same one research-solutioning enforces: requirements before products. Do not search or rank until the requirement summary is gathered and explicitly confirmed, rank by fit to those requirements rather than brand recognition or popularity, and never invent precise pricing, roadmaps, or customer metrics that the sources do not support.

This skill is interactive and runs in the main conversation: the requirements interview (Phases 1-2) needs a live user and a confirmation gate, so in non-interactive contexts (CI, loops, background runs) flag the missing requirements as a blocker instead of guessing. The search-heavy discovery (Phase 3) is delegated to the `deep-researcher` agent so the web churn stays out of the main context. This skill surveys the product landscape as a buyer; when the shortlist is engineering building blocks a developer integrates (libraries, databases, managed services), hand off to `research-solutioning` instead.

## Workflow

Copy this checklist and track progress:

```text
Evaluate software options:
- [ ] 1. Establish the application type and usage context
- [ ] 2. Gather and confirm requirements (explicit yes gate)
- [ ] 3. Discover candidates via the deep-researcher agent
- [ ] 4. Evaluate and rank by fit
- [ ] 5. Present the two-layer output
```

### 1. Establish the application type and usage context

Ask what type of application they are looking for, with concrete examples to anchor it ("for example: CRM, IT service management, data visualization, document management, project management"). If the type is vague, ask one brief follow-up covering scale (individual, small team, department, or enterprise-wide) and deployment (SaaS/cloud, on-premises, or open to either), since both reshape the candidate set. Restate the result in one sentence before proceeding ("Got it, you are looking for a cloud-based CRM for a mid-market sales team").

### 2. Gather and confirm requirements

Ask the broad requirements in a single grouped message, not one at a time, so the user is not drip-fed an interrogation. Cover:

- Core use cases or key capabilities they need
- Must-have integrations (email, ERP, CRM, analytics, SSO, whatever is load-bearing)
- Constraints (budget range, deployment model, industry or region, compliance needs)
- Preferences (open source versus commercial, vendor size, known vendors they like or dislike)

Summarize the answers back as bullet points and ask "Did I capture this correctly? Anything missing or wrong?" Apply corrections once. From that point the confirmed summary is the authoritative requirement set; everything downstream is scored against it. Treat "open source versus commercial" as a real axis: unless the user rules OSS out, the candidate set should include notable open-source or self-hostable options, not commercial products only.

### 3. Discover candidates via the deep-researcher agent

Dispatch the `deep-researcher` agent (Agent tool, `subagent_type: deep-researcher`) with a brief built from the confirmed requirements. The agent cannot ask the user anything, so the brief must be complete on its own; a thin brief yields a generic, popularity-ordered list. Aim for 5-10 candidates (fewer is fine for a genuinely narrow niche), and require it to include notable OSS/self-hostable options alongside commercial ones.

Brief template:

```text
Find software applications matching these requirements and gather evidence on each.

Application type: <type + deployment + scale from Phase 1>
Confirmed requirements:
<the confirmed bullet summary from Phase 2>

Return 5-10 real, actively maintained products (include notable open-source or
self-hostable options unless OSS was ruled out). For each product report, with
sources and explicit uncertainty flags:
- Category and a one-line description of what it does
- Deployment model (SaaS, self-hosted, on-prem, hybrid)
- Typical target customer size and any industry/vertical focus
- Relevant integrations (native or via API/connectors)
- Pricing model qualitatively (tiering, per-seat, minimums); for OSS, self-host
  cost drivers. Do not invent exact prices.
- Signals of market presence, product roadmap/update cadence, and customer
  experience (docs, support, third-party reviews)
- Any visible cautions: business-model, market-strategy, or pricing risks; for
  OSS, project health, maintenance cadence, governance, and bus factor
```

If web search is unavailable in the environment, say so plainly ("I don't have live web access here, so I can't search for current products") and offer the typical categories and selection criteria instead of fabricating a product list.

### 4. Evaluate and rank by fit

Score each candidate against the confirmed requirements, not against general popularity. For each, weigh alignment with core capabilities, fit with the deployment preference, integration coverage (native or via API), fit with constraints (customer-size focus, industry, compliance), and any red flags visible in the business model, market strategy, or pricing. Assign a qualitative fit rating (Excellent, Good, Partial, or Limited; optionally a 1-5 score) and rank best-fit to lowest. State assumptions explicitly wherever pricing, roadmap, or customer-experience detail is approximate or single-sourced; carry the agent's uncertainty flags through rather than laundering them into false confidence.

### 5. Present the two-layer output

Render the summary table first, then a detailed profile per product in ranked order, using the structures in the Output section. Keep the table scannable and push the depth into the profiles.

## Output

**Layer 1, summary ranking table.** One row per candidate, ranked:

```text
| Rank | Application | Fit | What it is (1 line) | Notable strengths | Key caution(s) |
```

**Layer 2, detailed profiles.** One per product, in ranked order:

```text
### <Rank>. <Application> - <Fit rating> (<category, e.g. "Cloud SaaS CRM" or "Open-source self-hosted CRM">)

<2-4 sentences: what it does, typical use cases, typical target customer/size and any vertical focus>

Fit to requirements:
- <requirement> -> <how it maps; call out strong fits, and gaps or uncertainties>

Strengths
- Market presence: <adoption, brand, ecosystem, partner network, reputation>
- Product roadmap: <innovation pace, visible themes such as AI or integrations, update frequency>
- Customer experience: <UI quality, onboarding, documentation, support, community, third-party reviews>

Cautions
- Business model: <upsell or add-on reliance, lock-in, long-term sustainability signals>
- Market strategy: <segment mismatch such as SMB-focused when you are enterprise, heavy vertical specialization, bundling>
- Pricing structure: <per-seat scaling, required minimums, complex tiering, paid-extra key features>

Best fit: <2-3 scenarios where this product is particularly suitable>
Limitations: <2-3 situations where it is not ideal versus alternatives>
```

For open-source or self-hostable products, reinterpret the commercial-only subheadings rather than leaving them blank: Market presence becomes adoption, community size, stars, and notable deployments; Business model becomes project health, maintenance cadence, governance (single-vendor versus community), and bus factor; Pricing structure becomes self-host total cost of ownership (infrastructure, ops effort, optional paid support) instead of vendor tiers.

## Gotchas

- **Requirements before products, or the ranking rationalizes a favorite.** Confirm the requirement summary before searching. A candidate set assembled first and scored second bends the criteria to fit whatever product looked impressive, which is the exact failure research-solutioning guards against.
- **Never invent pricing, roadmaps, or metrics.** If a number is not in the sources, describe it qualitatively and flag the uncertainty ("pricing appears tiered and likely scales per seat; exact cost needs a vendor quote"). A fabricated precise price is worse than an honest "unclear".
- **Rank by fit, not fame.** The best-known product is not automatically the best fit; a market leader aimed at enterprises is a poor fit for a five-person team. Order by how well each meets the confirmed requirements and say where the popular option loses.
- **Include and adapt OSS options.** Unless OSS was ruled out, a comparison of commercial products only hides a real alternative. Do not apply the commercial business-model and pricing lens to an open-source project; use the project-health and self-host-TCO reinterpretation instead, or the profile reads as a category error.
- **The interview needs a live user.** The Phase 2 confirmation gate cannot run in a subagent or a background loop; `AskUserQuestion` is unavailable there. In non-interactive contexts, stop and flag the missing requirements as a blocker rather than guessing them.
- **The deep-researcher brief must be self-contained.** The agent cannot come back with questions, so anything it needs to scope the search must be in the brief. Underspecify it and you get a generic top-10 listicle instead of a requirement-matched shortlist.

## Example

User wants a CRM for a roughly 50-person B2B SaaS sales team, cloud-based, open to open source.

Confirmed requirements (Phase 2, after one correction):

```text
- Type: cloud CRM, ~50 seats, B2B SaaS sales team
- Core: pipeline/deal management, email sync, reporting dashboards
- Integrations (must): Gmail/Workspace, Slack, an existing analytics warehouse
- Constraints: < $75/seat/mo target, SOC2, US data residency
- Preferences: open to OSS if self-host effort is reasonable; dislike heavy upsell
```

Layer 1 (excerpt):

```text
| Rank | Application | Fit | What it is (1 line) | Notable strengths | Key caution(s) |
|---|---|---|---|---|---|
| 1 | HubSpot Sales Hub | Excellent | Cloud CRM + sales engagement | Strong Gmail/Slack integ, fast onboarding | Add-on upsell, price jumps at higher tiers |
| 2 | Pipedrive | Good | Pipeline-first SaaS CRM | Simple, low per-seat cost | Lighter reporting, fewer enterprise integ |
| 3 | SuiteCRM | Partial | Open-source self-hosted CRM | No per-seat license, full control | Self-host ops + SOC2 falls on you |
```

Layer 2 profile for the OSS option (showing the adapted lens):

```text
### 3. SuiteCRM - Partial fit (Open-source self-hosted CRM)

SuiteCRM is an open-source CRM forked from SugarCRM, covering pipeline, accounts,
and reporting. Typically run by teams that want full data control or want to avoid
per-seat licensing, often with in-house ops capacity.

Fit to requirements:
- Pipeline/email/reporting -> covered; reporting is functional but less polished
- Gmail/Slack/warehouse -> via API and community add-ons, not turnkey (uncertain)
- < $75/seat -> no license cost, but self-host TCO and ops effort replace it
- SOC2 / US residency -> your responsibility as the host, not provided

Strengths
- Market presence: long-lived OSS project with an active community and many deployments
- Product roadmap: steady community releases; pace slower than funded SaaS rivals
- Customer experience: serviceable UI; docs and support are community-driven

Cautions
- Project health: single-vendor-led with community contributions; check recent commit cadence
- Governance / bus factor: smaller maintainer base than commercial alternatives
- Self-host TCO: infrastructure, upgrades, backups, and SOC2 controls are all on you

Best fit: teams with ops capacity that prioritize data control and no per-seat cost
Limitations: not ideal when you want turnkey integrations or vendor-provided compliance
```
