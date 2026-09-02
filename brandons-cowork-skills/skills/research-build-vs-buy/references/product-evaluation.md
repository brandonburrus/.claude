# Product-evaluation depth

Read this when the build-vs-buy call leans buy and you are discovering and ranking candidate products. It carries the deep-researcher brief template, the two-layer output structures, and the open-source reinterpretation of the commercial subheadings.

## Deep-researcher brief template

Build the brief from the confirmed requirements. The agent cannot come back with questions, so anything it needs to scope the search must be in the brief; underspecify it and you get a generic top-10 listicle instead of a requirement-matched shortlist.

```text
Find software applications matching these requirements and gather evidence on each.

Application type: <type + deployment + scale from step 4>
Confirmed requirements:
<the confirmed bullet summary from step 5>

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

## Output structures

Render the summary table first, then a detailed profile per product in ranked order. Keep the table scannable and push the depth into the profiles.

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

## Open-source reinterpretation

For open-source or self-hostable products, reinterpret the commercial-only subheadings rather than leaving them blank, or the profile reads as a category error:

- **Market presence** becomes adoption, community size, stars, and notable deployments.
- **Business model** becomes project health, maintenance cadence, governance (single-vendor versus community), and bus factor.
- **Pricing structure** becomes self-host total cost of ownership (infrastructure, ops effort, optional paid support) instead of vendor tiers.
