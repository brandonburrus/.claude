# Brandons Cowork Skills

![Brandons Cowork Skills icon](color.png)

Twelve of Brandon's personal skills, packaged as a Microsoft 365 Copilot
Cowork plugin: agentic research, writing, discovery, and design workflows. Structured as a standard M365 App Package (the same distribution
mechanism as Teams apps), so the `skills/` directory is also a valid GitHub
Copilot CLI / Claude Code plugin via `.claude-plugin/plugin.json`.

```
brandons-cowork-skills/
├── manifest.json              # M365 Unified App Manifest (v1.28), Cowork's format
├── color.png                  # 192x192 full-color icon
├── outline.png                # 32x32 white-on-transparent icon
├── brandons-cowork-skills.zip # packaged app, ready to sideload/upload
├── .claude-plugin/
│   └── plugin.json            # GitHub Copilot CLI / Claude Code manifest
└── skills/                    # Agent Skills (SKILL.md), shared by both formats
```

## Install into Cowork

1. Rebuild the zip after any change (must contain `manifest.json`, `color.png`,
   `outline.png`, and `skills/` at the zip root, not nested in a folder):

   ```shell
   zip -rq -X brandons-cowork-skills.zip manifest.json color.png outline.png skills/
   ```
2. Validate before uploading:

   ```shell
   atk validate --package-file ./brandons-cowork-skills.zip --validate-method validation-rules
   ```
3. Sideload for personal testing with the Microsoft 365 Agents Toolkit CLI:

   ```shell
   npm install -g @microsoft/m365agentstoolkit-cli
   atk auth login
   atk install --file-path "./brandons-cowork-skills.zip" --scope Personal
   ```

   Or publish tenant-wide via **M365 admin center > Manage apps > Upload
   custom app > Add agent**, then find it in **Cowork > Sources & Skills >
   Plugins**.

## Install into GitHub Copilot CLI / Claude Code

From a local checkout:

```shell
copilot plugin install /path/to/brandons-cowork-skills
```

Verify with `copilot plugin list`, then `/skills list` in an interactive
session to confirm all twelve skills loaded.

## Skills

| Skill | Purpose |
|---|---|
| `check-comprehension` | Verifies real understanding through interactive quizzing and restatement, for learning a concept or reviewing a change. |
| `design` | Builds and styles UI: components, pages, dashboards, and frontend polish. |
| `estimate-at-scale` | Produces order-of-magnitude cost, storage, or capacity estimates from rough scale parameters. |
| `humanize` | Edits text to remove AI-writing tells so it reads as natural, human-written prose. |
| `interrogate` | Interrogates a vague or underspecified request until scope is fully defined and user-confirmed. |
| `research-build-vs-buy` | Decides whether to build a capability in-house or adopt a product, and which one. |
| `research-solutions` | Decides among technical approaches and the specific dev tool that implements one. |
| `spec` | Writes product specs, tech specs, ADRs, and system design consults (API, schema, CI/CD, and more). |
| `scrutinize` | Scrutinizes a plan's premise and end-to-end path from an outsider's perspective before trusting it. |
| `teach-through-writing` | Writes tutorials, explainers, and onboarding docs that teach from first principles. |
| `visualize-data` | Builds interactive data visualizations and dashboards with marimo, Streamlit, or D3. |
| `analyze-data` | Analyzes, aggregates, and plots tabular data from CSV, Excel, JSON, Parquet, or SQLite. |

## Source of truth

Each skill here is a snapshot copy from the [`brandonburrus/.claude`](https://github.com/brandonburrus/.claude)
`skills/` library. To pick up upstream changes, re-copy the relevant skill
directory, bump `version` in both `manifest.json` and `.claude-plugin/plugin.json`,
and rebuild the zip.
