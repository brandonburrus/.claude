# Product Register: Dashboards, Admin, SaaS Apps, Dev Tools, Internal Tools

Design SERVES the product here. The bar is earned familiarity: a fluent user of Linear, Raycast, Stripe, GitHub, Figma, or Notion should trust this interface on sight. Restraint is the craft; the expressive playbook (atmospheric backgrounds, editorial typography, asymmetric layouts) is the anti-pattern in this register.

Before writing any component, list the "AI default" moves you would normally make for this surface, then do none of them.

## Contents

- Component standards
- Structure and spacing
- Hard No list
- Banned recurring patterns
- The Rule

## Component standards

- **Sidebars**: 240-260px fixed width, solid background, simple `border-right`. No floating shells, no rounded outer corners.
- **Headers**: plain `h1`/`h2` with proper hierarchy. No eyebrow labels, no uppercase decorative labels, no gradient text.
- **Sections**: standard 20-30px padding. No hero blocks inside dashboards, no decorative copy.
- **Navigation**: simple links, subtle hover. No transform animations, no badges unless functional.
- **Buttons**: solid fills or simple borders, 8-10px radius max. No pills, no gradients.
- **Cards**: simple containers, 8-12px radius max, subtle borders, shadow max `0 2px 8px rgba(0,0,0,0.1)`. No floating or glow effects.
- **Forms**: labels above fields, helper text present in markup, error text below input, `gap-2` spacing. No floating labels, no placeholder-as-label, ever.
- **Inputs**: solid borders, simple focus ring. No animated underlines or morphing shapes.
- **Modals**: centered overlay, simple backdrop, straightforward close. Render dropdowns and popovers with the native `<dialog>`/popover API, `position: fixed`, or a portal; `position: absolute` inside an `overflow: hidden` container clips them.
- **Dropdowns**: simple list, subtle shadow, clear selected state.
- **Tables**: clean rows, simple borders, subtle hover, left-aligned text.
- **Tabs**: underline or border indicator. No pill backgrounds, no sliding animations.
- **Badges**: small text, simple border or background, 6-8px radius, only when functional.
- **Icons**: one family, consistent 16-20px, monochrome or subtle color. No decorative icon backgrounds.

## Structure and spacing

- **Typography**: clean sans (system fonts acceptable here), clear hierarchy, body 14-16px. No decorative serif/sans mixing.
- **Spacing**: consistent 4/8/12/16/24/32px scale. No random gaps, no overpadding.
- **Borders**: `1px solid`, subtle colors. No thick or gradient borders.
- **Shadows**: max `0 2px 8px rgba(0,0,0,0.1)`. No dramatic or colored shadows.
- **Transitions**: 100-200ms ease on `opacity`/`color` only. No bounce, no transform hover effects.
- **Layouts**: standard grid/flex, predictable structure. No creative asymmetry.
- **Containers**: max-width 1200-1400px, centered, standard padding.
- **Panels**: background differentiation plus subtle borders. No floating detached panels, no glass.
- **Toolbars**: horizontal, 48-56px height, clear actions, no decoration.
- **States**: loading skeletons that match final layout shape, composed empty states, inline errors. The full cycle, not just success.

## Hard No list

- Oversized rounded corners or pill overload
- Floating glassmorphism shells as the default visual language
- Soft corporate gradients used to fake taste
- Generic dark SaaS blue-black composition; colors skewing blue by default (prefer dark, muted, calm tones)
- Decorative sidebar blobs or visual noise
- Serif headline + system sans as a shortcut to "premium"
- Sticky left rail unless the information architecture requires it
- Metric-card KPI grid as the first instinct for a dashboard
- Fake charts or visualizations that exist only to fill space
- Random glows, blur haze, frosted panels, conic-gradient donuts as decoration
- Hero sections inside app UI without a real product reason
- Alignment that creates dead space to look expensive; overpadded layouts
- Mobile collapse that thoughtlessly stacks everything into one long column
- Eyebrow labels (`MARCH SNAPSHOT`, uppercase decorative spans), `<small>` as heading
- Decorative copy as page headers ("Operational clarity without the clutter")
- Section notes explaining what the UI does
- Rounded `<span>` chips used decoratively

## Banned recurring patterns

Documented AI product-UI mistakes; recognize and reject:

| Pattern | Why banned |
|---|---|
| 20-32px border radii applied everywhere | Visually homogeneous; signals AI default |
| Floating sidebar with rounded outer shell | Decorative, not functional |
| Canvas chart in a glass card without product reason | Filler, not data |
| Donut chart with hand-wavy percentages | Vague decoration |
| Glows used instead of hierarchy | Glows are not structure |
| Mixed alignment (some left, some floating center-ish) | Inconsistent grid logic |
| Muted gray-blue text throughout | Weakens contrast and clarity |
| "Premium dark mode" = blue-black gradient + cyan accents | No atmosphere, no depth |
| Eyebrow labels with letter-spacing everywhere | Decorative noise |
| Hero strip with decorative copy inside a dashboard | Wrong context |
| `translateX` animations on nav hover | Gratuitous motion |
| Dramatic box shadows (`0 24px 60px`) | Over-designed depth |
| Status dots via `::before` on everything | Only real semantic state earns a dot |
| Pipeline/progress bars with gradient fills | Decoration over information |
| KPI card grid as the default dashboard opener | Cliched and uninformative |
| `.tag` badge on every table status cell | Tag overuse |
| Sidebar workspace blocks with CTAs | Wrong context for CTA |
| Brand marks with gradient backgrounds | Unnecessary decoration |
| Nav badges showing counts or "Live" labels | Functional clutter |
| Multiple nested panel types (panel, panel-2, rail-panel) | Structural confusion |
| Footer meta lines about the UI itself | Self-referential noise |
| Colored `trend-up`/`trend-flat` text classes | Cheap, templated |

## The Rule

If a UI choice feels like a default AI move, ban it and pick the harder, cleaner option. Colors stay calm and do not fight. When a dashboard looks like every AI-generated dashboard, it has failed even if every component is individually fine.
