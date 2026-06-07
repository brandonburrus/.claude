---
name: triage-security-finding
description: >-
  Use this skill to triage an incoming security finding to a disposition: a
  dependency or scanner alert (Dependabot, Snyk, npm audit), a CVE advisory, a
  SAST or DAST result, or a pentest or bug-bounty report. It decides whether the
  finding is real, whether it is reachable and exploitable in your context, its
  contextual severity, and the action. Use when the user says "triage this
  security finding", "is this CVE exploitable", "Dependabot flagged this", "Snyk
  alert", "npm audit found", "is this vulnerability real", "assess this pentest
  finding", "is this reachable", or "what's the real severity". Do not use for
  building security into a feature as you write it (use harden-security), for
  auditing your own diff for new vulnerabilities (use the security-reviewer
  agent or the bundled /security-review), for reproducing and fixing a confirmed
  issue once triaged (use fix, then follow-tdd), or for responding to an active
  breach (use respond-to-incident).
---

## Purpose

Triage an incoming security finding to a documented disposition: verify it is real, decide whether it is reachable and exploitable in your context, score its contextual severity, and choose the action. The deliverable is a triage verdict per finding with its reasoning, not the fix. The discipline is refusing to triage by the headline severity: the CVSS base score is the source's context, not yours, reachability is the gate that inverts the queue, and every disposition is a recorded decision, especially "accept", which is a choice with an owner and a review date, not a silent drop.

## The gate: reachability over base score

The single most important judgment is reachability in your deployment, not the number the source assigned. An unreachable critical is backlog; a reachable medium on your auth path can be a blocker. Triage by base score alone and you fix the loud finding while the quiet exploitable one waits. Establish reachability before you spend any fix budget.

## Workflow

Copy this checklist and track progress:

```text
Triage finding:
- [ ] 1. Establish what the finding claims
- [ ] 2. Verify it is real (not a false positive)
- [ ] 3. Assess reachability and exploitability in your context
- [ ] 4. Score the contextual severity
- [ ] 5. Decide the disposition
- [ ] 6. Record and route
```

### 1. Establish what the finding claims

Parse the report: the vulnerability (CVE or CWE), the affected component and version, the claimed impact, the severity the source assigned, and its proof (advisory link, PoC). Note the source's severity but treat it as an input, not the verdict; it was computed without your environment.

### 2. Verify it is real

Confirm the vulnerable component and version is actually present, and that the vulnerable code path exists in what you ship. Dependency and SAST scanners over-report: a flagged transitive dependency you never call, or a sink on a branch that cannot execute, is a false positive that should not consume fix budget. For a pentest or bug-bounty report, reproduce the claim or confirm the mechanism. An unverified finding is a claim, not a vulnerability.

### 3. Assess reachability and exploitability in your context

Walk the path to the vulnerable code. Does untrusted input reach it? Is the affected dependency a runtime dependency on a live path, or a dev-only or build-time tool? Is the attacker's precondition (authentication, network position, a specific config) actually achievable given how you deploy? This is the gate; an unreachable critical and a reachable medium have inverted real severities.

### 4. Score the contextual severity

Adjust the base severity by reachability, asset sensitivity (what it exposes if exploited), and exposure (internet-facing, internal, or air-gapped). The base score is the starting point; this environmental adjustment is the number that drives the disposition. State both, so the gap between "the advisory says 9.8" and "for us it is a 4" is visible and defensible.

### 5. Decide the disposition

Pick one, with the reason:

| Disposition | When | Then |
|---|---|---|
| Fix now | reachable, with meaningful impact | reproduce with `fix`, write the regression test with `follow-tdd`, or upgrade the dependency |
| Mitigate | exploitable but no immediate fix | compensating control (flag off, WAF rule, config change); the fix ticket stays open |
| Accept | genuinely low contextual risk | document the reason AND a review date in a tracked register; accept is a decision, not an omission |
| False positive | not present, not reachable, or scanner error | record why, so the next scan does not re-litigate it |

### 6. Record and route

Write the verdict per finding with its reasoning. Route fix-now items to `fix` (reproduce first) or a dependency upgrade, mitigations through `harden-security`, and accepted findings to a tracked register with the reason and review date. If the finding involves a reporter (bug bounty) or an upstream maintainer (a vulnerability you found in a dependency), coordinate disclosure rather than only patching locally.

## Gotchas

- **The CVSS base score is not your severity.** It is computed without your environment. A 9.8 in a dependency you never reach is not a 9.8 for you, and a 5.0 on your authentication path may be a blocker. The environmental adjustment is the real number.
- **Scanner findings are claims, not facts.** Dependency and SAST tools over-report transitive code you do not call and paths that cannot execute. Verify presence and reachability before opening a fix ticket; chasing every alert at face value burns the budget the real one needed.
- **Accept without a reason and a review date is just ignoring it.** The accept disposition is a deliberate, recorded decision with an owner and a revisit date. An undocumented "we will not fix" is how a known issue becomes the post-mortem.
- **A mitigation is not a fix.** A WAF rule or a feature flag buys time; the vulnerability remains and its ticket stays open. Closing on a compensating control hides live risk behind a green board.
- **Reachability is the gate, not the queue order.** Sorting the backlog by base score fixes the loud finding first and leaves the quiet exploitable one waiting. Sort by contextual severity, which is reachability-weighted.

## Example

Two findings from one weekly scan:

```text
A) Dependabot: prototype-pollution CVE in lodash 4.17.20, CVSS 9.8 (critical).
   Verify: present, but only via webpack (build-time), never in the runtime
   bundle. Reachability: not on any request path.
   Contextual severity: low. Disposition: ACCEPT, review at next major upgrade,
   bump opportunistically. A 9.8 that does not ship is not a 9.8 for us.

B) Snyk: no rate limit on POST /auth/reset, CVSS 5.3 (medium).
   Verify: real, the endpoint has no limiter. Reachability: internet-facing,
   unauthenticated, on the credential path; exploitable for user enumeration
   and credential stuffing. Contextual severity: high.
   Disposition: FIX NOW -> reproduce with fix, add the limiter, regression test
   with follow-tdd.
```

The base scores said 9.8 outranks 5.3; reachability inverted the queue, and B ships first.
