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
    mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
    mlflow.pydantic_ai.autolog()

    # LLM via AI Gateway (custom endpoint at /ai-gateway/mlflow/v1)
    from openai import AsyncOpenAI

    host = os.environ.get("DATABRICKS_HOST", w.config.host).rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    token = os.environ.get("DATABRICKS_TOKEN", "")
    client = AsyncOpenAI(api_key=token, base_url=f"{host}/ai-gateway/mlflow/v1")
    provider = OpenAIProvider(openai_client=client)
    model = OpenAIChatModel("maestro-endpoint", provider=provider)

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
  <span id="status"></span>

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


@app.get("/health")
async def health():
    """Health check for Databricks Apps."""
    return {"status": "ok", "service": "maestro-cdp"}
