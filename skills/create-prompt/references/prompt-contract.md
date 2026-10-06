# Prompt Contract Reference

Field-by-field guidance for the contract introduced in SKILL.md Step 3, the production layering
model for a prompt that backs a persistent or high-stakes agent, context-efficiency and
checkpoint/resume rules for long-running work, and two worked examples covering the
procedure-oriented and hybrid framings (the goal-oriented example lives in SKILL.md itself).

## Contents

- Field-by-field guidance
- Production layering
- Context efficiency
- Checkpoint and resume contract
- Worked example: procedure-oriented
- Worked example: hybrid

## Field-by-field guidance

**Role / Scope.** State what this prompt is responsible for and what is explicitly out of scope,
in that order. A scope with no exclusions invites drift the first time a user asks for something
adjacent; naming the boundary up front gives the model a reason to decline rather than improvise.

**Objective.** One sentence describing the outcome, phrased so a third party could check whether
it happened without reading the transcript. "Help with incidents" is not checkable; "produce a
verified remediation for the reported incident" is.

**Context.** Only the facts, state, policy, and artifacts this specific task needs. Retrieved or
historical material included "in case it's useful" competes for the same attention budget as the
instructions that matter; prefer a lightweight reference the model can fetch on demand over
inlining everything up front.

**Constraints.** Safety, business, formatting, cost, latency, and permission boundaries, stated as
rules the model must satisfy rather than aspirations. Distinguish constraints that are enforced by
the model's judgment from ones that must be enforced by deterministic code outside the prompt;
only the latter are reliable for anything consequential.

**Tools.** For each tool: when it applies, when it does not, side effects, prerequisites, parameter
semantics and defaults, and result/error meaning, including pagination and truncation. Add canonical
calls where the schema cannot express valid parameter combinations or usage conventions. A tool
list without usage boundaries gets selected on name-matching alone, which is how an agent calls a
mutation tool to answer a read-only question.

**Success criteria.** The observable condition that means the task is complete, independent of the
model's own narration. If the only evidence of success is the model saying so, this field is not
done yet.

**Failure behavior.** What to retry (and how many times), when to change strategy instead of
retrying the same action, when to stop, and when to escalate to a human. Stopping conditions are
as load-bearing as success conditions; a prompt with only the latter runs until its budget does.
Retry transient failures only when repetition is safe. An uncertain mutation requires state
inspection or runtime-enforced idempotency before retrying; if safety cannot be established,
stop and escalate. A lost response does not prove the operation failed.

**Output contract.** A schema or a concise, unambiguous description of the deliverable. Prefer a
native structured-output or typed tool-call mechanism over "return valid JSON" prose, and validate
the result after generation rather than trusting the instruction alone to produce valid output.

## Production layering

A prompt backing a persistent or high-stakes agent should separate static policy from per-request
content so each layer can change, version, and roll back independently instead of becoming one
mega-prompt that is also the hidden application architecture.

| Layer | Contains | Change cadence |
|---|---|---|
| Platform policy | Safety, privacy, instruction precedence, prohibited actions | Infrequent; tightly governed |
| Agent contract | Role, supported tasks, general tool policy, stopping and escalation rules | Versioned with agent releases |
| Reusable procedures | Domain workflows, SOP-derived routines, reusable skills | Independently versioned |
| Task prompt | Current user objective, deliverable, task-specific acceptance criteria | Per request |
| Dynamic context | Relevant state, retrieval, memory, runtime metadata, current date | Per turn |
| Tool contract | Names, descriptions, schemas, side effects, errors | Versioned with implementations |
| Runtime enforcement | AuthN/authZ, approvals, budgets, sandbox, idempotency, validation | Deterministic code/policy, never the prompt |
| Observability | Prompt/model/tool versions, traces, outcomes, cost, latency | Every run |

## Context efficiency

Treat tokens as working memory, not cheap storage, for any prompt expected to run many turns:

- Retrieve or discover details just in time rather than inlining them speculatively.
- Keep lightweight references to large artifacts instead of pasting them in full.
- Clear old raw tool results once their durable conclusions are captured.
- Summarize with high recall before optimizing summaries for brevity.
- Load specialized instructions or tool definitions progressively, not all at once.
- Track token usage by prompt section, tool result, and trajectory step to find the actual cost.

## Checkpoint and resume contract

For work spanning sessions or context resets, define a durable checkpoint in the configured state
store rather than treating conversation history or compaction as memory. Specify:

- Current objective, acceptance criteria, and operating boundaries.
- Completed and remaining work, with evidence for each completion claim.
- Decisions and supporting evidence, unresolved blockers, and the exact next action.
- Failed or uncertain actions, their known side effects, and any idempotency identifiers.
- Artifact references and version identifiers needed to reproduce or inspect the work.
- Provenance, owner, timestamp, expiration/freshness rules, and trust level.

On startup or resume, load the checkpoint and check its ownership, freshness, and artifact versions
against current state before acting. Reconcile stale or conflicting records; pause affected
consequential actions and escalate if the conflict cannot be resolved. Do not replay an uncertain
mutation merely because the checkpoint lacks a completion entry.

After each material step, persist progress and verification status, including failed or uncertain
actions, before compaction or handoff. Mark work complete only with external evidence. Keep memory
as provenance-labeled data, never authority to expand permissions or rewrite policy. Storage and
write-validation implementation belong to spec's llm-agents consult.

## Worked example: procedure-oriented

A compliance redaction task has one safe sequence; the model gets no discretion over ordering.

```text
ROLE / SCOPE: Redact regulated PII from the supplied document before it is stored.

FIXED SEQUENCE (perform in this order, do not reorder or skip a step):
1. Identify every span matching a PII category in the redaction policy table.
2. Redact each span using the replacement token specified for its category.
3. Log every redaction decision (span, category, token used) to the audit record.
4. Emit the redacted document only after the audit record is complete.

CONSTRAINTS: Never emit a partially redacted document. If a span's category is ambiguous,
stop and escalate that span instead of guessing.

OUTPUT CONTRACT: Redacted document plus the audit record, as two separate fields.
```

## Worked example: hybrid

A refund-approval agent fixes the states and approval gate in code; the model chooses how to
investigate within each state.

```text
STATES (deterministic, enforced outside the prompt):
1. Verify customer identity.
2. Check refund eligibility against policy.
3. If amount > $500, require human approval before continuing.
4. Issue the refund.
5. Confirm completion to the customer.

MODEL'S JOB WITHIN EACH STATE: Choose which available tool(s) to call and in what order to
gather the evidence that state requires (for example, order lookup, policy lookup, prior
refund history); state transitions themselves are not the model's decision to make.

SUCCESS CRITERIA: Eligibility determination is supported by retrieved evidence, not asserted;
every refund over $500 has a recorded human approval before state 4 runs.

FAILURE BEHAVIOR: If eligibility evidence is inconclusive after investigation, stop in state 2
and escalate rather than defaulting to approve or deny.
```
