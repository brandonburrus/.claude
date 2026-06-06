# Expressive Register: Landing Pages, Portfolios, Marketing, Editorial

Design IS the product here. The bar is distinctiveness: would someone remember this page? Read this entire file before building; the rules below come from documented production failures of AI-generated landing pages.

## Contents

- Direction and commitment
- Typography
- Color
- Hero discipline
- Layout diversification
- Eyebrow rationing
- Backgrounds and depth
- Motion
- Images and visual assets
- Content density
- Landing-page tells (banned patterns)
- Aesthetic direction starting points

## Direction and commitment

Derive the direction from the Design Read, then execute it with conviction. The enemy is not maximalism or minimalism; it is vagueness and hedging. Define the single most memorable thing about the interface before starting; everything else serves that anchor. Match implementation complexity to the vision: maximalist designs need elaborate motion and effects, refined designs need precision in spacing and type. Both fail when executed timidly.

## Typography

- One display face (characterful) + one body face (readable). Distinctive choices over defaults: avoid Inter, Roboto, Arial, system-ui as the personality-carrying face. Inter is acceptable only when the brief explicitly wants neutral/Linear-style or is accessibility-first public sector.
- Strong default pairings: Geist + Geist Mono, Satoshi + JetBrains Mono, Cabinet Grotesk + Inter Tight. Vary across projects; converging on the same font every generation is itself a tell (Space Grotesk is the canonical example).
- **Serif discipline.** Sans-serif display is the default, including for creative/premium/agency briefs. "Feels editorial" is not a reason to reach for serif; that reflex is the most-tested AI tell. A serif is justified only when the brand brief names one, or the aesthetic is genuinely editorial/luxury/publication AND you can articulate why that serif fits that brand. Fraunces and Instrument Serif are banned as defaults (the two LLM-favorite serifs). Do not reuse the same serif across consecutive projects.
- **Emphasis stays in-family.** To emphasize a word in a headline, use italic or bold of the same font. Injecting a serif word into a sans headline for visual interest is amateur.
- **Italic descender clearance.** Italic display words containing y g j p q clip under `leading-none`. Use `leading-[1.1]` minimum plus bottom padding reserve.
- One dominant size moment per composition; uniform evenly-distributed type sizes read as templated.

## Color

- Commit: dominant background + dominant foreground + one sharp accent, executed page-wide. A 2-3 color palette with conviction beats 10 colors used timidly. CSS custom properties for every color.
- One palette per project; do not drift between warm and cool grays.
- **The purple rule.** AI-purple gradients and neon glows are the default reach; banned unless the brand is actually purple, and then executed with a consistent palette, not gradient slop.
- **The warm-neutral ban.** Cream/sand/beige/parchment body backgrounds are the saturated AI default for anything "warm, premium, artisan, editorial". Token names like `--paper`, `--cream`, `--bone` are tells in themselves. Carry warmth in accent, typography, and imagery instead; pick a saturated brand color, a true off-white, or a clearly-branded mid-tone as the body.
- **Premium-consumer palette rotation.** For cookware/wellness/artisan/luxury briefs, the beige + brass/clay/oxblood + espresso family is banned as default; every AI-generated premium site uses it, making the brand invisible. Rotate families instead: cold luxury (silver/chrome/smoke), forest (deep green/bone/amber), black and tan, cobalt + cream, terracotta + slate, monochrome + one saturated pop. Never the same family twice in a row.
- Dark and light are both valid; neither is default. Write one sentence about who uses this, where, under what light; if it does not force the answer, add detail until it does.

## Hero discipline

The hero is one moment, not a feature list. Hard rules; failing any is shipping broken work:

- Hero fits the initial viewport: headline ≤ 2 lines desktop, subtext ≤ 20 words and ≤ 4 lines, CTA visible without scrolling. If copy does not fit, the value prop is unclear, not the rule too tight.
- Plan font scale and asset together: headlines over 6 words do not start at `text-7xl`. A 4-line hero headline is a font-size error, never a copy-length error.
- Top padding cap ≈ `pt-24` desktop; content floating halfway down the viewport reads as a bug, not as space.
- Max 4 text elements: (eyebrow OR brand strip OR neither) + headline + subtext + CTAs (1 primary + ≤ 1 secondary). Banned inside the hero: taglines under CTAs, trust micro-strips, pricing teasers, feature bullets, avatar rows. All move to sections below.
- The hero needs a real visual. Text plus a gradient blob is a placeholder, not a hero.
- "Trusted by" logo walls live in their own section under the hero, never inside it.
- Navigation: one line at desktop, height ≤ 80px. A two-line nav is broken design.

## Layout diversification

- Anti-center bias: prefer split-screen, left-content/right-asset, asymmetric whitespace, or scroll-pinned structures. Centered hero is fine for manifesto/launch briefs where the message is the design.
- **Section-layout-repetition ban.** Each layout family (3-column cards, full-width quote, image+text split) appears at most once per page; a page with 8 sections uses at least 4 distinct families.
- **Zigzag cap.** Max 2 consecutive image+text alternating splits; the third is a fail. Break with full-width, bento, marquee, or vertical stack.
- **Split-header ban.** "Giant left headline + small floating right paragraph" as a section header is banned as default; stack headline above body (max-width 65ch) unless the right column carries a real visual.
- **Bento rules.** Exactly as many cells as content (no blank filler tiles); rhythm through varied cell sizes; at least 2-3 cells with real visual variation (image, brand gradient, pattern), never all white-on-white text cards.
- **Long lists get a different component, not a longer list.** Over 5 items: grouped 2-column split, card grid, tabs/accordion, scroll-snap pills, or marquee. A 10-row spec table with a hairline under every row is the laziest layout; group into clusters or feature 3-4 hero specs with the rest collapsed.
- Cards only when elevation communicates hierarchy; otherwise group with borders, dividers, or space. Tint shadows to the background hue; no pure-black drop shadows.

## Eyebrow rationing

An eyebrow is the small uppercase wide-tracking label above a section headline. It is the single most violated rule in production tests: AI output puts one above every section, producing identical templated rhythm.

- Max 1 eyebrow per 3 sections, hero included. Mechanical check: count `uppercase tracking` labels; count must be ≤ ceil(sections / 3).
- Instead of an eyebrow: nothing. The headline is enough; position on the page already categorizes the section.

## Backgrounds and depth

Never default to flat solid backgrounds; create atmosphere matched to the aesthetic: layered radial-gradient meshes, subtle SVG noise, geometric patterns, layered transparencies with `backdrop-filter`, colored (not gray) shadows, grain overlays. Industrial gets hard shadows and concrete; luxury gets soft glow and fine grain; brutalist gets raw black or white and nothing. Apply grain/noise filters only to fixed `pointer-events-none` overlays, never scrolling containers (continuous GPU repaints destroy mobile FPS).

## Motion

- One orchestrated moment (staggered page-load reveal) creates more delight than scattered micro-interactions on everything. High-impact triggers: page load, scroll-into-view, meaningful hover.
- Motion claimed is motion shown: if the direction promises movement, the page must actually animate (hero entrance, scroll reveals, CTA hover physics). If you cannot ship working motion in scope, ship a clean static page instead; never half-built motion with cut-off triggers.
- Marquees: max one per page. Two or more reads as filler.
- Scroll-pinned patterns (sticky-stack, horizontal pan): pin with `start: "top top"` (not "top center", which fires mid-scroll and shows half a slide), `pin: true`, scrub the inner track, `useEffect` cleanup, reduced-motion bypass. Prefer `whileInView` for simple enter-on-scroll; save GSAP for real pin/scrub work. Never mix GSAP and Motion in the same component tree.
- Pattern vocabulary worth knowing: asymmetric split hero, editorial manifesto hero, kinetic type, sticky-stack sections, bento grid, magnetic buttons, text mask reveal, mesh gradient backgrounds. Reach for them when the read calls for them, not because they exist.

## Images and visual assets

Landing pages and portfolios are visual products; text-only pages with fake-screenshot divs are slop. Priority order:

1. **Image generation tool first.** If any image-gen tool is available, use it for hero photography, product shots, and textures at the right aspect ratio per section.
2. **Real photo URLs second.** `https://picsum.photos/seed/<descriptive-seed>/<w>/<h>` with seeds describing the section, or brief-provided assets.
3. **Labeled placeholder slots last.** Leave `<!-- TODO: hero product photo, 1600x1200 -->` and tell the user which images are needed. Never fill the gap with hand-rolled SVG illustrations or div-built fake product UI.

Even minimalist sites need 2-3 real images; pure text is incomplete work, not minimalism. Logo walls use real SVG logos (Simple Icons CDN, devicon) or generated monogram marks for invented brands, never styled text wordmarks, and carry no industry labels under the logos.

## Content density

First impressions, not full reads. Default section shape: headline ≤ 8 words + sub ≤ 25 words + one visual or one CTA. No 20-row tables or giant pricing matrices on marketing pages; top 3-5 highlights plus a link. Quotes: ≤ 3 lines of body, attribution as name + role (+ company), real typographic quotes or none. One copy register per page; do not mix technical mono, editorial prose, and marketing punch unless the brand voice demands it.

## Landing-page tells (banned patterns)

All banned as defaults; each is a documented signature of AI-generated pages:

- Version labels in the hero (`V0.6`, `BETA`, `EARLY ACCESS`) unless the brief is a launch
- Section-number eyebrows (`001 · Capabilities`, `00 / INDEX`) and pagination labels on tiles (`01 / 4`)
- Middle-dot separator chains (`foo · bar · baz · qux`); max one `·` per metadata line
- Generic step labels ("Step 1 / Step 2 / Phase 01"); the verb is the label ("Install", "Configure", "Ship")
- Poetic section labels ("From the field", "On our desks", "Field notes"); use plain labels or none
- "Quietly trusted by" social-proof headers; say "Trusted by" or let the logos speak
- Micro-meta sentences under eyebrows explaining the section
- Decoration text strips at hero bottom (`DESIGN · BUILD · SHIP`)
- Floating top-right explainer paragraphs in section headers
- Pills or labels overlaid on photos; captions only below images, and only functional ones
- Photo-credit captions as decoration (`Field study no. 12 · Ines Caetano`)
- Version footers on marketing pages (`v1.4.2`, `Build 0048`, `last sync 4s ago`)
- Locale/time/weather strips (`LIS 14:23 · 18°C`) unless the brief is genuinely place-bound
- Scroll cues (`↓ scroll to explore`); the user knows what scrolling is
- `<br>`-split italicized headline fragments and 90-degree rotated text as default moves
- Hairline crosshair grid lines as pure decoration
- Progress bars with filled background tracks as comparison visuals on marketing pages
- Live-stock counters ("Reservation 412 of 800") without real data

## Aesthetic direction starting points

Jumping-off points, not constraints; push the chosen one further than feels comfortable:

| Direction | Typography | Colors | Texture | Motion |
|---|---|---|---|---|
| Brutalist | Monospace, raw, oversized | Black/white + one harsh color | None or extreme | Abrupt, no easing |
| Editorial | Serif display (when justified), varied weights | Cream, ink black, 1 accent | Fine grain | Measured reveals |
| Luxury | Thin display, tight tracking | Deep neutral + metal accent | Soft glow, fine grain | Slow, deliberate |
| Retro-futuristic | Condensed sans, geometric | Dark + neon accent | Grid lines, scanlines | Glitch, flicker |
| Organic | Variable type, ink-like | Earth tones, muted | Paper, noise | Gentle, breathing |
| Technical | Mono + clean sans | Near-white or near-black | Subtle grid | Precise, mechanical |
| Playful | Rounded display, expressive | Saturated, high-contrast | Illustration | Springy, bouncy |
