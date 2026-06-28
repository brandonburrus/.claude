# Laws of UX (Audit Checks)

Source: lawsofux.com. The named cognitive and perceptual principles behind usability defects that look fine on screen but cost the user effort. Each law states what it says, then the violation to flag and the dimension it maps to. SKILL.md surfaces the highest-signal checks inline; this file is the full catalog of all 30. These are a usability lens, siblings to Nielsen's heuristics, not a replacement for the six visual and structural dimensions; file each finding under its mapped dimension and rank it by user impact like any other.

## Contents

- Reduce choices and load
- Group and structure (Gestalt)
- Memory and sequence
- Speed and flow
- Familiarity and expectation
- Targets, aesthetics, and bias

## Reduce choices and load

- **Hick's Law:** decision time grows with the number and complexity of choices. Flag: a single decision point (menu, nav, form group, plan grid) dumps many ungrouped options with no default and no progressive disclosure. Dimension: Hierarchy / Content.
- **Choice Overload:** too many options overwhelm and stall the decision. Flag: no recommended default, no "most popular", long undifferentiated lists where curation belongs. Dimension: Hierarchy / Content.
- **Miller's Law:** working memory holds about 7 (plus or minus 2) items. Flag: more than 7 peer items forced into one group with no chunking. Dimension: Hierarchy. (The 4 / 7 / 8 working-memory count in SKILL.md operationalizes this.)
- **Working Memory:** the mind briefly holds and manipulates task information. Flag: the user must remember a value from a previous screen or step instead of it being shown or prefilled. Dimension: Hierarchy / Content.
- **Cognitive Load:** the total mental effort to use the interface. Flag: extraneous load the design itself adds (ambiguous labels, inconsistent patterns, visual noise, detours). Do not flag intrinsic task difficulty. Dimension: Visual / Hierarchy. (See the intrinsic / extraneous / germane split in SKILL.md.)
- **Chunking:** information is easier to process when grouped into meaningful units. Flag: long unbroken content or forms with no sections; dense data with no scannable grouping. Dimension: Hierarchy / spacing.
- **Tesler's Law (Conservation of Complexity):** irreducible complexity must live somewhere. Flag: inherent complexity pushed onto the user as configuration the system could have defaulted or inferred. Dimension: Interaction / Content.
- **Occam's Razor:** the simplest solution that works is the right one. Flag: elements that earn no pixel competing for attention with the ones that matter. Dimension: Visual / Hierarchy.

## Group and structure (Gestalt)

- **Law of Proximity:** elements near each other are perceived as a group. Flag: related items spaced far apart, or unrelated items packed tight, so spacing implies the wrong grouping. Dimension: Hierarchy / spacing.
- **Law of Common Region:** elements sharing a bounded area are perceived as a group. Flag: a container (card, panel) binds unrelated items, or related controls are split across separate regions. Dimension: Hierarchy / spacing.
- **Law of Similarity:** visually similar elements are perceived as related. Flag: same-function elements styled differently (two primary buttons that look unlike), or unlike functions styled the same. Dimension: Hierarchy / consistency.
- **Law of Uniform Connectedness:** visually connected elements are perceived as the most related. Flag: related controls (a label and its input, a toggle group) with no visual connection, relying on proximity alone where the link is ambiguous. Dimension: Hierarchy.
- **Law of Pragnanz:** people read ambiguous forms as the simplest interpretation possible. Flag: needlessly irregular or complex layouts that slow scanning where a regular grid would read instantly. Dimension: Visual / Hierarchy.
- **Selective Attention:** people filter out goal-irrelevant regions (banner blindness). Flag: important content styled like an ad or dismissible chrome, or no clear focal point so attention has nowhere to land. Dimension: Visual / Hierarchy.

## Memory and sequence

- **Serial Position Effect:** the first and last items in a series are best remembered. Flag: the highest-value nav or menu items buried in the middle of a long list. Dimension: Hierarchy.
- **Peak-End Rule:** an experience is judged by its peak and its end. Flag: a flat or broken ending (no success confirmation, abrupt completion) or no peak moment in the core flow. Dimension: Interaction / Content.
- **Von Restorff Effect (Isolation Effect):** the item that differs is remembered. Flag: no single visual standout, or several elements competing for "primary" so the main action does not pop. Dimension: Visual / Hierarchy.
- **Zeigarnik Effect:** incomplete tasks stay in memory and nag for completion. Flag: a multi-step task with no signal of what remains; an interrupted task whose progress is silently lost. Dimension: Interaction / Content.
- **Goal-Gradient Effect:** motivation rises closer to the goal. Flag: a multi-step flow with no progress indicator, or progress that hides how near the finish is. Dimension: Interaction / Content.

## Speed and flow

- **Doherty Threshold:** interaction should respond within about 400ms. Flag: an action over about 400ms with no immediate feedback (frozen button, no skeleton, no optimistic state). Dimension: Interaction / feedback.
- **Flow:** focused immersion in a task. Flag: interruptions that break it (unprompted modals, surprise context switches, forced detours through the primary path). Dimension: Interaction.
- **Parkinson's Law:** work expands to fill the time available. Flag: a flow slower than it needs to be: no autofill, no saved state, re-entry of data the system already has. Dimension: Interaction / Content.
- **Pareto Principle:** roughly 80% of use comes from 20% of the features. Flag: the common-path 20% buried under rarely-used features competing for the same space. Dimension: Hierarchy.

## Familiarity and expectation

- **Jakob's Law:** users expect your product to work like the others they already know. Flag: a standard control reinvented to behave unlike its platform or category norm, breaking expectation for no gain. Dimension: Visual / Interaction.
- **Mental Model:** users act on an internal model of how the system works. Flag: labels, structure, or flows that contradict the obvious user model and force relearning. Dimension: Content / Interaction.
- **Postel's Law (Robustness Principle):** accept liberally, send conservatively. Flag: input rejected on a normalizable technicality (trailing space, phone or date format) the system could have accepted. Dimension: Content / Interaction.
- **Paradox of the Active User:** users dive in without reading docs. Flag: first use gated on a tutorial or manual, with no inline hints or sensible defaults to learn by doing. Dimension: Interaction / Content.

## Targets, aesthetics, and bias

- **Fitts's Law:** target acquisition time depends on distance and size. Flag: small or cramped frequent or primary targets; a destructive action adjacent to the primary; high-traffic controls placed far from where attention sits. Dimension: Responsive / Interaction.
- **Aesthetic-Usability Effect:** beautiful interfaces are perceived as more usable. Flag (auditor caution): do not let visual polish pass a broken flow. A clean look biases you toward rating it usable, so walk the primary task before you trust the surface. Dimension: all.
- **Cognitive Bias:** systematic judgment errors shape decisions. Flag: dark patterns that weaponize bias (confirmshaming, false urgency, preselected upsells, anchored fake discounts) to push the user against their own interest. Dimension: Content / Interaction.
