"""DBOS durable workflow for Beat 2 + 2.5.

Orchestrates: agent reasoning → persist decision → durable sleep → resume.
The workflow survives process restarts — DBOS checkpoints each step and
persists the sleep wake-up time to Lakebase.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from dbos import DBOS

from maestro.models import CartAbandonedEvent, DecisionArtifact

CT = ZoneInfo("America/Chicago")


# ── DBOS Steps (checkpointed, non-deterministic) ───────────────────────────


@DBOS.step()
def run_agent_step(event_json: str, model_name: str = "databricks-claude-sonnet-4-6") -> str:
    """Run the Maestro agent. Checkpointed because LLM calls are non-deterministic.

    Takes and returns JSON strings to avoid DBOS serialization issues
    with complex Pydantic objects.
    """
    import asyncio

    from maestro.agent import run_maestro
    from maestro.bootstrap import bootstrap

    event = CartAbandonedEvent.model_validate_json(event_json)
    model, db_url = bootstrap()
    result = asyncio.get_event_loop().run_until_complete(
        run_maestro(event, model, db_url)
    )
    return result.model_dump_json()


@DBOS.step()
def save_decision_step(decision_json: str, db_url: str) -> str:
    """Persist DecisionArtifact to Lakebase decisions table."""
    import psycopg2

    decision = json.loads(decision_json)
    decision_id = decision.get("decision_id", f"dec_{uuid.uuid4().hex[:8]}")

    from maestro.bootstrap import get_lakebase_conn_params
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


@DBOS.step()
def save_journey_step(
    journey_id: str,
    customer_id: str,
    step: str,
    due_ts: str,
    state_blob: str,
) -> str:
    """Persist journey state to Lakebase journey_state table."""
    import psycopg2

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
            next_action_due_ts = EXCLUDED.next_action_due_ts,
            state_blob = EXCLUDED.state_blob,
            updated_at = NOW()""",
        (journey_id, customer_id, step, due_ts, state_blob),
    )
    cur.close()
    conn.close()
    return journey_id


@DBOS.step()
def update_journey_status_step(journey_id: str, status: str) -> str:
    """Update journey_state status (e.g., pending → completed)."""
    import psycopg2

    from maestro.bootstrap import get_lakebase_conn_params
    params = get_lakebase_conn_params()

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
    """Read journey state from Lakebase and return the state_blob as JSON."""
    import psycopg2

    from maestro.bootstrap import get_lakebase_conn_params
    params = get_lakebase_conn_params()

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


# ── Main Workflow ───────────────────────────────────────────────────────────


@DBOS.workflow()
def journey_workflow(event_json: str, delay_seconds: int = 10) -> str:
    """Beat 2 + 2.5 orchestration workflow.

    1. Run the agent to produce a DecisionArtifact (Beat 2)
    2. Persist decision to Lakebase
    3. Persist journey_state to Lakebase
    4. Durable sleep until send_time (Beat 2.5)
    5. Resume: rehydrate context, mark completed

    Args:
        event_json: CartAbandonedEvent serialized as JSON
        delay_seconds: Seconds to sleep (demo: 10s; real: ~42120s for 11h42m)

    Returns:
        journey_id of the completed journey
    """
    # ── Beat 2: Agent reasoning ─────────────────────────────────────────
    DBOS.write_stream("journey", {
        "type": "agent_started",
        "status": "reasoning",
    })

    decision_json = run_agent_step(event_json)
    decision = json.loads(decision_json)

    DBOS.write_stream("journey", {
        "type": "decision_rendered",
        "verdict": decision.get("verdict"),
        "customer_id": decision.get("customer_id"),
    })

    # ── Persist decision ────────────────────────────────────────────────
    decision_id = save_decision_step(decision_json, "")

    # ── Persist journey state ───────────────────────────────────────────
    journey_id = decision.get("journey_id", f"jrn_{decision.get('customer_id', 'unknown')}_{uuid.uuid4().hex[:6]}")

    # Find send_time from decisions list
    send_time_decisions = [
        d for d in decision.get("decisions", []) if d.get("type") == "send_time"
    ]
    due_ts = send_time_decisions[0]["value"] if send_time_decisions else datetime.now(CT).isoformat()

    save_journey_step(
        journey_id=journey_id,
        customer_id=decision["customer_id"],
        step="awaiting_send",
        due_ts=due_ts,
        state_blob=decision_json,
    )

    DBOS.write_stream("journey", {
        "type": "journey_persisted",
        "journey_id": journey_id,
        "due_ts": due_ts,
        "storage": "DBOS on Lakebase",
    })

    # ── Beat 2.5: Durable sleep ─────────────────────────────────────────
    DBOS.write_stream("journey", {
        "type": "sleep_started",
        "delay_seconds": delay_seconds,
    })

    DBOS.sleep(delay_seconds)

    # ── Resume: rehydrate and execute ───────────────────────────────────
    DBOS.write_stream("journey", {
        "type": "journey_resumed",
        "journey_id": journey_id,
    })

    state_json = rehydrate_journey_step(journey_id)

    # Mark completed (Beat 3 would trigger email send here)
    update_journey_status_step(journey_id, "completed")

    DBOS.write_stream("journey", {
        "type": "decision_executed",
        "journey_id": journey_id,
        "status": "completed",
    })
    DBOS.close_stream("journey")

    return journey_id
