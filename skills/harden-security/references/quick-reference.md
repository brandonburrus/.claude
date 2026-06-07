# Security quick reference

Concrete values that complement the harden-security methodology. The skill says which headers and checks to apply and why; this is the copy-paste form, plus the OWASP mapping. It is a lookup, not a substitute for the threat-modeling pass.

## Security header values

```
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Leave `X-XSS-Protection` off (`0`); modern browsers rely on CSP, and the legacy auditor introduced its own bugs.

## CORS

```typescript
cors({
  origin: ['https://yourdomain.com', 'https://app.yourdomain.com'], // explicit allowlist
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
})
// never in production: a wildcard origin with credentials, cors({ origin: '*' })
```

## JWT validation

A received token is untrusted until every check passes: signature against the expected key and algorithm (reject `alg: none`), expiration (`exp`), not-before (`nbf`) when present, issuer (`iss`), and audience (`aud`). Validate it, do not merely decode it.

## Data at rest

- PII encrypted at rest where regulation requires it, and database backups encrypted too
- Sensitive values never logged (passwords, tokens, full card numbers); response shapes stay allowlists, per the skill's serialize-out rule

## Pre-commit secret scan

```bash
git diff --cached | grep -iE "password|secret|api[_-]?key|token|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"
```

A hit is a stop. A secret that already reached a remote is rotated, not just removed.

## OWASP Top 10 (2021)

| # | Class | Where the skill defends it |
|---|---|---|
| A01 | Broken access control | per-resource ownership checks (the big-four IDOR rule) |
| A02 | Cryptographic failures | HTTPS, argon2/scrypt/bcrypt, secrets from the environment |
| A03 | Injection | parameterized queries, output encoding |
| A04 | Insecure design | the threat-modeling pass |
| A05 | Security misconfiguration | the headers above, least privilege, dependency audit |
| A06 | Vulnerable components | `npm audit` by severity and reachability |
| A07 | Identification and auth failures | strong hashing, rate limits, session cookie flags |
| A08 | Software and data integrity | verify updates, pin CI actions to a SHA, signed artifacts |
| A09 | Logging and monitoring failures | log security events, never log secrets |
| A10 | SSRF | allowlist outbound URLs, treat fetch-by-client-URL as hostile |
