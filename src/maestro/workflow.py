"""Unified DBOS durable workflow for Beat 2 + 2.5 + 3.

Single async workflow orchestrating: agent reasoning -> persist decision ->
durable sleep -> re-evaluate context -> compose email -> simulate send.

The workflow survives process restarts — DBOS checkpoints each step
and persists the sleep wake-up time to Lakebase.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from dbos import DBOS

from maestro.models import CartAbandonedEvent

CT = ZoneInfo("America/Chicago")


def _get_db_params() -> dict:
    """Get Lakebase connection params — env vars (Apps) or SDK (local)."""
    import os
    if os.environ.get("LAKEBASE_PASSWORD"):
        return dict(
            host=os.environ.get("LAKEBASE_HOST", "ep-wispy-bonus-d2qqe068.database.us-east-1.cloud.databricks.com"),
            port=5432,
            database=os.environ.get("LAKEBASE_DATABASE", "maestro_cdp"),
            user=os.environ.get("LAKEBASE_USER", "maestro_app"),
            password=os.environ["LAKEBASE_PASSWORD"],
            sslmode="require",
        )
    from maestro.app import app
    if hasattr(app.state, "db_params") and app.state.db_params:
        return app.state.db_params

    return get_lakebase_conn_params()


# ── Async DBOS Steps (for LLM calls) ──────────────────────────────────────


def _get_model():
    """Get the module-level MODEL from app.py (already initialized)."""
    from maestro.app import MODEL
    return MODEL


@DBOS.step()
async def run_agent_step(event_json: str) -> str:
    """Run the Maestro agent. Returns DecisionArtifact as JSON."""
    from maestro.agent import run_maestro

    event = CartAbandonedEvent.model_validate_json(event_json)
    model = _get_model()
    result = await run_maestro(event, model, None)
    return result.model_dump_json()


@DBOS.step()
async def compose_email_step(artifact_json: str) -> str:
    """Compose personalized email via copywriter agent. Returns EmailContent JSON."""
    from maestro.email_agent import compose_email

    model = _get_model()
    email = await compose_email(artifact_json, model)
    return email.model_dump_json()


# ── Sync DBOS Steps (for DB operations) ───────────────────────────────────


@DBOS.step()
def persist_decision_step(decision_json: str) -> str:
    """Persist DecisionArtifact to Lakebase decisions table."""
    import psycopg2



    decision = json.loads(decision_json)
    decision_id = decision.get("decision_id", f"dec_{uuid.uuid4().hex[:8]}")
    params = get_lakebase_conn_params()

    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO decisions (decision_id, customer_id, journey_id,
            trigger_event_id, verdict, decisions, contributing_signals,
            rationale, trace_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (decision_id) DO UPDATE SET
            verdict = EXCLUDED.verdict,
            decisions = EXCLUDED.decisions,
            contributing_signals = EXCLUDED.contributing_signals,
            rationale = EXCLUDED.rationale""",
        (
            decision_id,
            decision["customer_id"],
            decision.get("journey_id", ""),
            decision.get("trigger_event_id", ""),
            decision["verdict"],
            json.dumps(decision.get("decisions", [])),
            json.dumps(decision.get("contributing_signals", [])),
            decision.get("rationale", ""),
            decision.get("trace_id"),
            decision.get("created_at", datetime.now(CT).isoformat()),
        ),
    )
    cur.close()
    conn.close()
    return decision_id


# Backward-compatible alias
save_decision_step = persist_decision_step


@DBOS.step()
def save_journey_step(
    journey_id: str, customer_id: str, step: str, due_ts: str, state_blob: str,
) -> str:
    """Persist journey state to Lakebase journey_state table."""
    import psycopg2

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
            next_action_due_ts = EXCLUDED.next_action_due_ts,
            state_blob = EXCLUDED.state_blob,
            updated_at = NOW()""",
        (journey_id, customer_id, step, due_ts, state_blob),
    )
    cur.close()
    conn.close()
    return journey_id


@DBOS.step()
def re_evaluate_step(journey_id: str, artifact_json: str) -> str:
    """Re-check context after sleep. Returns ReEvaluationResult as JSON."""
    from maestro.re_evaluate import re_evaluate_context

    result = re_evaluate_context(journey_id, artifact_json)
    return json.dumps(result)


@DBOS.step()
def simulate_send_step(journey_id: str, customer_id: str, email_json: str) -> str:
    """Write to sent_emails table, simulating delivery."""

    from maestro.send import build_send_record, insert_sent_email

    record = build_send_record(journey_id, customer_id, email_json)
    params = get_lakebase_conn_params()
    email_id = insert_sent_email(record, params)
    return email_id


@DBOS.step()
def update_journey_status_step(journey_id: str, status: str) -> str:
    """Update journey_state status."""
    import psycopg2

    params = _get_db_params()
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "UPDATE journey_state SET status = %s, updated_at = NOW() WHERE journey_id = %s",
        (status, journey_id),
    )
    cur.close()
    conn.close()
    return journey_id


@DBOS.step()
def rehydrate_journey_step(journey_id: str) -> str:
    """Read journey state from Lakebase (kept for backward compatibility)."""
    import psycopg2

    params = _get_db_params()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(
        "SELECT state_blob FROM journey_state WHERE journey_id = %s",
        (journey_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise ValueError(f"Journey not found: {journey_id}")
    return json.dumps(row[0]) if isinstance(row[0], dict) else str(row[0])


# ── Unified Async Workflow ─────────────────────────────────────────────────


@DBOS.workflow()
async def unified_journey_workflow(event_json: str, delay_seconds: int = 15) -> str:
    """Complete Beat 2 + 2.5 + 3 workflow (async).

    Steps:
      1. Agent reasoning -> DecisionArtifact
      2. Persist decision to Lakebase
      3. Save journey state
      4. Durable sleep (simulates optimal send window)
      5. Re-evaluate context (check for changes)
      6. Compose email (copywriter agent)
      7. Simulate send (write to sent_emails)

    Returns: JSON dict with journey_id, decision_id, email_id, evaluation
    """
    # ── Step 1: Agent reasoning ────────────────────────────────────────
    decision_json = await run_agent_step(event_json)
    decision = json.loads(decision_json)
    customer_id = decision.get("customer_id", "unknown")

    # ── Step 2: Save journey state (before decision — FK constraint) ──
    journey_id = decision.get(
        "journey_id",
        f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}",
    )
    send_time_decisions = [
        d for d in decision.get("decisions", []) if d.get("type") == "send_time"
    ]
    due_ts = (
        send_time_decisions[0].get("value", datetime.now(CT).isoformat())
        if send_time_decisions
        else datetime.now(CT).isoformat()
    )
    save_journey_step(
        journey_id=journey_id,
        customer_id=customer_id,
        step="awaiting_send",
        due_ts=due_ts,
        state_blob=decision_json,
    )

    # ── Step 3: Persist decision ───────────────────────────────────────
    decision_id = persist_decision_step(decision_json)

    # ── Step 4: Durable sleep ──────────────────────────────────────────
    await DBOS.sleep_async(delay_seconds)

    # ── Step 5: Re-evaluate context ────────────────────────────────────
    eval_json = re_evaluate_step(journey_id, decision_json)
    evaluation = json.loads(eval_json)

    # ── Step 6: Compose email (if proceed/adjust) ──────────────────────
    email_json = None
    email_id = None
    if evaluation["action"] in ("proceed", "adjust"):
        context = (
            decision_json
            if evaluation["action"] == "proceed"
            else evaluation.get("updated_artifact", decision_json)
        )
        email_json = await compose_email_step(context)

        # ── Step 7: Simulate send ──────────────────────────────────────
        email_id = simulate_send_step(journey_id, customer_id, email_json)
        update_journey_status_step(journey_id, "completed")
    else:
        update_journey_status_step(journey_id, "failed")

    return json.dumps({
        "journey_id": journey_id,
        "decision_id": decision_id,
        "email_id": email_id,
        "evaluation": evaluation["action"],
    })


# ── Backward-compatible alias ──────────────────────────────────────────────

journey_workflow = unified_journey_workflow
