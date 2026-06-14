Apply these practices whenever planning, writing, or reviewing Terraform code. Targets Terraform 1.5+ (version-specific items are flagged). Generic clean-code and naming rules live in CLAUDE.md; this reference is the Terraform-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Versioning and lockfile](#versioning-and-lockfile)
- [State and backends](#state-and-backends)
- [Iteration and conditionals](#iteration-and-conditionals)
- [Modules and contracts](#modules-and-contracts)
- [Variables and validation](#variables-and-validation)
- [Lifecycle and refactors](#lifecycle-and-refactors)
- [Secrets and data sources](#secrets-and-data-sources)
- [Workflow](#workflow)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Versioning and lockfile

| Practice | Detail |
|---|---|
| Set `required_version` and pin every provider | A `terraform` block with `required_version = ">= 1.7"` and a `required_providers` entry per provider stops a newer CLI or auto-upgraded provider from silently changing plan output between runs. Pin providers to a major and minor (`version = "~> 5.34"`), not a floating latest. |
| Commit `.terraform.lock.hcl` | The dependency lock file pins exact provider versions and checksums so every machine and CI run resolves the identical set. It is not generated fresh per run, so an uncommitted lockfile means each runner can drift to a different provider build. Update it deliberately with `terraform init -upgrade`. |
| Pin module sources to a version | A registry or git module reference without a `version` (or `?ref=` tag) re-resolves to the tip on every init, so a downstream change lands in your config unreviewed. Pin to a tag. |

## State and backends

| Practice | Detail |
|---|---|
| Configure a locking remote backend before the first apply | Local state races and loses updates when more than one actor runs Terraform. A versioned, locking backend (S3 with native lockfile or DynamoDB, GCS, HCP Terraform) prevents concurrent corruption from the start. State is plaintext at rest, so the backend must be encrypted and access-controlled. |
| Segment state by environment and by blast radius | One state per prod/stage/dev, and narrow compositions within each, keep plan and apply fast and contain the damage when an apply or incident goes wrong. A single shared state couples everything and makes targeted recovery impossible. |
| Read across states with `terraform_remote_state` or provider data sources | Pulling another composition's outputs is the standard way to share values without threading variable chains through every layer. Prefer a provider-native data source where one exists; it does not require the consumer to hold backend access to the producer's state. |
| Treat workspaces as short-lived, not as environments | CLI workspaces all share one backend, one set of credentials, and one access boundary, so they are not an isolation mechanism for prod versus dev. Use separate root directories or HCP workspaces for long-lived environments; reserve CLI workspaces for ephemeral copies of the same config. |

## Iteration and conditionals

| Practice | Detail |
|---|---|
| Prefer `for_each` over `count` for collections | `count` keys instances by list index, so removing a middle element shifts every later index and Terraform plans to replace or destroy resources that did not change. This is the single most common cause of accidental destroys. `for_each` keys by a stable map key or set value, so removing one entry touches only that one. |
| Reserve `count` for an on/off toggle | `count = var.enabled ? 1 : 0` is the legitimate use; reach for `for_each` for anything that is a named or growing collection. |
| Keep `for_each` keys stable and known at plan time | Changing a key churns the resource (destroy plus recreate), so treat keys as permanent IDs. Keys derived from a not-yet-created resource's attribute force `-target` or staged applies; derive them from inputs or literals instead. |

## Modules and contracts

| Practice | Detail |
|---|---|
| Keep resource modules small, focused, and script-free | A module should create one logical unit with no embedded provisioners or orchestration; push composition up to a root module that stays testable and reusable. |
| Treat variables and outputs as the public contract | Inputs flow in from the caller and outputs are the only supported surface, so callers should never reach into internal resource addresses. Group resources by shared purpose in files (`network.tf`, `compute.tf`), not one resource per file. |
| Do not route outputs through input variables | Passing a value out through a variable instead of referencing the resource breaks the implicit dependency graph, so Terraform can order operations wrong. Reference the resource attribute directly in the output. |
| Keep tfvars at the root only | Resource and infrastructure modules receive values from their caller; tfvars buried in a child module locks in values that should flow from the top. |

## Variables and validation

| Practice | Detail |
|---|---|
| Type and describe every variable; describe every output | The type plus description is the documented, checker-enforced contract that appears in generated docs for consumers who never read the source. |
| Add `validation` blocks for genuinely restrictive inputs | Failing fast at plan time on a bad range, enum, or format is far cheaper than discovering it mid-apply against live infrastructure. Do not validate what the type system already guarantees; reserve it for uniquely restrictive rules. |
| Name numeric values with their unit, booleans positively | `ram_size_gb` and `disk_size_gb` carry the unit so a caller cannot pass the wrong magnitude; `enable_external_access = true` reads cleaner than a negated `disable_*`. |
| Prefer simple types; set `nullable = false` where null is invalid | `string`, `number`, and lists or maps of those are easy to supply; reach for `object()` only when strict key constraints matter. `nullable = false` makes a passed null fall back to the default instead of propagating null into resource arguments. |

## Lifecycle and refactors

| Practice | Detail |
|---|---|
| Use `moved` blocks when renaming or restructuring | Renaming a resource or wrapping it in a module changes its address, which Terraform reads as destroy-old plus create-new. A `moved` block (1.1+) tells Terraform it is the same object so the plan shows no change. Prefer it over `terraform state mv`, which is unreviewable. |
| `create_before_destroy` for resources that cannot tolerate a gap | When a change forces replacement, the default destroys then creates, causing downtime. `create_before_destroy = true` builds the replacement first, but the resource type must allow two to coexist (unique names or ports will collide). |
| Know what `prevent_destroy` does not cover | `prevent_destroy = true` rejects a plan that would destroy the resource, but it does NOT stop a destroy when you remove the resource block entirely, because the rule lives only in config. It is a guardrail against accidental replacement, not a substitute for review. |
| Scope `ignore_changes` narrowly | List the specific attributes a controller or autoscaler mutates out of band; `ignore_changes = all` blinds Terraform to real drift on everything else. |
| Use the `import` block over CLI import (1.5+) | A declarative `import` block is reviewed in the plan and committed, unlike the imperative `terraform import` command whose effect leaves no trace in the diff. |

## Secrets and data sources

| Practice | Detail |
|---|---|
| Never hardcode secrets; source them at runtime | Any value passed to a resource argument is written to state in plaintext, so a hardcoded password becomes the durable record of truth readable by anyone with backend access. Pull secrets from a secrets manager data source or inject at runtime. |
| Understand the limit of `sensitive = true` | Marking a variable or output sensitive only redacts it from CLI output; it does NOT encrypt it in state. It restricts visibility everywhere the value is referenced, so use it for genuinely secret values whose downstream usage you control. |
| Prefer data sources over hardcoded IDs | Look up AMI IDs, VPC IDs, zones, and account IDs through data sources placed next to the resources that use them, so the config follows reality instead of pinning a stale ID that diverges silently. |
| Avoid `local-exec` and `remote-exec` provisioners | Resources a script creates are invisible to state, so Terraform cannot plan, drift-detect, or destroy them. Provisioners are a last resort; prefer a provider resource, `cloud-init`/user-data, or a separate config-management tool. |

## Workflow

| Practice | Detail |
|---|---|
| Run `fmt` and `validate` before every commit, lint in CI | `terraform fmt` and `terraform validate` are safe to run automatically; add TFLint or a policy tool for organization-specific rules the core toolchain does not enforce. |
| Plan in CI on the PR, review the plan, then apply | A saved plan is the only reliable preview of create, update, and destroy actions; surface it on the pull request so a human approves the diff before apply. Treat any unexpected replace or destroy as a stop signal, not a diff to approve through. |
| Do not use `-target` as a routine workflow | Targeting skips full dependency evaluation and hides drift elsewhere in the config. Reserve it for recovery from a broken state, never for normal changes. |

## Gotchas

- `count` keys by index: deleting a middle element shifts later indices and plans replacements for resources that did not change. Use `for_each`.
- `prevent_destroy` does not stop a destroy triggered by removing the resource block; only by an in-place plan that would replace it.
- `sensitive = true` redacts CLI output but stores the value in plaintext in state; it is not encryption.
- An uncommitted `.terraform.lock.hcl` lets each machine resolve different provider builds; commit it.
- Renaming a resource without a `moved` block reads as destroy-plus-create, not a rename.
- CLI workspaces share one backend and one credential boundary, so they are not environment isolation.
- A module source without a pinned version or ref re-resolves to tip on every init.

## Sources

- [Terraform Style Guide](https://developer.hashicorp.com/terraform/language/style) and [Recommended Practices](https://developer.hashicorp.com/terraform/cloud-docs/recommended-practices) - official HashiCorp; file structure, naming, version pinning, validation, workflow.
- [lifecycle meta-argument reference](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle) - official; exact create_before_destroy, prevent_destroy, ignore_changes semantics.
- [count vs for_each (HashiCorp support)](https://support.hashicorp.com/hc/en-us/articles/31348158569363-Terraform-count-versus-for-each-meta-argument) - official support article; the index-churn failure mode in detail.
- [HCP Terraform workspace best practices](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/best-practices) - official; why CLI workspaces are not environment isolation.
- [Google Cloud: Terraform general style and structure](https://docs.cloud.google.com/docs/terraform/best-practices/general-style-structure) - major cloud vendor; module contracts, outputs-through-inputs pitfall, unit-named variables, script avoidance.
- [Gruntwork Terraform Style Guide](https://docs.gruntwork.io/guides/style/terraform-style-guide/) - widely respected IaC consultancy; module layout (modules/examples/test) and testing conventions.
