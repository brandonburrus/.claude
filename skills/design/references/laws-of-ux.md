# Laws of UX (Build Directives)

Source: lawsofux.com. The named cognitive and perceptual principles behind the universal rules in SKILL.md, turned into build-time directives. Each law states what it says, then how to apply it while building. SKILL.md surfaces the highest-leverage ones inline; this file is the full catalog of all 30. Where a law restates a rule already enforced elsewhere (accessibility.md, interaction.md, product.md, expressive.md), the cross-link is noted instead of repeating it.

## Contents

- Reduce choices and load
- Group and structure (Gestalt)
- Memory and sequence
- Speed and flow
- Familiarity and expectation
- Targets, aesthetics, and bias

## Reduce choices and load

- **Hick's Law:** decision time grows with the number and complexity of choices. Apply: cap a single decision point at about 5 visible options; past that, group, paginate, or progressively disclose, and split a complex choice into steps.
- **Choice Overload:** too many options overwhelm and stall the decision. Apply: curate to a recommended set, mark one default ("Most popular"), and move the long tail behind "More" or advanced settings.
- **Miller's Law:** working memory holds about 7 (plus or minus 2) items. Apply: chunk content (phone numbers, nav, long forms) into groups of 5 to 7; chunk by meaning, never treat the literal 7 as a target.
- **Working Memory:** the mind briefly holds and manipulates task information. Apply: never make the user carry a value from one screen to the next; show it, prefill it, or keep it visible. Recognition over recall.
- **Cognitive Load:** the total mental effort to understand and use the interface. Apply: spend the budget on the task itself (intrinsic, germane) and cut the effort the design adds (extraneous): ambiguous labels, inconsistent patterns, visual noise, detours between intent and result.
- **Chunking:** information is easier to process when grouped into meaningful units. Apply: break long content and forms into labeled sections, group related actions, and structure dense data into scannable blocks.
- **Tesler's Law (Conservation of Complexity):** every system has irreducible complexity that someone must absorb. Apply: the system absorbs it, not the user. Reach for smart defaults, inference, and automation before a wall of configuration.
- **Occam's Razor:** the simplest solution that works is the right one. Apply: remove any element that does not earn its pixels and cut steps to the minimum the task truly needs. (See the minimalist rule in SKILL.md and the Hard No lists in the register references.)

## Group and structure (Gestalt)

- **Law of Proximity:** elements near each other are perceived as a group. Apply: communicate relationship with spacing first; tighten space within a group and widen it between groups before adding borders or labels.
- **Law of Common Region:** elements sharing a bounded area are perceived as a group. Apply: bind related controls inside a card, panel, or bordered region; never box unrelated things together.
- **Law of Similarity:** visually similar elements are perceived as related. Apply: style same-function elements identically (every primary button looks the same), and use visual difference only to signal a real difference in function. (Backs the consistency locks in SKILL.md.)
- **Law of Uniform Connectedness:** visually connected elements are perceived as the most related of all. Apply: connect items that must read as one unit with a line, container, or shared background (a labeled fieldset, a joined toggle group) rather than proximity alone when the link must be unambiguous.
- **Law of Pragnanz:** people read ambiguous or complex forms as the simplest interpretation possible. Apply: favor simple, regular shapes and a clean grid; reduce visual complexity to the simplest form that still carries the meaning.
- **Selective Attention:** people focus on a goal-relevant subset and filter the rest (banner blindness). Apply: do not style important content like an ad or dismissible chrome, and keep one clear focal point per view so attention lands where it should.

## Memory and sequence

- **Serial Position Effect:** the first and last items in a series are best remembered. Apply: place the highest-value nav and menu items at the start and end, and put the least important in the middle.
- **Peak-End Rule:** an experience is judged by its peak and its end, not its average. Apply: invest in the peak moment (the core payoff) and the ending (success states, confirmations, completion screens); a strong finish outweighs a flat middle.
- **Von Restorff Effect (Isolation Effect):** the item that differs from the rest is the one remembered. Apply: exactly one primary action per view, visually distinct from secondary and tertiary; when everything is emphasized, nothing is.
- **Zeigarnik Effect:** incomplete tasks stay in memory and nag for completion. Apply: show progress on unfinished work (checklists, "2 of 3 done", profile completeness) to pull users toward the finish, and make resuming an interrupted task easy.
- **Goal-Gradient Effect:** motivation to finish rises closer to the goal. Apply: show a progress indicator on any multi-step flow and make the finish feel near; consider endowed progress (start the bar partly filled).

## Speed and flow

- **Doherty Threshold:** productivity holds when the system and user respond within about 400ms of each other. Apply: acknowledge every action in under 400ms; if the real result is slower, show optimistic UI or a skeleton at once, never a frozen control. (See the states rules in SKILL.md and interaction.md.)
- **Flow:** the focused, immersed state of being fully absorbed in a task. Apply: protect it. Remove interruptions (unprompted modals, surprise context switches), keep the next step obvious, and let an experienced user move without friction.
- **Parkinson's Law:** work expands to fill the time available for it. Apply: shorten time-to-done with autofill, smart defaults, and saved state; a flow that can be finished faster will be.
- **Pareto Principle:** roughly 80% of use comes from 20% of the features. Apply: give that 20% the prime real estate and the least friction, and never let rarely-used features crowd the common path.

## Familiarity and expectation

- **Jakob's Law:** users spend most of their time on other sites and expect yours to work the same way. Apply: standard components (nav, search, cart, forms) follow platform and category convention; spend novelty on the brand layer, not the controls. (Backs "earned familiarity" in product.md.)
- **Mental Model:** users act on a compressed internal model of how the system works. Apply: match labels, structure, and flows to that model and close the gap between expectation and behavior rather than teaching a new one.
- **Postel's Law (Robustness Principle):** be liberal in what you accept, conservative in what you send. Apply: accept input forgivingly (trim whitespace, accept multiple formats, normalize), then emit clear, strict output; never reject on a technicality you could normalize. (Extends the forms rules in interaction.md.)
- **Paradox of the Active User:** users start using software immediately and never read the manual. Apply: make it learnable in place through sensible defaults, inline hints, and obvious affordances; never gate first use on reading docs.

## Targets, aesthetics, and bias

- **Fitts's Law:** the time to acquire a target is a function of its distance and its size. Apply: size frequent and primary targets generously (at least 44px), place them near where attention already sits, keep destructive actions clear of the primary, and exploit screen edges and corners (effectively infinite-depth targets) for high-traffic controls.
- **Aesthetic-Usability Effect:** people perceive aesthetically pleasing design as more usable. Apply: this is the premise of the whole skill, a polished UI buys trust and patience, but treat it as a floor, not a substitute; never let polish stand in for a flow that actually works.
- **Cognitive Bias:** systematic errors in judgment shape how users perceive and decide. Apply: design with known biases (anchoring on the first price seen, defaults read as recommendations, social proof) to reduce honest effort; never weaponize them into dark patterns that trick the user against their interest.
