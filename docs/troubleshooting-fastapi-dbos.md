# Troubleshooting: FastAPI + DBOS + Pydantic AI Agent

## The Problem
The `/api/run` endpoint (which calls the Pydantic AI agent) blocks the FastAPI/uvicorn async event loop, making `/health` and all other endpoints unresponsive until the agent call completes (~30s).

## What Works
1. **Agent standalone** (`run_maestro_sync` in a plain script): 25-29s, correct verdict ✅
2. **Agent + DBOS standalone** (both in same script, no FastAPI): 25s, correct verdict ✅  
3. **DBOS workflow via FastAPI** (`/api/workflow`): persist → sleep → complete, SUCCESS ✅
4. **Health endpoint**: instant when no agent call running ✅
5. **AI Gateway**: `maestro-endpoint` responds in 1.5-2s for simple prompts ✅

## What Fails
- `/api/run` as `async def` → `_get_model()` does sync `subprocess.run()` calls inside async endpoint, blocks event loop
- `/api/run` as `def` (sync) with `run_maestro_sync` → `agent.run_sync()` calls `asyncio.run()` internally, deadlocks with DBOS's event loop
- `/api/run` as `def` (sync) with `asyncio.run(run_maestro(...))` → same deadlock
- Module-level model init → slow startup (subprocess + DBOS init), server takes >60s to become ready

## Root Cause Analysis
The conflict is between three async/sync boundaries:
1. **uvicorn** runs an asyncio event loop
2. **DBOS** manages its own event loop (via `DBOS(fastapi=app)` LifespanMiddleware)
3. **Pydantic AI `agent.run()`** is async, uses `AsyncOpenAI` client
4. **`_get_model()`** does sync `subprocess.run()` for Lakebase credentials

The problem: you can't call sync blocking code (subprocess) inside an async endpoint without blocking the loop, AND you can't call `asyncio.run()` inside a thread when another loop is running.

## DeepWiki Findings
From DeepWiki (pydantic/pydantic-ai + dbos-inc/dbos-transact-py):
- Use `DBOS(fastapi=app, config=config)` — LifespanMiddleware handles launch/destroy
- Use `async def` endpoints with `await dbos_agent.run(prompt)`
- `DBOSAgent` wraps agent for durable execution
- DBOS integrates with uvicorn's event loop — no conflict

## What Hasn't Been Tried
1. Move ALL sync subprocess calls (`get_lakebase_conn_params`) to **environment variables** set before app starts — eliminate subprocess entirely from runtime
2. Use `DBOSAgent` wrapper properly with `await dbos_agent.run()` in async endpoint
3. Cache Lakebase creds in env vars from `__main__` before `uvicorn.run()`
4. Use `asyncio.to_thread()` ONLY for `_get_model()` on first call, then cache

## Key Files
- `src/maestro/app.py` — FastAPI app
- `src/maestro/agent.py` — Agent definition with `run_maestro()` (async) and `run_maestro_sync()`
- `src/maestro/bootstrap.py` — `get_lakebase_conn_params()` with subprocess calls
- `src/maestro/tools.py` — 9 tool functions (all async, but just dict lookups)

## Infrastructure
- Workspace: fevm-serverless-9cefok.cloud.databricks.com (profile: 9cefok)
- Lakebase: maestro-cdp project, maestro_cdp database
- AI Gateway: maestro-endpoint at /ai-gateway/mlflow/v1
- DBOS: v2.19.0 on Lakebase
