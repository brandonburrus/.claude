# My Claude Code Harness Setup ✴️

This repository is my personal [Claude Code](https://claude.com/claude-code) harness configuration: the contents of `~/.claude`. It holds a curated library of skills, a fleet of subagents, a few enforcement hooks, and the global behavioral instructions that shape how the agent works across every project.

It is tuned for one operator (me), so it favors strong conventions, hard guardrails, and high-signal automation over breadth. Most of it is portable; the parts that are personal (blog target, paths) are noted where they appear.

## Skills (62)

Skills auto-load when their description matches the task, except where noted. One skill is manual-invoke-only: `rubber-duck` (call it with `/rubber-duck`).

### Understand and plan

- `clarify-ambiguity` - sharpen a vague request before any work starts
- `explore-solutions` - generate genuinely distinct approaches and converge on a decision
- `onboard-codebase` - build an understanding of an unfamiliar repository
- `rubber-duck` - learn a concept or think through a problem; manual-invoke (`/rubber-duck`)
- `estimate-at-scale` - order-of-magnitude estimates of cost, storage, capacity, or throughput
- `create-code-plan` - structured implementation plan before writing code
- `create-migration-plan` - staged migration or deprecation plan for live systems
- `decompose-into-tasks` - break a spec or plan into tracker work units
- `research-market` - assess product-market opportunity (sizing, competition, demand, the wedge)
- `synthesize-feedback` - turn raw product feedback into signal-ranked themes and opportunities
- `prioritize-roadmap` - rank and sequence what to build next, with an explicit cut pile
- `research-solutioning` - compare external tools, libraries, or vendors against requirements, with a recommendation

### Specs and decisions

- `write-product-spec` - PRD: what a feature is and why it should exist
- `write-tech-spec` - system design or architecture document
- `write-proposal` - persuasive proposal for stakeholder buy-in
- `write-adr` - architecture decision record

### Design

- `design-api` - REST, GraphQL, and typed interface contracts
- `design-cli` - durable command-line tool design
- `design-data-schema` - SQL and NoSQL schema and access patterns
- `design-llm-agent` - LLM application and agent architecture
- `design-mcp` - MCP server design (tools vs resources vs prompts)
- `design-ui` - building and styling user interfaces
- `create-diagram` - architecture, flow, sequence, state, and ER diagrams

### Build

- `execute-code-plan` - drive an approved plan to completion through the agent pipeline (plan -> implement -> verify -> review)
- `code-with-best-practices` - implementation across the core stacks
- `follow-tdd` - test-first, with the golden-path / error-case / edge-case floor
- `vibe-code` - throwaway prototype or spike to answer a design question
- `refactor-code` - behavior-preserving cleanup
- `optimize-performance` - make code, queries, or pages faster against a goal
- `harden-security` - threat-model and harden untrusted surfaces, proactively and reactively

### Debug and operate

- `fix` - diagnose anything broken before proposing a fix
- `respond-to-incident` - drive a live outage: mitigate, classify, communicate, report
- `prepare-for-deploy` - release prep and rollback plan; never auto-deploys to production
- `open-pull-request` - open a PR for the current branch
- `triage-backlog` - triage an incoming backlog of issues
- `triage-review-feedback` - handle review feedback on your own PR
- `triage-security-finding` - triage an incoming vuln/CVE/scanner finding to a disposition

### Review and verify

- `review-pull-request` - review someone else's pull request
- `scrutinize` - intent-level adversarial review: should this exist, does it do what it claims
- `audit-architecture` - codebase architecture and tech-debt audit
- `validate-web` - drive a real browser (agent-browser) to validate a web change end to end, with evidence
- `validate-api` - send real requests (Bruno) to validate an API change; leaves a reusable collection behind

### Data and files

- `analyze-data` - analyze, aggregate, and plot tabular data (CSV, Excel, SQLite, and more)
- `edit-excel-sheet` - create, edit, and read Excel spreadsheets
- `edit-word-doc` - create, edit, and read Word documents
- `edit-powerpoint-slides` - create, edit, and read PowerPoint decks
- `edit-pdf` - create, edit, read, and fill PDF files

### Write and communicate

- `write-docs` - Diataxis-structured documentation sets from code
- `write-blog-post` - posts for blog.brandonburrus.com (personal)
- `write-post-mortem` - engineering RCA of a fixed and validated bug
- `write-eval` - build an eval suite
- `teach-through-writing` - tutorials and explainers from first principles
- `translate-for-leadership` - reshape engineering content for leadership channels
- `format-for-obsidian` - Obsidian-flavored Markdown
- `humanize` - strip AI-writing tells from prose
- `ground-in-docs` - fetch and digest real documentation before coding against an API

### Library and context (meta)

- `create-skill` - author, improve, and verify a skill
- `create-claude-agent` - author a subagent
- `create-claude-hook` - author a hook
- `learn-from-context` - capture durable learnings mid-session
- `tune-context` - audit and tighten the always-on context
- `audit-agent-context` - audit a project's AGENTS.md coverage and conformance against the standard

## Agents (9)

Subagents are thin wrappers: each preloads the relevant library skill and adds autonomous overrides (decide-and-disclose instead of asking, return-only instead of acting) plus hard guardrails. Four form a `plan -> review -> implement -> verify` pipeline; the rest are specialists.

- `implementation-planner` - produces an approved-ready implementation plan (wraps `create-code-plan`)
- `plan-reviewer` - adversarially reviews a large or complex plan before execution; read-only, never edits the plan (wraps `scrutinize` + `create-code-plan`)
- `product-spec-reviewer` - adversarially reviews a PRD before it is built on; leads with problem validity and simpler-path, read-only (wraps `scrutinize` + `write-product-spec`)
- `tech-spec-reviewer` - adversarially reviews a system design, tracing it against the real system; read-only (wraps `scrutinize` + `write-tech-spec`)
- `task-implementer` - executes one plan task test-first and returns an evidence-based report
- `completion-verifier` - independently verifies claimed-complete work; read-only, never fixes
- `root-cause-investigator` - diagnoses a failure without fixing it; restores the tree before returning
- `code-reviewer` - anti-noise PR review; never posts to GitHub
- `security-reviewer` - exploitability-ranked findings with a proof-of-concept bar for high severity

## Hooks (3)

Hooks run automatically on harness events, wired in `settings.json`.

- `inject-agents-md.py` (SessionStart, PostToolUse) - auto-injects `AGENTS.md` files, since Claude Code natively loads only `CLAUDE.md`. Root file at session start, nested files lazily when their subtree is touched.
- `block-interactive-cmds.sh` (PreToolUse: Bash) - blocks `cp`/`mv`/`rm` without `-f`, which macOS aliases to interactive variants that hang the agent on a prompt.
- `block-gh-watch.sh` (PreToolUse: Bash) - blocks `gh run watch`, which polls every few seconds and can exhaust the GitHub API rate limit.

## Conventions

Working conventions and hard constraints live in `AGENTS.md` (repository-wide) and the directory-proximate `agents/AGENTS.md` and `hooks/AGENTS.md`. Global behavioral rules that apply in every project live in `CLAUDE.md`. The authority on skill structure and conventions is the `create-skill` skill.
