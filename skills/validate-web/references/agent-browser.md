## agent-browser reference

Command reference and validation recipes for the `agent-browser` CLI, digested from the official docs (agent-browser.dev/commands) so the syntax is exact. agent-browser is a browser-automation CLI built for agents: its `snapshot` returns a compact accessibility tree with element refs (`@e1`) instead of raw DOM, which keeps output token-efficient.

### Contents

- [Setup](#setup)
- [Snapshots and element refs](#snapshots-and-element-refs)
- [Semantic locators](#semantic-locators)
- [Command reference](#command-reference)
- [Recipes by use case](#recipes-by-use-case)

### Setup

| Step | Command |
|---|---|
| Install (global) | `npm install -g agent-browser` or `brew install agent-browser` |
| Install (no global) | `npx agent-browser <command>` |
| Download Chrome (first run) | `agent-browser install` |
| Diagnose the install | `agent-browser doctor` (flags: `--quick`, `--fix`, `--json`) |

Global flags worth knowing: `--session <name>` (isolated session), `--headed` (show the window), `--json` (structured output), `--profile <path>` (reuse a logged-in Chrome profile), `--ignore-https-errors`.

### Snapshots and element refs

`agent-browser snapshot` prints an accessibility tree where each interactable element has a stable ref like `@e1`, `@e2`. Use refs as selectors in any action (`click @e3`, `fill @e4 "..."`). Add `-i` to include iframe content (refs then carry frame context, so you can act across frames without switching). Refs are valid for the session but reflect the snapshot you took: after a navigation or re-render, snapshot again before reusing refs.

Prefer `snapshot` over `get html`; it is the token-efficient view the tool is designed around.

### Semantic locators

Use these with an action verb (`click`, `fill`, `type`, `hover`, `focus`, `check`, `uncheck`, `text`) to target by meaning rather than CSS. They survive refactors and validate the accessible name as a side effect.

| Locator | Form | Example |
|---|---|---|
| ARIA role | `find role <role> <action> [value]` (flag `--name`) | `find role button --name "Save" click` |
| Visible text | `find text <text> <action>` (flag `--exact`) | `find text "Sign out" click` |
| Label | `find label <label> <action> [value]` | `find label "Email" fill "a@b.com"` |
| Placeholder | `find placeholder <ph> <action> [value]` | `find placeholder "Search" fill "shoes"` |
| Test id | `find testid <id> <action> [value]` | `find testid submit click` |
| Position | `find first\|last\|nth <n> <sel> <action>` | `find nth 2 "li" click` |

### Command reference

**Navigation:** `open [url]` (aliases `goto`, `navigate`), `back`, `forward`, `reload`, `pushstate <url>` (SPA history nav).

**Interaction:** `click <sel>` (`--new-tab`), `dblclick`, `fill <sel> <text>` (clear then type), `type <sel> <text>`, `press <key>` (e.g. `Enter`, `Control+a`), `hover`, `focus`, `select <sel> <val>`, `check`/`uncheck <sel>`, `scroll <dir> [px]`, `scrollintoview <sel>`, `drag <src> <dst>`, `upload <sel> <files>`.

**Read state:** `get text <sel>`, `get value <sel>`, `get attr <sel> <attr>`, `get html <sel>`, `get count <sel>`, `get title`, `get url`, `get box <sel>`, `get styles <sel>`, `eval <js>`.

**Assert and wait:** `is visible <sel>`, `is enabled <sel>`, `is checked <sel>`; `wait <sel>` (appears), `wait <sel> --state hidden` (disappears), `wait <ms>`, `wait --text "..."`, `wait --url "**/pattern"`, `wait --load networkidle`, `wait --fn "<js condition>"`, `wait --download [path]`.

**Evidence:** `screenshot [path]` (`--full`, `--annotate`, `--screenshot-format jpeg`), `pdf <path>`.

**Console and errors:** `console` (`--json`, `--clear`), `errors` (`--clear`), `highlight <sel>`, `inspect`.

**Network:** `network requests` (filters `--filter <pat>`, `--type xhr,fetch`, `--method POST`, `--status 2xx|5xx`), `network request <id>` (full detail), `network route <url>` (`--abort` to block, `--body <json>` to mock), `network unroute [url]`, `network har start` / `har stop [out.har]`.

**Storage and auth:** `cookies` / `cookies set <n> <v>` / `cookies clear`, `storage local [key]` / `storage local set <k> <v>` / `storage local clear`, `storage session ...`; `auth save <name> [--url --username --password]` / `auth login <name>`; `state save <path>` / `state load <path>` (persist and restore session storage state).

**Tabs and frames:** `tab` (list, IDs `t1`), `tab new [url] [--label <name>]`, `tab <tN|label>` (switch), `tab close`; `frame <sel|@eN|main>`.

**Settings and emulation:** `set viewport <w> <h> [scale]`, `set device <name>`, `set media dark|light`, `set offline [on|off]`, `set geo <lat> <lng>`, `set headers <json>`.

**React and vitals:** `open --enable react-devtools <url>`, `react tree`, `react renders start|stop [--json]`, `vitals [url] [--json]`.

**Batch:** `batch "cmd1" "cmd2"` (`--bail`, `--json`), or chain with shell `&&`.

**Close:** `close` (aliases `quit`, `exit`), `close --all`.

### Recipes by use case

**Login / authenticated flow.** Log in once, then reuse the session so later validations skip the login.

```bash
agent-browser open http://localhost:3000/login
agent-browser find label "Email" fill "user@example.com"
agent-browser find label "Password" fill "correct-horse"
agent-browser find role button --name "Sign in" click
agent-browser wait --url "**/dashboard"
agent-browser state save ./.auth/session.json        # reuse with: open --state ./.auth/session.json
```

**Form submission with validation errors.** Validate both the failure and success paths.

```bash
agent-browser find role button --name "Submit" click   # submit empty
agent-browser wait --text "Required"                    # expected validation error
agent-browser is visible "[data-error]"                 # -> true
agent-browser find label "Name" fill "Sam"
agent-browser find role button --name "Submit" click
agent-browser wait --text "Saved"                       # success path
```

**SPA navigation (no full reload).** Click a client-side link and confirm the view changed without a reload.

```bash
agent-browser find role link --name "Settings" click
agent-browser wait --url "**/settings"
agent-browser get text "h1"                             # -> "Settings"
agent-browser snapshot                                  # re-snapshot: refs changed after the route swap
```

**List / table assertion.** Confirm a row count or that a deleted item is gone.

```bash
agent-browser get count "table tbody tr"                # -> 3
agent-browser find text "Delete" click
agent-browser wait "table tbody tr:nth-child(3)" --state hidden
agent-browser get count "table tbody tr"                # -> 2
```

**Runtime-error and failed-request check.** The step that turns a render into a real pass.

```bash
agent-browser console                                   # assert: no exceptions
agent-browser errors                                    # assert: empty
agent-browser network requests --status 5xx             # assert: no failed calls
```

**Backend-failure handling.** Mock a 500 to validate the UI's error state without breaking the backend.

```bash
agent-browser network route "**/api/orders" --abort
agent-browser reload
agent-browser wait --text "Something went wrong"        # the UI's error state renders
agent-browser network unroute "**/api/orders"
```

**Responsive / viewport check.** Validate a layout at a target width.

```bash
agent-browser set viewport 375 812                      # iPhone-ish
agent-browser is visible "[data-mobile-menu]"           # -> true
agent-browser screenshot ./evidence/mobile.png --full
```

**File upload.**

```bash
agent-browser find label "Avatar" upload ./fixtures/face.png
agent-browser wait --text "Uploaded"
```
