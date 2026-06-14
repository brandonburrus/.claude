Apply these practices whenever planning, writing, or reviewing AWS CDK code. Targets CDK v2 (`aws-cdk-lib` + `constructs`); v1 reached end of support in June 2023. Generic clean-code, naming, and secrets-hygiene rules live in CLAUDE.md; this reference is the CDK-specific, version-current, easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Constructs vs stacks](#constructs-vs-stacks)
- [Construct levels](#construct-levels)
- [Logical IDs and refactoring](#logical-ids-and-refactoring)
- [Environments and config](#environments-and-config)
- [IAM and security defaults](#iam-and-security-defaults)
- [Removal policies and state](#removal-policies-and-state)
- [Cross-stack references](#cross-stack-references)
- [Aspects and compliance](#aspects-and-compliance)
- [Synthesis and testing](#synthesis-and-testing)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Constructs vs stacks

| Practice | Detail |
|---|---|
| Model with constructs, deploy with stacks | A logical unit (a website, a service) is a `Construct` that composes its S3 bucket, API, and Lambdas; a `Stack` only describes how constructs are composed for a deployment scenario. Modeling a logical unit as a `Stack` forces every reuse into a separate deployable unit. |
| Extend `Construct`, not `Stack`, for reusable units | Reusable resource groups extend `Construct` so the same unit can be instantiated in dev and prod stacks with different props. |
| Configure with props, not env vars | Constructs and stacks accept a typed props object; env-var lookups inside a construct couple synthesis to the machine it runs on. Confine `process.env` reads to the app entrypoint. |
| Keep infra and runtime code in one package | The same package that defines the Lambda's infrastructure should hold its handler code, so both version and test together; they need not be split across repos or packages. |
| One app per repository | Multiple CDK apps in one repo widen the deploy blast radius: a change to one app triggers deploys of the others and a break in one blocks the rest. |

## Construct levels

| Practice | Detail |
|---|---|
| Prefer L2 over L1 `Cfn*` | L2 constructs (`s3.Bucket`) carry sane defaults, encryption, SSL, and `grant*` helpers; reaching for L1 `Cfn*` by default discards all of that and forces hand-reimplementation. |
| Use L1 only as an escape hatch | L1 maps one-to-one to CloudFormation and exposes every property, so it is correct for a brand-new resource feature an L2 has not surfaced yet, not the default. |
| Reach for L3 patterns before hand-wiring | AWS Solutions Constructs and Construct Hub L3 patterns encode multi-service Well-Architected wiring (for example API-to-Lambda-to-DynamoDB); composing them beats re-deriving the same plumbing. |
| Wrapper L2+ constructs are guidance, not enforcement | A `MyCompanyBucket` surfaces security defaults early but a developer can bypass it with L1 or a third-party construct, and your wrapper cannot be used by Solutions Constructs built on stock L2. Enforce with SCPs, permission boundaries, and Aspects, not wrappers alone. |
| Verify props against the installed version | L2 props are added and deprecated between `aws-cdk-lib` minors, so a prop recalled from memory may not exist in the pinned version and will fail synth; check `package.json` first. |

## Logical IDs and refactoring

| Practice | Detail |
|---|---|
| Never rename a stateful resource's construct ID | The logical ID is derived from the construct `id` plus its path in the tree, so a rename makes CloudFormation delete and recreate, destroying a database or bucket. |
| Moving a construct between scopes is a rename | Reparenting changes the path-derived logical ID exactly as renaming does, so refactoring the tree can silently trigger a stateful replace. |
| Use `cdk refactor` to move resources safely | The `cdk refactor` command (2025) computes the old-to-new logical-ID mapping and uses CloudFormation's refactor API to preserve deployed resources across renames and cross-stack moves, instead of replacing them. |
| Pin stateful logical IDs in a test | A fine-grained assertion or snapshot on those IDs catches an accidental replacement at review time rather than during a prod deploy. |
| Let CDK generate physical names | Hardcoding `bucketName`/`tableName` blocks replacement (the new resource cannot take a name the old one still holds) and blocks deploying the stack twice in one account; pass the generated `table.tableName` onward instead. |

## Environments and config

| Practice | Detail |
|---|---|
| Model all stages in code | Create a distinct stack (or `Stage`) per environment with its config baked into source, rather than one parameterized template; this keeps synthesis deterministic and unit-testable. |
| Model environments as a literal union | `type Env = "dev" | "qa" | "prod"` plus `Record<Env, T>` config maps makes the compiler flag every map when a new environment is added. |
| Choose env-agnostic vs explicit deliberately | A stack with no `env` is region/account-agnostic and uses pseudo-params, but `fromLookup` context providers (VPC, AMI) require a concrete `env` to resolve. Set explicit `account`/`region` when you do environment-specific lookups. |
| Source accounts and regions from typed constants | Reading them at runtime (`process.env`, SDK calls) makes synth nondeterministic; pass them as props or constants. |
| Keep secrets out of code and templates | Reference Secrets Manager / SSM by name or ARN (`Secret.fromSecretNameV2`); a literal in source or a plaintext env var lands in version control and in the synthesized template. |

## IAM and security defaults

| Practice | Detail |
|---|---|
| Use `grant*` methods, never hand-written policies | `bucket.grantRead(fn)` generates a least-privilege policy with correct actions and resource ARNs and wires the role for you; a hand-authored `PolicyStatement` drifts toward over-broad permissions. |
| Let CDK create roles and security groups | Predefining roles for a security team to hand out cripples CDK's auto-scoping; enforce guardrails with SCPs and permission boundaries at the org level instead. |
| Encrypt at rest and enforce SSL by default | At least `S3_MANAGED` encryption, `enforceSSL: true`, `blockPublicAccess: BLOCK_ALL`, and `enableKeyRotation` on symmetric KMS keys; these are cheap audit findings to prevent up front. |
| Deny by default on egress | `allowAllOutbound: false` with explicit egress rules; permissive egress is easy to leave in and widens blast radius. |

## Removal policies and state

| Practice | Detail |
|---|---|
| Set `removalPolicy` explicitly on stateful resources | CDK defaults data-bearing resources to `RETAIN` (orphaned, not deleted); use `RETAIN` in prod and `DESTROY` in throwaway dev so a stack deletion's data behavior is never ambiguous. |
| Isolate stateful resources in their own stack | Databases, buckets, and VPCs in a dedicated stack let you enable termination protection on it and freely destroy or recreate the stateless stack with no data risk; they are also the most rename-sensitive. |
| Set `retention` on every LogGroup | CDK retains logs forever by default, so an unset retention silently accrues storage cost; set it on each LogGroup or validate it with an Aspect. |

## Cross-stack references

| Practice | Detail |
|---|---|
| Same app: pass construct references | Save a resource as a stack attribute and pass it to the consuming stack's constructor; CDK auto-creates the CloudFormation export/import. |
| Watch for export deadlock | An automatic export cannot be removed while another stack still imports it, so deleting a cross-stack reference can wedge a deploy; remove the consumer first, or break the link before changing the producer. |
| Different apps: import by ARN/name | Use static `from*` methods (`Table.fromTableArn`) against a value surfaced via `CfnOutput`, rather than a live reference across app boundaries. |
| Declare deps CDK cannot infer | Call `stack.addDependency(other)` when no token reference links two stacks, since without a reference CDK cannot order the deploy. |

## Aspects and compliance

| Practice | Detail |
|---|---|
| Use Aspects for cross-cutting policy | `Aspects.of(scope).add(...)` runs a visitor over every construct in scope during the prepare phase to tag, validate, or mutate; use it to assert encryption, removal policies, or log retention across a whole app. |
| Aspects run during synth, top-down | The `visit` method is called after all other code runs; in typed languages narrow with `node instanceof s3.CfnBucket` before touching specific props, and add an error annotation (`Annotations.of(node).addError`) to fail synth on a violation. |
| Aspects stop at `Stage` boundaries | Aspects do not propagate across a `Stage`; apply them on the `Stage` itself or lower to reach constructs inside it. |
| Run cdk-nag as an Aspect | Add a NagPack (`AwsSolutionsChecks`, plus HIPAA / NIST 800-53 / PCI rule packs) to catch security issues at synth before deploy. |
| Suppress cdk-nag rules narrowly with a reason | Suppress per-finding (`AwsSolutions-IAM5[Action::s3:*]`), not per-resource, always with a justification; a blanket suppression hides real findings. |

## Synthesis and testing

| Practice | Detail |
|---|---|
| Keep `cdk synth` side-effect free | Synthesis must make no AWS mutations and ideally no network calls; side effects make builds nondeterministic and unsafe in CI. Push runtime mutation into custom resources. |
| Even read-only lookups are risky | A `fromLookup` value that changes between deploys (a new AZ, a new AMI) can force-replace subnets or instances later; this is why context is cached. |
| Commit `cdk.context.json` | The cached context (`fromLookup` results) is what makes every machine synth the same template; an uncommitted cache lets CDK re-resolve and produce a surprise diff. |
| Decide at synth time in code | Use language `if`, maps, and loops over CloudFormation `Conditions`/`Parameters`; resolving logic in code yields concrete, reviewable templates. |
| Pair fine-grained assertions with a snapshot | `Template.fromStack(...).hasResourceProperties(...)` checks specific intent; a snapshot test fails on any template change, making refactors visible and confident. |

## Gotchas

- Renaming a construct ID or moving it between scopes replaces the resource; for stateful resources that destroys data. Use `cdk refactor`.
- A stack with no `env` cannot resolve `fromLookup` context providers; they need a concrete account and region.
- Hardcoded physical names block both resource replacement and a second deployment of the same stack in one account.
- CDK orphans data-bearing resources (`RETAIN`) and keeps logs forever by default, quietly growing your bill; set `removalPolicy` and LogGroup `retention` explicitly.
- An auto-generated cross-stack export cannot be deleted while a consumer still imports it; the deploy deadlocks until the consumer is removed first.
- Aspects do not cross `Stage` boundaries, so an app-level Aspect can silently skip everything inside a `Stage`.
- cdk-nag emits multiple findings per resource; suppress each by its specific finding id, never the whole resource.

## Sources

- [AWS CDK v2 Developer Guide: Best practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html), [Aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html), [Identifiers](https://docs.aws.amazon.com/cdk/v2/guide/identifiers.html), [cdk refactor](https://docs.aws.amazon.com/cdk/v2/guide/refactor.html) - the official, authoritative CDK v2 guidance on constructs vs stacks, logical IDs, synth determinism, and grants.
- [AWS Prescriptive Guidance: Best practices for using the AWS CDK in TypeScript](https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-cdk-typescript-iac/introduction.html) - AWS-authored prescriptive patterns for large-scale CDK IaC, including construct creation and refactoring.
- [cdk-nag (cdklabs)](https://github.com/cdklabs/cdk-nag) - the canonical AWS-labs tool for synth-time compliance checks; NagPacks, per-finding suppression semantics.
- [AWS Solutions Constructs](https://github.com/awslabs/aws-solutions-constructs) and [Construct Hub](https://constructs.dev/) - AWS-vetted L3 multi-service patterns and the central registry for discovering constructs.
- [Towards The Cloud: AWS CDK Best Practices (Danny Steenman)](https://towardsthecloud.com/blog/aws-cdk-best-practices) - widely cited, regularly updated practitioner guide covering testing, Projen, and grant patterns.
- [Ran the Builder: AWS CDK Best Practices From The Trenches](https://www.ranthebuilder.cloud/post/aws-cdk-best-practices) - recognized AWS Serverless Hero's field guide to construct organization and testing.
