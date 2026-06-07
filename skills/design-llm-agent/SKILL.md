---
name: design-llm-agent
description: >-
  Use this skill when designing or architecting an LLM-powered application,
  agent, or agentic workflow, including agent loops, tool interfaces, context
  window management, prompt ownership, evals, human-in-the-loop steps, and
  reliability patterns. Use when the user says "build an agent", "design an
  AI workflow", "add an LLM feature", "why is my agent unreliable", or "how
  should this agent be structured". Do not use for Claude API mechanics and
  SDK usage (use the bundled claude-api reference), for authoring Claude Code
  subagents (use create-claude-agent), or for general system design with no
  LLM in the loop (use write-tech-spec).
---

## Purpose

Design LLM-powered software that survives contact with production. The grounding observation (12-factor agents): the good "agents" in production are mostly deterministic software with LLM decisions placed at exactly the right points, not a prompt, a bag of tools, and a loop. Frameworks get teams to 80% quality fast; the last 20% requires owning the prompts, the context, and the control flow, which is why the design decisions below are about ownership.

## First decision: how much agency does this need?

Most "agent" requests are a workflow with one or two judgment points. Place the LLM only where the decision genuinely requires language understanding or open-ended reasoning; everything else stays deterministic code (cheaper, testable, debuggable). The spectrum: deterministic pipeline with one LLM step, then a DAG with LLM-chosen branches, then a bounded micro-agent loop (3-10 steps), then a long-running autonomous agent. Move right only when the left fails, and say which point on the spectrum the design sits at; "agent" is not a design.

## The twelve factors, condensed

Adapted from 12-factor agents (HumanLayer); each row is a design obligation:

| # | Factor | The obligation |
|---|---|---|
| 1 | Natural language to tool calls | The LLM's job is converting intent to structured decisions; the smaller and crisper that conversion, the more reliable |
| 2 | Own your prompts | Prompts are production code: in the repo, reviewed, versioned, testable; not buried in a framework's defaults |
| 3 | Own your context window | Context is built deliberately per call (structured, dense, curated), not accumulated by appending everything |
| 4 | Tools are just structured outputs | A "tool call" is JSON the model emits and your code interprets; design the schema like an API contract |
| 5 | Unify execution state and business state | One state object that serializes; avoid a hidden second state machine inside the framework |
| 6 | Launch/pause/resume with simple APIs | Agents that cannot checkpoint cannot survive deploys, rate limits, or human approval waits |
| 7 | Contact humans with tool calls | Asking a human is a tool like any other: structured, awaitable, resumable; not an exception path |
| 8 | Own your control flow | The loop, retries, and branching live in your code where you can break, test, and instrument them |
| 9 | Compact errors into context | Feed back the distilled failure (what failed, why, what to try), not the raw stack trace, and cap repair attempts |
| 10 | Small, focused agents | 3-10 step micro-agents with crisp jobs compose; god-loops with 30 tools degrade |
| 11 | Trigger from anywhere | Entry points (chat, cron, webhook, CLI) are thin adapters over the same agent core |
| 12 | Stateless reducer | The agent is a function of (state, event) to (state, action); statelessness is what makes 6, 8, and 11 cheap |

## Design workflow

1. **Define the job and its completion criteria** before anything else: what event starts it, what "done" looks like as a checkable condition, and what failure should do (retry, escalate to human, park). An agent without completion criteria runs until the budget stops it.
2. **Place the LLM decisions** on the spectrum above; write down which steps are deterministic and which are model calls, and why each model call cannot be code.
3. **Design the tool surface** as the contract it is: few tools (a dozen focused beats fifty general), parameter schemas that make invalid calls unrepresentable, descriptions written for the model as the audience, and every destructive operation gated (confirmation, allowlist, or human tool call per factor 7).
4. **Design the context build**: what each call actually needs (task, relevant state, compacted history, distilled errors), what it must never contain (the whole database, raw logs, stale turns), and the budget. Quality degrades with bloat well before the window fills; attention is the scarce resource, not capacity.
5. **Design the failure paths**: error compaction with a bounded repair loop (two or three attempts, then escalate), idempotent tools wherever retries exist, checkpointed state at every pause point, and the human-contact tool for the decisions the agent must not make alone.
6. **Write the evals before the implementation** (the eval-first loop): a capability eval (does it do the job, on a graded set of representative cases) and a regression eval (do yesterday's cases still pass). Run the baseline, build, re-run, compare. An agent without evals is vibes with an API bill; "it worked on my three test prompts" is how 80% quality ships.
7. **Route models by tier** and record the routing: small models for classification and extraction, mid for implementation-grade reasoning, large for architecture-grade judgment; escalate a step's tier only when the lower tier fails with a reasoning gap, not preemptively.

## Reliability rules

- **Every model call returns structured output that code validates** before acting; free-text parsing in the action path is a production incident scheduled for later.
- **The loop is bounded.** Max steps, max cost, max wall-clock per run, all enforced by code (factor 8), because the model cannot be the thing that decides when the model has run too long.
- **State serializes.** Any run can be paused, inspected, resumed, or replayed from its state object; debugging an agent without replayable state is archaeology.
- **Log every model call**: inputs, outputs, latency, cost, decision taken. The eval set grows out of production failures, and failures you did not log are failures you keep.
- **Prompt changes go through the regression eval** like code changes go through tests; prompts drift quality silently in both directions.

## Gotchas

- **The framework trap is the 80% trap.** Frameworks demo brilliantly and plateau at the quality bar where you must reverse-engineer their prompts and control flow to go further; for production, owning factors 2, 3, and 8 from the start is cheaper than excavating them later.
- **More tools make the agent dumber.** Every added tool dilutes selection accuracy across all of them; the fix for "the agent picks wrong tools" is usually fewer, sharper tools, not better descriptions.
- **Multi-agent is a context partition, not a personality choice.** Reach for multiple agents when one context window cannot hold the job's state cleanly (factor 10), not to mirror an org chart; every agent boundary is a lossy serialization point.
- **Human-in-the-loop is a feature, not an admission of defeat.** The highest-leverage production agents do 95% autonomously and route the irreversible 5% through factor-7 approval; full autonomy as a design goal is how demos are built.
- **This skill designs; the spec records.** A non-trivial agent design still flows into write-tech-spec for the system around it and create-code-plan for implementation; the twelve factors shape those documents rather than replace them.
