---
name: harden-security
description: >-
  Use this skill when building or modifying anything that touches untrusted
  input, authentication, authorization, sessions, secrets, file uploads,
  payments, PII, or external integrations, and when the user says "make this
  secure", "harden this", "add auth", "is this safe", or "handle user input".
  Apply it while writing the feature, not after. Do not use for auditing an
  existing diff (use the bundled /security-review), for API contract auth
  design (use design-api), or for triaging a reported vulnerability (use fix
  to reproduce it first).
---

## Purpose

Build security into code as it is written: treat every external input as hostile, every secret as radioactive, and every authorization check as mandatory. Security is a constraint on each line that touches user data, not a phase; retrofitting it costs roughly ten times what building it in does, because retrofits chase data that already flowed through unguarded paths.

## The three-tier boundary system

**Always, no exceptions:**

- Validate all external input at the system boundary (route handlers, form handlers, webhook receivers, env loading) with a schema; internal code then trusts types
- Parameterize every database query; user input never concatenates into SQL, shell commands, or HTML
- Encode output; use the framework's auto-escaping and never bypass it (`innerHTML`, `dangerouslySetInnerHTML`, `eval` with user data are findings, not techniques)
- Hash passwords with argon2, scrypt, or bcrypt (cost >= 12); never reversible, never plaintext
- Session cookies are `httpOnly`, `secure`, `sameSite`; auth tokens never live in localStorage
- HTTPS everywhere; security headers on (CSP, HSTS, X-Content-Type-Options, X-Frame-Options); helmet or the platform equivalent
- Secrets come from the environment or a secrets manager, never from code, and never go into logs

**Ask the user first** (these change the security posture, so they are the user's call):

- New or changed authentication flows
- Storing a new category of sensitive data (PII, payment, health)
- New external service integrations or webhook endpoints
- CORS changes, file upload handlers, rate limit changes, role or permission grants

**Never, even when asked casually:**

- Commit a secret, log a credential or token, echo internal errors or stack traces to clients
- Treat client-side validation as a security boundary (it is UX; the server validates regardless)
- Disable a security header, certificate check, or CSRF protection "temporarily" to make something work; that workaround is the vulnerability, surface the real problem instead

## The big four, by incident frequency

| Class | The rule | The one-liner |
|---|---|---|
| Injection | Parameterize, never concatenate | `db.query("... WHERE id = $1", [userId])`, never a template string with `userId` in it |
| Broken access control | Authorization is per-resource, not per-route | After auth, check ownership: `if (task.ownerId !== req.user.id) return 403`; a missing ownership check is an IDOR every scanner finds |
| XSS | Encode on output, sanitize only when HTML is the feature | `<div>{userInput}</div>` is safe in React; `DOMPurify.sanitize()` when rendering user HTML is genuinely required |
| Secrets exposure | Environment in, allowlist out | Strip sensitive fields when serializing (`const { passwordHash, resetToken, ...pub } = user`); response shapes are allowlists, not the whole record |

## Boundary validation pattern

One schema validation at the edge, typed trust inside:

```typescript
const result = CreateTaskSchema.safeParse(req.body);
if (!result.success) {
  return res.status(422).json({ error: { code: "VALIDATION_ERROR", details: result.error.flatten() } });
}
const task = await taskService.create(result.data); // typed, validated, trusted from here
```

Boundaries that need this treatment: request bodies and params, form input, webhook payloads, third-party API responses (vendors get compromised; their data is untrusted too), environment variables (validate at startup so misconfiguration fails loudly at boot, not silently at 2am), file uploads (allowlist MIME types AND check magic bytes when it matters; extension checks are decoration), and anything read from the DOM.

## Standing infrastructure

- **Rate limiting**: on by default for APIs; stricter on auth endpoints (login, reset, signup are credential-stuffing targets; think 10 attempts per 15 minutes, not 100)
- **Password reset**: tokens are single-use, expire within an hour, and the response never reveals whether the email exists
- **CORS**: explicit origin list from config; a wildcard origin with credentials is a misconfiguration, not a convenience
- **Dependency audit**: run `npm audit` (or the ecosystem equivalent) before release; triage by severity AND reachability: a critical in a runtime dependency on a reachable path is a blocker, a moderate in a dev-only tool is backlog. Deferred findings get a documented reason and a review date
- **Secrets hygiene**: `.env*` and key files in `.gitignore`, `.env.example` with placeholders committed; a secret that reaches a remote is rotated, not deleted (open-pull-request's staged-diff scan is the last line, not the plan)

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's an internal tool" | Internal tools have weaker review, broader permissions, and end up exposed; attackers route through the weakest link |
| "It's just a prototype" | Prototypes ship. The auth shortcut taken today is the production CVE later; prototype skill or not, the Never tier holds |
| "No one would target this" | Scanners target everything indiscriminately; obscurity is a delay, not a defense |
| "The framework handles it" | Frameworks hand you the safe tools; they cannot stop you from interpolating into a query or disabling escaping |
| "We'll add security later" | Later means migrating live data and existing users through a retrofit; the cost asymmetry is the whole argument |

## Verification

Before calling security-relevant work done:

- [ ] Every new endpoint checks authentication AND per-resource authorization
- [ ] All new external inputs validated at the boundary with a schema
- [ ] No secrets in code, config files headed to git, or log output
- [ ] Error responses carry codes and safe messages, not internals
- [ ] Dependency audit clean of reachable critical/high findings
- [ ] Sensitive fields absent from API responses (check the serializer, not the intent)

## Gotchas

- **Authentication is not authorization.** The most common real-world hole is a logged-in user reaching another user's resource because the route checked "is someone" but never "is the owner". Check both, per resource, every time.
- **The second boundary is the one that gets missed.** Teams validate the public API and trust the webhook, the queue consumer, the cron input, or the admin panel; an attacker finds the unguarded door, not the guarded one.
- **Timing and existence leaks live in error paths.** "Wrong password" vs "no such user", instant rejection vs slow hash check; uniform errors and constant-time comparison where it matters (auth, token checks).
- **File uploads are remote code execution with extra steps.** Stored where the web server executes, named by the client, or fetched server-side from a client URL (SSRF): treat the upload pipeline as the attack surface it historically is.
- **This skill builds; /security-review audits.** When the change is done, the bundled /security-review over the diff is the independent second pass, not a substitute for having built it right.
