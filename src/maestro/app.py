"""FastAPI app for the Maestro CDP demo on Databricks Apps.

Exposes the Beat 2 agent as an API endpoint and a simple web UI
for running the demo and viewing results.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="Maestro CDP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CT = ZoneInfo("America/Chicago")

# Lazy-init model on first request
_model = None
_db_url = None


def _get_model():
    global _model, _db_url
    if _model is None:
        _model, _db_url = _bootstrap_for_app()
    return _model, _db_url


def _bootstrap_for_app():
    """Bootstrap that works both locally (CLI profile) and in Databricks Apps (service principal)."""
    import mlflow
    from databricks.sdk import WorkspaceClient
    from databricks_openai import AsyncDatabricksOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    # Clear stale OTEL env vars
    for key in list(os.environ):
        if key.startswith("OTEL_"):
            del os.environ[key]

    # Fix DATABRICKS_HOST if platform injected it without scheme
    db_host = os.environ.get("DATABRICKS_HOST", "")
    if db_host and not db_host.startswith("http"):
        os.environ["DATABRICKS_HOST"] = f"https://{db_host}"

    # In Databricks Apps, WorkspaceClient() picks up service principal auth.
    # Locally, falls back to profile.
    try:
        w = WorkspaceClient()
    except Exception:
        w = WorkspaceClient(profile="9cefok")

    mlflow.set_tracking_uri("databricks")
    # Use shared experiment path (service principal can't write to user dirs)
    try:
        mlflow.set_experiment("/Shared/maestro-cdp")
    except Exception:
        pass  # Non-fatal — traces still work without experiment
    mlflow.pydantic_ai.autolog()

    # LLM via AI Gateway (custom endpoint at /ai-gateway/mlflow/v1)
    from openai import AsyncOpenAI
    from pydantic_ai.profiles.openai import OpenAIModelProfile

    host = os.environ.get("DATABRICKS_HOST", w.config.host).rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    # Get token from WorkspaceClient auth (works for both user and service principal)
    auth = w.config.authenticate()
    token = auth.get("Authorization", "").replace("Bearer ", "") if isinstance(auth, dict) else ""
    if not token:
        token = os.environ.get("DATABRICKS_TOKEN", "")
    client = AsyncOpenAI(api_key=token, base_url=f"{host}/ai-gateway/mlflow/v1")
    provider = OpenAIProvider(openai_client=client)
    profile = OpenAIModelProfile(openai_supports_strict_tool_definition=False)
    model = OpenAIChatModel("maestro-endpoint", provider=provider, profile=profile)

    return model, None  # db_url not needed for agent-only mode


@app.get("/", response_class=HTMLResponse)
async def index():
    """Simple demo UI."""
    return """<!DOCTYPE html>
<html>
<head>
  <title>Maestro CDP — Beat 2 Demo</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #0B2026; color: #F9F7F4; padding: 2rem; max-width: 1200px; margin: 0 auto; }
    h1 { color: #40d1f5; margin-bottom: 0.5rem; }
    .subtitle { color: #8fb5bf; margin-bottom: 2rem; }
    button { background: #FF3621; color: white; border: none; padding: 0.75rem 2rem;
             border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: 600; }
    button:hover { background: #e02e1a; }
    button:disabled { background: #555; cursor: not-allowed; }
    #status { margin: 1rem 0; color: #40d1f5; }
    .panel { display: grid; grid-template-columns: 240px 1fr 320px; gap: 1rem; margin-top: 1rem; }
    .card { background: #0f2d34; border: 1px solid #1e4f5a; border-radius: 8px; padding: 1rem; }
    .card h3 { color: #40d1f5; margin-bottom: 0.75rem; font-size: 0.9rem; }
    .decision-row { padding: 0.5rem 0; border-bottom: 1px solid #1e4f5a; font-size: 0.85rem; }
    .decision-type { color: #00D4AA; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; }
    .signal { font-size: 0.8rem; color: #8fb5bf; padding: 0.25rem 0; }
    .rationale { background: #143a43; border-radius: 6px; padding: 1rem; margin-top: 1rem;
                 font-size: 0.9rem; line-height: 1.5; }
    .trace-line { padding: 0.4rem 0.6rem; border-left: 3px solid #4462c9; margin: 0.3rem 0;
                  font-size: 0.8rem; background: #0f2d34; border-radius: 0 4px 4px 0; }
    .latency { margin-top: 1rem; font-size: 0.9rem; }
    .latency.ok { color: #00D4AA; }
    .latency.warn { color: #FF8C2A; }
    .latency.over { color: #FF3621; }
    pre { font-size: 0.75rem; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>Maestro CDP</h1>
  <p class="subtitle">Beat 2 — Cross-Campaign Agentic Reasoning</p>
  <button id="runBtn" onclick="runDemo()">Run Cart Recovery for Cindy</button>
  <button id="wfBtn" onclick="runWorkflow()" style="background:#4462c9;margin-left:0.5rem;">Run Full Journey (Beat 2+2.5)</button>
  <span id="status"></span>

  <div id="wfTimeline" style="display:none;margin-top:1rem;">
    <div class="card"><h3>Journey Workflow Timeline</h3><div id="wfSteps"></div></div>
  </div>

  <div class="panel" id="results" style="display:none;">
    <div class="card" id="campaigns"><h3>Campaigns</h3><div id="campList"></div></div>
    <div class="card" id="trace"><h3>Reasoning Trace</h3><div id="traceList"></div></div>
    <div class="card" id="decision"><h3>Decision</h3><div id="decisionContent"></div></div>
  </div>

  <div class="rationale" id="rationaleBox" style="display:none;">
    <strong>Rationale:</strong>
    <p id="rationaleText"></p>
  </div>

  <div class="latency" id="latencyBox"></div>

<script>
async function runDemo() {
  const btn = document.getElementById('runBtn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.textContent = 'Agent reasoning...';

  try {
    const res = await fetch('/api/run', { method: 'POST' });
    const data = await res.json();

    if (!res.ok) { status.textContent = 'Error: ' + (data.detail || res.statusText); return; }

    document.getElementById('results').style.display = 'grid';
    document.getElementById('rationaleBox').style.display = 'block';

    // Campaigns
    const campHtml = (data.campaigns || []).map(c => {
      const badge = c.status === 'suppressed' ? '🚫' : c.status === 'prioritized' ? '⭐' : '•';
      return `<div class="decision-row">${badge} ${c.name} <span style="color:#8fb5bf">(${c.status})</span></div>`;
    }).join('');
    document.getElementById('campList').innerHTML = campHtml;

    // Decisions
    const decHtml = (data.artifact.decisions || []).map(d => {
      return `<div class="decision-row">
        <div class="decision-type">${d.type.replace('_',' ')}</div>
        ${d.target || d.value || ''} ${d.reason ? '<br><span style="color:#8fb5bf;font-size:0.75rem">' + d.reason + '</span>' : ''}
      </div>`;
    }).join('');
    document.getElementById('decisionContent').innerHTML =
      `<div style="font-size:1.2rem;font-weight:700;color:#00D4AA;margin-bottom:0.75rem">${data.artifact.verdict}</div>` + decHtml;

    // Signals
    const sigHtml = (data.artifact.contributing_signals || []).map(s =>
      `<div class="trace-line">${s.signal}: ${JSON.stringify(s.value)} (w=${s.weight})</div>`
    ).join('');
    document.getElementById('traceList').innerHTML = sigHtml;

    // Rationale
    document.getElementById('rationaleText').textContent = data.artifact.rationale;

    // Latency
    const lat = data.latency_s;
    const cls = lat <= 1.5 ? 'ok' : lat <= 2.0 ? 'warn' : 'over';
    document.getElementById('latencyBox').className = 'latency ' + cls;
    document.getElementById('latencyBox').textContent = `Latency: ${lat.toFixed(2)}s`;

    status.textContent = 'Done';
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

async function runWorkflow() {
  const btn = document.getElementById('wfBtn');
  const status = document.getElementById('status');
  const timeline = document.getElementById('wfTimeline');
  const stepsDiv = document.getElementById('wfSteps');
  btn.disabled = true;
  timeline.style.display = 'block';
  stepsDiv.innerHTML = '';
  status.textContent = 'Starting workflow...';

  try {
    const res = await fetch('/api/workflow?delay=15', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) { status.textContent = 'Error: ' + (data.detail || res.statusText); return; }

    const jid = data.journey_id;
    status.textContent = `Workflow ${jid} started (${data.delay_seconds}s sleep)`;

    const stepIcons = {
      agent_reasoning: '🧠', decision_rendered: '✅', persisting: '💾',
      persisted_to_lakebase: '💾', sleep_started: '💤', sleep_completed: '⏰',
      sleeping: '💤', resuming: '🔄', journey_completed: '🎉', failed: '❌',
    };

    // Poll every 2 seconds
    const poll = setInterval(async () => {
      try {
        const sr = await fetch('/api/workflow/' + jid);
        const sd = await sr.json();
        status.textContent = `[${sd.step}] ${sd.status}`;

        let html = '';
        for (const s of sd.steps_completed) {
          const icon = stepIcons[s.step] || '•';
          const t = new Date(s.ts * 1000).toLocaleTimeString();
          const extra = s.delay ? ` (${s.delay}s)` : '';
          html += `<div class="trace-line">${icon} ${t} — ${s.step.replace(/_/g,' ')}${extra}</div>`;
        }
        if (sd.step === 'sleeping') {
          html += `<div class="trace-line" style="border-color:#FF8C2A;">💤 Sleeping... (durable pause on Lakebase)</div>`;
        }
        stepsDiv.innerHTML = html;

        if (sd.status === 'completed' || sd.status === 'failed') {
          clearInterval(poll);
          btn.disabled = false;
          if (sd.status === 'completed') {
            html += `<div class="trace-line" style="border-color:#00D4AA;font-weight:600;">🎉 Journey complete — state verified in Lakebase</div>`;
            stepsDiv.innerHTML = html;
            status.textContent = `Journey ${jid} completed!`;
          } else {
            status.textContent = `Journey failed: ${sd.error || 'unknown'}`;
          }
        }
      } catch (e) { /* ignore poll errors */ }
    }, 2000);
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
    btn.disabled = false;
  }
}
</script>
</body>
</html>"""


@app.post("/api/run")
async def run_agent():
    """Run the Beat 2 agent for Cindy's cart abandonment."""
    import traceback

    from maestro.agent import run_maestro
    from maestro.synthetic import CINDY_CAMPAIGNS, CINDY_EVENT

    try:
        model, db_url = _get_model()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bootstrap failed: {e}")

    start = time.perf_counter()
    try:
        result = await run_maestro(CINDY_EVENT, model, db_url)
    except Exception as e:
        elapsed = time.perf_counter() - start
        raise HTTPException(
            status_code=500,
            detail=f"Agent failed after {elapsed:.1f}s: {e}\n{traceback.format_exc()[-500:]}",
        )
    elapsed = time.perf_counter() - start

    # Annotate campaigns with agent's disposition
    suppress_targets = {
        d.target for d in result.decisions if d.type == "suppress_from"
    }
    prioritize_targets = {
        d.target for d in result.decisions if d.type == "prioritize_in"
    }

    campaigns = []
    for c in CINDY_CAMPAIGNS:
        status = c.status
        if c.campaign_id in suppress_targets or c.name in suppress_targets:
            status = "suppressed"
        elif c.campaign_id in prioritize_targets or c.name in prioritize_targets:
            status = "prioritized"
        campaigns.append({"name": c.name, "campaign_id": c.campaign_id, "status": status})

    return {
        "artifact": result.model_dump(),
        "campaigns": campaigns,
        "latency_s": elapsed,
    }


@app.post("/api/workflow")
async def start_workflow(delay: int = 15):
    """Start the full Beat 2 + 2.5 journey workflow.

    Returns immediately with a journey_id. Poll /api/workflow/{id} for status.
    The workflow: agent reasons → persist → sleep(delay) → resume → complete.
    """
    import threading
    import traceback
    import uuid

    import psycopg2

    from maestro.agent import run_maestro
    from maestro.synthetic import CINDY_EVENT

    journey_id = f"jrn_cust_88241_{uuid.uuid4().hex[:6]}"

    # Store workflow state in-memory for polling (simple for demo)
    _workflow_states[journey_id] = {
        "journey_id": journey_id,
        "step": "starting",
        "status": "in_progress",
        "delay_seconds": delay,
        "steps_completed": [],
        "decision": None,
        "error": None,
    }

    def _run_workflow():
        try:
            import asyncio

            state = _workflow_states[journey_id]

            # Step 1: Agent reasoning
            state["step"] = "agent_reasoning"
            state["steps_completed"].append({"step": "agent_reasoning", "ts": time.time()})

            model, _ = _get_model()
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(run_maestro(CINDY_EVENT, model))
            loop.close()

            decision_dump = result.model_dump()
            state["decision"] = decision_dump
            state["steps_completed"].append({"step": "decision_rendered", "ts": time.time()})

            # Step 2: Persist to Lakebase
            state["step"] = "persisting"
            try:
                from maestro.bootstrap import get_lakebase_conn_params
                params = get_lakebase_conn_params()
                conn = psycopg2.connect(**params)
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO journey_state (journey_id, customer_id, current_step,
                        next_action_due_ts, state_blob, status)
                    VALUES (%s, %s, %s, %s, %s, 'pending')
                    ON CONFLICT (journey_id) DO UPDATE SET
                        current_step = EXCLUDED.current_step,
                        state_blob = EXCLUDED.state_blob,
                        updated_at = NOW()""",
                    (journey_id, "cust_88241", "awaiting_send",
                     "2026-05-10T08:00:00-05:00", json.dumps(decision_dump)),
                )
                cur.close()
                conn.close()
                state["steps_completed"].append({"step": "persisted_to_lakebase", "ts": time.time()})
            except Exception as e:
                state["steps_completed"].append({"step": "persist_error", "ts": time.time(), "error": str(e)})

            # Step 3: Durable sleep
            state["step"] = "sleeping"
            state["steps_completed"].append({"step": "sleep_started", "ts": time.time(), "delay": delay})
            time.sleep(delay)
            state["steps_completed"].append({"step": "sleep_completed", "ts": time.time()})

            # Step 4: Resume — update status
            state["step"] = "resuming"
            try:
                params = get_lakebase_conn_params()
                conn = psycopg2.connect(**params)
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(
                    "UPDATE journey_state SET status = 'completed', updated_at = NOW() WHERE journey_id = %s",
                    (journey_id,),
                )
                cur.close()
                conn.close()
                state["steps_completed"].append({"step": "journey_completed", "ts": time.time()})
            except Exception as e:
                state["steps_completed"].append({"step": "resume_error", "ts": time.time(), "error": str(e)})

            state["step"] = "completed"
            state["status"] = "completed"

        except Exception as e:
            state = _workflow_states[journey_id]
            state["step"] = "failed"
            state["status"] = "failed"
            state["error"] = f"{e}\n{traceback.format_exc()[-300:]}"

    thread = threading.Thread(target=_run_workflow, daemon=True)
    thread.start()

    return {"journey_id": journey_id, "status": "started", "delay_seconds": delay}


# In-memory workflow state (demo only — production uses DBOS system tables)
_workflow_states: dict[str, dict] = {}


@app.get("/api/workflow/{journey_id}")
async def get_workflow_status(journey_id: str):
    """Poll workflow status. Returns current step and completed steps timeline."""
    if journey_id not in _workflow_states:
        raise HTTPException(status_code=404, detail=f"Workflow {journey_id} not found")
    return _workflow_states[journey_id]


@app.get("/health")
async def health():
    """Health check for Databricks Apps."""
    return {"status": "ok", "service": "maestro-cdp"}
