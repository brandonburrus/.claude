---
name: research-build-vs-buy
description: >-
  This skill should be used when deciding whether to build a capability in-house or adopt an
  existing product, and, if buying, which product to adopt for a business or team need. It applies
  when the user says "build vs buy", "should we build or buy X", "make or buy", "build it
  ourselves or use a product", "is there a product for this or do we build it", "what CRM/tool
  should we buy", "find software for X", "compare these apps", or "which platform should we use".
  It covers business applications (CRM, ITSM, project management, helpdesk, analytics, document
  management, and similar). It should not be used for selecting a developer-integrated library,
  framework, database, managed service, or dev tool, or deciding a technical approach including a
  dev component weighed against building it (use research-solutions), for assessing a product's
  own market opportunity (use research-market), or for writing the spec (use write-product-spec).
---

## Purpose

Decide whether a capability, product, or team need is better built in-house, bought or embedded from a third party, partnered for, or deferred, and when the decision leans buy, discover and rank candidate products against confirmed requirements. The deliverable is a decision with its reasoning, and, on the buy path, a ranked product comparison. The discipline is leading the decision on differentiation and user value rather than engineering cost alone, and never running the product evaluation until the call actually leans buy. Do not invent pricing, roadmaps, or customer metrics the sources do not support, and rank by fit to confirmed requirements, not by fame or popularity.

This skill is interactive and runs in the main conversation. The build-vs-buy framing and the requirements interview both need a live user and a confirmation gate, so in non-interactive contexts (CI, loops, background runs) flag the missing requirements or unconfirmed framing as a blocker instead of guessing. The search-heavy product discovery is delegated to the `deep-researcher` agent so the web churn stays out of the main context.

## Workflow

Copy this checklist and track progress:

```text
Research build vs buy:
- [ ] 1. Frame the need as an outcome, not a feature
- [ ] 2. Decide build vs buy vs partner vs defer
- [ ] 3. If lean-to-build: name the riskiest assumption and cheapest experiment
- [ ] 4. (Buy path only) Establish application type and usage context
- [ ] 5. (Buy path only) Gather and confirm requirements (explicit yes gate)
- [ ] 6. (Buy path only) Discover candidates via the deep-researcher agent
- [ ] 7. (Buy path only) Rank by fit and present the two-layer output
```

### 1. Frame the need as an outcome, not a feature

State the problem as a desired outcome and the user opportunity beneath it, not a feature request or a named product. "Should we build a dashboard" or "should we buy Salesforce" is a solution in disguise that has already foreclosed the alternatives. Name the job the user is hiring this for, the moment of need, and what they do today instead. If the need cannot be stated without naming a feature or a tool, the decision is not yet framed. For the deeper opportunity-solution-tree framing, read references/build-decision.md.

### 2. Decide build vs buy vs partner vs defer

Generate the genuinely distinct directions and weigh them. Force real distance rather than three flavors of one idea:

- **Build**: own the experience and the differentiation, at higher cost and slower time to value.
- **Buy or embed**: adopt or integrate a third-party product to get users value sooner, commoditizing that part.
- **Partner or integrate**: borrow another product's reach or capability instead of owning it.
- **Defer or do nothing**: name what the user does without this and whether that is actually painful now. This option is mandatory, not optional: roadmaps overbuild far more often than they underbuild.

Lead the decision on differentiation and user value, not engineering cost alone. Building undifferentiated surface area is cost without a moat: if users would not care who built it, that is a buy-or-embed candidate. Score the directions against the criteria in references/build-decision.md (user value, adoption, differentiation, reversibility), name the strongest rejected direction and why it lost, and state the condition that would change the call. If the decision leans buy or adopt, continue to step 4; otherwise stop after step 3.

### 3. If the call leans build, test the riskiest assumption first

A build call that scores well on paper still rests on assumptions that, if wrong, sink it. Before committing the build, name the riskiest assumption (highest uncertainty times highest cost if false) across the four product risks (value, usability, viability, feasibility), and design the cheapest experiment that would move your confidence in it. Run the experiment before the expensive build, and converge with an explicit deferral line: the slice you ship now, the slice you defer, and the signal that gates building it. See references/build-decision.md for the risk sort and experiment design.

### 4. Establish the application type and usage context

Run steps 4 through 7 only once the decision leans buy or adopt. Ask what type of application they need, with concrete examples to anchor it ("for example: CRM, IT service management, data visualization, document management, project management"). If the type is vague, ask one brief follow-up covering scale (individual, small team, department, or enterprise-wide) and deployment (SaaS/cloud, on-premises, or open to either), since both reshape the candidate set. Restate the result in one sentence before proceeding.

### 5. Gather and confirm requirements

Ask the broad requirements in a single grouped message, not one at a time, so the user is not drip-fed an interrogation. Cover:

- Core use cases or key capabilities they need
- Must-have integrations (email, ERP, CRM, analytics, SSO, whatever is load-bearing)
- Constraints (budget range, deployment model, industry or region, compliance needs)
- Preferences (open source versus commercial, vendor size, known vendors they like or dislike)

Summarize the answers back as bullet points and ask "Did I capture this correctly? Anything missing or wrong?" Apply corrections once. From that point the confirmed summary is the authoritative requirement set; everything downstream is scored against it. Treat "open source versus commercial" as a real axis: unless the user rules OSS out, the candidate set must include notable open-source or self-hostable options, not commercial products only. This confirmation gate cannot run in a subagent or background loop; in non-interactive contexts, stop and flag the missing requirements as a blocker.

### 6. Discover candidates via the deep-researcher agent

Dispatch the `deep-researcher` agent (Agent tool, `subagent_type: deep-researcher`) with a brief built from the confirmed requirements. The agent cannot ask the user anything, so the brief must be complete on its own; a thin brief yields a generic, popularity-ordered list. Aim for 5 to 10 candidates (fewer for a genuinely narrow niche), and require it to include notable OSS or self-hostable options unless OSS was ruled out. Use the brief template in references/product-evaluation.md. If web search is unavailable, say so plainly and offer the typical categories and selection criteria instead of fabricating a product list.

### 7. Rank by fit and present the two-layer output

Score each candidate against the confirmed requirements, not against general popularity. For each, weigh alignment with core capabilities, fit with the deployment preference, integration coverage, fit with constraints (customer-size focus, industry, compliance), and any red flags in the business model, market strategy, or pricing. Assign a qualitative fit rating (Excellent, Good, Partial, or Limited) and rank best-fit to lowest. Carry the agent's uncertainty flags through rather than laundering them into false confidence. Render the summary ranking table first, then a detailed profile per product in ranked order, using the structures in references/product-evaluation.md.

## Gotchas

- **Frame the fork as an outcome, or the options foreclose themselves.** Arriving with "build feature X" or "buy product Y" and comparing flavors of it is fake divergence. Go back up to the opportunity and regenerate the build, buy, partner, and defer directions from there.
- **Differentiation leads, not engineering cost.** Spending the team's differentiation budget on undifferentiated surface area is a product mistake, not just an engineering one. Raw build cost enters only as time to value and as a tie-breaker, never as the lead axis.
- **The buy evaluation runs only once the call leans buy.** Discovering and ranking products before the build-vs-buy decision is settled answers a question the user may not be asking and bends the framing toward whatever product looked impressive.
- **Requirements before products, or the ranking rationalizes a favorite.** Confirm the requirement summary before searching. A candidate set assembled first and scored second bends the criteria to fit whatever product looked impressive.
- **Never invent pricing, roadmaps, or metrics.** If a number is not in the sources, describe it qualitatively and flag the uncertainty ("pricing appears tiered and likely scales per seat; exact cost needs a vendor quote"). A fabricated precise price is worse than an honest "unclear".
- **Rank by fit, not fame.** The best-known product is not automatically the best fit; a market leader aimed at enterprises is a poor fit for a five-person team. Order by how well each meets the confirmed requirements and say where the popular option loses.
- **Include and adapt OSS options.** Unless OSS was ruled out, a comparison of commercial products only hides a real alternative. Apply the project-health and self-host-TCO reinterpretation in references/product-evaluation.md, not the commercial business-model lens, or the profile reads as a category error.
- **The interview needs a live user.** Both the framing confirmation and the Phase 5 requirements gate need `AskUserQuestion`, which is unavailable in a subagent or background loop. In non-interactive contexts, stop and flag the missing input as a blocker rather than guessing.

## Example

User asks "should we build our own customer support tool or buy one?" for a 40-person SaaS company.

Step 1 reframes the fork: the outcome is "support agents resolve tickets faster and customers self-serve common issues," not "build a helpdesk." Step 2 weighs the directions: helpdesk is table-stakes, not where this product differentiates, so building it is differentiation budget spent on commodity surface area. The call leans buy. (Had it leaned build, step 3 would name the riskiest assumption, for example whether agents would adopt a custom tool over their current workaround, and design a concierge-style probe before committing.)

The buy path then runs. Step 4 establishes type and context (cloud helpdesk, ~15 agents, mid-market). Step 5 gathers and confirms requirements behind the yes gate (ticketing, email and Slack integration, knowledge base, SOC2, open to OSS). Step 6 dispatches the deep-researcher with a self-contained brief including notable OSS options (for example Zammad). Step 7 returns the two-layer output: a ranked summary table, then per-product profiles with the OSS lens applied to the self-hostable candidate.
