---
name: diagrams-as-code
description: Use this skill when generating architecture, infrastructure, or system
  diagrams as Python code using the diagrams library. Use for cloud architecture diagrams
  (AWS, Azure, GCP), infrastructure diagrams, network topology, Kubernetes diagrams,
  C4 model diagrams, or any visual system diagram expressible as code. Do not use for
  flowcharts, sequence diagrams, or state machines — use Mermaid for those.
---

## Purpose

Generate Python scripts that produce architecture and infrastructure diagrams using the `diagrams` library (https://diagrams.mingrammer.com). The scripts use Python context managers and operator overloading to define nodes, connections, and groupings that render as professional diagrams with provider-specific icons.

Every generated script must be self-contained, runnable with `python <filename>.py`, and produce an image file in the current directory.

## Prerequisites

The `diagrams` library requires both a Python package and a system-level dependency.

**Python package:**

```shell
pip install diagrams
```

**System dependency (Graphviz):**

| Platform        | Command                             |
| --------------- | ----------------------------------- |
| macOS (Homebrew)    | `brew install graphviz`             |
| Ubuntu/Debian       | `sudo apt install graphviz`         |
| Fedora/RHEL         | `sudo dnf install graphviz`         |
| Windows (Chocolatey)| `choco install graphviz`            |

Verify with `dot -V`. Without Graphviz installed, scripts fail at runtime with `ExecutableNotFound: failed to execute 'dot'`.

## Rules

1. **Always set `show=False`** on every `Diagram()` call. The default `show=True` tries to open the image with the OS viewer, which fails in headless and agent environments.

2. **Always assign nodes to variables** when they are referenced in more than one connection. Calling `EC2("web")` twice creates two separate nodes with the same label.

3. **Never connect two lists directly.** `[a, b] >> [c, d]` is not valid Python. Use a single node as an intermediary, or connect individual nodes.

4. **Use parentheses when mixing `-` with `>>` or `<<`.** Python's `-` operator has different precedence than shift operators. `(a >> b) - c` is safe; `a >> b - c` is not.

5. **Prefer `outformat="png"` for general use and `outformat="svg"` for documentation.** For transparent backgrounds in docs, add `graph_attr={"bgcolor": "transparent"}`.

6. **Set an explicit `filename` parameter** to control the output path. Without it, the diagram title is slugified (spaces become underscores, lowercased) and used as the filename.

## Core API

### Diagram

The top-level context manager. Wraps all nodes, clusters, and connections.

```python
from diagrams import Diagram

with Diagram(
    name="My Architecture",       # Title displayed on the diagram and default filename
    filename="my_architecture",   # Output filename without extension
    outformat="png",              # "png", "jpg", "svg", "pdf", "dot", or a list like ["png", "svg"]
    direction="LR",               # "LR" (default), "RL", "TB", "BT"
    show=False,                   # Prevent auto-opening the image
    graph_attr={},                # Graphviz graph-level attributes
    node_attr={},                 # Graphviz node-level attributes
    edge_attr={},                 # Graphviz edge-level attributes
):
    pass
```

### Cluster

Groups nodes visually inside a labeled box. Supports arbitrary nesting.

```python
from diagrams import Cluster, Diagram

with Diagram("Example", show=False):
    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            pass
        with Cluster("Private Subnet"):
            pass
```

Customize appearance with `graph_attr`:

```python
with Cluster("DB Cluster", graph_attr={"bgcolor": "lightblue"}):
    pass
```

### Node

A node represents a system component. The constructor takes a single string label.

```python
from diagrams.aws.compute import EC2

web = EC2("web server")  # Class determines the icon; string is the display label
```

Import path pattern: `diagrams.<provider>.<category>.<ClassName>`

### Connection Operators

| Operator | Meaning          | Example                |
| -------- | ---------------- | ---------------------- |
| `>>`     | Left to right    | `web >> db`            |
| `<<`     | Right to left    | `db << web`            |
| `-`      | Undirected       | `primary - replica`    |

Chaining: `a >> b >> c` creates connections a->b and b->c.

Fan-out to multiple nodes:

```python
ELB("lb") >> [EC2("w1"), EC2("w2"), EC2("w3")] >> RDS("db")
```

### Edge

Customize individual connections with labels, colors, and styles.

```python
from diagrams import Edge

web >> Edge(label="HTTPS", color="darkgreen", style="bold") >> api
primary - Edge(color="brown", style="dotted") - replica
metrics << Edge(color="firebrick", style="dashed") << grafana
```

| Attribute | Values                                        |
| --------- | --------------------------------------------- |
| `label`   | Any string                                    |
| `color`   | Graphviz color name: `"firebrick"`, `"darkgreen"`, `"brown"`, `"black"` |
| `style`   | `"solid"` (default), `"dashed"`, `"dotted"`, `"bold"` |

### Direction and Layout

| Value | Meaning         |
| ----- | --------------- |
| `"LR"` | Left to right (default) |
| `"RL"` | Right to left   |
| `"TB"` | Top to bottom   |
| `"BT"` | Bottom to top   |

Useful `graph_attr` settings:

```python
graph_attr = {
    "fontsize": "45",
    "bgcolor": "transparent",
    "splines": "spline",       # "ortho" for right-angle edges
    "concentrate": "true",     # Merge parallel edges (only with splines=spline)
    "pad": "0.5",
    "nodesep": "0.5",
    "ranksep": "1.0",
}
```

### Output Formats

| Format | Notes                                      |
| ------ | ------------------------------------------ |
| `png`  | Default. Raster.                           |
| `svg`  | Vector. Good for docs and embedding.       |
| `pdf`  | Vector. Good for printing.                 |
| `jpg`  | Raster, lossy.                             |
| `dot`  | Raw Graphviz source. Useful for debugging. |

Generate multiple formats at once: `outformat=["png", "svg"]`

## Provider Quick-Reference

### AWS (`diagrams.aws.*`)

```python
# Compute
from diagrams.aws.compute import EC2, ECS, EKS, Lambda, Fargate, Batch
# Database
from diagrams.aws.database import RDS, Aurora, Dynamodb, ElastiCache, Redshift
# Network
from diagrams.aws.network import ELB, ALB, NLB, CloudFront, Route53, VPC, APIGateway
# Storage
from diagrams.aws.storage import S3, EFS
# Integration
from diagrams.aws.integration import SQS, SNS, Eventbridge, StepFunctions
# Security
from diagrams.aws.security import IAM, Cognito, WAF, KMS, SecretsManager
# Management
from diagrams.aws.management import Cloudwatch, Cloudformation, Cloudtrail
# General
from diagrams.aws.general import Users, Client, User
```

### Azure (`diagrams.azure.*`)

```python
from diagrams.azure.compute import VM, FunctionApps, KubernetesServices, AppServices
from diagrams.azure.database import CosmosDb, SQLDatabases, CacheForRedis
from diagrams.azure.network import LoadBalancers, ApplicationGateway, Firewall, VirtualNetworks, FrontDoors
from diagrams.azure.storage import StorageAccounts, DataLakeStorage
from diagrams.azure.integration import ServiceBus, LogicApps, EventGridTopics, APIManagement
from diagrams.azure.identity import ActiveDirectory, ManagedIdentities
from diagrams.azure.devops import Pipelines, Repos
```

### GCP (`diagrams.gcp.*`)

```python
from diagrams.gcp.compute import AppEngine, ComputeEngine, KubernetesEngine, Functions, Run
from diagrams.gcp.database import Firestore, Memorystore, Spanner, SQL
from diagrams.gcp.network import LoadBalancing, DNS, CDN, Armor, VPC
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.storage import Storage
from diagrams.gcp.security import KeyManagementService, SecretManager
```

### Kubernetes (`diagrams.k8s.*`)

```python
from diagrams.k8s.compute import Pod, Deployment, StatefulSet, ReplicaSet, DaemonSet, Job, Cronjob
from diagrams.k8s.network import Ingress, Service, NetworkPolicy
from diagrams.k8s.storage import PV, PVC, StorageClass
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.podconfig import ConfigMap, Secret
from diagrams.k8s.rbac import ClusterRole, ServiceAccount
from diagrams.k8s.controlplane import APIServer
from diagrams.k8s.infra import ETCD, Master, Node
from diagrams.k8s.group import Namespace
from diagrams.k8s.ecosystem import Helm, Kustomize
```

### On-Premises (`diagrams.onprem.*`)

```python
# Web / Network
from diagrams.onprem.network import Nginx, Apache, Caddy, Haproxy, Traefik, Kong, Envoy, Istio, Consul
# Compute
from diagrams.onprem.compute import Server, Nomad
# Containers
from diagrams.onprem.container import Docker, K3S
# Databases
from diagrams.onprem.database import PostgreSQL, MySQL, MongoDB, Cassandra, CockroachDB, ClickHouse
# In-Memory
from diagrams.onprem.inmemory import Redis, Memcached
# Queues
from diagrams.onprem.queue import Kafka, RabbitMQ, Celery, Nats
# Monitoring
from diagrams.onprem.monitoring import Prometheus, Grafana, Datadog, Splunk, Sentry
# Logging
from diagrams.onprem.logging import Loki, Fluentbit
from diagrams.onprem.aggregator import Fluentd, Vector
# CI/CD
from diagrams.onprem.ci import Jenkins, GithubActions, GitlabCI
from diagrams.onprem.cd import Spinnaker, Tekton
# IaC
from diagrams.onprem.iac import Terraform, Ansible, Pulumi
# GitOps
from diagrams.onprem.gitops import ArgoCD, Flux
# Security
from diagrams.onprem.security import Vault, Trivy
# VCS
from diagrams.onprem.vcs import Git, Github, Gitlab
# Tracing
from diagrams.onprem.tracing import Jaeger, Tempo
# Client
from diagrams.onprem.client import Client, User, Users
# Workflow
from diagrams.onprem.workflow import Airflow, Kubeflow
# Storage
from diagrams.onprem.storage import Ceph
# DNS
from diagrams.onprem.dns import Coredns
# Certificates
from diagrams.onprem.certificates import CertManager, LetsEncrypt
# Analytics
from diagrams.onprem.analytics import Spark, Flink, Trino, Dbt, Metabase, Superset
```

### Generic (`diagrams.generic.*`)

```python
from diagrams.generic.blank import Blank
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL
from diagrams.generic.device import Mobile, Tablet
from diagrams.generic.network import Firewall, Router, Subnet, Switch, VPN
from diagrams.generic.os import Ubuntu, Windows, LinuxGeneral, Android, IOS
from diagrams.generic.place import Datacenter
from diagrams.generic.storage import Storage
from diagrams.generic.virtualization import Vmware, Virtualbox
```

### Programming (`diagrams.programming.*`)

```python
from diagrams.programming.language import Python, Javascript, TypeScript, Go, Rust, Java, Kotlin, Ruby, Bash
from diagrams.programming.framework import React, Angular, Vue, Django, Flask, FastAPI, Spring, NextJs, GraphQL
from diagrams.programming.flowchart import Action, Decision, StartEnd, Database, Document, InputOutput
```

### SaaS (`diagrams.saas.*`)

```python
from diagrams.saas.chat import Slack, Teams, Discord, Telegram
from diagrams.saas.alerting import Pagerduty, Opsgenie
from diagrams.saas.cdn import Cloudflare, Akamai, Fastly
from diagrams.saas.identity import Auth0, Okta
from diagrams.saas.analytics import Snowflake
from diagrams.saas.payment import Stripe
from diagrams.saas.communication import Twilio
```

### Firebase (`diagrams.firebase.*`)

```python
from diagrams.firebase.base import Firebase
from diagrams.firebase.develop import Authentication, Firestore, Functions, Hosting, RealtimeDatabase, Storage
from diagrams.firebase.grow import Messaging, RemoteConfig
from diagrams.firebase.quality import Crashlytics, TestLab
```

### C4 Model (`diagrams.c4`)

C4 nodes use keyword arguments instead of positional labels. Use `Relationship` instead of `Edge`.

```python
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship

with Diagram("C4 Container Diagram", direction="TB", show=False):
    customer = Person(name="Customer", description="A user of the system.")

    with SystemBoundary("My System"):
        api = Container(name="API", technology="Go", description="Handles requests.")
        db = Database(name="Database", technology="PostgreSQL", description="Stores data.")

    external = System(name="Payment Provider", description="Processes payments.", external=True)

    customer >> Relationship("Uses [HTTPS]") >> api
    api >> Relationship("Reads/writes") >> db
    api >> Relationship("Sends requests [HTTPS]") >> external
```

### Custom Nodes (`diagrams.custom`)

Use any local PNG image as a node icon.

```python
from diagrams.custom import Custom

my_service = Custom("My Service", "./path/to/icon.png")
```

## Examples

### Three-Tier Web App

```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Web Service", show=False):
    ELB("lb") >> EC2("web") >> RDS("userdb")
```

### AWS Architecture with Clusters

```python
from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB, Route53

with Diagram("Clustered Web Services", show=False):
    dns = Route53("dns")
    lb = ELB("lb")

    with Cluster("Services"):
        svc_group = [ECS("web1"), ECS("web2"), ECS("web3")]

    with Cluster("DB Cluster"):
        db_primary = RDS("userdb")
        db_primary - [RDS("userdb ro")]

    memcached = ElastiCache("memcached")

    dns >> lb >> svc_group
    svc_group >> db_primary
    svc_group >> memcached
```

### On-Prem with Custom Edges

```python
from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka

with Diagram("On-Prem Platform", show=False):
    ingress = Nginx("ingress")
    metrics = Prometheus("metrics")
    metrics << Edge(color="firebrick", style="dashed") << Grafana("dashboards")

    with Cluster("App Cluster"):
        workers = [Server("app1"), Server("app2"), Server("app3")]

    with Cluster("Cache HA"):
        cache_primary = Redis("session")
        cache_primary - Edge(color="brown", style="dotted") - Redis("replica")

    with Cluster("Database HA"):
        db_primary = PostgreSQL("primary")
        db_primary - Edge(color="brown", style="dotted") - PostgreSQL("replica")

    ingress >> workers
    workers >> Edge(color="black") >> db_primary
    workers >> Edge(color="brown") >> cache_primary
    workers >> Kafka("events")
```

### Kubernetes Deployment

```python
from diagrams import Diagram
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet
from diagrams.k8s.network import Ingress, Service

with Diagram("K8s Pod Exposure", show=False, direction="LR"):
    net = Ingress("domain.com") >> Service("svc")
    net >> [Pod("pod1"), Pod("pod2"), Pod("pod3")] << ReplicaSet("rs") << Deployment("dp") << HPA("hpa")
```

## When to Use This Skill

- Generating architecture or infrastructure diagrams from a description
- Visualizing cloud deployments (AWS, Azure, GCP)
- Documenting Kubernetes cluster topology
- Creating on-premises or hybrid infrastructure diagrams
- Building C4 model diagrams
- Any request that mentions "diagram", "architecture diagram", or "infra diagram" where the output is a visual diagram generated from code

## When NOT to Use This Skill

- Drawing flowcharts, sequence diagrams, or state machines (use Mermaid or PlantUML instead)
- Creating UI mockups or wireframes
- Editing existing image files
- Generating diagrams that do not represent system architecture or infrastructure

