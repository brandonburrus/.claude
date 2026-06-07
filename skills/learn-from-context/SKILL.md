---
name: learn-from-context
description: >-
  Use this skill when extracting durable learnings from the current session,
  including after the user corrects the same behavior, when a hard-won lesson,
  gotcha, or convention surfaces mid-work, at natural wrap-up points, or when
  the user says "what did we learn", "remember this", "make sure this sticks",
  "don't make that mistake again", or "capture this for next time". Also use
  proactively when noticing a repeated correction. Do not use for facts only
  relevant to this conversation, for creating the skill itself once routing
  says skill (use create-skill), or for wiring automation (use
  create-claude-hook or update-config).
---

## Purpose

Turn what this session actually demonstrated into durable, correctly-homed knowledge, so the same lesson never has to be learned twice. The discipline has two halves: extraction (only record what the session evidences, with the evidence) and routing (each learning goes to the one home where it will actually fire next time). A lesson recorded in the wrong home is a lesson lost; a lesson recorded without evidence is a guess wearing a memory's clothes.

## What counts as a learning

Mine the session for these, in descending value order:

1. **User corrections**: the user overrode, redirected, or fixed something. The single highest-value signal; it marks exactly where default behavior diverges from what this user wants. Corrections the user made twice are non-negotiable capture candidates.
2. **Hard-won discoveries**: a gotcha, bug mechanism, undocumented constraint, or environment quirk that cost real effort to find and is not derivable from the code.
3. **Repeated improvisation**: the same helper logic, command sequence, or explanation produced more than once; repetition is the signal that something reusable exists.
4. **Decisions with rationale**: choices the user made that future work must respect.

Evidence bar: a learning needs at least one explicit correction or two independent observations from the session. One-off events, preferences inferred from silence, and "they would probably want" do not qualify; over-extraction pollutes the always-on context that tune-context exists to clean.

## Routing table

Each accepted learning goes to exactly one home:

| Learning shape | Home | Why there |
|---|---|---|
| Behavioral rule that applies in every project ("always present alternatives", "never use emojis") | CLAUDE.md | Unconditionally in context; routing bets are for conditional knowledge |
| Project fact, convention, decision, or gotcha | The project's AGENTS.md (nearest one) | The global rules already mandate this; it loads with the project |
| Reusable multi-step procedure or domain expertise | A skill, via create-skill | Loads on demand by trigger; too big for always-on |
| Mechanically-checkable rule that must never be violated | A hook, via create-claude-hook | Hooks fire deterministically; instructions are probabilistic and can be argued out of |
| Recurring automation wish ("every time X, do Y") | settings.json hooks, via the bundled update-config | The harness executes these, not the model |
| Reusable role with its own context and tools | An agent, via create-claude-agent | Identity plus isolation, not just procedure |
| True this week but not durable (current branch state, in-flight work) | Nowhere, or session notes the user keeps | Recording transient state as durable knowledge plants future contradictions |

When a learning is load-bearing enough that violating it must be impossible rather than discouraged, prefer the hook over the instruction even though it costs more to build; the session that taught the lesson is the cheapest place to decide that.

## Workflow

1. **Sweep the session**: corrections, discoveries, repetitions, decisions, each with where in the conversation it happened.
2. **Filter by the evidence bar** and by durability (will this matter in a month, in another session?).
3. **Draft each learning as it would be written in its home**: a CLAUDE.md bullet in rule form, an AGENTS.md entry with the why, a skill candidate as a one-line scope, a hook candidate as event plus rule. Generalize from the instance to the rule (the narrative-is-not-a-skill principle: "we found X caused Y once" becomes the directive that prevents Y).
4. **Present the batch for approval** before writing anything: the learning, the evidence, the proposed home, the exact text. CLAUDE.md and AGENTS.md edits change standing behavior, so they are the user's call, every time. Per-item approval, not blanket.
5. **Apply the approved ones**: direct edits for CLAUDE.md/AGENTS.md entries; hand-offs to create-skill, create-claude-hook, create-claude-agent, or update-config for the rest (those skills own their own quality bars and verification).
6. **Check for contradictions while writing**: a new learning that conflicts with an existing rule or AGENTS.md entry is surfaced, not silently added alongside it; the user decides which one is now true.

## Self-correction in flight

The proactive half: when the user corrects the same thing a second time in one session, do not wait for a wrap-up. Acknowledge the pattern, apply the correction immediately, and offer the durable capture in one line ("Second time you have fixed this; want it in CLAUDE.md as a standing rule?"). Counting to two matters: offering after every single correction is noise, and never offering means the third correction is coming.

## Gotchas

- **The home determines whether the lesson fires.** A project convention written to CLAUDE.md pollutes every other project; a global rule buried in one project's AGENTS.md vanishes everywhere else; a procedure pasted into CLAUDE.md as fifty always-on lines is what tune-context will later remove. Routing is most of the value of this skill.
- **Corrections beat additions.** When a learning contradicts something already recorded, updating or deleting the old entry is the work; appending the new truth next to the old falsehood makes both unusable.
- **Do not capture what the repo already records.** Code structure, git history, and existing docs are not learnings; capturing them duplicates reality and drifts. The bar is "not derivable from the project itself".
- **Instructions decay, hooks do not.** A rule the user has now stated three times across sessions is empirically not sticking as an instruction; that is the signal to propose the hook form instead of recording the same sentence a fourth time.
- **Wrap-up sweeps miss mid-session lessons.** The best capture moment is right after the lesson lands, while the evidence is concrete; the end-of-session sweep is the backstop, not the plan.
