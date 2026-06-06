Apply these practices whenever planning, writing, or reviewing AWS CDK code.

## Contents

- Construct Levels
- Stack and Stage Boundaries
- Logical ID Stability
- Environment Configuration
- Secrets and Security Defaults
- Removal Policies and Stateful Resources
- Synthesis Discipline
- Verification

## Construct Levels

| Practice | Detail |
|---|---|
| Prefer L2 constructs over L1 | L2 constructs (for example `s3.Bucket`) apply sane defaults and grant helpers, so reaching for L1 `Cfn*` resources by default loses encryption, SSL, and IAM conveniences you would then have to reimplement by hand. |
| Use L1 `Cfn*` only when L2 cannot express it | L1 maps one to one to CloudFormation and exposes every property, so it is the correct escape hatch for new or niche resource features, not the default starting point. |
| Build L3 constructs for reused resource groups | Extend `Construct` (an L3 pattern) when a group of resources repeats across stacks, because copy pasting the same wiring drifts over time and a shared construct keeps it consistent. |
| L3 constructs extend `Construct`, never `Stack` | A reusable resource group is a modeling unit, not a deployment unit, so extending `Stack` would wrongly turn every reuse into a separate deployable stack. |
| Verify L2 props against the installed version | L2 constructs add and deprecate props between minor `aws-cdk-lib` versions, so a prop recalled from memory may not exist in the project's pinned version and will fail synthesis. |

## Stack and Stage Boundaries

| Practice | Detail |
|---|---|
| Stacks are deployment units | Group resources that must deploy and roll back together, because the stack is the atomic unit CloudFormation deploys and splitting tightly coupled resources across stacks creates ordering fragility. |
| A Stage is the composition root | Each deployment target gets a `Stage` subclass that owns its account, region, and stack instantiation, so cross stack wiring lives in one place instead of being scattered. |
| Separate stateful from stateless stacks | Put DynamoDB, S3, and KMS in dedicated stacks, because mixing them with frequently changing stateless resources raises the risk of an accidental replacement of data bearing resources. |
| Wire cross stack references through typed props | Pass ARNs and names as strings through props rather than passing construct references, because raw construct references across stacks trigger CDK cross stack export deprecation behavior and tighten coupling. |
| Declare explicit dependencies when CDK cannot infer them | Call `stack.addDependency(other)` when no token reference links two stacks, because without a reference CDK has no way to know the deploy order and may sequence them wrong. |
| Never derive behavior from parsing stage or stack ID strings | Read typed constants and props instead, because string parsing of IDs is brittle and silently breaks when a naming convention changes. |

## Logical ID Stability

| Practice | Detail |
|---|---|
| Do not rename construct IDs of stateful resources | The construct ID determines the CloudFormation logical ID, so renaming it makes CloudFormation delete the old resource and create a new one, destroying data on a database or bucket. |
| Treat moving a construct between scopes as a rename | Reparenting a construct changes its logical ID path just like renaming does, so refactoring the construct tree can silently trigger a replace of stateful resources. |
| Snapshot or assert logical IDs of stateful resources in tests | A test that pins these IDs catches an accidental replacement at review time rather than during a production deploy. |
| Prefer generated resource names over hardcoded ones | Hardcoded physical names block resource replacement and prevent deploying the same stack twice, because CloudFormation cannot create a new resource while the old one holds the fixed name. |

## Environment Configuration

| Practice | Detail |
|---|---|
| Model environments as a string literal union | Define `type Environment = "dev" | "qa" | "prod"`, because a union lets the compiler enforce exhaustive handling everywhere environments are used. |
| Store per environment values in `Record<Environment, T>` maps | TypeScript then requires a value for every environment, so adding a new environment to the union flags every map that still needs an entry. |
| Branch on environment with exhaustive maps, not scattered booleans | A single `envSpecificValue` map is scannable and exhaustive, whereas ad hoc boolean flags and ternaries hide which environments were considered. |
| Source accounts and regions from typed constants | Read account IDs and regions from a constants file rather than `process.env` or runtime lookups, because runtime resolution makes synthesis nondeterministic and hard to review. |
| Keep `process.env` out of constructs | Pass configuration through props and confine env vars to the `main.ts` entrypoint for local development, because env reads inside constructs make the same code synthesize differently depending on the shell. |

## Secrets and Security Defaults

| Practice | Detail |
|---|---|
| Never put secrets in constants or env vars | Store sensitive values in Secrets Manager or SSM Parameter Store, because anything in source or plaintext env vars ends up in version control and synthesized templates. |
| Block public access and enforce SSL on S3 | Set `blockPublicAccess: BLOCK_ALL` and `enforceSSL: true`, because the safe posture must be explicit and a forgotten flag can expose a bucket publicly. |
| Encrypt data at rest by default | Use at least `S3_MANAGED` encryption and enable `enableKeyRotation` on symmetric KMS keys, because unencrypted storage and static keys are common audit findings that are cheap to prevent up front. |
| Prefer CDK grant methods over hand written IAM | Use `bucket.grantRead(role)` instead of authoring a `PolicyStatement`, because grants scope actions and resource ARNs correctly and avoid over broad permissions written by hand. |
| Deny by default on security groups | Set `allowAllOutbound: false` with explicit egress rules, because permissive egress is easy to leave in place and widens the blast radius of a compromise. |

## Removal Policies and Stateful Resources

| Practice | Detail |
|---|---|
| Set `removalPolicy` explicitly on stateful resources | Use `RETAIN` in prod and accept `DESTROY` in dev, because relying on the implicit default leaves it ambiguous whether a stack deletion will drop production data. |
| Pair `deletionProtection` with retention in prod | Enable deletion protection on production databases and tables, so an accidental stack or resource deletion is blocked at the AWS layer rather than relying on policy alone. |
| Set `retention` on every LogGroup | CDK defaults log retention to infinite, so an unset retention silently accumulates storage cost forever. |

## Synthesis Discipline

| Practice | Detail |
|---|---|
| Keep `cdk synth` read only | Synthesis must make no AWS API mutations, because side effects during synth make builds nondeterministic and unsafe to run in CI; move runtime mutations into custom resources. |
| Make decisions at synthesis time in TypeScript | Branch with `if`, maps, and loops rather than CloudFormation `Conditions` and `Parameters`, because resolving logic in code produces concrete templates that are far easier to review and test. |
| Commit `cdk.context.json` | Checking in the context cache ensures every machine synthesizes the same template, because uncommitted context can cause CDK to re resolve values and produce a different diff. |

## Verification

| Practice | Detail |
|---|---|
| Do not implement CDK patterns from memory | Confirm construct props and defaults against the official CDK API reference, because the library evolves quickly and recalled props may be wrong or removed in the pinned version. |
| Check the installed `aws-cdk-lib` version first | Read `package.json` before recommending a construct or prop, so you do not suggest something unavailable in the project's version. |
| Flag patterns you cannot verify | State plainly when official docs do not confirm a behavior, because a clearly marked unverified pattern is safer than a confident guess presented as fact. |
