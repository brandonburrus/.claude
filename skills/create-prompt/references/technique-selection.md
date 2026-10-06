# Technique Selection Reference

The full technique assessment and vendor-comparison tables for SKILL.md Step 5: use these to
decide whether a prompt should name a specific agentic technique, and to check that choice
against how Anthropic, OpenAI, and Google currently frame the same tradeoff.

## Technique assessment

| Technique | Current assessment | Best fit |
|---|---|---|
| Few-shot demonstrations | Strong support, especially for style, routing, edge behavior, and tool conventions | Tasks with stable examples and ambiguous natural-language rules |
| Prompt chaining | Strong when decomposition is natural; easier stages plus deterministic gates improve control | Predictable, sequential workflows |
| Routing | Strong; separates specialized prompts, tools, and models | Clearly distinguishable intents or difficulty levels |
| ReAct-style loops | Foundational but not universally optimal; interleaved reasoning, action, and observation improves grounding | Dynamic tasks where each next action depends on tool output |
| Plan-and-execute | Situational; useful for long decomposable tasks, but plans need checkpoints and replanning | Stable multi-stage work or parallelizable subtasks |
| Reflection / critic | Useful only with a trustworthy external verifier; self-critique without one can reinforce mistakes | Code tests, schema checks, explicit rubrics, or an independent evaluator agent |
| Self-consistency | Empirically supported for closed-answer reasoning, but multiplies cost | Math, classification, or problems where candidate answers can be aggregated |
| Scratchpads / explicit CoT | Model-dependent and often overused; native reasoning controls increasingly supersede verbose scratchpads | Evaluate only when it improves target metrics; never treat it as audit evidence |
| Evaluator-optimizer | Strong when criteria are measurable | Writing, research completeness, code, iterative refinement |
| RAG and context retrieval | Strong, but retrieval quality and trust labeling are critical | Current, private, or domain-specific knowledge |
| Multi-agent prompting | High upside, high cost, situational; major gains for breadth-first parallel research, but much greater token usage and coordination complexity | High-value tasks with independent subtasks and separable contexts |
| Mega-prompts / named frameworks | Generally overhyped as universal algorithms | Education or initial scaffolding only; replace with an eval-driven, task-specific contract |

## Vendor comparison

| Area | Anthropic | OpenAI | Google | Vendor-neutral conclusion |
|---|---|---|---|---|
| Architecture | Start simple; distinguish deterministic workflows from autonomous agents | Maximize a single agent before introducing multi-agent orchestration | Decompose, chain, route, and tune agent behavior explicitly | Complexity must earn its latency, cost, and reliability burden |
| Context | Smallest high-signal context; progressive disclosure, compaction, notes, subagents | Preserve relevant reasoning/state across tool calls; calibrate exploration explicitly | Structure long context carefully; put the task after large context blocks | Context assembly is a primary engineering discipline |
| Tools | Treat tool design as an agent-computer interface; optimize descriptions and outputs | Use standardized reusable tools; split agents when overlapping tools cause confusion | Clear names, descriptions, strong typing, validation, bounded active tool sets | Tool contracts are executable prompt components |
| Reasoning | Extended/interleaved thinking can help, but visible reasoning is not fully faithful | Reasoning effort and persisted reasoning state are model/API controls | Newer models reason internally; returned step-by-step reasoning is usually unnecessary | Prefer native reasoning controls and outcome verification over CoT rituals |
| Evaluation | Outcomes, transcripts, multiple trials, balanced tasks, mixed graders | Trace grading followed by repeatable datasets and eval runs | Evaluate outcome, reasoning/process, tools, and memory; mix deterministic, model, and human review | Evaluate both end state and trajectory, but avoid mandating one exact path |
