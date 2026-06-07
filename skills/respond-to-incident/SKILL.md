---
name: respond-to-incident
description: >-
  Use this skill when responding to a live production incident or outage: a
  service is down, users are blocked, an alert is firing, data is at risk, or
  someone declares a SEV. Use when the user says "prod is down", "we have an
  outage", "the site is down", "users can't log in", "sev1", "sev2", "page the
  team", "mitigate this now", or "stabilize the system". The skill drives
  stabilization, severity classification, and stakeholder communication during
  the incident, then hands the rest off. Do not use for the internal
  engineering RCA after the fix is validated (use write-post-mortem), for
  debugging the root cause itself (use fix), or for pre-release deploy
  preparation (use prepare-for-deploy).
---

## Purpose

Drive the live response to a production incident: confirm it is real, classify its severity, stabilize the system before understanding why it broke, and keep stakeholders informed on a cadence. The deliverable during the incident is a restored system and a clean comms trail; the artifact after is a customer or stakeholder facing incident report. Restoring service is the job, not diagnosing it. Root cause comes later, from a calmer chair.

## The one rule that orders everything

**Mitigate before you diagnose.** Stop the bleeding first (roll back, flag off, fail over, scale, kill the bad job), then hunt the root cause once users are no longer harmed. An engineer debugging a live outage while customers are down has the priority inverted. The only thing that competes with mitigation is preserving the evidence the mitigation is about to destroy (see step 3).

## Workflow

Copy this checklist and keep it in the incident log:

```text
Incident response:
- [ ] 1. Confirm and declare (assign IC, start the timeline)
- [ ] 2. Classify severity and blast radius
- [ ] 3. Stabilize (capture evidence, then mitigate)
- [ ] 4. Communicate (initial notice, then on cadence)
- [ ] 5. Verify recovery (baseline holds for a stated window)
- [ ] 6. Hand off (fix, write-post-mortem, incident report)
```

### 1. Confirm and declare

Confirm the signal is real before mobilizing: an alert is a claim, not a fact. Reproduce the user-visible symptom or read the metric directly. Once confirmed, declare the incident, name yourself incident commander (IC), and start an append-only timeline log with timestamps. Even solo, separate the hats: IC decides and coordinates, comms updates stakeholders, ops has hands on the keyboard. The timeline started now is what the post-mortem and incident report are both built from later.

### 2. Classify severity and blast radius

Classify on impact, not on how alarming it feels. Severity sets the comms cadence and who gets paged.

| Sev | Criteria | Response |
|---|---|---|
| SEV1 | Full outage, data loss or corruption, security breach, or revenue-stopping. Getting worse. | All hands, immediate, comms every 15-30 min |
| SEV2 | Major feature broken or severe degradation for many users; a workaround may exist | Active response, comms every 30-60 min |
| SEV3 | Minor or partial impact, few users, not spreading | Normal hours, single owner, comms on resolution |

Record who and what is affected, how many, whether data is at risk, and whether the blast radius is growing. A SEV that is spreading escalates regardless of its starting tier.

### 3. Stabilize

Reach for the fastest safe mitigation, in rough order of preference: roll back to the last known-good release, disable the offending feature flag, fail over, scale out, rate-limit, or kill the bad job. Prefer reverting to a known-good state over a hot patch you cannot test under pressure; fixing forward during an incident is how a one-incident day becomes two.

Before you mitigate, snapshot the evidence the mitigation will erase: the bad build artifact and its SHA, current logs, the metric graphs, a copy of the corrupt state. A rollback that destroys the only record of what went wrong leaves the post-mortem blind.

### 4. Communicate

Silence during an incident reads as chaos; a steady cadence reads as control, even with no new information. Send an initial notice fast, then update on the cadence the severity sets, and always state the next update time.

```text
[SEV2] Investigating: some users cannot log in (since 14:02 UTC).
Impact: ~15% of login attempts failing. Sign-ups unaffected.
Status: mitigation in progress (rolling back release 4.7.1).
Next update: 14:35 UTC or sooner if status changes.
```

Match the audience: a status page and customer notice carry impact and ETA in plain terms; an internal channel carries the technical detail. "Still investigating, next update in 30 minutes" is a complete and useful message.

### 5. Verify recovery

Recovery is metrics back to the pre-incident baseline, held for a stated window, not a single green blip. Watch the same signals prepare-for-deploy names as rollback triggers: error rate, p50/p95/p99 latency, and availability. State the window ("error rate at baseline for 30 minutes") before standing down, and announce the all-clear only when it holds.

### 6. Hand off

The incident ending is the start of three separate threads:

- **Root cause** goes to the fix skill: now is when the calm, evidence-based debugging happens, against the snapshot from step 3.
- **Internal engineering RCA** goes to write-post-mortem once the fix is validated: mechanism, why it slipped through, action items.
- **Customer or stakeholder incident report** is produced here, because it is a different document from the internal RCA. Use the structure below.

Open every follow-up as an action item with an owner and a tracking artifact; an unowned action item is a wish that resurfaces in the next incident.

## Incident report structure

The external report answers "what did this cost us and what are we doing about it", not "which function had the bug". Keep that detail for the post-mortem.

| Section | Content |
|---|---|
| Summary | One paragraph in user terms: what was impacted, when, for how long, and that it is resolved |
| Timeline | Key timestamps: detection, declaration, mitigation, recovery, all-clear (from the step 1 log) |
| Impact / blast radius | Who and how many were affected, which features, data or revenue impact, in concrete numbers |
| Resolution | What restored service (the mitigation), in plain language |
| Follow-up | What is being done so it does not recur, each with an owner; links to the post-mortem when ready |

## Gotchas

- **Mitigation destroys evidence.** The rollback that saves the users also erases the broken state the post-mortem needs. Snapshot first; it costs seconds.
- **Fixing forward under pressure is a trap.** A hot patch you cannot test can compound the incident. Roll back to known-good and patch later in calm.
- **Severity is about impact, not adrenaline.** Classify on users, data, and revenue. Both inflation (paging everyone for a SEV3) and deflation (sitting on a spreading SEV1) burn trust.
- **The all-clear is a held baseline, not a blip.** Declaring victory on the first green data point invites a second incident when the metric sags back.
- **The incident report and the post-mortem are different documents.** This skill produces the external report (timeline, blast radius, comms); the internal mechanism-level RCA is write-post-mortem's job. Producing one when the audience needs the other wastes the work.
