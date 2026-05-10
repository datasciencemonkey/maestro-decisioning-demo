# Maestro — Agentic CDP Demo

## Project Overview

Maestro is an agentic CDP (Customer Data Platform) demo showcasing cross-campaign optimization and personalized customer engagement on Databricks. The demo follows a customer ("Cindy") through a Shutterfly-like retail journey:

1. **In-Browser Identification & NBA** — Recognize Cindy in real-time, serve Next Best Action recommendations, detect cart abandonment
2. **Cross-Campaign Optimization** — Agent aggregates customer data, prioritizes campaigns (e.g., abandoned cart over seasonal promo), removes customer from lower-priority campaigns
3. **Personalized Outreach** — Agent triggers segment-of-1 email via partner API with personalized content (e.g., matching cat photos)

### Tech Stack
- **Pydantic AI** — Agent framework (`@agent.tool`, structured `output_type`, `RunContext` deps injection, async-first)
- **MLflow** — Tracing via `mlflow.pydantic_ai.autolog()` (auto-captures tool calls, LLM requests, tokens, latency, MCP ops). No Logfire.
- **MLflow ResponsesAgent** — Wrapping for AI Playground, Agent Eval, Agent Monitoring
- **DBOS on Lakebase** — Durable execution (no external Postgres)
- **UC Functions + MCP** — Tool governance
- **Foundation Models via AI Gateway** — Claude for reasoning (Llama as documented alt)
- **Mosaic AI Vector Search** — Auto-synced from Delta (Beat 1/3 multimodal)
- **Databricks Apps** — UI hosting
- **Databricks** — Data + compute platform (all customer + measurement data ingested here)
- **uv** — Python package/project management

### Assumptions
- All customer data + measurement data are ingested into Databricks
- Agent loop is the core artifact of the demo

### Infrastructure (Verified)
- **Workspace:** `fevm-serverless-9cefok.cloud.databricks.com` (profile: `9cefok`)
- **Lakebase project:** `maestro-cdp` → database `maestro_cdp`
- **Lakebase endpoint:** `ep-wispy-bonus-d2qqe068.database.us-east-1.cloud.databricks.com`
- **Tables:** `journey_state`, `decisions` (created)
- **DBOS:** System tables migrated, checkpointing verified on Lakebase
- **LLM routing:** `databricks-openai` → `AsyncDatabricksOpenAI` → `OpenAIProvider` → Pydantic AI
- **Model:** `databricks-claude-sonnet-4-6` via AI Gateway
- **Tracing:** `mlflow.pydantic_ai.autolog()` — auto-captures tool calls, LLM requests, tokens
- **MLflow experiment:** `/Users/sathish.gangichetty@databricks.com/maestro-cdp` on 9cefok

## Current Focus: Beat 2 — Cross-Campaign Agentic Reasoning

Beat 2 is the demo's only differentiation moment. Build it first; everything else gates on it.

### What We're Building
A single Pydantic AI supervisor agent that, given a `cart_abandoned` event, reasons across 9 domains and produces a structured decision within 1.5s target / 2.0s ceiling.

### 3 Required Outputs
1. **MLflow trace** — readable by a non-technical viewer as intelligent reasoning
2. **Decision artifact** — structured JSON persisted to Lakebase + Delta mirror
3. **Journey state row** — DBOS-persisted for Beat 2.5 resumption

### 9 Tools (Pydantic AI `@agent.tool`)
| Tool | Source |
|---|---|
| `read_profile(customer_id)` | UC `customers` |
| `read_cart(customer_id)` | UC `orders` + `order_items` |
| `check_production_feasibility(product_id, ship_by)` | UC `production_calendar` |
| `list_active_campaigns(customer_id)` | UC `campaigns` + `campaign_membership` |
| `check_frequency_cap(customer_id, channel, window_days)` | UC `campaigns` aggregation |
| `read_support_tickets(customer_id, lookback_days)` | UC `support_tickets` |
| `score_propensity(customer_id, intent)` | Model Serving endpoint |
| `optimal_send_time(customer_id, cohort, propensity)` | Model output / service |
| `persist_journey_state(customer_id, step, due_ts, blob)` | Writes to Lakebase via DBOS |

### Demo Scenario (Cindy)
- **Customer:** Cindy (`cust_88241`), tabby kitten "Whiskers", repeat buyer, `America/Chicago`
- **Cart:** "Welcome Home" photo book, $42, abandoned
- **Conflict:** Spring Seasonal promo queued + frequency cap 2/week = breach
- **Expected decision:** Suppress Spring Seasonal, prioritize Abandoned Cart Recovery, warm tone with Whiskers context, email at 8 AM CT, email channel

### Acceptance Criteria (non-negotiable)
The agent must demonstrably:
1. **Branch** — choose tool order based on prior outputs (not a fixed sequence)
2. **Reconcile contradictions** — active campaign + frequency cap breach = suppress
3. **Apply shortcuts** — skip tools when prior output makes them unnecessary
4. **Justify** — human-legible `rationale` in the decision artifact

**Auto-block:** trace looks scripted, decision looks templated, latency >2.5s, reviewer calls it "function-calling LLM with extra steps"

### Week 1 Substrate (build first — agent loop depends on these)
1. **`journey_state` table** in Lakebase — schema + example row + query notebook
2. **9 Pydantic tool contracts** — typed inputs/outputs, MLflow-traced, callable standalone
3. **DBOS workflow** — `persist_journey_state` decorated function, unit test proving state survives restart

### UI (Marketing Ops Panel — 3 regions)
- **Left (~240px):** Campaign list with animated states (flagged → suppressed → prioritized)
- **Center (flexible):** Reasoning trace streaming with customer summary card
- **Right (~320px):** Decision panel — verdict + 5 decision rows + persistence card

### Reference Files
- `files/beat-2-build-brief.md` — Full build brief with schemas and acceptance criteria
- `files/fluttershy-demo-design-doc.md` — Phase A locked script with beat-level detail
- `files/fluttershy-demo-spec.md` — Strategic spec (tiering, build plan, tool appendix)
- `files/00-README.md` — Handoff index and key decisions

### Bootstrap (copy into any new script)

```python
import os
for key in list(os.environ):  # Clear stale OTEL env vars
    if key.startswith("OTEL_"):
        del os.environ[key]

import mlflow
from databricks.sdk import WorkspaceClient
from databricks_openai import AsyncDatabricksOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# Workspace + MLflow
w = WorkspaceClient(profile="9cefok")
os.environ["DATABRICKS_HOST"] = w.config.host
os.environ["DATABRICKS_TOKEN"] = w.config.authenticate()["Authorization"].replace("Bearer ", "")
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
mlflow.pydantic_ai.autolog()

# LLM via AI Gateway
client = AsyncDatabricksOpenAI(workspace_client=w)
provider = OpenAIProvider(openai_client=client)
model = OpenAIChatModel("databricks-claude-sonnet-4-6", provider=provider)

# Lakebase connection helper
import subprocess, json
from urllib.parse import quote_plus

def get_lakebase_url(database="maestro_cdp"):
    host = json.loads(subprocess.run(
        ["databricks", "postgres", "list-endpoints",
         "projects/maestro-cdp/branches/production",
         "--profile", "9cefok", "--output", "json"],
        capture_output=True, text=True).stdout)[0]["status"]["hosts"]["host"]
    token = json.loads(subprocess.run(
        ["databricks", "postgres", "generate-database-credential",
         "projects/maestro-cdp/branches/production/endpoints/primary",
         "--profile", "9cefok", "--output", "json"],
        capture_output=True, text=True).stdout)["token"]
    email = json.loads(subprocess.run(
        ["databricks", "current-user", "me",
         "--profile", "9cefok", "--output", "json"],
        capture_output=True, text=True).stdout)["userName"]
    return f"postgresql://{email}:{quote_plus(token)}@{host}:5432/{database}?sslmode=require"

# DBOS init
from dbos import DBOS, DBOSConfig
db_url = get_lakebase_url()
DBOS(config=DBOSConfig(name="maestro-cdp", system_database_url=db_url, application_database_url=db_url))
```

## Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root — use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- Keep files under 500 lines
- Validate input at system boundaries

## Behavioral Guidelines (Karpathy-style)

### 1. Think Before Coding
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.

### 2. Simplicity First
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes
- Don't "improve" adjacent code, comments, or formatting.
- Match existing style, even if you'd do it differently.
- Remove imports/variables/functions that YOUR changes made unused.
- Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution
- Transform tasks into verifiable goals with success criteria.
- For multi-step tasks, state a brief plan with verification checks.
- Loop until verified. Weak criteria require clarification before implementation.
- ALWAYS write a test to check functionality after implementation.
- ALWAYS validate any implemented functionality works before claiming completion.

## Agent Comms (SendMessage-First Coordination)

Named agents coordinate via `SendMessage`, not polling or shared state.

```
Lead (you) ←→ architect ←→ developer ←→ tester ←→ reviewer
              (named agents message each other directly)
```

### Spawning a Coordinated Team

```javascript
// ALL agents in ONE message, each knows WHO to message next
Agent({ prompt: "Research the codebase. SendMessage findings to 'architect'.",
  subagent_type: "researcher", name: "researcher", run_in_background: true })
Agent({ prompt: "Wait for 'researcher'. Design solution. SendMessage to 'coder'.",
  subagent_type: "system-architect", name: "architect", run_in_background: true })
Agent({ prompt: "Wait for 'architect'. Implement it. SendMessage to 'tester'.",
  subagent_type: "coder", name: "coder", run_in_background: true })
Agent({ prompt: "Wait for 'coder'. Write tests. SendMessage results to 'reviewer'.",
  subagent_type: "tester", name: "tester", run_in_background: true })
Agent({ prompt: "Wait for 'tester'. Review code quality and security.",
  subagent_type: "reviewer", name: "reviewer", run_in_background: true })

// Kick off the pipeline
SendMessage({ to: "researcher", summary: "Start", message: "[task context]" })
```

### Patterns

| Pattern | Flow | Use When |
|---------|------|----------|
| **Pipeline** | A → B → C → D | Sequential dependencies (feature dev) |
| **Fan-out** | Lead → A, B, C → Lead | Independent parallel work (research) |
| **Supervisor** | Lead ↔ workers | Ongoing coordination (complex refactor) |

### Rules

- ALWAYS name agents — `name: "role"` makes them addressable
- ALWAYS include comms instructions in prompts — who to message, what to send
- Spawn ALL agents in ONE message with `run_in_background: true`
- After spawning: STOP, tell user what's running, wait for results
- NEVER poll status — agents message back or complete automatically

## Swarm & Routing

### Config
- **Topology**: hierarchical-mesh (anti-drift)
- **Max Agents**: 15
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

```bash
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

### Agent Routing

| Task | Agents | Topology |
|------|--------|----------|
| Bug Fix | researcher, coder, tester | hierarchical |
| Feature | architect, coder, tester, reviewer | hierarchical |
| Refactor | architect, coder, reviewer | hierarchical |
| Performance | perf-engineer, coder | hierarchical |
| Security | security-architect, auditor | hierarchical |

### When to Swarm
- **YES**: 3+ files, new features, cross-module refactoring, API changes, security, performance
- **NO**: single file edits, 1-2 line fixes, docs updates, config changes, questions

### 3-Tier Model Routing

| Tier | Handler | Use Cases |
|------|---------|-----------|
| 1 | Agent Booster (WASM) | Simple transforms — skip LLM, use Edit directly |
| 2 | Haiku | Simple tasks, low complexity |
| 3 | Sonnet/Opus | Architecture, security, complex reasoning |

## Memory & Learning

### Before Any Task
```bash
npx @claude-flow/cli@latest memory search --query "[task keywords]" --namespace patterns
npx @claude-flow/cli@latest hooks route --task "[task description]"
```

### After Success
```bash
npx @claude-flow/cli@latest memory store --namespace patterns --key "[name]" --value "[what worked]"
npx @claude-flow/cli@latest hooks post-task --task-id "[id]" --success true --store-results true
```

### MCP Tools (use `ToolSearch("keyword")` to discover)

| Category | Key Tools |
|----------|-----------|
| **Memory** | `memory_store`, `memory_search`, `memory_search_unified` |
| **Bridge** | `memory_import_claude`, `memory_bridge_status` |
| **Swarm** | `swarm_init`, `swarm_status`, `swarm_health` |
| **Agents** | `agent_spawn`, `agent_list`, `agent_status` |
| **Hooks** | `hooks_route`, `hooks_post-task`, `hooks_worker-dispatch` |
| **Security** | `aidefence_scan`, `aidefence_is_safe`, `aidefence_has_pii` |
| **Hive-Mind** | `hive-mind_init`, `hive-mind_consensus`, `hive-mind_spawn` |

### Background Workers

| Worker | When |
|--------|------|
| `audit` | After security changes |
| `optimize` | After performance work |
| `testgaps` | After adding features |
| `map` | Every 5+ file changes |
| `document` | After API changes |

```bash
npx @claude-flow/cli@latest hooks worker dispatch --trigger audit
```

## Agents

**Core**: `coder`, `reviewer`, `tester`, `planner`, `researcher`
**Architecture**: `system-architect`, `backend-dev`, `mobile-dev`
**Security**: `security-architect`, `security-auditor`
**Performance**: `performance-engineer`, `perf-analyzer`
**Coordination**: `hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`
**GitHub**: `pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`

Any string works as a custom agent type.

## Build & Test

- ALWAYS run tests after code changes
- ALWAYS verify build succeeds before committing

```bash
npm run build && npm test
```

## CLI Quick Reference

```bash
npx @claude-flow/cli@latest init --wizard           # Setup
npx @claude-flow/cli@latest swarm init --v3-mode     # Start swarm
npx @claude-flow/cli@latest memory search --query "" # Vector search
npx @claude-flow/cli@latest hooks route --task ""    # Route to agent
npx @claude-flow/cli@latest doctor --fix             # Diagnostics
npx @claude-flow/cli@latest security scan            # Security scan
npx @claude-flow/cli@latest performance benchmark    # Benchmarks
```

26 commands, 140+ subcommands. Use `--help` on any command for details.

## Setup

```bash
claude mcp add claude-flow -- npx -y @claude-flow/cli@latest
npx @claude-flow/cli@latest daemon start
npx @claude-flow/cli@latest doctor --fix
```

**Agent tool** handles execution (agents, files, code, git). **MCP tools** handle coordination (swarm, memory, hooks). **CLI** is the same via Bash.
