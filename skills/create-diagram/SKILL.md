---
name: create-diagram
description: Use this skill when creating any kind of diagram, including architecture,
  infrastructure, and cloud diagrams (AWS, Azure, GCP, Kubernetes, on-prem), network
  topology, C4 models, flowcharts, sequence diagrams, state machines, ER diagrams,
  class diagrams, Gantt charts, and git graphs. Use when the user says "diagram this",
  "draw the architecture", "visualize this flow", or wants any visual representation
  of a system or process. Do not use for UI mockups or wireframes (use ui-ux), editing
  existing images, or plotting charts from datasets.
---

## Purpose

Produce a correct, rendered diagram from a description, routing each request to the right tool. The deliverable is a verified image plus its source, or, when rendering tooling is genuinely unavailable, validated source clearly labeled as not render-verified. Never deliver diagram code you have not run or validated: unrendered diagram source is the primary failure mode of this skill, because syntax and import errors only surface at render time.

## Workflow

Copy this checklist and track progress:

```text
Diagram Progress:
- [ ] 1. Routed by type and destination
- [ ] 2. Matching reference read
- [ ] 3. Content planned
- [ ] 4. Source written, names resolved not guessed
- [ ] 5. Rendered and verified
- [ ] 6. Delivered with source
```

### 1. Route by diagram type and destination

| Request | Tool | Read |
|---|---|---|
| Cloud architecture, infrastructure, network topology, Kubernetes, on-prem, anything wanting provider icons | Python `diagrams` library | `references/diagrams-library.md` |
| Flowchart, sequence, state machine, ER, class, Gantt, git graph, mindmap | Mermaid | `references/mermaid.md` |
| C4 model | `diagrams` library by default; Mermaid when the destination is a Markdown file | per choice above |

Destination overrides type: when the diagram lives inside a Markdown file that GitHub, GitLab, or Obsidian will render (README, docs, vault note), prefer a fenced Mermaid block even for simple architecture, because the destination renders it natively and keeps the source editable in place. Standalone image deliverables prefer the `diagrams` library for anything infrastructure-shaped, because provider icons carry real information.

### 2. Read the matching reference

The reference files contain the tool-specific API, syntax, failure modes, and examples. Do not write source from memory of either tool; both have non-obvious traps (import casing in `diagrams`, reserved words in Mermaid) documented there.

### 3. Plan the content

List the nodes and relationships before writing source. Keep one diagram to one concern: a diagram that shows the deployment topology, the request flow, and the CI pipeline at once communicates none of them. Offer multiple diagrams instead. Around 15-20 nodes is the practical readability ceiling for a single diagram.

### 4. Write the source

- `diagrams` library: never guess an import path or class name. For any node not copied verbatim from the reference's starter list, resolve it first with `uv run scripts/find-node.py <term>`; the library has ~2,900 node classes with inconsistent casing, and guessed imports are the top cause of render failure.
- Mermaid: follow the syntax rules in the reference; quote any label containing special characters or reserved words.

### 5. Render and verify

Mandatory; this is the step that makes the skill reliable.

**Python `diagrams` path:**

```shell
uv run <filename>.py && ls <filename>.png
```

Generated scripts include PEP 723 metadata (see the reference) so `uv run` resolves the `diagrams` dependency without environment setup. On `ImportError`, resolve the correct path with `uv run scripts/find-node.py <name>` and fix; on `ExecutableNotFound: failed to execute 'dot'`, Graphviz is missing (install per the reference). Re-run until the image file exists.

**Mermaid path**, in order:

1. If `mmdc` or `npx` is available: `npx -y @mermaid-js/mermaid-cli -i <file>.mmd -o <file>.svg` (first run downloads a headless Chromium; it is slow once, then cached)
2. If neither exists, attempt one install: `npm install -g @mermaid-js/mermaid-cli`; do not retry on failure
3. If rendering is still unavailable, deliver the fenced source and state explicitly that it was validated but not render-verified
4. Markdown-destination diagrams need no image file; the fenced block is the deliverable, but render locally anyway when tooling exists, because catching a syntax error before commit is the point

**Look at the result.** After any successful render, open the image with the Read tool and check it: overlapping labels, orphaned nodes, and a layout direction that fights the content are render-success-but-diagram-failure outcomes. Fix and re-render.

### 6. Deliver

Provide the rendered image and the source file. State what was verified: "rendered and inspected" or "validated, not render-verified, because no renderer was available". Send the image to the user when it is the deliverable.

## Universal Rules

- **Never deliver source you have not run or validated.** Diagram code fails at render time, not at write time; handing over unrun source hands over the debugging.
- **Resolve names, never guess them.** Applies to `diagrams` import paths and Mermaid icon or shape names alike.
- **No keep-alive processes.** Preview servers and watch modes hang agent sessions; render to a file instead.
- **One source file per diagram**, named for its content (`payment-flow.mmd`, `vpc_topology.py`), so re-rendering and editing stay trivial.

## Gotchas

- **Renaming a class to its "correct" casing breaks it.** The `diagrams` library uses `Cronjob`, `Dynamodb`, `IOS`; the natural-looking `CronJob` or `DynamoDB` raises `ImportError`. The script resolves exact casing; trust its output over instinct.
- **Mermaid renders in more places than you think.** GitHub, GitLab, and Obsidian all render fenced `mermaid` blocks natively; an image file is often the wrong deliverable for docs because it cannot be edited or diffed.
- **A successful render is not a successful diagram.** Graphviz happily renders overlapping edges and unreadable layouts. The inspection step exists because exit code 0 proves syntax, not communication.
- **First Mermaid render is slow, not broken.** mermaid-cli downloads a headless Chromium on first use; do not abort it or conclude the tool is unavailable mid-download.
