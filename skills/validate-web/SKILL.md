---
name: validate-web
description: >-
  Use this skill to validate a web change by driving a real browser with the
  agent-browser CLI, confirming user-visible behavior and capturing evidence
  (screenshots, console, network). Use after implementing a frontend change, or
  when the user says "validate this in the browser", "check the UI works",
  "smoke-test the page", "does the form actually submit", "click through the
  flow", or "verify it end to end in a browser". The deliverable is a
  pass/fail-with-evidence report, not a test file. Do not use for authoring an
  automated e2e suite (use Playwright via follow-tdd), for API-only validation
  (use validate-api), or for visual design work (use design-ui).
---

## Purpose

Validate a web change by driving a real browser with the `agent-browser` CLI, confirming the user-visible behavior actually holds and capturing the evidence that it did. This is semi-manual validation: you drive the browser step by step and read real output, which catches what unit tests miss (it renders, the route is reachable, the click does the thing, nothing throws in the console). The deliverable is a pass/fail report with evidence per behavior. This complements automated testing; it does not replace a Playwright e2e suite, and a validation worth keeping graduates into one. It runs after the change's automated tests are green, as the live-confirmation step in the red, green, refactor, validate sequence, never a substitute for the suite.

## Iron rules

- **A running target and a stated expected outcome are both required.** No dev-server URL means stop and get one. No expected observable means you are clicking around, not validating; define what success looks like first.
- **This is validation, not test authoring.** The output is an evidence-backed verdict, not a committed test file. When a flow is worth permanent regression coverage, say so and graduate it to Playwright; do not leave the app's correctness resting on manual reruns.
- **agent-browser is an external CLI.** If it is not installed, instruct the user to install it (`npm install -g agent-browser`, then `agent-browser install` to download Chrome on first use) or run via `npx agent-browser`. Do not silently install global packages.

The full command reference and per-use-case recipes are in [references/agent-browser.md](references/agent-browser.md); read it for the exact syntax of any command below.

## Workflow

```text
Validate (web):
- [ ] 1. State the expected outcomes
- [ ] 2. Confirm the tool and the running app
- [ ] 3. Open and snapshot
- [ ] 4. Drive each behavior to its expected state
- [ ] 5. Capture evidence and check for runtime errors
- [ ] 6. Report pass/fail per behavior
```

### 1. State the expected outcomes

List the user-visible behaviors the change must produce, each with a checkable observable: "submitting the empty form shows a 'Required' error", "after login the header greets the user by name", "the deleted row disappears without a reload". Pull them from the diff, the spec, or the acceptance criteria. A behavior with no observable cannot be validated; resolve that before opening the browser.

### 2. Confirm the tool and the running app

Check the tool with `agent-browser doctor`. Get the running app URL; if nothing is serving, start it with the project's run command or ask the user to. Validation against a stale build proves nothing.

### 3. Open and snapshot

`agent-browser open <url>`, then `agent-browser snapshot`. The snapshot is a compact accessibility tree where each element carries a ref like `@e1`. Target elements by ref or by semantic locator (`find role`, `find text`, `find label`), not brittle CSS. Prefer the snapshot over dumping HTML; it is built to be token-efficient.

### 4. Drive each behavior to its expected state

Act, then wait for the result, then assert it:

- **Act:** `click @e3`, `fill @e4 "text"`, `find role button --name "Save" click`, `press Enter`, `select`, `check`.
- **Wait on the condition, never sleep:** `wait --text "Saved"`, `wait --url "**/dashboard"`, `wait <sel> --state hidden`, `wait --load networkidle`. A fixed `wait <ms>` is flaky and slow; wait on the thing that actually marks the outcome.
- **Assert:** `is visible <sel>`, `get text <sel>`, `is enabled`, `is checked`, `get count <sel>`.

Re-snapshot after any navigation or re-render; a ref from an earlier snapshot points at an element that may no longer exist.

### 5. Capture evidence and check for runtime errors

- `agent-browser screenshot <path>` at each key state (`--full` for the whole page). The screenshot is the evidence the behavior rendered.
- `agent-browser console` and `agent-browser errors` after the flow, and `agent-browser network requests --status 5xx` for failed calls. A green-looking UI with a console exception or a failed background fetch is a failure, not a pass. Check these before declaring success.

### 6. Report

Per behavior: pass or fail, the observable that decided it (quoted text, screenshot path, "console clean"), and anything you could not validate with the reason. Close the browser with `agent-browser close`. If a flow is worth keeping, recommend graduating it into a Playwright e2e test.

## Gotchas

- **A screenshot is not a pass on its own.** The page can render and still throw in the console or 500 on a background fetch. Check console, errors, and network, not just pixels.
- **Refs go stale.** They come from the latest snapshot; after a navigation or re-render, re-snapshot before targeting by ref.
- **Wait on a condition, not a clock.** `wait <ms>` as the primary sync is the source of flaky validation. Wait on the text, URL, or element state that marks the outcome.
- **Semantic locators beat CSS.** `find role button --name "Submit"` survives a class rename and also validates the accessible name, which is itself part of the behavior.
- **This is not an e2e suite.** If you re-run the same fifteen steps every change, that flow has earned a Playwright test. Manual validation is for the change in front of you, not permanent regression coverage.

## Example

Validating a login flow against a dev server on `http://localhost:3000`:

```bash
agent-browser open http://localhost:3000/login
agent-browser snapshot                                  # -> email @e2, password @e3, submit @e5
agent-browser fill @e2 "user@example.com"
agent-browser fill @e3 "correct-horse"
agent-browser find role button --name "Sign in" click
agent-browser wait --url "**/dashboard"                 # outcome marker, not a sleep
agent-browser get text "header .greeting"               # -> "Welcome, Sam" (expected observable)
agent-browser console                                   # -> clean; no exceptions
agent-browser screenshot ./evidence/login-success.png
agent-browser close
```

Report: "Login flow passes. After valid credentials the URL reaches `/dashboard` and the header greets `Welcome, Sam`; console clean, no 5xx. Evidence: `login-success.png`. Worth graduating to a Playwright test."
