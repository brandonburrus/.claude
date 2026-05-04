---
name: create-skill
description: Use this skill when the user wants to create a new personal skill, add
  a skill to their skills library, teach the agent a new reusable behavior, or capture
  domain expertise as a skill. Also use when the user says "make this a skill", "save
  this as a skill", "create a skill for X", "I want to always do Y", or pastes
  instructions and asks to invoke them on demand. Do not use for editing an existing
  SKILL.md or configuring automated hooks (use update-config for hooks).
---

## Purpose

Extract domain expertise from the user and produce a well-structured SKILL.md file following this library's conventions. Do not begin writing the skill until Phase 1 is complete — a skill written without grounded expertise will be generic and low-value. The deliverable is a single SKILL.md file at the correct path, ready to use.

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

## Workflow

### Phase 1 — Extract Domain Expertise

Before writing anything, send the user all of these questions in a single message:

1. What task or situation should trigger this skill? (defines the description trigger)
2. Walk me through how you do this from start to finish. (extracts the core procedure)
3. What do agents or people most often get wrong about this? (yields the Gotchas section)
4. What should never be done here, and why? (yields anti-patterns and When NOT to Use)
5. Is there a concrete example, past artifact, or reference I can look at? (grounds the skill in reality)
6. How broad should this skill be — one scenario or a family of related tasks? (scope decision)

Skip questions the user's original message already answers. Do not proceed to Phase 2 until the scope is unambiguous. If the user's answer introduces unrelated additions, push back — each unrelated behavior added is a signal the scope should be split into two skills.

### Phase 2 — Design the Structure

Make three decisions before writing:

**Scope:** Is this one coherent skill or should it be split? A skill that spans unrelated behaviors triggers imprecisely. A skill scoped to a single micro-step forces the agent to load multiple skills for one task. The right unit covers a complete procedure the agent performs start-to-finish.

**Progressive disclosure:** Will this skill need a `references/` subdirectory? Use `references/` only when reference material (large option tables, API docs, format specs) is needed conditionally. Put the core procedure in SKILL.md and tell the agent exactly when to read each reference file. For most skills under 300 lines, no `references/` subdirectory is needed.

**Format:** Match structure to content type:
- Sequential phases with dependencies: numbered H3 phases under a Workflow H2
- A set of rules with no ordering: bulleted list with directive verbs
- Comparison or lookup reference: table
- Decision procedure: explicit conditional ("if X, do Y; if Z, do W")

### Phase 3 — Write the SKILL.md

Use the template below. Fill every section; delete placeholder text. Specific rules:

- `name` field must exactly match the directory name (kebab-case)
- Write the description field last (see Phase 4)
- H2 for major sections, H3 for subsections; never H1 inside the body
- Directive language throughout: "Always," "Never," "Prefer," "Avoid" — not "you might want to" or "consider"
- Every code block must include a language identifier, even for shell snippets
- Use tables for comparisons, option lists, and anti-pattern catalogues
- Every skill needs both "When to Use" and "When NOT to Use" sections
- No emojis anywhere in the file
- No em dashes anywhere in the file
- Target 80-250 lines; hard limit 500 lines; if running long, move reference material to `references/`
- Each sentence must survive this test: "Would the agent get this wrong without this line?" If no, delete it

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

- <Near-miss boundary 1 — name the other skill to use instead, if one exists>
- <Near-miss boundary 2>

## Workflow

### 1. <First phase name>

<Directive instructions. Use "Always," "Never," "Prefer." Bullet list or short paragraph.>

### 2. <Second phase name>

<Continue.>

## <Domain-specific section — Rules, Standards, Anti-Patterns, etc.>

<Tables, bulleted rules, or prose as appropriate to the content type.>

## Gotchas

- **<Non-obvious pitfall>**: <What defies reasonable assumptions and why.>

## Examples

<One concrete, realistic example. Not a toy. Runnable if code.>
```

### Phase 4 — Write the Description Field

Write the description after the body is complete — the body reveals the true scope. A bad description causes the skill to never load (too narrow) or load at the wrong time (too broad).

| Principle | Do | Avoid |
|---|---|---|
| Imperative phrasing | "Use this skill when..." | "This skill does X" |
| User intent focus | Name what the user asks for | Name what the skill outputs |
| Trigger phrases | List exact phrasings the user would type | Vague categories only |
| Near-miss boundary | Name at least one thing it does NOT cover | Omitting boundaries entirely |
| Length | 300-600 characters | Over 1024 characters (hard limit) |
| Indirect cases | Cover implicit triggers | Only cover explicit requests |

Validate before finalizing: if a different agent read only this description and the user's message, would it confidently decide to load this skill? If not, revise.

## Local Conventions

- Skill directory: `/Users/brandon/.claude/skills/<skill-name>/`
- SKILL.md path: `/Users/brandon/.claude/skills/<skill-name>/SKILL.md`
- Directory name must be kebab-case and match the `name` frontmatter field exactly
- Reference files: `/Users/brandon/.claude/skills/<skill-name>/references/<filename>.md`
- Scripts: `/Users/brandon/.claude/skills/<skill-name>/scripts/<filename>`
- No emojis anywhere in any skill file
- No em dashes anywhere in any skill file
- No H1 headings inside the body (the frontmatter `name` serves as the title)
- Confirm the path with the user before saving if there is any ambiguity about the name

## Gotchas

- **Write the description last.** Writing it before the body produces a description of what you intended to write, not what you wrote. Finish the body, then derive the description from it.

- **Scope creep during the interview.** Users often start with a narrow task and keep adding "and also when X." Push back on unrelated additions — each one that crosses a domain boundary is a signal this should be two skills.

- **Generic content the agent already knows.** A skill that says "write clean code" or "be thorough" adds nothing. Every line must be something the agent would not do by default or would get wrong without being told. If the agent would produce the same output without the skill loaded, delete that sentence.

- **"When to Use" and the description serve different functions.** The description is read by the routing mechanism before the skill loads. "When to Use" inside the body is read by the agent after loading. Both must be present and consistent.

- **Declarations are not procedures.** "The output should be well-structured" is a declaration and is useless. "Use H2 for major sections and include a fillable template block" is a procedure. Skills teach the agent how to approach a class of problems.

- **Missing near-miss boundary in the description causes false triggers.** Without at least one explicit exclusion, the skill loads on tangentially related requests. Name the most likely false positive.

- **`name` field and directory name must be identical.** Create the directory first, then write the SKILL.md with the name field matching. If they diverge, skill routing can fail silently.
