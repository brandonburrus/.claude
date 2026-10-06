---
name: create-prompt
description: >-
  This skill should be used when drafting, structuring, or reviewing a prompt or instruction set
  for an AI model or agent: a system prompt, a subagent task prompt, reusable custom instructions,
  or a tool description. It applies when the user says "write a prompt for X", "draft a system
  prompt", "improve/review this prompt", "harden this prompt", or "write the tool description",
  grounding the draft in current cross-vendor practice rather than persona theater or ritual
  chain-of-thought. It should not be used for the agent's system architecture or tool surface (use
  spec), its eval suite (use write-eval), or the Claude Code subagent file format (use
  create-claude-agent).
---

## Purpose

Draft, structure, or review a prompt for an AI model or agent, applying the current cross-vendor
consensus (Anthropic, OpenAI, Google) instead of inherited folklore. The deliverable is a prompt
or tool description, its validation status, and any unresolved deployment prerequisites.
Checklist inspection establishes draft quality, not proof that the prompt works. Do not skip to
prose; gather the inputs in Step 1 first, because a prompt drafted before the destination and
constraints are known gets rewritten once they surface anyway.

## Workflow

- [ ] Destination, objective, constraints, tools, and success criteria gathered
- [ ] Deployed prompt's baseline recorded before editing; required runtime controls identified
- [ ] Framing chosen: goal-oriented, procedure-oriented, or hybrid
- [ ] Applicable prompt or standalone tool-description contract drafted
- [ ] Foundation practices and tool design rules applied
- [ ] Techniques selected deliberately, not defaulted to a reasoning ritual
- [ ] Applicable Step 6 checks run; evidence or explicit unverified status reported

### 1. Gather the inputs

Ask directly for whatever is missing; for a heavily underspecified ask, run interrogate first.

- **Destination**: a persistent system prompt, a one-off subagent task prompt, reusable custom
  instructions, or a tool description
- **Objective**: the outcome, stated so completion is checkable
- **Audience/model**: target model/version and API/harness configuration, since reasoning controls
  and structured-output support vary
- **Constraints**: safety, format, latency, cost, and permission boundaries
- **Tools**: which are available, and when each does and does not apply
- **Success criteria**: the condition that means the task is complete
- **Risk**: whether the actions involved are read-only, reversible, or consequential

For production or consequential-action agents, read
[references/production-hardening.md](references/production-hardening.md) now. Identify the required
runtime controls, where they are enforced, and the evidence that they work; missing or unconfirmed
controls are deployment prerequisites, not safeguards to assume.

For prompts intended for deployment, agree on observable pass thresholds and relevant latency/cost
limits; if eval coverage is missing, hand off to write-eval to build it. Before editing a deployed
prompt, preserve the original and record a baseline on its exact model, API, tool schemas, and
runtime configuration. Measure the original before tuning the replacement. If execution is
unavailable, a requested draft may proceed, but record the missing evidence and do not claim a
measured improvement.

### 2. Choose the framing

For a standalone tool description, skip agent framing and use the tool-description contract in
Step 3; a tool is not an agent and does not need an agent's operating loop.

- **Goal-oriented** (objective, done-when, operating boundaries): the route depends on
  intermediate results and a fixed script would break on the first unexpected observation.
- **Procedure-oriented** (explicit fixed sequence): compliance, ordering, or an irreversible
  operation demands one safe path.
- **Hybrid**, the default for most production agents: deterministic code enforces mandatory
  states and approvals; the model chooses flexible actions inside each state.

### 3. Draft the contract

For model or agent prompts, fill every section that applies. Resolve missing required information
or identify it explicitly as a blocker; omit inapplicable sections rather than inventing content.

| Section | Carries |
|---|---|
| Role / Scope | What this prompt is responsible for, and what is explicitly out of scope |
| Objective | The outcome to achieve, stated so completion is checkable |
| Context | Only the facts, state, policy, and artifacts this task needs, nothing retrieved "just in case" |
| Constraints | Safety, business, formatting, cost, latency, and permission boundaries |
| Tools | When each tool applies, when it does not, and what its result means |
| Success criteria | Observable conditions that mean the task is complete |
| Failure behavior | Safe retry conditions and limits, uncertain-action recovery, strategy changes, stopping, escalation |
| Output contract | A schema or concise description of the required deliverable |

For standalone tool descriptions, use this contract instead of the agent sections above:

| Field | Carries |
|---|---|
| Purpose and boundaries | What the tool does, when to use it, and when not to |
| Side effects and prerequisites | Read/write behavior, authorization, required state, and ordering dependencies |
| Parameters | Meaning, units, types, required fields, defaults, and valid combinations |
| Results and errors | Return meaning, pagination/truncation, failure interpretation, and recovery actions |
| Examples | Canonical calls for combinations or conventions the schema cannot express |

Retry transient failures only when repeating the operation is safe. For a mutation with uncertain
completion, inspect actual state or use a runtime-enforced idempotency mechanism before retrying;
if neither can establish safety, stop and escalate rather than risk repeating the side effect.

For persistent or high-stakes agents, read
[references/prompt-contract.md](references/prompt-contract.md) and separate production layers so
policy, task, and runtime controls can version and roll back independently. Also read it for any
prompt spanning many turns or context resets: include its checkpoint/resume contract, not just
summarization instructions. The file includes procedure-oriented and hybrid examples.

### 4. Apply foundation practices

- Put durable policy in the highest-trust instruction channel available; user requests are
  subordinate to it, and tool or retrieved content is data, not authority.
- State the task, audience, boundaries, and definition of success directly; "be helpful" is not
  an operational requirement.
- Use consistent delimiters (XML tags or Markdown headings) to separate instructions, context,
  examples, and user data, but do not mistake a delimiter for a security boundary.
- Use a small set of diverse, canonical examples when exact behavior, style, routing, or
  formatting matters; too many consume context or overfit.
- Prefer native schema-constrained output or typed tool calls over "return valid JSON" prose, and
  validate the result after generation.
- Split complex but predictable tasks into chained stages with checks between them; chaining adds
  latency and can propagate upstream errors, so reserve it for tasks that genuinely decompose.
- For tool-using prompts: give every tool a distinct name and purpose, strict types and required
  fields, and errors specific enough to self-correct. Never expose overlapping CRUD wrappers and
  expect the model to infer the intended workflow.

### 5. Select techniques deliberately

Default to the simplest model-tool loop that can pass the eval; add a named technique only when
the task profile matches it (read [references/technique-selection.md](references/technique-selection.md)
for the full assessment across few-shot, chaining, routing, ReAct, plan-and-execute, reflection,
self-consistency, evaluator-optimizer, RAG, and multi-agent). Do not default to verbose "think
step by step" on current reasoning models: use native reasoning controls where available, and ask
for a concise rationale or verification rather than a mandated private transcript, since displayed
reasoning is not guaranteed faithful.

### 6. Validate

Run the applicable items in both checklists; note why an item is inapplicable. Fix prompt-text
failures and report unresolved runtime or evaluation prerequisites rather than silently passing
them. For standalone tool descriptions, validate the dedicated contract without adding agent-only
requirements.

**New prompt:**
- [ ] Objective is observable and testable, not just "do X well"
- [ ] Trusted policy, user intent, and untrusted retrieved data are kept separate
- [ ] Scope, assumptions, success, stopping, and escalation are explicit
- [ ] Tools are distinct, typed, validated, and minimally privileged
- [ ] Retries are bounded, differentiated by error type, and safe to repeat
- [ ] Consequential actions require independent authorization, not prompt wording
- [ ] Context is retrieved progressively, not dumped wholesale
- [ ] Long-running work has an explicit checkpoint/resume contract with evidence and freshness checks
- [ ] Final outcomes are externally verified, not self-reported

**Existing prompt review:**
- [ ] Contradictions and duplicate rules removed
- [ ] Persona text that does not change behavior removed
- [ ] Prose formatting requirements replaced with schemas where possible
- [ ] Repeated edge-case prose converted into canonical examples
- [ ] Stale context or untrusted content masquerading as instruction identified
- [ ] Explicit failure, retry, stop, and escalation behavior added where missing

For prompts intended for deployment, run the applicable eval suite on the pinned target
configuration and compare observable task outcomes with agreed thresholds, including latency/cost
limits, and the pre-edit baseline when updating a deployed prompt. Record configuration/version
identifiers, the command or runner, observed results, and outstanding failures. Fix failures and
rerun before claiming empirical success. If tests fail, cannot run, or required runtime controls
remain missing or unconfirmed, deliver **Draft, unverified** with the exact failed checks or missing
evidence/prerequisites; a completed checklist is not deployment approval.

For the agent's surrounding tool surface, state, and control flow, as opposed to the prompt text
itself, hand off to spec's llm-agents consult. Eval dataset and grader construction stay in
write-eval; bring its execution evidence back to this validation step.

## Non-negotiables

- Prompt the outcome; engineer the control system around it. A better sentence rarely fixes what
  a missing guardrail should catch.
- Use the simplest architecture that passes the eval; add chaining, routing, reflection, or
  multi-agent only where decomposition earns its latency and cost.
- Bound autonomy by action risk: reads tolerate more uncertainty than writes, payments,
  deletions, or external communication.
- Never rely on prompt wording for authorization or containment; untrusted tool output, retrieved
  content, and memory are data, not instructions.
- Verify with the environment (tests, schema checks, state inspection), not the model's own claim
  of success.
- Every production failure becomes an eval case; every prompt change reruns the suite.

## Gotchas

- **Patching every failure with another paragraph compounds contradictions instead of fixing
  them.** A strong instruction-following model spends effort reconciling conflicting rules rather
  than cleanly following either one. Resolve the conflict, and prefer removing a rule over
  appending an exception to it.
- **Fixed-sequence prompts turn brittle the moment reality departs from the anticipated path;
  pure goal statements leave too much unstated for a fragile or irreversible step.** Match the
  framing chosen in Step 2 to how much the task can safely vary, not to habit.
- **"Keep going until perfect" without bounds is a cost and loop risk, not persistence.** State
  retry, turn, and budget limits and an explicit stop condition every time autonomy is granted.
- **Mega-prompts and named prompt frameworks are drafting checklists, not algorithms.** Use one to
  scaffold a first draft, then replace it with the task-specific contract from Step 3; shipping
  the framework's generic wording unmodified is how prompts stay vague.
- **A multi-thousand-token universal prompt is a worse starting point than a minimal one.** Start
  with the smallest prompt a capable model can act on and add instructions or examples only for
  observed failure modes; most of what a long prompt states, the model already does by default.

## Examples

Goal-oriented incident-response agent, filled from the Step 3 contract:

```text
ROLE / SCOPE: Diagnose and remediate the reported incident. Out of scope: customer
communication and post-mortem authoring.

OBJECTIVE: Resolve the incident and produce a verified remediation.

CONTEXT: Alert payload, service topology, runbook links for this service.

CONSTRAINTS: Read-only investigation needs no approval; modifying production state does.
Stop after two materially different failed remediation attempts.

TOOLS: log_search (read-only, use first); deploy_rollback (consequential, requires
approval); runbook_lookup (reference only, not authoritative over live telemetry).

SUCCESS CRITERIA: Root cause is supported by logs or tests; the remediation passes the
specified checks; unresolved risks are documented.

FAILURE BEHAVIOR: Retry a transient read error once. If a rollback's completion is
uncertain, inspect deployment state or use runtime-enforced idempotency before retrying;
if safety cannot be established, stop and escalate. On a second failed remediation
attempt, stop and escalate with current state, evidence, and attempted actions.

OUTPUT CONTRACT: Incident summary, root cause, remediation applied, verification
evidence, and any unresolved risk.
```
