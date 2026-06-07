# Accessibility (WCAG 2.1 AA)

Verification reference for design-ui. The component-build mechanics (keyboard reach, focus-visible rings, the eight-state matrix, roving tabindex, 44px touch targets, native `dialog`/`inert`) live in `interaction.md`; this file covers what to verify for WCAG AA conformance: screen readers, contrast, forms, ARIA, and testing.

## Screen readers

- Every image has `alt` text, or `alt=""` when it is purely decorative
- Every form input has an associated label (`<label for>` or `aria-label`)
- Buttons and links have descriptive text, never "click here"
- Icon-only controls carry an `aria-label`
- One `<h1>` per page; headings do not skip levels
- Dynamic content changes are announced through an `aria-live` region
- Data tables use `<th>` with `scope`

## Visual and contrast

- Text contrast at least 4.5:1 (normal) or 3:1 (large text: 18px, or 14px bold, and up)
- UI components and meaningful graphics contrast at least 3:1 against adjacent color
- Color is never the only carrier of meaning; pair it with an icon, text, or pattern
- Layout survives text zoom to 200% without clipping or overlap
- Nothing flashes more than three times per second

## Forms

- Visible label on every field; a placeholder is not a label
- Required state shown by more than color (text, or an asterisk with a legend)
- Error messages are specific and programmatically tied to their field
- Error state shown by more than color (icon, text, border)
- Submit-time errors are summarized, and the summary is focusable
- Known fields set `autocomplete` (`type="email" autocomplete="email"`)

## ARIA patterns

Live regions, by urgency:

| Mechanism | Announced | Use for |
|---|---|---|
| `aria-live="polite"` or `role="status"` | at the next pause | saved confirmations, status updates |
| `aria-live="assertive"` or `role="alert"` | immediately | errors, time-sensitive alerts |

Common roles:

```html
<nav aria-label="Main">...</nav>              <!-- name each of multiple navs -->
<div role="status" aria-live="polite">Saved</div>
<div role="alert">Title is required</div>
<dialog aria-modal="true" aria-labelledby="t"><h2 id="t">Confirm</h2>...</dialog>
<div aria-busy="true" aria-label="Loading">...</div>
```

Reach for ARIA only where a native element cannot express the role; native semantics are correct by default and ARIA is easy to get wrong.

## Testing

- Automated: `npx axe-core` or `npx pa11y <url>`, plus the Lighthouse accessibility audit in Chrome DevTools
- Tree: DevTools Elements, Accessibility pane, to read the computed name and role
- Screen reader: VoiceOver (Cmd+F5) on macOS, NVDA on Windows, Orca on Linux

Automated tools catch roughly half of issues; tab through every interactive flow and listen once before calling it done.

## Anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| `div` or `span` as a button | not focusable, no keyboard support | use `<button>` |
| missing `alt` | image is invisible to assistive tech | add descriptive `alt`, or `alt=""` if decorative |
| color-only state | invisible to color-blind users | add an icon, text, or pattern |
| autoplaying media | disorienting and hard to stop | controls on, no autoplay |
| custom dropdown with no ARIA | unusable by keyboard or screen reader | native `<select>`, or a proper listbox pattern |
| removed focus outline | the user loses their place | style the outline, never remove it |
| empty link or button | announced with no name | add text or `aria-label` |
| `tabindex` greater than 0 | breaks natural tab order | use only `0` or `-1` |
