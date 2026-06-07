# My Claude Code Harness Setup ✴️

This repository is my personal [Claude Code](https://claude.com/claude-code) harness configuration: the contents of `~/.claude`. It holds a curated library of skills, a fleet of subagents, a handful of enforcement hooks, and the global behavioral instructions that shape how the agent works across every project.

It is tuned for one operator (me), so it favors strong conventions, hard guardrails, and high-signal automation over breadth. Most of it is portable; the personal parts (blog target, paths) are noted where they appear. This README is the map, not the index: the `skills/`, `agents/`, and `hooks/` directories are the source of truth for what exists.

## How the skills fit together

The library mirrors the arc of building software, and skills auto-load when a task matches their description, so the right method shows up at the right moment without being asked for by name.

**Understand the problem.** A vague ask gets sharpened before any work starts, an unfamiliar repo gets mapped, and product-shaped questions (market opportunity, roadmap priority, feedback synthesis) get their own treatment.

**Write it down.** Once the problem is clear it becomes a spec or a decision record: a PRD, a system design, a proposal, or an ADR. Each interrogates before it drafts rather than guessing intent.

**Design the pieces.** Contracts and structures are designed before they are built. APIs, data schemas, CLIs, MCP servers, LLM agents, UIs, CI/CD pipelines, data migrations, and observability each have a dedicated `design-*` method.

**Plan and build.** A non-trivial change is planned, sliced into tracker tasks, then built test-first with stack-specific best practices. `execute-code-plan` drives an approved plan to completion through the agent pipeline below.

**Review, verify, validate.** Finished work is reviewed for intent and quality, then validated against reality by actually running it: one skill drives a real browser, another sends real API requests. A green test suite is necessary, never sufficient.

**Ship and operate.** Releases are prepared with a rollback plan but never auto-deployed to production, live incidents are driven to mitigation, and the aftermath is captured as a post-mortem.

Around this arc sit data and document skills (tabular analysis, visualization, Office and PDF editing), writing and communication skills, and a meta layer that maintains the library itself (authoring skills, agents, and hooks; tuning the always-on context). Each skill's `SKILL.md` is its own documentation.

## The agent pipeline

Subagents run work in isolated context and report back. They are thin wrappers: each preloads the relevant library skill, then adds the overrides a subagent needs (decide-and-disclose instead of asking the user, return-only instead of acting) plus hard read-only guardrails for anything that reviews.

The core loop is **plan -> review -> implement -> verify**: a planner produces the plan, a plan-reviewer adversarially vets it, an implementer builds each task test-first, and a completion-verifier independently confirms the work is done and actually wired in. Code and security reviewers do the final pass, and a root-cause-investigator is the off-ramp when something breaks. Spec-stage reviewers, a silent-failure auditor, and a deep-researcher are on-demand specialists dispatched as needed. Definitions live in `agents/`.

## The enforcement layer

Hooks are the rules that cannot be talked out of: they fire deterministically on harness events, wired in `settings.json`. As a class they inject project `AGENTS.md` context that Claude Code would otherwise miss, block secrets and hook-bypass flags before they land, scan ingested file and web content for prompt injection, and stop a few commands that hang the agent or burn API quota. Each is documented in `hooks/AGENTS.md`.

## Where the rules live

Global behavioral rules that apply in every project live in `CLAUDE.md`. Repository and directory conventions live in the `AGENTS.md` files (root, `agents/`, `hooks/`). The authority on skill structure and conventions is the `create-skill` skill.
