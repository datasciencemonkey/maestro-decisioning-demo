"""Phase 5: DBOS workflow durability tests — requires Lakebase + LLM."""

import json
import os

import psycopg2
import pytest

pytestmark = [pytest.mark.integration]


@pytest.fixture(scope="module")
def db_params():
    """Get Lakebase connection params."""
    for key in list(os.environ):
        if key.startswith("OTEL_"):
            del os.environ[key]

    from maestro.bootstrap import get_lakebase_conn_params
    return get_lakebase_conn_params()


@pytest.fixture(scope="module")
def dbos_setup(db_params):
    """Initialize DBOS with Lakebase for the test module."""
    from urllib.parse import quote_plus

    from dbos import DBOS, DBOSConfig

    host = db_params["host"]
    port = db_params["port"]
    db = db_params["database"]
    user = db_params["user"]
    pw = db_params["password"]
    db_url = f"postgresql://{user}:{quote_plus(pw)}@{host}:{port}/{db}?sslmode=require"

    config = DBOSConfig(
        name="maestro-cdp-test",
        system_database_url=db_url,
        application_database_url=db_url,
    )
    DBOS(config=config)
    DBOS.launch()

    yield DBOS

    DBOS.destroy()


def test_save_and_rehydrate_journey(db_params, dbos_setup):
    """Test that journey state persists and can be rehydrated."""
    from maestro.workflow import (
        rehydrate_journey_step,
        save_journey_step,
        update_journey_status_step,
    )

    journey_id = "jrn_test_workflow_001"
    test_blob = json.dumps({"test": True, "verdict": "re-prioritize"})

    # Save
    result = save_journey_step(
        journey_id=journey_id,
        customer_id="cust_88241",
        step="awaiting_send",
        due_ts="2026-05-10T08:00:00-05:00",
        state_blob=test_blob,
    )
    assert result == journey_id

    # Verify via direct query
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, current_step, status FROM journey_state WHERE journey_id = %s",
        (journey_id,),
    )
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "cust_88241"
    assert row[1] == "awaiting_send"
    assert row[2] == "pending"

    # Rehydrate
    state_json = rehydrate_journey_step(journey_id)
    state = json.loads(state_json)
    assert state["test"] is True
    assert state["verdict"] == "re-prioritize"

    # Update status
    update_journey_status_step(journey_id, "completed")
    cur.execute(
        "SELECT status FROM journey_state WHERE journey_id = %s",
        (journey_id,),
    )
    row = cur.fetchone()
    assert row[0] == "completed"

    # Cleanup
    cur.execute("DELETE FROM journey_state WHERE journey_id = %s", (journey_id,))
    conn.commit()
    cur.close()
    conn.close()


def test_save_decision(db_params, dbos_setup):
    """Test that decision artifact persists to Lakebase."""
    from maestro.workflow import save_decision_step, save_journey_step

    journey_id = "jrn_test_dec_001"
    decision_id = "dec_test_workflow_001"

    # FK: must create journey_state row first (decisions references journey_state)
    save_journey_step(
        journey_id=journey_id,
        customer_id="cust_88241",
        step="awaiting_send",
        due_ts="2026-05-10T08:00:00-05:00",
        state_blob=json.dumps({"test": True}),
    )

    decision = {
        "decision_id": decision_id,
        "customer_id": "cust_88241",
        "journey_id": journey_id,
        "trigger_event_id": "evt_test",
        "verdict": "re-prioritize",
        "decisions": [{"type": "suppress_from", "target": "Spring Seasonal"}],
        "contributing_signals": [{"signal": "freq_cap", "value": "breach", "weight": 1.0}],
        "rationale": "Test rationale",
        "created_at": "2026-05-10T08:00:00-05:00",
    }

    result = save_decision_step(json.dumps(decision), "")
    assert result == decision_id

    # Verify
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        "SELECT verdict, rationale FROM decisions WHERE decision_id = %s",
        (decision_id,),
    )
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "re-prioritize"
    assert row[1] == "Test rationale"

    # Cleanup (decision first due to FK)
    cur.execute("DELETE FROM decisions WHERE decision_id = %s", (decision_id,))
    cur.execute("DELETE FROM journey_state WHERE journey_id = %s", (journey_id,))
    conn.commit()
    cur.close()
    conn.close()
