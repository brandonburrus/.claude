# API contract migrations: evolving an interface consumers depend on

Read this for the execution craft of changing a public API or interface that consumers depend on: distinguishing additive from breaking changes, versioning when a break is unavoidable, signaling a deprecation, migrating consumers, and removing the old contract only after they have moved.

## Additive changes are safe; breaking changes are not

The cheapest migration is the one that never breaks a consumer. Sort the change before designing the rollout.

- **Additive (backward compatible), ship in place:** a new optional field, a new endpoint, a new optional parameter, a new enum value consumers can ignore. Existing consumers keep working untouched. Prefer expressing the change additively whenever it can carry the same intent.
- **Breaking (not backward compatible), needs a versioned migration:** removing or renaming a field, making an optional parameter required, changing a type or a default, tightening validation, changing status-code or error semantics. Any of these breaks a deployed consumer the moment it ships in place.
- Hyrum's Law sets the bar for what counts as breaking: with enough consumers, every observable behavior is depended on, including field ordering, timing, and quirks. "No one relies on that" needs traffic data, not assumption.

## Version when the break is unavoidable

Versioning is the expand beat for contracts: the new version runs alongside the old so consumers move on their own timeline.

- Stand up the new contract version next to the old (a `/v2` path, a version header, a new GraphQL field or type, a new typed method) and serve both. The old version stays fully functional through the window.
- Keep one implementation behind both versions where you can, with the old version adapting to the new internals, so you are not maintaining two divergent code paths. This is the adapter form of parallel-change.
- Prefer the smallest versioning unit that contains the break (a single endpoint or field over a whole-API version bump) so consumers migrate only what actually changed.

## Deprecate with a signal and a window, not a surprise

Removal is the contract beat and runs last; the deprecation window is how consumers get from old to new before it does.

- **Signal the deprecation in-band:** a `Deprecation` and `Sunset` header (RFC 8594), a deprecated marker in the schema or SDK, a logged warning on use. The signal names the replacement and the sunset date or "no hard deadline".
- **Default to advisory** (consumers migrate on their own timeline); go compulsory (a hard sunset date) only when security, unsustainable maintenance, or a blocking dependency justifies forcing it.
- **Own the migration, do not just announce it.** The Churn Rule: the owner of the deprecated contract migrates the consumers it controls or ships tooling (a codemod, a client-library bump, a compat shim) that makes the move near-free. Announce-and-wait produces zombie deprecations that linger for years.

## Migrate consumers, then remove the old contract

- Track consumer adoption of the new version with real signals: request counts per version, SDK version telemetry, the deprecated-endpoint hit rate trending toward zero.
- Migrate the consumers you own first; for external consumers, the deprecation window plus the migration tooling is the mechanism.
- **Remove the old contract only on evidence of zero usage** over a representative window (no traffic to the old version, no deprecated-field reads), not absence of complaints. Remove the endpoint, its tests, its docs, and the deprecation notices themselves together; a notice for a removed contract is noise that erodes trust in the remaining ones.

## Pitfalls

- **Breaking in place to "keep it clean."** Renaming a field or tightening validation on the live contract breaks every deployed consumer instantly. If it is breaking, it needs a new version, not an edit.
- **Deprecating without a replacement.** Announcing a sunset before the new contract covers the depended-upon behavior strands consumers in limbo. Confirm the replacement is complete and live before any deprecation signal.
- **Announce-and-wait with no tooling.** A deprecation notice that puts all the migration work on consumers and offers no codemod or client bump produces a zombie deprecation: the old contract lives forever because no one is made able to leave it.
- **Removing on silence.** Deleting the old version because complaints stopped, rather than because usage metrics hit zero, breaks the quiet long-tail consumer that never spoke up. Require zero-usage evidence over a real window.
