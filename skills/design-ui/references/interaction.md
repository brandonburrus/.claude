# Interaction States and Modern Overlay APIs

Read this when building anything interactive: forms, buttons, modals, dropdowns, tooltips, tabs, or keyboard-driven components. Applies to both registers.

## Contents

- The eight interactive states
- Focus rings
- Forms
- Modals and focus containment
- Dropdowns, tooltips, and overlay positioning
- Destructive actions
- Keyboard navigation patterns
- Touch and gesture rules

## The eight interactive states

Every interactive element ships with all applicable states designed, not just default and hover:

| State | When | Treatment |
|---|---|---|
| Default | At rest | Base styling |
| Hover | Pointer over (not touch) | Subtle lift or color shift |
| Focus | Keyboard or programmatic focus | Visible ring (rules below) |
| Active | Being pressed | Pressed in, darker, `scale-[0.98]` |
| Disabled | Not interactive | Reduced opacity, no pointer events |
| Loading | Processing | Skeleton or inline spinner |
| Error | Invalid | Border color, icon, message |
| Success | Completed | Confirmation state |

The common miss is designing hover without focus or vice versa; they are different states and keyboard users never see hover.

## Focus rings

Never `outline: none` without a replacement. Use `:focus-visible` so the ring appears for keyboard users without flashing on every mouse click:

```css
button:focus { outline: none; }
button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

Ring design: 2-3px thick, offset outside the element, at least 3:1 contrast against adjacent colors, identical treatment across every interactive element on the page.

## Forms

- Labels are visible `<label>` elements above the field; a placeholder is not a label, it disappears on input
- Validate on blur, not on every keystroke (exception: live password-strength feedback). Keystroke validation yells at users mid-typing
- Error text sits below the field, connected with `aria-describedby`, so screen readers announce it with the input
- Helper text exists in markup from the start, not injected on error
- Error messages name the fix ("Email must include @"), never just "Invalid input"

## Modals and focus containment

Use the native `<dialog>` element with `showModal()`; it provides focus trapping, Escape-to-close, and a backdrop for free. When content behind a custom modal must be inactive, mark it `inert` instead of writing a JavaScript focus trap:

```html
<main inert>...</main>
<dialog open>...</dialog>
```

## Dropdowns, tooltips, and overlay positioning

A dropdown rendered `position: absolute` inside any ancestor with `overflow: hidden` or `auto` gets clipped; this is the most common overlay bug in generated code. In order of preference:

1. **Popover API** for tooltips, menus, and non-modal overlays: `popovertarget` + `popover`. The element renders in the top layer (above everything regardless of z-index or overflow) with light-dismiss and accessibility built in. No portal, no z-index wars.
2. **CSS anchor positioning** (`anchor-name`, `position-anchor`, `position-area`, `@position-try` for viewport-edge flipping) tethers the overlay without JavaScript. Chromium-only at present; pair with a fallback.
3. **Portal to the document root** (`createPortal` in React, `<Teleport to="body">` in Vue) with `position: fixed` coordinates from `getBoundingClientRect()`, recalculated on scroll and resize.

Never solve clipping by escalating z-index; the top layer and portals exist for this.

## Destructive actions

Prefer undo over confirmation dialogs: remove from the UI immediately, show an undo toast, commit when the toast expires. Users click through confirmations mindlessly, so a confirm dialog protects nothing routine. Reserve confirmation for genuinely irreversible or high-cost actions (account deletion, batch operations) and make the confirm button name the action ("Delete 14 files", not "OK").

## Keyboard navigation patterns

- **Roving tabindex** for composite widgets (tabs, menus, radio groups): one item has `tabindex="0"`, the rest `-1`; arrow keys move the active item, Tab leaves the whole group. Tab-stopping every item makes the page unwalkable
- **Skip link** as the first focusable element on full pages: `<a href="#main-content">Skip to main content</a>`, visually hidden until focused
- Custom controls without keyboard support and ARIA are not done; if a native element exists (`<select>`, `<details>`, `<dialog>`), prefer it over rebuilding

## Touch and gesture rules

- Touch targets minimum 44x44px; smaller visual elements get padding to reach it
- Gestures (swipe-to-delete, drag) are invisible; always provide a visible alternative path to the same action, and hint the gesture (partially revealed action, first-use coach mark)
- Hover-only affordances are unreachable on touch; anything revealed on hover needs a tap-accessible equivalent
