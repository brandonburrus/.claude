---
name: demo
description: This skill should be used when the user wants to see or show off a working
  demo of recent work, such as a feature just built, a codebase just landed in, or work
  completed this session. It applies when the user says "demo this", "/demo", "show me it
  working", "set up a demo", "let me see it", or "re-setup the demo", optionally naming a
  specific target. It stages realistic local demo data and proactively opens the best demo
  for the project type (web, API, CLI, library, service). It should not be used to confirm
  a change is correct (use verify) or to just launch the app without staging a presentable
  demo (use run).
---

## Purpose

When invoked, stage and open a working, presentable demo of recent work, then hand the user something to actually experience. The default target is whatever was built this session; an optional argument points the demo at something specific. This is presentation-first, not a correctness check: seed realistic data so the work shows at its best, get it into a compelling state, and proactively open it. The deliverable is an open, usable demo plus a one-line note on what to look at, never a half-built setup the user has to finish.

## Workflow

Checklist:
- [ ] 1. Pick the demo target (session work by default, or the named target)
- [ ] 2. Find the most compelling thing to show
- [ ] 3. Stage realistic demo data, always local
- [ ] 4. Open the best demo for the project type
- [ ] 5. Hand it off with a one-line "look here"

### 1. Pick the demo target

- Default to this session's work. Reconstruct it from `git status` / `git diff` against where the session started, plus what was built in the conversation.
- If the user named a target, demo that specific thing instead.
- If nothing was built this session (a freshly-landed codebase), demo the project's headline happy-path feature, the thing it exists to do.
- If the session touched several unrelated changes, confirm which one to demo rather than guessing or demoing all of them. A demo shows one thing well.

### 2. Find the most compelling thing to show

- Identify the user-facing entry point and the single most compelling moment, the "money shot" that makes the work land.
- Demo the outcome, not the plumbing. Show the feature doing its job, not the migration that created its table.

### 3. Stage realistic demo data, always local

- Always run the demo against the local environment.
- Seed believable, illustrative data so the feature shows at its best. Empty states and lorem ipsum undersell the work: use real-looking names, varied records, and the specific states that exercise the feature (an overdue invoice, a thread with replies, a near-full cart).
- Make it idempotent. Re-invoking `/demo` rebuilds a clean demo state rather than piling on duplicates; this is the "re-setup."
- If data cannot be scaffolded cleanly on local, if seeding would reset or overwrite existing local data, or if the only realistic data lives off-local, stop and review the demo strategy with the user before proceeding. Never silently wipe data or fabricate it in a way that misrepresents what the feature does.

### 4. Open the best demo for the project type

Pick the most illustrative form, and reuse the project's normal run or launch command for the mechanics.

| Project type | How to demo |
|---|---|
| Web app / UI | Start the dev server, open the browser to the relevant route, leave it running |
| HTTP API | Fire live example requests and show the responses, or open the API docs / a REST client primed with them |
| CLI | Run the command with realistic example args; show the input and the output |
| Library / SDK | Write a short demo script exercising the headline API, run it, show the output |
| Background worker / pipeline | Trigger it with sample input and surface the resulting output, logs, or side effects |
| Data / notebook | Run the analysis and surface the chart or table it produces |

### 5. Hand it off

- Actually open or launch it; do not set it up and stop. "Proactively open" is the point of the skill.
- Tell the user exactly where to look: the URL, the command they can rerun, the screen, or the click sequence for the money shot.
- If you started a server or opened a browser, give the address and leave it running so the user can keep poking at it.

## Gotchas

- **demo is not verify and not run.** verify confirms a change is correct; run just launches the app. demo stages a presentable experience with realistic data and opens it to be seen. If the user wants to know "does it work," that is verify, not this.
- **The data is the demo.** A correct feature shown over empty or garbage data reads as broken. The believable seed data is what makes the work look like the work, so invest there before launching anything.
- **Do not leave it half-built.** Setting up the demo and stopping is the most common failure. The skill is done when something is open and the user has been told what to look at.
- **Confirm an ambiguous target.** When the session built several unrelated things, demoing the wrong one (or all of them) wastes the moment. Ask which one.

## Examples

Just finished adding a saved-searches feature to a Next.js + Postgres app.

1. Target: `git diff` shows a new `SavedSearch` model, a `/saved-searches` route, and its API handlers. That is the session's work, so that is the demo.
2. Money shot: the alert toggle on a saved search, the feature's reason to exist.
3. Data: seed 6 believable saved searches ("Remote React roles, under $120k", "2BR rentals near Dolores Park") across 2 demo users, idempotently (clear prior demo rows first), all on the local Postgres.
4. Open: `npm run dev`, then open the browser to `/saved-searches`.
5. Hand off: "Running at http://localhost:3000/saved-searches, logged in as demo@acme.test. Six saved searches are listed; click the bell on any row to toggle its alert, which is the new bit."
