"""Maestro CDP FastAPI app with DBOS durable workflows.

Key pattern from DeepWiki:
- DBOS(fastapi=app, config=config) — handles launch/destroy via middleware
- DBOSAgent wraps the agent for durable execution
- Async endpoints call await dbos_agent.run()
- No manual DBOS.launch() needed — middleware does it
"""

from __future__ import annotations

import json
import os
import time
from urllib.parse import quote_plus

import psycopg2
from dbos import DBOS, DBOSConfig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Fix DATABRICKS_HOST before anything reads it ────────────────────────────
db_host = os.environ.get("DATABRICKS_HOST", "")
if db_host and not db_host.startswith("http"):
    os.environ["DATABRICKS_HOST"] = f"https://{db_host}"
for key in list(os.environ):
    if key.startswith("OTEL_"):
        del os.environ[key]

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Maestro CDP", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── WorkspaceClient (needed by both DBOS config and model init) ────────────
from databricks.sdk import WorkspaceClient

if os.environ.get("DATABRICKS_HOST"):
    _w = WorkspaceClient()
else:
    _w = WorkspaceClient(profile="9cefok")


def _get_db_config():
    """Get DBOS config. Tries SDK auth first, falls back to native Postgres role."""
    # Lakebase endpoint (static — doesn't change)
    pg_host = "ep-wispy-bonus-d2qqe068.database.us-east-1.cloud.databricks.com"
    database = "maestro_cdp"

    # Resolve Lakebase password: direct env var OR Databricks secret scope
    lakebase_pw = os.environ.get("LAKEBASE_PASSWORD")
    if not lakebase_pw:
        try:
            lakebase_pw = _w.secrets.get_secret(scope="sgscope", key="LAKEBASE_PASSWORD").value
            print("Lakebase password loaded from secret scope: sgscope/LAKEBASE_PASSWORD")
        except Exception as e:
            print(f"Failed to read secret sgscope/LAKEBASE_PASSWORD: {e}")

    if lakebase_pw:
        print("Using Lakebase native Postgres role")
        params = dict(
            host=os.environ.get("LAKEBASE_HOST", pg_host),
            port=5432,
            database=os.environ.get("LAKEBASE_DATABASE", database),
            user=os.environ.get("LAKEBASE_USER", "maestro_app"),
            password=lakebase_pw,
            sslmode="require",
        )
    else:
        # Local: use SDK-based auth (profile credentials)
        try:
            params = _get_lakebase_params_sdk()
        except Exception as e:
            print(f"SDK Lakebase auth failed: {e}")
            app.state.db_params = None
            return None

    try:
        db_url = (
            f"postgresql://{params['user']}:{quote_plus(params['password'])}"
            f"@{params['host']}:{params['port']}/{params['database']}?sslmode=require"
        )
        app.state.db_params = params
        return DBOSConfig(
            name="maestro-cdp-app",
            system_database_url=db_url,
            application_database_url=db_url,
        )
    except Exception as e:
        print(f"DBOS init failed: {e}")
        app.state.db_params = None
        return None


def _get_lakebase_params_sdk(database: str = "maestro_cdp") -> dict:
    """Get Lakebase connection params using the Databricks REST API (no CLI needed)."""
    import requests

    host = _w.config.host.rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    headers = _w.config.authenticate()

    project = "maestro-cdp"
    branch_path = f"projects/{project}/branches/production"

    # GET /api/2.0/postgres/{branch_path}/endpoints
    resp = requests.get(
        f"{host}/api/2.0/postgres/{branch_path}/endpoints",
        headers=headers,
    )
    resp.raise_for_status()
    pg_host = resp.json()["endpoints"][0]["status"]["hosts"]["host"]

    # POST /api/2.0/postgres/credentials
    resp = requests.post(
        f"{host}/api/2.0/postgres/credentials",
        headers=headers,
        json={"endpoint": f"{branch_path}/endpoints/primary"},
    )
    resp.raise_for_status()
    token = resp.json()["token"]

    # Get current user
    resp = requests.get(f"{host}/api/2.0/preview/scim/v2/Me", headers=headers)
    resp.raise_for_status()
    user = resp.json()["userName"]

    return dict(host=pg_host, port=5432, database=database,
                user=user, password=token, sslmode="require")


# DBOS integrates with FastAPI — handles launch/destroy via lifespan middleware
_dbos_config = _get_db_config()
if _dbos_config:
    DBOS(fastapi=app, config=_dbos_config)
else:
    print("Running without DBOS — workflow endpoints will be unavailable")


# ── DBOS Steps + Workflow (only if DBOS initialized) ──────────────────────

if _dbos_config:

    @DBOS.step()
    def persist_journey(journey_id: str, customer_id: str, decision_json: str, delay_seconds: int) -> str:
        from datetime import datetime, timedelta, timezone
        # Compute due_ts from now + delay (what DBOS.sleep will wait)
        due_ts = (datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)).isoformat()
        # Also check if decision has a send_time
        try:
            decision = json.loads(decision_json)
            send_times = [d["value"] for d in decision.get("decisions", []) if d.get("type") == "send_time" and d.get("value")]
            if send_times:
                due_ts = send_times[0]
        except Exception:
            pass
        params = app.state.db_params
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO journey_state (journey_id, customer_id, current_step,
                next_action_due_ts, state_blob, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            ON CONFLICT (journey_id) DO UPDATE SET
                current_step = EXCLUDED.current_step,
                next_action_due_ts = EXCLUDED.next_action_due_ts,
                state_blob = EXCLUDED.state_blob, updated_at = NOW()""",
            (journey_id, customer_id, "awaiting_send", due_ts, decision_json),
        )
        cur.close()
        conn.close()
        return journey_id

    @DBOS.step()
    def complete_journey(journey_id: str) -> str:
        params = app.state.db_params
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            "UPDATE journey_state SET status = 'completed', updated_at = NOW() WHERE journey_id = %s",
            (journey_id,),
        )
        cur.close()
        conn.close()
        return journey_id

    @DBOS.workflow()
    def journey_workflow(journey_id: str, customer_id: str, decision_json: str, delay_seconds: int) -> str:
        persist_journey(journey_id, customer_id, decision_json, delay_seconds)
        DBOS.sleep(delay_seconds)
        complete_journey(journey_id)
        return journey_id


# ── Model init (module level — runs before uvicorn, never blocks event loop) ─

from databricks_openai import AsyncDatabricksOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

# Use AsyncDatabricksOpenAI — handles auth (incl. service principal token refresh)
# Override base_url to route through AI Gateway instead of serving-endpoints
_host = os.environ.get("DATABRICKS_HOST", _w.config.host).rstrip("/")
if not _host.startswith("http"):
    _host = f"https://{_host}"

_client = AsyncDatabricksOpenAI(workspace_client=_w)
_client.base_url = f"{_host}/ai-gateway/mlflow/v1"
_provider = OpenAIProvider(openai_client=_client)
_profile = OpenAIModelProfile(openai_supports_strict_tool_definition=False)
MODEL = OpenAIChatModel("maestro-endpoint", provider=_provider, profile=_profile)


# ── API Endpoints ───────────────────────────────────────────────────────────

@app.post("/api/events")
async def receive_event(body: dict):
    """Receive cart_abandoned event from frontend. Bridge to Beat 2."""
    event_type = body.get("event_type")
    if event_type != "cart_abandoned":
        raise HTTPException(status_code=400, detail=f"Unknown event type: {event_type}")
    # Store for the Beat 2 page (in-memory, demo only)
    app.state.last_event = body
    return {"status": "received", "event_type": event_type, "customer_id": body.get("customer_id")}



@app.post("/api/run")
async def run_agent():
    """Run Beat 2 agent — async endpoint, works with DBOS event loop."""
    import traceback
    try:
        from maestro.agent import run_maestro
        from maestro.synthetic import CINDY_CAMPAIGNS, CINDY_EVENT

        start = time.perf_counter()
        result = await run_maestro(CINDY_EVENT, MODEL)
        elapsed = time.perf_counter() - start
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}\n{traceback.format_exc()[-500:]}")

    suppress_targets = {d.target for d in result.decisions if d.type == "suppress_from"}
    prioritize_targets = {d.target for d in result.decisions if d.type == "prioritize_in"}
    campaigns = []
    for c in CINDY_CAMPAIGNS:
        st = c.status
        if c.campaign_id in suppress_targets or c.name in suppress_targets:
            st = "suppressed"
        elif c.campaign_id in prioritize_targets or c.name in prioritize_targets:
            st = "prioritized"
        campaigns.append({"name": c.name, "campaign_id": c.campaign_id, "status": st})

    return {"artifact": result.model_dump(), "campaigns": campaigns, "latency_s": elapsed}


@app.post("/api/workflow")
async def start_unified_workflow(body: dict):
    """Start unified Beat 2+2.5+3 workflow: agent -> persist -> sleep -> re-eval -> email -> send."""
    import random

    from maestro.synthetic import CINDY_EVENT
    from maestro.workflow import unified_journey_workflow

    event_json = CINDY_EVENT.model_dump_json()
    delay = body.get("delay", random.randint(15, 20))

    handle = await DBOS.start_workflow_async(unified_journey_workflow, event_json, delay)
    return {
        "workflow_id": handle.get_workflow_id(),
        "delay": delay,
        "status": "started",
    }


@app.get("/api/workflow/{workflow_id}")
def get_workflow_status(workflow_id: str):
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        status = handle.get_status()
        return {"workflow_id": workflow_id, "status": status.status if hasattr(status, 'status') else str(status)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/workflow/{workflow_id}/phases")
def get_workflow_phases(workflow_id: str):
    """Return phase-level status for the unified workflow.

    Frontend polls this every 2s to drive the auto-cascade UI.
    """
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        status_obj = handle.get_status()
        status = status_obj.status if hasattr(status_obj, 'status') else str(status_obj)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Map DBOS workflow status to phase progression
    phases = {
        "agent": {"status": "pending"},
        "persist": {"status": "pending"},
        "sleep": {"status": "pending"},
        "re_evaluate": {"status": "pending"},
        "email": {"status": "pending"},
        "send": {"status": "pending"},
    }

    if status == "PENDING":
        # Workflow is running — approximate phase from status
        phases["agent"] = {"status": "done"}
        phases["persist"] = {"status": "done"}
        phases["sleep"] = {"status": "active"}
        current_phase = "sleep"
    elif status == "SUCCESS":
        try:
            result_json = handle.get_result()
            result = json.loads(result_json) if isinstance(result_json, str) else result_json
        except Exception:
            result = {}

        for key in phases:
            phases[key] = {"status": "done"}

        phases["re_evaluate"]["data"] = {"action": result.get("evaluation", "proceed")}
        if result.get("email_id"):
            phases["send"]["data"] = {"email_id": result["email_id"]}

        current_phase = "done"
    elif status in ("ERROR", "RETRIES_EXCEEDED"):
        phases["agent"] = {"status": "done"}
        current_phase = "error"
    else:
        current_phase = "unknown"

    return {
        "workflow_id": workflow_id,
        "workflow_status": status,
        "current_phase": current_phase,
        "phases": phases,
    }


@app.get("/api/workflows")
def list_workflows():
    """List recent journey workflows with their status from both tables."""
    if not app.state.db_params:
        raise HTTPException(status_code=503, detail="Lakebase not available")
    conn = psycopg2.connect(**app.state.db_params)
    cur = conn.cursor()
    # Business state
    cur.execute("""
        SELECT journey_id, customer_id, current_step, status,
               created_at, updated_at
        FROM journey_state ORDER BY updated_at DESC LIMIT 10
    """)
    journeys = [
        {"journey_id": r[0], "customer_id": r[1], "step": r[2], "status": r[3],
         "created_at": str(r[4]), "updated_at": str(r[5])}
        for r in cur.fetchall()
    ]
    # DBOS workflow state
    cur.execute("""
        SELECT workflow_uuid, status, name, created_at
        FROM dbos.workflow_status
        WHERE name = 'journey_workflow'
        ORDER BY created_at DESC LIMIT 10
    """)
    workflows = [
        {"workflow_id": r[0], "status": r[1], "name": r[2], "created_at": str(r[3])}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return {"journeys": journeys, "dbos_workflows": workflows}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "maestro-cdp"}


# ── Serve React frontend (SPA catch-all, must be AFTER all API routes) ──────

import pathlib
from fastapi.responses import FileResponse
_frontend_dist = pathlib.Path(__file__).parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    # SPA catch-all: any non-API route serves index.html (React Router handles it)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_frontend_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
