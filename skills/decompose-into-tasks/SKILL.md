---
name: decompose-into-tasks
description: >-
  Use this skill when breaking a spec, plan, PRD, or feature into work units
  for an issue tracker such as GitHub Issues, Jira, Rally, or Linear. Use when
  the user says "break this down into tickets", "create issues from this
  spec", "slice this into stories", "decompose into work units", "turn this
  plan into tasks", or "create the epics and stories". Do not use for a
  single-session implementation plan you will execute yourself right now (use
  create-code-plan) or for writing the spec being decomposed (use
  write-product-spec or write-tech-spec).
---

## Purpose

Decompose a spec into independently implementable, independently verifiable work units and publish them to whatever tracker the project uses. The unit of decomposition is the tracer bullet: a thin vertical slice cutting through every layer end-to-end, demoable on its own. The deliverable is an approved breakdown pushed to the tracker; nothing is ever pushed before the user approves the breakdown, because issues in a shared tracker are visible to the whole team the moment they exist.

## Workflow

### 1. Gather the source material

Work from the spec in context, or fetch what the user points at (a PRD, tech spec, plan file, or an existing parent issue/epic). With no spec at all, do not invent one; offer write-product-spec or write-tech-spec first, or decompose from a conversation-level description only if the user explicitly wants rough tickets.

### 2. Identify the tracker and conventions

Detect what the project uses before drafting, because the breakdown's shape depends on it: `gh` CLI and an Issues-enabled repo, a Jira or Rally MCP/CLI, or none (then the deliverable is files the user can paste). Ask only what detection cannot answer: which project/epic is the parent, and whether the team sizes stories (points are included only if the team uses them). Read a few existing issues for title and label conventions; tickets that match the team's voice get picked up, alien ones get re-triaged.

### 3. Explore the codebase

Skim the code the work touches so slices use the project's actual domain vocabulary and respect its structure. A breakdown written against imagined architecture produces tickets that dissolve on first contact.

### 4. Draft tracer-bullet slices

- Each slice cuts through ALL layers the behavior needs (schema, API, UI, tests), not a horizontal layer of everything
- A completed slice is demoable or verifiable on its own; "user can reset password via email link" is a slice, "build all the DTOs" is not
- Prefer many thin slices over few thick ones
- Mark each slice **HITL** (needs a human decision: design review, architectural choice, credentials) or **AFK** (implementable and mergeable without human interaction); prefer AFK, and isolate the human-dependent parts into their own slices so they do not block the rest
- Order by dependency; high-risk and unknown-heavy slices first, so a doomed approach fails before work stacks on it

**Size limits per slice** (roughly one reviewable PR):

| Signal | Threshold |
|---|---|
| Files touched | ~10 or fewer |
| Acceptance criteria | 5 or fewer |
| Duration | A focused day or two, not a week |
| Title | No "and" joining two deliverables |

**When a slice is too big, split by layer** (infra, then backend, then frontend, in that dependency order) while keeping each piece independently verifiable. Layer-splitting is the remedy for an oversized slice, not the default decomposition; defaulting to per-layer tickets recreates horizontal slicing and defers all integration risk to the last ticket.

A slice is too small when it cannot be demonstrated or verified on its own ("create the file" / "fill the file" pairs); merge it back.

### 5. Present the breakdown for review

A numbered list, one line per slice: title, HITL/AFK, blocked-by, and which spec requirement it covers. Then confirm: granularity right? dependencies correct? anything to merge or split? every spec requirement covered by some slice (walk the spec back through the list; uncovered requirements are the most common defect)? Iterate until the user approves. Offer to save the breakdown to files (one per unit) when the user wants review outside chat.

### 6. Publish in dependency order

Only after explicit approval. Create blockers first so later units reference real ticket IDs in their blocked-by field, not titles. Use the team's labels; never close or modify the parent issue or epic beyond linking. Per-unit body:

```markdown
## What to build

<the end-to-end behavior of this slice, in domain vocabulary; not layer-by-layer
implementation steps>

## Acceptance criteria

- [ ] <specific, independently testable condition>
- [ ] <...>

## Blocked by

<real ticket reference, or "None; can start immediately">
```

Add the team's optional sections only when they use them: a user-story sentence (As a / I want / so that) where the tracker culture expects it, points if the team estimates.

### 7. Report

Created IDs with links, anything that failed with the error, and the dependency graph in one glance (a simple indented list suffices; offer create-diagram if the graph is genuinely tangled).

## Guardrails

- Never publish to a tracker without explicit approval of the final breakdown; "looks good so far" mid-iteration is not approval.
- Never put file paths or code snippets in ticket bodies; tickets outlive the code they describe and stale paths actively mislead. The one exception is a decision-rich artifact (a state machine, schema, or type shape from a prototype) that encodes a choice prose cannot, trimmed to the decision.
- Every unit traces to a spec requirement, and every spec requirement traces to a unit; the two failure modes are invented work and dropped work, and both are checked in step 5.
- Do not fabricate estimates; points come from the team's scale or not at all.

## Gotchas

- **This skill writes tickets; create-code-plan writes marching orders.** A code plan is executed this session and benefits from exact file paths and ordered tasks; a ticket is picked up in three weeks by someone else and benefits from behavior descriptions and acceptance criteria. Using one where the other belongs produces either vague plans or stale tickets.
- **Horizontal breakdowns look organized and fail late.** "All schemas, all endpoints, all UI" produces three weeks of green tickets and an integration surprise in week four; the tracer bullet exists to surface that surprise in ticket one.
- **The HITL/AFK split is leverage.** Isolating human decisions into their own small tickets means everything else can proceed (or be delegated to agents) without waiting; burying a design decision inside an implementation ticket stalls the whole slice.
- **Publish order is dependency order for a mechanical reason.** Tracker blocked-by fields want real IDs; drafting them with titles and fixing them after creation is the step that always gets skipped.
