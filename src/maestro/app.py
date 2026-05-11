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
from fastapi.responses import HTMLResponse

# ── Fix DATABRICKS_HOST before anything reads it ────────────────────────────
db_host = os.environ.get("DATABRICKS_HOST", "")
if db_host and not db_host.startswith("http"):
    os.environ["DATABRICKS_HOST"] = f"https://{db_host}"
for key in list(os.environ):
    if key.startswith("OTEL_"):
        del os.environ[key]

# ── App + DBOS init ─────────────────────────────────────────────────────────
app = FastAPI(title="Maestro CDP", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _get_db_config():
    """Get DBOS config. Returns None if Lakebase CLI not available (e.g., Databricks Apps)."""
    try:
        from maestro.bootstrap import get_lakebase_conn_params
        params = get_lakebase_conn_params()
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
        print(f"DBOS init skipped (Lakebase creds unavailable): {e}")
        app.state.db_params = None
        return None


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

from databricks.sdk import WorkspaceClient
from databricks_openai import AsyncDatabricksOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

# In Databricks Apps: WorkspaceClient() uses service principal (DATABRICKS_HOST is set)
# Locally: use profile
if os.environ.get("DATABRICKS_HOST"):
    _w = WorkspaceClient()
else:
    _w = WorkspaceClient(profile="9cefok")

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


# ── HTML UI ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html><head><title>Maestro CDP</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0B2026;color:#F9F7F4;padding:2rem;max-width:1200px;margin:0 auto}
h1{color:#40d1f5;margin-bottom:.5rem}.subtitle{color:#8fb5bf;margin-bottom:2rem}
button{color:white;border:none;padding:.75rem 2rem;border-radius:6px;cursor:pointer;font-size:1rem;font-weight:600}
button:hover{opacity:.9}button:disabled{background:#555;cursor:not-allowed}
.btn-red{background:#FF3621}.btn-blue{background:#4462c9;margin-left:.5rem}
#status{margin:1rem 0;color:#40d1f5;display:block}
.panel{display:grid;grid-template-columns:240px 1fr 320px;gap:1rem;margin-top:1rem}
.card{background:#0f2d34;border:1px solid #1e4f5a;border-radius:8px;padding:1rem}
.card h3{color:#40d1f5;margin-bottom:.75rem;font-size:.9rem}
.decision-row{padding:.5rem 0;border-bottom:1px solid #1e4f5a;font-size:.85rem}
.decision-type{color:#00D4AA;font-weight:600;text-transform:uppercase;font-size:.75rem}
.trace-line{padding:.4rem .6rem;border-left:3px solid #4462c9;margin:.3rem 0;font-size:.8rem;background:#0f2d34;border-radius:0 4px 4px 0}
.rationale{background:#143a43;border-radius:6px;padding:1rem;margin-top:1rem;font-size:.9rem;line-height:1.5}
.latency{margin-top:1rem;font-size:.9rem}.latency.ok{color:#00D4AA}.latency.warn{color:#FF8C2A}.latency.over{color:#FF3621}
.wf-step{padding:.5rem .75rem;border-left:3px solid #4462c9;margin:.4rem 0;font-size:.85rem;background:#0f2d34;border-radius:0 4px 4px 0;transition:all .3s}
.wf-step.done{border-color:#00D4AA}.wf-step.active{border-color:#FF8C2A;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
</style></head><body>
<h1>Maestro CDP</h1>
<p class="subtitle">Beat 2 — Cross-Campaign Agentic Reasoning</p>
<button class="btn-red" id="runBtn" onclick="runDemo()">Run Cart Recovery for Cindy</button>
<button class="btn-blue" id="wfBtn" onclick="runWorkflow()">Run Full Journey (Beat 2+2.5)</button>
<div id="status"></div>
<div id="wfTimeline" style="display:none;margin-top:1rem"><div class="card"><h3>Journey Workflow Timeline (DBOS Durable)</h3><div id="wfSteps"></div></div></div>
<div class="panel" id="results" style="display:none">
<div class="card"><h3>Campaigns</h3><div id="campList"></div></div>
<div class="card"><h3>Reasoning Trace</h3><div id="traceList"></div></div>
<div class="card"><h3>Decision</h3><div id="decisionContent"></div></div>
</div>
<div class="rationale" id="rationaleBox" style="display:none"><strong>Rationale:</strong><p id="rationaleText"></p></div>
<div class="latency" id="latencyBox"></div>
<script>
function setStatus(m){document.getElementById('status').textContent=m}
async function runDemo(){
  const btn=document.getElementById('runBtn');btn.disabled=true;setStatus('Agent reasoning (~30s)...');
  try{const r=await fetch('/api/run',{method:'POST'});const d=await r.json();
  if(!r.ok){setStatus('Error: '+(d.detail||r.statusText));return}showResults(d);setStatus('Done');}
  catch(e){setStatus('Error: '+e.message)}finally{btn.disabled=false}}
function showResults(data){
  document.getElementById('results').style.display='grid';document.getElementById('rationaleBox').style.display='block';
  document.getElementById('campList').innerHTML=(data.campaigns||[]).map(c=>'<div class="decision-row">'+(c.status==='suppressed'?'&#x1F6AB;':c.status==='prioritized'?'&#x2B50;':'&#x2022;')+' '+c.name+' <span style="color:#8fb5bf">('+c.status+')</span></div>').join('');
  document.getElementById('decisionContent').innerHTML='<div style="font-size:1.2rem;font-weight:700;color:#00D4AA;margin-bottom:.75rem">'+data.artifact.verdict+'</div>'+(data.artifact.decisions||[]).map(d=>'<div class="decision-row"><div class="decision-type">'+d.type.replace(/_/g,' ')+'</div>'+(d.target||d.value||'')+'</div>').join('');
  document.getElementById('traceList').innerHTML=(data.artifact.contributing_signals||[]).map(s=>'<div class="trace-line">'+s.signal+': '+JSON.stringify(s.value)+' (w='+s.weight+')</div>').join('');
  document.getElementById('rationaleText').textContent=data.artifact.rationale;
  const lat=data.latency_s,el=document.getElementById('latencyBox');el.className='latency '+(lat<=1.5?'ok':lat<=2.0?'warn':'over');el.textContent='Latency: '+lat.toFixed(2)+'s'}
async function runWorkflow(){
  const btn=document.getElementById('wfBtn'),tl=document.getElementById('wfTimeline'),sd=document.getElementById('wfSteps');
  btn.disabled=true;tl.style.display='block';
  sd.innerHTML=['&#x1F9E0; Agent Reasoning','&#x1F4BE; Persist to Lakebase','&#x1F4A4; Durable Sleep (DBOS)','&#x1F389; Resume & Complete'].map((s,i)=>'<div class="wf-step" id="wf-'+i+'">'+s+'</div>').join('');
  setStatus('[1/4] Agent reasoning (~30s)...');document.getElementById('wf-0').classList.add('active');
  try{const ar=await fetch('/api/run',{method:'POST'});const ad=await ar.json();
  if(!ar.ok){setStatus('Error: '+(ad.detail||''));btn.disabled=false;return}
  document.getElementById('wf-0').classList.replace('active','done');showResults(ad);
  setStatus('[2/4] Starting DBOS workflow...');document.getElementById('wf-1').classList.add('active');
  const wr=await fetch('/api/workflow',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({decision:ad.artifact,delay:15})});
  const wd=await wr.json();if(!wr.ok){setStatus('Error: '+(wd.detail||''));btn.disabled=false;return}
  document.getElementById('wf-1').classList.replace('active','done');
  document.getElementById('wf-2').classList.add('active');setStatus('[3/4] DBOS durable sleep (15s) — wf:'+wd.workflow_id);
  const poll=setInterval(async()=>{try{const s=await(await fetch('/api/workflow/'+wd.workflow_id)).json();
  if(s.status==='SUCCESS'){clearInterval(poll);document.getElementById('wf-2').classList.replace('active','done');
  document.getElementById('wf-3').classList.add('done');setStatus('Journey '+wd.journey_id+' completed!');btn.disabled=false}
  }catch(e){}},2000);
  }catch(e){setStatus('Error: '+e.message);btn.disabled=false}}
</script></body></html>"""


# ── API Endpoints ───────────────────────────────────────────────────────────

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
def start_dbos_workflow(body: dict):
    """Start DBOS durable workflow: persist -> sleep -> complete."""
    import uuid
    decision = body.get("decision", {})
    delay = body.get("delay", 15)
    customer_id = decision.get("customer_id", "cust_88241")
    journey_id = decision.get("journey_id", f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}")

    handle = DBOS.start_workflow(journey_workflow, journey_id, customer_id, json.dumps(decision), delay)
    return {"workflow_id": handle.get_workflow_id(), "journey_id": journey_id, "delay": delay, "status": "started"}


@app.get("/api/workflow/{workflow_id}")
def get_workflow_status(workflow_id: str):
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        status = handle.get_status()
        return {"workflow_id": workflow_id, "status": status.status if hasattr(status, 'status') else str(status)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
