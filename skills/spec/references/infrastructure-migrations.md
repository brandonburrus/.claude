# Infrastructure migrations: moving between platforms, providers, regions

Read this for the execution craft of moving a running system to new infrastructure: a different platform, cloud provider, region, cluster, or datastore engine. Run old and new in parallel, sync the data, cut traffic over gradually, verify, and decommission the old only after the new is proven.

## Stand up the new alongside the old

This is the universal method's expand beat in infrastructure form: the new environment exists and serves before any traffic depends on it.

- Provision the new target (platform, region, cluster, engine) fully and bring it to a serving state with the old still authoritative. Use the same infrastructure-as-code path you use elsewhere so the new environment is reproducible and reviewable, not hand-built.
- Make the new environment reachable for verification (a separate hostname, a weighted route at 0 percent, an internal endpoint) without it being in the live path yet.
- Keep the old environment fully operational and authoritative throughout; it is the rollback target until decommissioning.

## Sync the data before cutover

Traffic cannot move until the new datastore holds the data the old one does, and keeps holding it as the old one keeps changing.

- **Bulk-load, then catch up.** Snapshot and restore (or bulk-copy) the historical data, then run continuous replication or change-data-capture to keep the new store current with writes still landing on the old.
- **Dual-write or replicate through the window.** Either replicate old to new continuously, or have the application dual-write to both, so the new store stays current right up to the cutover instant. This is the dual-write gate from the universal method.
- **Verify the data agrees before switching reads.** Run a consistency check (row counts, checksums, a sampled diff) proving the new store matches the old. A cutover onto unverified data is silent corruption.

## Cut traffic over incrementally

Move traffic in slices and watch each, never all at once; the slice bounds the blast radius.

- **DNS weight or load-balancer weight** is the cutover lever: shift a small percentage to the new environment first (a canary), watch error rates and latency, then ramp. Lower DNS TTL ahead of the cutover so a shift-back propagates fast.
- **Per-tenant or per-region** routing is the alternative slice: move one tenant or one region, validate, then proceed. This makes the rollback a per-slice flip rather than a global one.
- **Hold the rollback ready at every step.** The way back is shifting weight back to the old environment, which still runs. Rehearse it; an unrehearsed shift-back is not a rollback.

## Verify, then decommission

Decommissioning is the irreversible contract beat; it runs last and only on evidence.

- After full cutover, verify the new environment under real traffic (error budget intact, latency within SLO, data consistency holding) over a representative window before touching the old.
- **Decommission only on evidence of zero usage**: the old environment receives no traffic, holds no authoritative writes, and nothing references its endpoints. Confirm with metrics and logs, not absence of complaints.
- Remove the old environment, its DNS records, its IaC, and its monitoring together, so no orphaned config or stale alert outlives the system it watched.

## Pitfalls

- **Hard cutover with no parallel window.** Flipping DNS to the new environment in one move, with the old already torn down, has no rollback. Run both in parallel and ramp the weight.
- **Stale data at the cutover instant.** A bulk copy taken hours before cutover misses every write since; without continuous replication or dual-write up to the switch, the new store is behind. Close the gap with CDC or dual-write, and verify before switching reads.
- **DNS TTL traps the rollback.** A high TTL means a shift-back takes hours to propagate while users hit the broken target. Lower the TTL well before the cutover so the rollback is fast.
- **Decommissioning on a hunch.** Tearing down the old environment because the new "seems fine" strands you when a long-tail client or a forgotten job still depended on it. Require zero-usage evidence over a real window first.
