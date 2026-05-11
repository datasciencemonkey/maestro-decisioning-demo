"""FastAPI app for the Maestro CDP demo.

DBOS integration follows the correct pattern:
- Workflow/step decorators at module level
- DBOS init in __main__ before uvicorn.run()
- DBOS.start_workflow() for background execution
- All workflow state persists to Lakebase automatically
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg2
from dbos import DBOS, DBOSConfig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="Maestro CDP", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CT = ZoneInfo("America/Chicago")

# ── Model init (lazy, first request) ────────────────────────────────────────

_model_cache = {}


def _get_model():
    if "model" not in _model_cache:
        import mlflow
        from databricks.sdk import WorkspaceClient
        from openai import AsyncOpenAI
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.profiles.openai import OpenAIModelProfile
        from pydantic_ai.providers.openai import OpenAIProvider

        for key in list(os.environ):
            if key.startswith("OTEL_"):
                del os.environ[key]

        db_host = os.environ.get("DATABRICKS_HOST", "")
        if db_host and not db_host.startswith("http"):
            os.environ["DATABRICKS_HOST"] = f"https://{db_host}"

        try:
            w = WorkspaceClient()
        except Exception:
            w = WorkspaceClient(profile="9cefok")

        mlflow.set_tracking_uri("databricks")
        try:
            mlflow.set_experiment("/Shared/maestro-cdp")
        except Exception:
            pass
        mlflow.pydantic_ai.autolog()

        host = os.environ.get("DATABRICKS_HOST", w.config.host).rstrip("/")
        if not host.startswith("http"):
            host = f"https://{host}"
        auth = w.config.authenticate()
        token = auth.get("Authorization", "").replace("Bearer ", "") if isinstance(auth, dict) else ""
        if not token:
            token = os.environ.get("DATABRICKS_TOKEN", "")

        client = AsyncOpenAI(api_key=token, base_url=f"{host}/ai-gateway/mlflow/v1")
        provider = OpenAIProvider(openai_client=client)
        profile = OpenAIModelProfile(openai_supports_strict_tool_definition=False)
        _model_cache["model"] = OpenAIChatModel("maestro-endpoint", provider=provider, profile=profile)
    return _model_cache["model"]


def _get_db_params():
    if "db_params" not in _model_cache:
        from maestro.bootstrap import get_lakebase_conn_params
        _model_cache["db_params"] = get_lakebase_conn_params()
    return _model_cache["db_params"]


# ── DBOS Steps (module level, before DBOS.launch) ──────────────────────────


@DBOS.step()
def persist_journey(journey_id: str, customer_id: str, decision_json: str) -> str:
    """Persist journey state + decision to Lakebase."""
    params = _get_db_params()
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
        (journey_id, customer_id, "awaiting_send",
         "2026-05-10T08:00:00-05:00", decision_json),
    )
    cur.close()
    conn.close()
    return journey_id


@DBOS.step()
def complete_journey(journey_id: str) -> str:
    """Mark journey as completed after sleep."""
    params = _get_db_params()
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


# ── DBOS Workflow (module level) ────────────────────────────────────────────


@DBOS.workflow()
def journey_workflow(journey_id: str, customer_id: str, decision_json: str, delay_seconds: int) -> str:
    """Beat 2+2.5: persist decision → durable sleep → resume → complete.

    This workflow is fully durable — survives process restarts.
    DBOS persists each step's result and the sleep wake-up time to Lakebase.
    """
    # Step 1: Persist to Lakebase
    persist_journey(journey_id, customer_id, decision_json)

    # Step 2: Durable sleep (survives restart)
    DBOS.sleep(delay_seconds)

    # Step 3: Resume and complete
    complete_journey(journey_id)

    return journey_id


# ── HTML UI ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html>
<head>
  <title>Maestro CDP</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #0B2026; color: #F9F7F4; padding: 2rem; max-width: 1200px; margin: 0 auto; }
    h1 { color: #40d1f5; margin-bottom: 0.5rem; }
    .subtitle { color: #8fb5bf; margin-bottom: 2rem; }
    button { color: white; border: none; padding: 0.75rem 2rem;
             border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: 600; }
    button:hover { opacity: 0.9; }
    button:disabled { background: #555; cursor: not-allowed; }
    .btn-red { background: #FF3621; }
    .btn-blue { background: #4462c9; margin-left: 0.5rem; }
    #status { margin: 1rem 0; color: #40d1f5; display: block; }
    .panel { display: grid; grid-template-columns: 240px 1fr 320px; gap: 1rem; margin-top: 1rem; }
    .card { background: #0f2d34; border: 1px solid #1e4f5a; border-radius: 8px; padding: 1rem; }
    .card h3 { color: #40d1f5; margin-bottom: 0.75rem; font-size: 0.9rem; }
    .decision-row { padding: 0.5rem 0; border-bottom: 1px solid #1e4f5a; font-size: 0.85rem; }
    .decision-type { color: #00D4AA; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; }
    .trace-line { padding: 0.4rem 0.6rem; border-left: 3px solid #4462c9; margin: 0.3rem 0;
                  font-size: 0.8rem; background: #0f2d34; border-radius: 0 4px 4px 0; }
    .rationale { background: #143a43; border-radius: 6px; padding: 1rem; margin-top: 1rem;
                 font-size: 0.9rem; line-height: 1.5; }
    .latency { margin-top: 1rem; font-size: 0.9rem; }
    .latency.ok { color: #00D4AA; } .latency.warn { color: #FF8C2A; } .latency.over { color: #FF3621; }
    .wf-step { padding: 0.5rem 0.75rem; border-left: 3px solid #4462c9; margin: 0.4rem 0;
               font-size: 0.85rem; background: #0f2d34; border-radius: 0 4px 4px 0; transition: all 0.3s; }
    .wf-step.done { border-color: #00D4AA; }
    .wf-step.active { border-color: #FF8C2A; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
  </style>
</head>
<body>
  <h1>Maestro CDP</h1>
  <p class="subtitle">Beat 2 — Cross-Campaign Agentic Reasoning</p>
  <button class="btn-red" id="runBtn" onclick="runDemo()">Run Cart Recovery for Cindy</button>
  <button class="btn-blue" id="wfBtn" onclick="runWorkflow()">Run Full Journey (Beat 2+2.5)</button>
  <div id="status"></div>

  <div id="wfTimeline" style="display:none;margin-top:1rem;">
    <div class="card"><h3>Journey Workflow Timeline (DBOS Durable)</h3><div id="wfSteps"></div></div>
  </div>

  <div class="panel" id="results" style="display:none;">
    <div class="card"><h3>Campaigns</h3><div id="campList"></div></div>
    <div class="card"><h3>Reasoning Trace</h3><div id="traceList"></div></div>
    <div class="card"><h3>Decision</h3><div id="decisionContent"></div></div>
  </div>
  <div class="rationale" id="rationaleBox" style="display:none;"><strong>Rationale:</strong><p id="rationaleText"></p></div>
  <div class="latency" id="latencyBox"></div>

<script>
function setStatus(msg) { document.getElementById('status').textContent = msg; }

async function runDemo() {
  const btn = document.getElementById('runBtn');
  btn.disabled = true; setStatus('Agent reasoning...');
  try {
    const res = await fetch('/api/run', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) { setStatus('Error: '+(data.detail||res.statusText)); return; }
    showResults(data);
    setStatus('Done');
  } catch(e) { setStatus('Error: '+e.message); }
  finally { btn.disabled = false; }
}

function showResults(data) {
  document.getElementById('results').style.display = 'grid';
  document.getElementById('rationaleBox').style.display = 'block';
  document.getElementById('campList').innerHTML = (data.campaigns||[]).map(c =>
    `<div class="decision-row">${c.status==='suppressed'?'&#x1F6AB;':c.status==='prioritized'?'&#x2B50;':'&#x2022;'} ${c.name} <span style="color:#8fb5bf">(${c.status})</span></div>`
  ).join('');
  document.getElementById('decisionContent').innerHTML =
    `<div style="font-size:1.2rem;font-weight:700;color:#00D4AA;margin-bottom:0.75rem">${data.artifact.verdict}</div>` +
    (data.artifact.decisions||[]).map(d => `<div class="decision-row"><div class="decision-type">${d.type.replace(/_/g,' ')}</div>${d.target||d.value||''}</div>`).join('');
  document.getElementById('traceList').innerHTML = (data.artifact.contributing_signals||[]).map(s =>
    `<div class="trace-line">${s.signal}: ${JSON.stringify(s.value)} (w=${s.weight})</div>`).join('');
  document.getElementById('rationaleText').textContent = data.artifact.rationale;
  const lat = data.latency_s, el = document.getElementById('latencyBox');
  el.className = 'latency '+(lat<=1.5?'ok':lat<=2.0?'warn':'over');
  el.textContent = `Latency: ${lat.toFixed(2)}s`;
}

async function runWorkflow() {
  const btn = document.getElementById('wfBtn');
  const timeline = document.getElementById('wfTimeline');
  const stepsDiv = document.getElementById('wfSteps');
  btn.disabled = true; timeline.style.display = 'block';
  setStatus('Starting workflow...');

  const steps = [
    {id:'reason', label:'Agent Reasoning', icon:'&#x1F9E0;'},
    {id:'persist', label:'Persist to Lakebase', icon:'&#x1F4BE;'},
    {id:'sleep', label:'Durable Sleep (DBOS)', icon:'&#x1F4A4;'},
    {id:'resume', label:'Resume & Complete', icon:'&#x1F389;'},
  ];
  stepsDiv.innerHTML = steps.map(s => `<div class="wf-step" id="wf-${s.id}">${s.icon} ${s.label}</div>`).join('');

  try {
    // Step 1: Run agent
    document.getElementById('wf-reason').classList.add('active');
    setStatus('[1/4] Agent reasoning...');
    const agentRes = await fetch('/api/run', { method: 'POST' });
    const agentData = await agentRes.json();
    if (!agentRes.ok) { setStatus('Error: '+(agentData.detail||'')); btn.disabled=false; return; }
    document.getElementById('wf-reason').classList.remove('active');
    document.getElementById('wf-reason').classList.add('done');
    showResults(agentData);

    // Step 2: Start DBOS workflow (persist + sleep + resume)
    document.getElementById('wf-persist').classList.add('active');
    setStatus('[2/4] Persisting to Lakebase via DBOS...');
    const wfRes = await fetch('/api/workflow', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({decision: agentData.artifact, delay: 15}),
    });
    const wfData = await wfRes.json();
    if (!wfRes.ok) { setStatus('Error: '+(wfData.detail||'')); btn.disabled=false; return; }
    document.getElementById('wf-persist').classList.remove('active');
    document.getElementById('wf-persist').classList.add('done');

    // Step 3: Poll for sleep + completion
    document.getElementById('wf-sleep').classList.add('active');
    setStatus(`[3/4] DBOS durable sleep (${wfData.delay}s) — workflow ${wfData.workflow_id}`);

    const poll = setInterval(async () => {
      const sr = await fetch(`/api/workflow/${wfData.workflow_id}`);
      const sd = await sr.json();
      if (sd.status === 'SUCCESS') {
        clearInterval(poll);
        document.getElementById('wf-sleep').classList.remove('active');
        document.getElementById('wf-sleep').classList.add('done');
        document.getElementById('wf-resume').classList.add('done');
        setStatus(`Journey ${wfData.journey_id} completed! Verified in Lakebase.`);
        btn.disabled = false;
      } else if (sd.status === 'ERROR') {
        clearInterval(poll);
        setStatus('Workflow failed: ' + (sd.error || ''));
        btn.disabled = false;
      } else {
        setStatus(`[3/4] DBOS sleeping... (${sd.status}) — workflow ${wfData.workflow_id}`);
      }
    }, 2000);
  } catch(e) { setStatus('Error: '+e.message); btn.disabled=false; }
}
</script>
</body>
</html>"""


# ── API Endpoints ───────────────────────────────────────────────────────────

@app.post("/api/run")
async def run_agent():
    """Run Beat 2 agent only — returns decision artifact."""
    import traceback
    from maestro.agent import run_maestro
    from maestro.synthetic import CINDY_CAMPAIGNS, CINDY_EVENT

    model = _get_model()
    start = time.perf_counter()
    try:
        result = await run_maestro(CINDY_EVENT, model)
    except Exception as e:
        elapsed = time.perf_counter() - start
        raise HTTPException(status_code=500, detail=f"Agent failed after {elapsed:.1f}s: {e}\n{traceback.format_exc()[-500:]}")
    elapsed = time.perf_counter() - start

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
def start_dbos_workflow(body: dict):
    """Start DBOS durable workflow: persist → sleep → complete.

    Accepts the decision artifact from /api/run and kicks off
    a background DBOS workflow. Returns workflow_id for polling.
    """
    import uuid

    decision = body.get("decision", {})
    delay = body.get("delay", 15)
    customer_id = decision.get("customer_id", "cust_88241")
    journey_id = decision.get("journey_id", f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}")
    decision_json = json.dumps(decision)

    # Start DBOS workflow in background — returns immediately
    handle = DBOS.start_workflow(journey_workflow, journey_id, customer_id, decision_json, delay)

    return {
        "workflow_id": handle.get_workflow_id(),
        "journey_id": journey_id,
        "delay": delay,
        "status": "started",
    }


@app.get("/api/workflow/{workflow_id}")
def get_workflow_status(workflow_id: str):
    """Poll DBOS workflow status."""
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        status = handle.get_status()
        return {
            "workflow_id": workflow_id,
            "status": status.status if hasattr(status, 'status') else str(status),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "maestro-cdp"}


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from urllib.parse import quote_plus
    from maestro.bootstrap import get_lakebase_conn_params

    params = get_lakebase_conn_params()
    db_url = (
        f"postgresql://{params['user']}:{quote_plus(params['password'])}"
        f"@{params['host']}:{params['port']}/{params['database']}?sslmode=require"
    )
    config = DBOSConfig(
        name="maestro-cdp-app",
        system_database_url=db_url,
        application_database_url=db_url,
    )
    DBOS(config=config)
    DBOS.launch()

    uvicorn.run(app, host="0.0.0.0", port=8080)
