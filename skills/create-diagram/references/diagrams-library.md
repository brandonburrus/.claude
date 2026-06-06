# Python diagrams Library: Architecture and Infrastructure Diagrams

Generates diagrams with provider-specific icons (https://diagrams.mingrammer.com) from Python scripts. Every generated script must be self-contained, runnable with `uv run <filename>.py`, and produce an image file in the current directory.

## Contents

- Prerequisites
- Script template
- Rules
- Finding the right import path
- Core API (Diagram, Cluster, Node, connections, Edge, layout)
- Provider starter reference
- C4 model and custom nodes
- Example

## Prerequisites

The library needs Graphviz at the system level; without it, scripts fail with `ExecutableNotFound: failed to execute 'dot'`. Verify with `dot -V`.

| Platform | Command |
|---|---|
| macOS (Homebrew) | `brew install graphviz` |
| Ubuntu/Debian | `sudo apt install graphviz` |
| Fedora/RHEL | `sudo dnf install graphviz` |
| Windows (Chocolatey) | `choco install graphviz` |

The Python dependency is handled per-script via PEP 723; no pip install needed.

## Script template

Start every generated script from this shape:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = ["diagrams>=0.23"]
# ///
from diagrams import Diagram

with Diagram("Title", filename="output_name", show=False, direction="LR"):
    ...
```

## Rules

1. **Always set `show=False`.** The default tries to open the image in an OS viewer, which fails in headless and agent environments.
2. **Always assign nodes to variables** when referenced in more than one connection. Calling `EC2("web")` twice creates two separate nodes with the same label.
3. **Never connect two lists directly.** `[a, b] >> [c, d]` is not valid; connect through a single intermediary node or connect individual nodes.
4. **Use parentheses when mixing `-` with `>>` or `<<`.** Python operator precedence makes `a >> b - c` parse wrong; `(a >> b) - c` is safe.
5. **Set an explicit `filename`** to control the output path; otherwise the title is slugified into one.
6. **`outformat="png"` for general use, `"svg"` for docs.** For transparent doc backgrounds add `graph_attr={"bgcolor": "transparent"}`.
7. **Never recall import paths from memory.** Resolve anything not in the starter reference below with the finder script (next section). The library has ~2,900 node classes and the casing is not guessable.

## Finding the right import path

A wrong import path is the most common render failure. The starter reference below covers a fraction of the library; for everything else:

```shell
uv run ${CLAUDE_SKILL_DIR}/scripts/find-node.py <term> [<term> ...]
```

`${CLAUDE_SKILL_DIR}` renders as this skill's directory when the skill is invoked; if you are reading this file directly, substitute the directory containing it (one level up).

It searches every node class in the installed library case-insensitively and prints paste-ready imports with exact casing:

```shell
$ uv run ${CLAUDE_SKILL_DIR}/scripts/find-node.py sagemaker cronjob
=== 'sagemaker' : 2 match(es) ===
  from diagrams.aws.ml import Sagemaker
  from diagrams.aws.ml import SagemakerModel
=== 'cronjob' : 1 match(es) ===
  from diagrams.k8s.compute import Cronjob
```

No matches means the node may not exist under that name; retry with a shorter or broader term (`gateway`, `db`) rather than inventing a path. Use the printed import line verbatim.

## Core API

### Diagram

```python
with Diagram(
    name="My Architecture",       # title on the diagram, default filename source
    filename="my_architecture",   # output filename without extension
    outformat="png",              # "png", "jpg", "svg", "pdf", "dot", or a list
    direction="LR",               # "LR" (default), "RL", "TB", "BT"
    show=False,
    graph_attr={}, node_attr={}, edge_attr={},
):
    ...
```

### Cluster

Groups nodes in a labeled box; nests arbitrarily.

```python
with Cluster("VPC"):
    with Cluster("Private Subnet", graph_attr={"bgcolor": "lightblue"}):
        ...
```

### Nodes and connections

Import path pattern: `diagrams.<provider>.<category>.<ClassName>`; the class picks the icon, the string is the label.

| Operator | Meaning | Example |
|---|---|---|
| `>>` | left to right | `web >> db` |
| `<<` | right to left | `db << web` |
| `-` | undirected | `primary - replica` |

Chaining and fan-out:

```python
ELB("lb") >> [EC2("w1"), EC2("w2"), EC2("w3")] >> RDS("db")
```

### Edge

```python
from diagrams import Edge
web >> Edge(label="HTTPS", color="darkgreen", style="bold") >> api
primary - Edge(color="brown", style="dotted") - replica
```

Styles: `"solid"` (default), `"dashed"`, `"dotted"`, `"bold"`. Colors are Graphviz names.

### Layout tuning

```python
graph_attr = {
    "fontsize": "45",
    "bgcolor": "transparent",
    "splines": "spline",      # "ortho" for right-angle edges
    "pad": "0.5", "nodesep": "0.5", "ranksep": "1.0",
}
```

## Provider starter reference

Common, verified imports. A convenience starter set, NOT the full catalog; anything not listed here, and any name you are not certain of, must be resolved with `scripts/find-node.py`. Do not extrapolate new class names from these patterns.

### AWS (`diagrams.aws.*`)

```python
from diagrams.aws.compute import EC2, ECS, EKS, Lambda, Fargate
from diagrams.aws.database import RDS, Aurora, Dynamodb, ElastiCache, Redshift
from diagrams.aws.network import ELB, ALB, CloudFront, Route53, VPC, APIGateway
from diagrams.aws.storage import S3, EFS
from diagrams.aws.integration import SQS, SNS, Eventbridge, StepFunctions
from diagrams.aws.security import IAM, Cognito, WAF, KMS, SecretsManager
from diagrams.aws.management import Cloudwatch, Cloudformation
from diagrams.aws.general import Users, Client, User
```

### Azure (`diagrams.azure.*`)

```python
from diagrams.azure.compute import VM, FunctionApps, KubernetesServices, AppServices
from diagrams.azure.database import CosmosDb, SQLDatabases, CacheForRedis
from diagrams.azure.network import LoadBalancers, ApplicationGateway, Firewall, VirtualNetworks
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.integration import ServiceBus, LogicApps, APIManagement
from diagrams.azure.identity import ActiveDirectory
```

### GCP (`diagrams.gcp.*`)

```python
from diagrams.gcp.compute import AppEngine, ComputeEngine, KubernetesEngine, Functions, Run
from diagrams.gcp.database import Firestore, Memorystore, Spanner, SQL
from diagrams.gcp.network import LoadBalancing, DNS, CDN
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.storage import Storage
```

### Kubernetes (`diagrams.k8s.*`)

```python
from diagrams.k8s.compute import Pod, Deployment, StatefulSet, ReplicaSet, DaemonSet, Job, Cronjob
from diagrams.k8s.network import Ingress, Service, NetworkPolicy
from diagrams.k8s.storage import PV, PVC, StorageClass
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.podconfig import ConfigMap, Secret
from diagrams.k8s.group import Namespace
```

### On-premises (`diagrams.onprem.*`)

```python
from diagrams.onprem.network import Nginx, Haproxy, Traefik, Kong, Istio, Consul
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL, MySQL, MongoDB, Cassandra
from diagrams.onprem.inmemory import Redis, Memcached
from diagrams.onprem.queue import Kafka, RabbitMQ, Celery, Nats
from diagrams.onprem.monitoring import Prometheus, Grafana, Datadog
from diagrams.onprem.ci import Jenkins, GithubActions, GitlabCI
from diagrams.onprem.iac import Terraform, Ansible
from diagrams.onprem.gitops import ArgoCD, Flux
from diagrams.onprem.vcs import Git, Github, Gitlab
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.workflow import Airflow
```

### Generic, programming, SaaS

```python
from diagrams.generic.network import Firewall, Router, Subnet, Switch, VPN
from diagrams.generic.device import Mobile, Tablet
from diagrams.generic.storage import Storage
from diagrams.programming.language import Python, Javascript, TypeScript, Go, Rust, Java
from diagrams.programming.framework import React, Django, Flask, FastAPI, Spring
from diagrams.saas.chat import Slack, Discord
from diagrams.saas.identity import Auth0, Okta
from diagrams.saas.cdn import Cloudflare
```

## C4 model and custom nodes

C4 nodes use keyword arguments and `Relationship` instead of `Edge`:

```python
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship

with Diagram("C4 Container Diagram", direction="TB", show=False):
    customer = Person(name="Customer", description="A user of the system.")
    with SystemBoundary("My System"):
        api = Container(name="API", technology="Go", description="Handles requests.")
        db = Database(name="Database", technology="PostgreSQL", description="Stores data.")
    external = System(name="Payment Provider", external=True)
    customer >> Relationship("Uses [HTTPS]") >> api
    api >> Relationship("Reads/writes") >> db
    api >> Relationship("Sends requests [HTTPS]") >> external
```

Custom nodes use any local PNG as the icon:

```python
from diagrams.custom import Custom
my_service = Custom("My Service", "./path/to/icon.png")
```

## Example

```python
# /// script
# requires-python = ">=3.9"
# dependencies = ["diagrams>=0.23"]
# ///
from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB, Route53

with Diagram("Clustered Web Services", filename="clustered_web", show=False):
    dns = Route53("dns")
    lb = ELB("lb")

    with Cluster("Services"):
        svc_group = [ECS("web1"), ECS("web2"), ECS("web3")]

    with Cluster("DB Cluster"):
        db_primary = RDS("userdb")
        db_primary - Edge(color="brown", style="dotted") - RDS("userdb ro")

    dns >> lb >> svc_group
    svc_group >> db_primary
    svc_group >> ElastiCache("memcached")
```

Render and verify: `uv run clustered_web.py && ls clustered_web.png`, then inspect the image.
