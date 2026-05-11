# Maestro CDP

**One decision. Nine domains. Zero rules engines.**

*Watch an agent think — then act.*

Maestro is an agentic CDP (Customer Data Platform) demo on Databricks. A single AI agent reasons across nine domains to make cross-campaign disposition decisions — suppressing, prioritizing, and scheduling customer outreach in real time.

```
👤  Who are they?
🛒  What did they leave behind?
📅  Can we still ship it?
📢  What campaigns are they in?
⚠️  Would another email breach the cap?
🎫  Any recent complaints?
📊  How likely are they to convert?
⏰  When should we reach out?
💾  Lock the decision — durably.
💤  Wait for the right moment.
📧  Execute — at exactly the right time.
```

*9 domains. 1 judgment call. Durable execution. Delivered on schedule.*

---

## What This Proves

Databricks owns 7 of 8 CDP functions. This demo shows how an **agentic reasoning loop** — not a rules engine, not a pipeline — makes cross-campaign decisions that legacy CDPs structurally cannot replicate.

The agent:
- **Branches** — chooses tool order based on what it learns
- **Reconciles contradictions** — active campaign + frequency cap breach = suppress
- **Applies shortcuts** — skips tools when prior output makes them unnecessary
- **Justifies** — produces human-legible rationale, not templated output

## Architecture

```
Event Trigger (cart_abandoned)
    │
    ▼
Pydantic AI Agent + Skills
    │  9 tools · SkillsCapability · structured output
    │
    ├──► AI Gateway (maestro-endpoint → Claude)
    ├──► MLflow Tracing (auto-captured spans)
    │
    ▼
DBOS on Lakebase
    │  ACID persist · durable sleep · auto-resume
    │
    ▼
Partner ESP (Braze / SendGrid)
    │
    ▼
Unity Catalog Governance
    All tools · All models · All state · Single audit plane
```

## Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | [Pydantic AI](https://pydantic.dev/docs/ai/) with `@agent.tool`, structured `output_type`, `RunContext` |
| Skills | [pydantic-ai-skills](https://github.com/DougTrajano/pydantic-ai-skills) — progressive disclosure |
| LLM Routing | Databricks AI Gateway (`maestro-endpoint`) |
| Observability | MLflow `pydantic_ai.autolog()` — tool calls, tokens, latency |
| Durability | DBOS on Lakebase — ACID state, durable sleep, auto-resume |
| Data | Unity Catalog tables on Databricks |
| App Hosting | Databricks Apps (FastAPI) |
| Package Mgmt | uv |

## Demo Scenario

**Customer:** Cindy (`cust_88241`) — repeat buyer, gold tier, tabby kitten named Whiskers

**Event:** Cart abandoned — "Welcome Home, Whiskers" photo book, $42

**Conflict:** Spring Seasonal Promo queued + email frequency cap 2/week = breach

**Agent Decision:**
- Suppress Spring Seasonal (frequency cap breach — triggered outranks scheduled)
- Prioritize Abandoned Cart Recovery (propensity 0.81)
- Warm tone referencing Whiskers by name
- Send at 8 AM CT (shifted from 11:48 PM for quiet hours)
- Email channel (consented + preferred)
- Persist to Lakebase → durable sleep → execute on schedule

## Quick Start

```bash
# Clone
git clone https://github.com/datasciencemonkey/maestro-decisioning-demo.git
cd maestro-decisioning-demo

# Install
uv sync

# Seed Lakebase tables (requires 9cefok profile)
make seed

# Run tests
make test-local    # 22 tests — models + tools (no network)
make test-dbos     # DBOS workflow: persist → sleep(8s) → resume
make test-dev      # 17 tests — full system against deployed app

# Run locally
uv run uvicorn maestro.app:app --port 8080

# Deploy to Databricks Apps
make deploy
```

## Project Structure

```
src/maestro/
  models.py        # 14 Pydantic models — input events, tool returns, decision artifact
  synthetic.py     # Cindy's demo data — story-coherent across all 9 domains
  tools.py         # 9 async tool functions with synthetic data
  agent.py         # CDP reasoning agent with system prompt
  workflow.py      # DBOS workflow: persist → sleep → resume
  bootstrap.py     # Workspace, MLflow, AI Gateway, Lakebase init
  app.py           # FastAPI app for Databricks Apps

skills/
  cdp-reasoning/   # Domain best practices (freq caps, prioritization, tone)
  automl-propensity/  # AutoML model training stub (Beat 2.5)

data/
  seed_tables.sql  # 9 UC tables, 6 customers
  seed_tables.py   # Lakebase seeder

tests/
  test_models.py   # Schema validation (10 tests)
  test_tools.py    # Tool contracts (12 tests)
  test_agent.py    # Agent integration (4 tests, needs LLM)
  test_workflow.py # DBOS durability (2 tests, needs Lakebase)
  test_system.py   # 5-layer system tests (10 tests)
  test_app_endpoints.py  # Deployed app HTTP tests (7 tests)
```

## Demo Beats

| Beat | What Happens | Duration |
|------|-------------|----------|
| **Beat 1** | Browser — recognize customer, serve personalization | 3:00 |
| **Beat 2** | Reasoning — agent reasons across 9 domains, produces decision | 5:45 |
| **Beat 2.5** | Durability — DBOS persists state, durable sleep, auto-resume | 0:45 |
| **Beat 3** | Activation — personalized email with photo match via partner ESP | 3:30 |

Beat 2 is the only differentiation moment. Everything else sets it up or pays it off.

## App URLs

| Environment | URL |
|------------|-----|
| Databricks App | `https://maestro-cdp-demo-7474645105283837.aws.databricksapps.com` |
| Local Dev | `http://localhost:8080` |
| Workspace | `fevm-serverless-9cefok.cloud.databricks.com` |

## Test Coverage

| Layer | What | Tests |
|-------|------|-------|
| Models + Synthetic | Schema validation, story coherence | 22 |
| AI Gateway | maestro-endpoint connectivity, latency | 3 |
| Tools | All 9 tool contracts | 12 |
| MLflow | Experiment exists, traces captured | 2 |
| App Deploy | Compute active, health, agent endpoint | 7 |
| DBOS Workflow | persist → sleep(8s) → resume → complete | 1 |
| Agent | Suppress, prioritize, rationale, structure | 4 |
| **Total** | | **51** |
