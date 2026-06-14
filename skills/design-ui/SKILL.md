---
name: design-ui
description: Use this skill when building, styling, or redesigning any kind of User
  Interface, including web components, pages, landing pages, dashboards, or frontend
  interfaces. Also use when the user says "make this look better", "style this",
  "design a page for X", or asks for UI polish. Do not use for auditing existing
  UI without changing it (use audit-ui), writing backend logic with no visual output, or generating
  design tokens without an actual UI component.
---

## Purpose

Build distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. The deliverable is real working code, not a mockup. Do not write any UI code before declaring a Design Read (step 1): most bad LLM design output comes from jumping to a default aesthetic instead of reading the brief.

## Workflow

```text
UI Progress:
- [ ] 1. Design Read declared
- [ ] 2. Register picked, reference file read
- [ ] 3. Design system or stack chosen
- [ ] 4. Build with universal rules
- [ ] 5. Pre-flight check and visual verification
```

### 1. The Design Read

Before any code, read the signals: page kind, vibe words the user used, reference URLs or screenshots, the audience, existing brand assets, and quiet constraints (public sector, regulated industry, accessibility-first, kids' products). The audience picks the aesthetic, not your taste, and quiet constraints override aesthetic preference entirely.

Then declare one line before generating: **"Reading this as: \<page kind> for \<audience>, \<register>, leaning toward \<design system or aesthetic family>."**

With the declaration, set three dials (1-10) and hold them for the whole task; they make downstream choices auditable instead of vibes ("why does a settings page have scroll choreography?" becomes a dial violation):

| Context | Density | Motion | Richness |
|---|---|---|---|
| Admin dashboard, data-heavy tool | 7-9 | 2-3 | 3-4 |
| Internal ops tool | 7-8 | 1-2 | 2-3 |
| Customer-facing SaaS product | 5-6 | 3-4 | 5-6 |
| Marketing or landing page | 3-4 | 5-7 | 6-8 |
| Settings or configuration page | 5-6 | 2 | 3 |
| Onboarding or wizard flow | 4-5 | 4-5 | 5-6 |
| Public sector, accessibility-first | 5-6 | 1-2 | 2-3 |

Density 1 is spacious marketing, 10 is cockpit; Motion 1 is static, 10 is choreographed scroll sequences; Richness 1 is wireframe-clean, 10 is textured and layered.

If the read genuinely diverges into two directions, ask exactly one clarifying question ("closer to Linear-clean or Awwwards-experimental?"). If you can infer confidently, declare and proceed; do not ask reflexively.

### 2. Pick the register

Every UI task belongs to one of two registers. They have opposite failure modes, so the rules differ; read the matching reference file before building:

| Register | Surfaces | Bar | Read |
|---|---|---|---|
| Expressive (design IS the product) | Landing pages, portfolios, marketing, campaigns, editorial | Distinctiveness: would someone remember it? | `references/expressive.md` |
| Product (design SERVES the product) | Dashboards, admin, SaaS apps, dev tools, internal tools | Earned familiarity: would a fluent Linear/Stripe/Raycast user trust it? | `references/product.md` |

Mixed projects (marketing site + app) pick the register per surface, not per project.

### 3. Choose the foundation

If the brief reads as an established ecosystem, install and use the official package; do not recreate its CSS by hand, and do not import its tokens only to override most of them:

| Brief reads as | Use |
|---|---|
| Microsoft / enterprise SaaS | `@fluentui/react-components` |
| Material / Google-flavored | `@material/web` + Material 3 tokens |
| IBM-style B2B analytics | `@carbon/react` |
| Shopify app surfaces | Polaris (required for Shopify admin) |
| Atlassian-style product | `@atlaskit/*` |
| GitHub-style devtool | `@primer/css` (Brand variant for marketing) |
| UK / US public sector | `govuk-frontend` / `uswds` |
| Modern SaaS you own | shadcn/ui or Radix Themes + Tailwind; never ship shadcn in default state |

One design system per project. Aesthetics (glassmorphism, bento, brutalism, editorial) are not systems; build those with native CSS or Tailwind and say so honestly. Before importing any third-party package, check it exists in `package.json`; output the install command first if missing.

### 4. Build with the universal rules

These apply in both registers.

**Consistency locks.** Pick once, lock page-wide, audit before shipping:
- One accent color. A warm-grey site does not get a blue CTA in section 7.
- One corner-radius system (all-sharp, all-soft 12-16px, or a documented per-element rule). Round buttons in a square layout is broken design.
- One theme. Sections never invert from dark to light mid-page; the user must not feel they changed websites mid-scroll.
- One icon family (Phosphor, HugeIcons, Radix, or Tabler; standardize strokeWidth). Never hand-roll SVG icon paths.
- At most 3 font families (display + body + optional mono). Pair on a contrast axis (serif + sans, geometric + humanist), never two similar-but-different sans.

**Accessibility baseline**, without being asked:
- Contrast: body text ≥ 4.5:1, large text and UI components ≥ 3:1. This includes placeholder text and button labels; muted-gray-on-tinted-white body copy is the single biggest reason AI designs feel hard to read. Gray text on a colored background looks washed out: use a darker shade of the background's own hue instead.
- All interactive elements keyboard-reachable; visible styled focus states (never `outline: none` without replacement); labels associated with inputs; meaningful `alt` text; ARIA only where native semantics fall short.
- `prefers-reduced-motion` alternatives for every animation. Non-negotiable.

For full WCAG 2.1 AA verification (contrast, screen readers, ARIA live regions, forms, testing tools, anti-patterns), read `references/accessibility.md`; `interaction.md` owns the keyboard, focus, and touch-target mechanics.

**Serif discipline.** A serif typeface is permitted only when one of two gates is met: the brief explicitly names a serif, or the aesthetic genuinely calls for one (editorial, luxury, publication, manuscript, heritage, vintage) and you can state in one sentence why this serif fits this brand. Everything else (creative agency, design studio, modern brand, premium consumer, portfolio, lifestyle) defaults to a sans display face. "It feels creative, premium, or editorial" is not a gate; reaching for a serif on a generic creative brief is a top AI design tell, because the model's reflex equates "creative" with "serif."

**Typography numbers:**
- Body line length 65-75ch. Hierarchy through scale and weight with ≥ 1.25 ratio between steps.
- Display ceiling: clamp() max ≤ 6rem. Above that the page is shouting. Letter-spacing floor ≥ -0.04em.
- `text-wrap: balance` on h1-h3, `text-wrap: pretty` on long prose. No all-caps body copy.
- Test headings at every breakpoint; overflowing text is a shipped bug, the viewport is part of the design.

**Motion engineering:**
- Default to `transform` and `opacity`. The hard rule is never animate layout-driving properties (`width`, `height`, `top`, `left`, margins) casually; expand and reflow with FLIP-style transforms or `grid-template-rows` instead. Atmospheric properties (blur, `backdrop-filter`, `clip-path`, masks, shadows) are legitimate when bounded to small isolated areas and verified smooth on target devices.
- `window.addEventListener("scroll")` is banned (per-frame jank): use `useScroll()`, ScrollTrigger, IntersectionObserver (unobserve after firing once), or CSS scroll-driven animations.
- Never track continuous input (mouse, scroll progress) in `useState`; it re-renders the tree per frame and collapses on mobile. Use motion values (`useMotionValue` / `useTransform`).
- Every animation must be justifiable in one sentence as hierarchy, storytelling, feedback, or state transition. "It looked cool" means delete it.
- Reveal animations must enhance an already-visible default. Gating visibility on a class-triggered transition ships blank sections in hidden tabs and headless renderers, where transitions never fire.
- Duration by purpose, not taste: 100-150ms instant feedback (press, toggle), 200-300ms state changes (menu, tooltip, hover), 300-500ms layout changes (accordion, modal, drawer), 500-800ms entrances (hero reveal only). Over 500ms for feedback feels laggy. Exits run ~75% of the matching entrance.
- Ease out with exponential curves; define them as tokens (`--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1)`, `--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)`), never CSS default `ease`. No bounce or elastic in product UI.
- Stagger is for siblings (cards in a grid, list items), never whole sections. `animation-delay: calc(var(--i) * 50ms)` with capped total: 10 items at 50ms is the ceiling; more items means smaller per-item delay, not a longer wave.
- `will-change` only on elements about to animate (`:hover`, an `.animating` class), never preemptively across the page; it costs memory per layer.

**States and feedback.** Implement the full cycle, not just the success state: skeleton loaders matching final layout shape (not generic spinners), composed empty states that show how to populate, inline error states, and tactile `:active` feedback (`scale-[0.98]`). Two CTA hard rules, both pre-flight fails: a CTA label must fit on one line at desktop width (shorten the label or widen the button, never constrain CTA `max-width`), and one CTA intent gets one label across the whole page (nav, hero, footer), so "Get in touch" and "Let's talk" co-existing is a defect, not stylistic variety.

**Interactive components.** When the task includes forms, buttons, modals, dropdowns, tabs, or any keyboard-driven component, read `references/interaction.md` before building: it covers the eight-state matrix, `:focus-visible` rings, validate-on-blur, the native `<dialog>`/`inert`/Popover APIs that replace z-index and focus-trap hacks, undo-over-confirm, roving tabindex, and 44px touch targets.

**Content and copy:**
- Re-read every visible string before shipping. Rewrite anything grammatically broken, referent-unclear, or LLM-poetic. Boring copy beats AI-cute copy.
- Realistic data: no "John Doe", no "Acme", no `99.99%` fake-perfect numbers, no invented spec precision the brand never claimed.
- Button labels are verb + object ("Save changes", not "OK"). Link text has standalone meaning ("View pricing", not "Click here").
- No marketing buzzwords (seamless, empower, supercharge, next-generation, elevate). Name what the product literally does.
- No aphoristic cadence as the page voice: the "serious statement, then punchy short negation" rhythm is an LLM signature. Three or more sections landing on a rebuttal-shaped sentence means rewrite. Specific beats aphoristic.
- Headings in sentence case, not Title Case On Every Word. No exclamation marks in success messages; confident, not loud.

**Code quality:** semantic HTML elements; CSS custom properties for every design token; semantic z-index scale (dropdown, sticky, modal, toast, tooltip), never `z-[9999]`; `min-h-[100dvh]` never `h-screen` (iOS address bar); CSS Grid over flexbox percentage math; mobile collapse declared explicitly per multi-column section; fonts via `next/font` or self-hosted `@font-face` with `font-display: swap`, max 2 families 2-3 weights loaded.

### 5. Pre-flight check and visual verification

Before delivering, verify mechanically:

- [ ] Design Read was declared and the output matches it, including the three dials
- [ ] Consistency locks hold: one accent, one radius system, one theme, one icon family
- [ ] Contrast passes for body, placeholders, buttons, and forms
- [ ] Every animation motivated, inside its duration band, and reduced-motion wrapped
- [ ] Interactive elements have focus-visible rings and 44px touch targets; full state matrix on forms and overlays
- [ ] Any serif passes a gate (named in brief, or aesthetic fits with a stated reason); no default serif on a generic creative brief
- [ ] No CTA label wraps at desktop; no two CTAs share one intent
- [ ] Loading, empty, and error states present (product UI)
- [ ] Copy self-audit done; no banned patterns from the register reference
- [ ] No text overflow at 375px, 768px, 1280px
- [ ] Register reference checklist passed

When browser tooling is available (screenshot, Playwright, dev server), render the result and look at it in both light and dark modes before declaring done. A UI verified only by reading its code is unverified.

## Absolute Bans (both registers)

| Ban | Why |
|---|---|
| Side-stripe borders (`border-left` > 1px as colored accent on cards/alerts) | Never intentional; use full borders, tints, or nothing |
| Gradient text (`background-clip: text`) | Decorative, never meaningful; emphasize with weight or size |
| Glassmorphism as default visual language | Rare and purposeful, or not at all |
| Hero-metric template (big number + small label + gradient accent) | Saturated SaaS cliche |
| Identical card grids (icon + heading + text, repeated) | The definition of templated |
| Uppercase tracked eyebrow above every section | Appears on most AI generations regardless of brief; one deliberate kicker is voice, eyebrows everywhere is AI grammar |
| Numbered section markers (01 / 02 / 03) as scaffolding | Numbers earn their place only when order carries real information |
| Em dashes anywhere in visible copy | The most recognized LLM tell; restructure with commas, colons, periods |
| Custom cursors | Outdated, accessibility-hostile |
| Pure `#000000` or `#ffffff` | Kills depth; use off-black and off-white |
| Decorative status dots, scroll cues, locale/weather strips | Agency-portfolio decoration tells; only real semantic state earns a dot |
| Div-built fake screenshots (fake dashboards/terminals from styled rectangles) | The #1 visual tell; use real screenshots, generated images, or nothing |
| Ghost cards: `1px` border plus a soft shadow (blur ≥ 16px) on the same element | Pick one, border or shadow (≤ 8px blur), never both as decoration |
| Over-rounding: border-radius above 16px on cards, sections, or inputs | Cards cap at 12-16px; 24-40px radii are a current-generation tell. Full pill is for tags and buttons only |
| Hand-drawn or sketchy SVG illustrations (`doodle`/`sketch` classes, `feTurbulence` grain, crude path scenes) | Reads amateurish, not whimsical; if real assets are unavailable, ship no illustration |
| `repeating-linear-gradient` stripe backgrounds | Pure generated decoration with no brand meaning |
| "X theater" / "not just X, it's Y" copy constructions | Meta-criticism phrasing is instant slop; name the specific thing |

## The AI Slop Test

If someone could look at the interface and say "AI made that" without doubt, it failed. Check at two altitudes:

1. **First-order reflex:** could someone guess the theme and palette from the product category alone? (Cookware brief = beige + brass; fintech = navy + gold; AI tool = dark + purple glow.) If yes, rework until the category does not predict the design.
2. **Second-order reflex:** could someone guess it from category plus anti-reference ("AI tool that's not SaaS-dark, so editorial-typographic")? The first dodge is also a reflex. Rework until neither answer is obvious.

## Redesign Mode

When modifying an existing UI, classify first: **preserve** (modernize without breaking the brand) or **overhaul** (new visual language, content and IA preserved). If ambiguous, ask once.

- Audit before touching: extract existing brand tokens (colors, type, radii), information architecture, and patterns worth preserving. Existing brand colors override the universal palette guidance; a purple brand stays purple.
- Apply modernization levers in order of lift-per-risk, stopping when the brief is satisfied: typography refresh, spacing and rhythm, color recalibration, motion layer, hero recomposition, full block replacement.
- Never change silently: URL slugs, primary nav labels, form field names (breaks analytics and autofill), the logo, or legal/consent copy. Do not regress existing accessibility wins.

## Gotchas

- **The audience picks the aesthetic, not your taste.** "Pick a bold direction and commit" only applies after the Design Read; conviction in the wrong direction is still wrong. A procurement-panel B2B site executed as Awwwards-experimental fails regardless of craft.
- **Restraint is a register, not a failure.** In product UI the expressive playbook (atmospheric backgrounds, editorial type, asymmetric grids) is the anti-pattern. Recognizing which register you are in is most of the skill.
- **Consistency beats novelty within a page.** A page with one committed accent, one radius system, and one theme reads as designed; a page with five clever ideas reads as generated.
- **Transitions never fire in headless renderers.** Content gated behind reveal-on-scroll classes ships invisible in screenshots and hidden tabs. The default state must be visible.
- **shadcn/ui in default state is a tell.** It is a starting point you own; customize radii, colors, and typography to the project or you have shipped a template.
