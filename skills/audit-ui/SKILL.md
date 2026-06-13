---
name: audit-ui
description: Use this skill to review or critique an existing UI for quality and accessibility without changing it, returning a severity-ranked findings report. Use when the user says "review this UI", "audit the frontend", "critique this design", or "is this accessible", or hands over a live page, screenshots, or a component. Covers anti-slop visual quality, hierarchy and typography, accessibility (contrast, focus, ARIA, keyboard, alt text), responsive behavior, and interaction states. Do not use for building or fixing UI (use design-ui); this skill reports problems and never implements the fix.
---

## Purpose

Review an existing UI for quality and accessibility and return a severity-ranked findings report. The deliverable is the report only: this skill finds and names problems, it never edits, restyles, or rebuilds the interface. Hand fixes off to design-ui. Do not report a finding you cannot point to: every finding names a location, the dimension it fails, why it harms the user, and a concrete fix. A vague "improve the hierarchy" is not a finding.

## Workflow

```text
Audit Progress:
- [ ] 1. Target and inputs resolved
- [ ] 2. Each dimension checked against its table
- [ ] 3. Findings located, severity-ranked, fixes written
- [ ] 4. Report assembled: anti-slop verdict first, then findings by severity
```

### 1. Resolve the target and how you can observe it

Pin the target to a concrete artifact before judging: a source component file, a live URL, or screenshots. Each gives you different evidence, so record which one you have. A live page or dev server lets you check focus order, keyboard nav, hover and active states, and responsive reflow; screenshots fix the visual state only and cannot prove interaction; source code reveals semantics, ARIA, and tokens but not rendered contrast. State the inputs you have and, in the report, mark any dimension you could not verify because the input did not allow it (for example, "keyboard nav: not verifiable from screenshots"). Never infer a pass you did not observe.

When a browser tool is available and the target is viewable, inspect the live page in both light and dark modes; a clean source read is not a substitute for looking at the rendered result.

### 2. Check every dimension

Walk all six. Skipping a dimension silently reads as a pass; if a dimension does not apply, say so in the report rather than omit it.

| Dimension | What to check | Tells / common failures |
|---|---|---|
| Visual quality / anti-slop | Would someone say "AI made this" on sight? Generic palette predicted by the product category, identical card grids, gradient text, glassmorphism-everywhere, hero-metric template, uppercase tracked eyebrows on every section, numbered section markers, decorative status dots | First-order reflex: does category alone predict the palette and layout. If yes, it is templated |
| Hierarchy / spacing / typography | One clear focal point per view; spacing follows a scale, not random gaps; type hierarchy through scale and weight; body line length 65-75ch; consistent radius, accent, and icon family | Flat hierarchy (everything one weight), arbitrary gaps, gray-on-tinted body copy, over-rounding above 16px on cards |
| Accessibility (WCAG 2.1 AA) | Use the a11y checklist below | Contrast under 4.5:1 body, missing focus rings, icon-only buttons without labels, color as the only signal, skipped heading levels |
| Responsive behavior | No horizontal scroll or text overflow at 375 / 768 / 1280; touch targets at least 44x44px; layout reflows logically, not just shrinks; text stays at least 14px on mobile | Fixed widths, content clipped at narrow viewports, targets too small or too close |
| Interaction / feedback states | Every interactive element has hover, focus, active, disabled; async actions show loading; lists have empty states; errors are inline and recoverable; success is confirmed | Missing focus state, spinner where a skeleton belongs, blank "No results", destructive action with no confirm or undo |
| Content / copy | Strings read like a person wrote them; button labels are verb plus object; no marketing buzzwords; no em dashes; realistic data, not "John Doe" or fake-perfect numbers | LLM-poetic cadence, "Click here" links, exclamation marks in success messages |

### 3. Accessibility checklist

Run every item; a11y findings are the ones most often missed by eye and carry the highest user cost.

```text
- [ ] Body text contrast >= 4.5:1; large text and UI components/icons >= 3:1 (includes placeholders and button labels)
- [ ] Every interactive element reachable and operable by keyboard alone; no keyboard traps
- [ ] Visible focus indicator on every focusable element (no `outline: none` without a styled replacement)
- [ ] Tab/focus order follows visual/reading order; no positive tabIndex
- [ ] Inputs have associated labels (htmlFor/id); errors linked via aria-describedby and announced
- [ ] Heading levels sequential (no h1 -> h4 skips); landmarks present
- [ ] Meaningful images have alt text; decorative images use alt="" and aria-hidden
- [ ] Icon-only controls have an accessible name (aria-label)
- [ ] ARIA used only where native semantics fall short; no aria-hidden on focusable elements
- [ ] Meaning never conveyed by color alone
- [ ] Animations respect prefers-reduced-motion
```

### 4. Rank by severity and write the report

Assign each finding one severity. Rank by user impact, not by how easy the fix is.

| Severity | Meaning | Examples |
|---|---|---|
| Blocker | Breaks the task or fails WCAG AA; some users cannot proceed | Keyboard trap, unlabeled form input, contrast far below 4.5:1, action with no feedback at all |
| Major | Significant friction or a clear quality defect, but a workaround exists | Missing focus ring, no empty/error state, text overflow at a common breakpoint, flat hierarchy on a key screen |
| Nit | Polish; no real user impact | Slightly off spacing, minor copy awkwardness, one icon optically misaligned |

Order the report so the reader acts in the right order: lead with the anti-slop verdict (a direct yes/no on whether it looks AI-generated, with the specific tells), then findings grouped Blocker, Major, Nit. Name systemic patterns once rather than filing the same nit twenty times ("hard-coded grays instead of tokens across all cards"). Note 2-3 genuine strengths so the handoff knows what to preserve. Resist nit inflation: a report that is 90% nits buries the findings that matter. Close by pointing the fix work to design-ui; do not implement anything.

## Gotchas

- **Audit, do not redesign.** The pull toward "and here is the fixed code" is strong and wrong; this skill stops at the report. The fix belongs to design-ui, which owns the build and the design read. Mixing them produces unrequested rewrites and hides which problems were real.
- **Unverifiable is not the same as passing.** A dimension you could not observe (interaction from a screenshot, rendered contrast from source alone) is reported as not verified, with the reason. Inferring a pass you did not see is how audits miss real defects.
- **Severity is about the user, not the fix effort.** A one-line CSS fix for a contrast failure that locks out low-vision users is a Blocker, not a nit. Rank by who is harmed and how badly.
- **Reminding about accessibility at build time makes designs timid; auditing it afterward does not.** This skill is the dedicated place for the WCAG pass precisely because it runs on finished UI, not while it is being designed.

## Example finding set

Auditing a live pricing page (`/pricing`, inspected in Chrome at 1280 and 375).

```text
Anti-slop verdict: FAIL. Three identical feature cards (icon + heading + text),
an uppercase tracked eyebrow above every section, and a purple-to-blue gradient
on the hero CTA. Category (SaaS) predicts the entire look.

Blocker
- "Most popular" plan badge is conveyed by color only (green border), no text or
  icon. Dimension: Accessibility. Impact: colorblind users cannot tell which plan
  is recommended. Fix: add a visible "Most popular" text label inside the badge.
- Monthly/annual toggle is a <div onClick>; not focusable, no keyboard operation.
  Dimension: Accessibility. Impact: keyboard users cannot switch billing period.
  Fix: use a <button> (or role + tabIndex + onKeyDown) with aria-pressed.

Major
- Plan price uses #9aa0a6 gray on white (~2.9:1). Dimension: Accessibility.
  Impact: the most important number on the page is hard to read. Fix: darken to
  meet 4.5:1.
- Feature list has no empty/loading state; while plans fetch, the section is blank
  with no skeleton. Dimension: Interaction states. Fix: add a skeleton matching the
  card shape.

Nit
- Card corner radius is 20px while inputs in the FAQ below use 8px. Dimension:
  Hierarchy/consistency. Fix: standardize on one radius system (cards 12-16px).

Strengths to preserve: clear single focal point (the recommended plan), genuine
copy with no buzzwords, logical heading order.

Hand the fixes to design-ui.
```
