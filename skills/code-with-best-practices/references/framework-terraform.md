Apply these practices whenever planning, writing, or reviewing Terraform code.

## State and Remote Backends

| Practice | Detail |
|---|---|
| Configure a remote backend before the first apply | Local state files cause race conditions and lost updates when more than one actor runs Terraform. A versioned, locking remote backend (S3 plus DynamoDB, Terraform Cloud, GCS) protects against concurrent corruption from the start. |
| Give each environment its own state file | Shared state across prod, stage, and dev couples them so a single bad apply can damage all of them, and it makes targeted rollbacks impossible. Isolated state keeps blast radius contained. |
| Scope compositions narrowly | Fewer resources per state file means faster plan and apply cycles and a smaller impact when a misconfiguration or security incident hits one state. |
| Glue states together with terraform_remote_state and data sources | Reading another composition's outputs via remote state is the standard way to share values, and it avoids threading long variable chains through every layer. |
| Never put secrets into state as plaintext you can avoid | Anything passed to a resource argument lands in state, which is readable by anyone with backend access. Source secrets from a secrets manager or runtime injection so the sensitive value is not the durable record of truth. |

## Plan and Apply Discipline

| Practice | Detail |
|---|---|
| Always run plan and inspect it before apply | A plan is the only reliable preview of create, update, and destroy actions. Applying blind risks silent replacement or deletion of live infrastructure. |
| Treat any unexpected replace or destroy as a stop signal | A resource scheduled for replacement often means downtime or data loss. Investigate why before proceeding rather than approving the diff to make it pass. |
| Detect and reconcile drift explicitly | Out-of-band console changes make the real world diverge from state, so a later apply may revert or clobber them. Run plan to surface drift and decide whether to import, adopt, or overwrite it. |
| Do not use targeted applies as a normal workflow | Narrowly targeting resources skips dependency evaluation and hides drift in the rest of the config. Reserve it for recovery, not routine changes. |

## Module Design

| Practice | Detail |
|---|---|
| Keep resource modules small, focused, and plain | A resource module should create one logical unit and avoid embedded scripts, provisioners, and orchestration logic. Complexity pushed up into composition modules stays testable and reusable. |
| Do not hardcode environment-specific values | Anything that varies per environment or deployment belongs in a variable or data source. Hardcoded values create copy-paste drift that diverges silently over time. |
| Keep tfvars at the composition level only | Resource and infrastructure modules receive values from their caller. Embedding tfvars deep in a module locks in values that should flow in from the top. |
| Name the single resource of a type this | When a module makes one resource of a given type, name it this; when several exist, use descriptive singular nouns like public, private, database. This keeps resource addresses predictable for callers and refactors. |

## Naming Conventions

| Practice | Detail |
|---|---|
| Use snake_case for all Terraform identifiers | Resources, data sources, variables, outputs, and locals all use underscores. Dashes are reserved for human-facing argument values like DNS names and tags, so mixing them creates inconsistent references. |
| Do not repeat the resource type in its name | Write aws_route_table.public, not aws_route_table.public_route_table. The type is already part of the address, so repeating it is noise. |
| Match singular and plural names to the value shape | Use singular names for scalars and single resources, plural for lists and maps. The name then signals the shape without the reader checking the type. |
| Name outputs as name_type_attribute | For example security_group_id or rds_cluster_instance_endpoints. A predictable scheme lets consumers guess output names and read generated docs without the source. |
| Use positive names to avoid double negatives | Prefer encryption_enabled = true over encryption_disabled = false. Negated booleans force the reader to invert logic in their head and invite mistakes. |

## Variables and Validation

| Practice | Detail |
|---|---|
| Give every variable a description | Descriptions are the module's documented contract and appear in generated docs, so consumers who cannot read the source still understand each input. |
| Add validation blocks for constrained inputs | Failing fast at plan time on an invalid value is far cheaper than discovering it mid-apply against live infrastructure. Validate ranges, allowed values, and formats where they exist. |
| Prefer simple types over nested object schemas | string, number, and list or map of those are easy for callers to supply. Reach for object() only when strict key constraints genuinely matter. |
| Set nullable = false where null is not valid | This makes a passed null fall back to the default instead of propagating null into resource arguments and producing confusing errors downstream. |
| Order keys description, type, default, validation | Consistent ordering makes a long variables.tf fast to scan and review. |

## Outputs

| Practice | Detail |
|---|---|
| Give every output a description | Outputs are the module's public API, and an undocumented output is unusable to anyone who cannot read the implementation. |
| Prefer try() over element(concat(...)) | try(aws_security_group.this[0].id, "") is readable and safe, while the legacy concat and coalescelist pattern is error-prone and hard to verify. |
| Set sensitive = true only when you own all consumers | Marking an output sensitive restricts its visibility everywhere it is referenced, so use it for genuinely secret values whose full downstream usage you control. |

## Code Structure

| Practice | Detail |
|---|---|
| Split config into main, variables, outputs, versions | Separating resources, inputs, outputs, and version pins into conventional files makes any Terraform codebase navigable without exploration. |
| Pin Terraform and provider versions in versions.tf | Unpinned providers can upgrade between runs and change behavior or plan output unexpectedly. Explicit constraints make runs reproducible. |
| Place count or for_each first, then a blank line | Putting meta-arguments at the top lets a reader see immediately whether a resource is conditional or iterated before reading its body. |
| Use # for comments | The hash is the idiomatic HCL comment style; // and block comments read as foreign to the toolchain and community. |
