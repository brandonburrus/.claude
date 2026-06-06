---
name: create-skill
description: Use this skill when the user wants to create a new personal skill, add
  a skill to their skills library, teach the agent a new reusable behavior, or capture
  domain expertise as a skill. Also use when the user says "make this a skill", "save
  this as a skill", "turn this into a skill", "create a skill for X", "I want to
  always do Y", or pastes instructions and asks to invoke them on demand. Do not use
  for editing an existing SKILL.md or configuring automated hooks (use update-config
  for hooks).
---

## Purpose

Extract domain expertise from the user and produce a well-structured, verified skill following this library's conventions. Do not begin writing the skill until Phase 1 is complete: a skill written without grounded expertise will be generic and low-value. Do not declare the skill done until Phase 5 verification has run: a skill verified only by reading it is unverified. The deliverable is a skill directory containing SKILL.md, plus optional `scripts/` and `references/` files when warranted.

## When to Use

- User explicitly asks to create a new skill or add one to their library
- User says "make this a skill," "save this as a skill," "create a skill for X"
- User describes a repeating task they want captured as reusable behavior
- User pastes a set of instructions and says "I want to be able to invoke this"
- User says "I want the agent to always do Y" (where Y is a domain-specific procedure)

## When NOT to Use

- Editing or updating content of an existing SKILL.md (direct file edit, not a skill creation workflow)
- Configuring automated hooks or settings.json behaviors (use `update-config` instead)
- Creating an AGENTS.md or CLAUDE.md (different conventions and purpose)
- The user wants to rename or reorganize an existing skill
- Project-specific conventions with no reuse value across projects (put those in the project's AGENTS.md)

## Workflow

### Phase 1 - Extract Domain Expertise

First, mine the current conversation. If the user is saying "make this a skill" about work just completed, the answers already exist in the transcript: the procedure followed, tools used, corrections the user made along the way, and input/output formats observed. Extract these, present them back as a summary, and ask only about the gaps. Corrections the user made mid-task are the highest-value content; they mark exactly where default behavior was wrong.

If the conversation does not contain the expertise, send the user all of these questions in a single message:

1. What task or situation should trigger this skill? (defines the description trigger)
2. Walk me through how you do this from start to finish. (extracts the core procedure)
3. What do agents or people most often get wrong about this? (yields the Gotchas section)
4. What should never be done here, and why? (yields anti-patterns and When NOT to Use)
5. Is there a concrete example, past artifact, or reference I can look at? (grounds the skill in reality)
6. How broad should this skill be, one scenario or a family of related tasks? (scope decision)

Skip questions the user's original message already answers. Do not proceed to Phase 2 until the scope is unambiguous. If the user's answer introduces unrelated additions, push back; each unrelated behavior added is a signal the scope should be split into two skills.

### Phase 2 - Design the Structure

Make these decisions before writing:

**Skill type.** Classify the skill; the type drives format and how Phase 5 tests it.

| Type | Content | Test focus |
|---|---|---|
| Technique | Concrete steps to follow | Can a fresh agent apply it correctly? |
| Pattern | A way of thinking about a class of problems | Does the agent recognize when it applies and when not? |
| Reference | Lookup material: options, APIs, formats | Can the agent find and correctly use the right entry? |
| Discipline | Rules the agent has incentive to bypass | Does the agent comply under pressure? Read `references/testing-skills.md` |

**Scope.** Is this one coherent skill or should it be split? A skill that spans unrelated behaviors triggers imprecisely. A skill scoped to a single micro-step forces the agent to load multiple skills for one task. The right unit covers a complete procedure the agent performs start-to-finish.

**Degrees of freedom.** Match instruction specificity to how fragile the task is:

- High freedom (prose heuristics): multiple approaches are valid and context determines the best one. Example: review processes.
- Medium freedom (template or pseudocode with parameters): a preferred pattern exists but variation is acceptable.
- Low freedom (exact script, no deviation): the operation is fragile, must be consistent, or has one safe sequence. Write a `scripts/` script and instruct "run exactly this."

Over-specifying judgment calls makes the skill brittle; under-specifying fragile operations makes it unreliable.

**Scripts.** Bundle a script when the operation is deterministic (validation, transformation, formatting), when the same code would be regenerated on every invocation, or when errors need explicit handling. A bundled script is more reliable than generated code, costs no context until run, and its output is the only part that consumes tokens. See the Scripts section for conventions.

**Progressive disclosure.** Use `references/` only for material needed conditionally (large option tables, API docs, format specs, methodology detail). Put the core procedure in SKILL.md and state exactly when to read each reference file. Keep references one level deep: every reference file links directly from SKILL.md, never from another reference file, because nested references get partially read. Give any reference file over 100 lines a table of contents at the top. Most skills under 300 lines need no `references/` at all.

**Format.** Match structure to content type:
- Sequential phases with dependencies: numbered H3 phases under a Workflow H2
- A set of rules with no ordering: bulleted list with directive verbs
- Comparison or lookup reference: table
- Decision procedure: explicit conditional ("if X, do Y; if Z, do W")

### Phase 3 - Write the SKILL.md

Use the template below. Fill every section; delete placeholder text. Specific rules:

- `name` field must exactly match the directory name (kebab-case)
- Write the description field last (see Phase 4)
- H2 for major sections, H3 for subsections; never H1 inside the body
- Directive language: "Always," "Never," "Prefer," "Avoid." Pair each directive with its reason unless the reason is obvious. A rule whose why is understood generalizes to situations the rule's author never anticipated; a bare MUST invites loopholes the moment the literal wording does not fit
- Every code block must include a language identifier, even for shell snippets
- Use tables for comparisons, option lists, and anti-pattern catalogues
- Every skill needs both "When to Use" and "When NOT to Use" sections
- One excellent, runnable, real example beats several mediocre ones. Never implement the same example in multiple languages; the agent can port
- Use one term per concept throughout (always "endpoint", not a mix of "endpoint", "URL", "route")
- No time-sensitive content ("before August 2025, use the old API"); if legacy behavior matters, put it in a collapsed "Old patterns" subsection
- For workflows of four or more steps, include a copyable checklist at the top of the workflow so the agent can track progress and not skip validation steps
- Build feedback loops around quality-critical steps: "run the validator, fix errors, run again; proceed only when it passes"
- No emojis anywhere in the file
- No em dashes anywhere in the file
- Target 80-250 lines; hard limit 500 lines; if running long, move reference material to `references/`
- Each sentence must survive this test: "Would the agent get this wrong without this line?" If no, delete it. Assume the agent is already smart; only add context it does not have

**Template:**

```markdown
---
name: <skill-name>
description: Use this skill when <primary trigger>. Also use when <secondary triggers
  and exact user phrases>. Do not use for <near-miss boundary>.
---

## Purpose

<One short paragraph. What the agent does when this skill loads. What the deliverable is.
What the agent must NOT do before a certain condition is met, if applicable.>

## When to Use

- <Trigger condition 1>
- <Trigger condition 2>
- <Indirect trigger: user says X but means Y>

## When NOT to Use

- <Near-miss boundary 1, naming the other skill to use instead if one exists>
- <Near-miss boundary 2>

## Workflow

### 1. <First phase name>

<Directive instructions with reasons. Bullet list or short paragraph.>

### 2. <Second phase name>

<Continue.>

## <Domain-specific section: Rules, Standards, Anti-Patterns, etc.>

<Tables, bulleted rules, or prose as appropriate to the content type.>

## Gotchas

- **<Non-obvious pitfall>**: <What defies reasonable assumptions and why.>

## Examples

<One concrete, realistic example. Not a toy. Runnable if code.>
```

### Phase 4 - Write the Description Field

Write the description after the body is complete; the body reveals the true scope. A bad description causes the skill to never load (too narrow) or load at the wrong time (too broad).

| Principle | Do | Avoid |
|---|---|---|
| Imperative phrasing | "Use this skill when..." | "This skill does X" |
| User intent focus | Name what the user asks for | Name what the skill outputs |
| Trigger phrases | List exact phrasings the user would type | Vague categories only |
| Keyword coverage | Include symptoms, error messages, file types, synonyms the routing match could hit | Abstract category words only |
| Near-miss boundary | Name at least one thing it does NOT cover | Omitting boundaries entirely |
| Triggers only | Describe WHEN to use, never HOW the skill works | Summarizing the workflow |
| Generous triggering | Enumerate trigger contexts, including ones where the user does not name the skill | Single narrow trigger |
| Length | 300-600 characters | Over 1024 characters (hard limit) |

Never summarize the skill's workflow in the description. A description that says "does X by doing A then B" becomes a shortcut: the agent follows the two-word summary instead of reading the body, and the body's actual procedure silently stops executing. Triggers in the description; procedure in the body.

Err generous on triggers. Skills undertrigger by default, and the routing mechanism only consults a skill for tasks substantial enough to benefit; an extra trigger phrase rarely causes false loads, but a missing one guarantees missed loads.

Validate before finalizing: if a different agent read only this description and the user's message, would it confidently decide to load this skill? If not, revise.

### Phase 5 - Verify Before Deploying

A skill is a behavior change, and behavior changes get tested. The default verification is lightweight; offer it, and skip only if the user explicitly declines.

1. **Write 2-3 realistic test prompts.** The kind of message a real user would actually type: concrete, with file paths, specifics, and casual phrasing. Not "use the skill to do X." Confirm them with the user.
2. **Run baseline and with-skill in parallel.** For each prompt, spawn two subagents in the same message: one given only the task, one told to read the SKILL.md first and then do the task. Parallel spawning matters; serial runs tempt you to skip the baseline.
3. **Compare.** The question is not "is the with-skill output good?" but "did the skill change behavior in the intended way?" If the baseline output is equivalent, the skill adds nothing where it claims to; cut the redundant content or sharpen what remains. If the with-skill run ignored part of the procedure, that part is unclear or buried; fix the skill, not the prompt.
4. **Check for repeated improvisation.** If with-skill subagents independently write similar helper code, that code belongs in `scripts/` so future invocations stop reinventing it.
5. **Trigger check.** For each test prompt plus one near-miss negative (a prompt that shares keywords but should NOT trigger), judge whether the description alone would fire correctly. Revise the description on misses.
6. **Iterate.** Apply fixes, rerun the affected cases. Stop when behavior matches intent or the user is satisfied.

For discipline skills (rules the agent will be tempted to bypass under pressure), lightweight testing is insufficient; read `references/testing-skills.md` for pressure-scenario methodology before verifying. For skills with subjective outputs (writing style, design taste), skip assertions and have the user qualitatively review the with-skill outputs instead.

## Scripts

All bundled scripts are Python, executed with `uv run`. Conventions:

- Path: `scripts/<verb-noun>.py` inside the skill directory; descriptive names, never `helper.py` or `util.py`
- Declare dependencies inline with PEP 723 metadata so the script is fully self-contained; `uv run` resolves them in an ephemeral environment with no venv or project setup:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2"]
# ///
```

- Invoke as `uv run scripts/<name>.py <args>` in the SKILL.md instructions
- Solve, don't punt: handle foreseeable error conditions inside the script (missing file, bad input) instead of failing and leaving the agent to figure it out
- Validation errors must be verbose and actionable ("Field 'signature_date' not found. Available fields: customer_name, order_total") because the agent uses the message to self-correct
- No unexplained constants; justify every threshold or timeout in a comment. If you cannot justify the value, the agent cannot adapt it correctly
- State execution intent in SKILL.md: "Run `uv run scripts/x.py`" means execute; "Read `scripts/x.py` for the algorithm" means load as reference. Default to execute; the script's output is cheaper than its source

## Local Conventions

- Skill directory: `/Users/brandon/.claude/skills/<skill-name>/`
- SKILL.md path: `/Users/brandon/.claude/skills/<skill-name>/SKILL.md`
- Directory name must be kebab-case and match the `name` frontmatter field exactly
- Reference files: `/Users/brandon/.claude/skills/<skill-name>/references/<filename>.md`
- Scripts: `/Users/brandon/.claude/skills/<skill-name>/scripts/<filename>.py`, Python only, run via `uv run`
- No emojis anywhere in any skill file
- No em dashes anywhere in any skill file
- No H1 headings inside the body (the frontmatter `name` serves as the title)
- Confirm the path with the user before saving if there is any ambiguity about the name

## Gotchas

- **Write the description last.** Writing it before the body produces a description of what you intended to write, not what you wrote. Finish the body, then derive the description from it.

- **A workflow summary in the description silently disables the body.** The routing agent reads the description, thinks it knows the procedure, and never reads the actual steps. This is a documented failure mode, not a style preference: a description mentioning "review between tasks" caused one review where the body required two.

- **Scope creep during the interview.** Users often start with a narrow task and keep adding "and also when X." Push back on unrelated additions; each one that crosses a domain boundary is a signal this should be two skills.

- **Generic content the agent already knows.** A skill that says "write clean code" or "be thorough" adds nothing. Every line must be something the agent would not do by default or would get wrong without being told. The Phase 5 baseline run is the empirical test: if the baseline output matches the with-skill output, that content is dead weight.

- **"When to Use" and the description serve different functions.** The description is read by the routing mechanism before the skill loads. "When to Use" inside the body is read by the agent after loading. Both must be present and consistent.

- **Declarations are not procedures.** "The output should be well-structured" is a declaration and is useless. "Use H2 for major sections and include a fillable template block" is a procedure. Skills teach the agent how to approach a class of problems.

- **Missing near-miss boundary in the description causes false triggers.** Without at least one explicit exclusion, the skill loads on tangentially related requests. Name the most likely false positive.

- **A colon-space inside an unquoted description breaks the frontmatter.** YAML plain scalars cannot contain ": "; the description silently fails to parse and the skill router falls back to garbage (observed: a description showing as "Purpose"). Avoid inline colons in the description, or quote the whole string. Verify after writing: the parsed description must match what you wrote.

- **`name` field and directory name must be identical.** Create the directory first, then write the SKILL.md with the name field matching. If they diverge, skill routing can fail silently.

- **Narrative is not a skill.** "In one session we found that X caused Y" is a story about one instance. Extract the reusable rule, state it directively, and drop the narrative.
