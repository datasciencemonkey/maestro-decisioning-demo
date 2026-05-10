"""Test Lakebase connectivity and DBOS checkpointing."""
import subprocess
import json
import psycopg2
from urllib.parse import quote_plus

PROFILE = "9cefok"
PROJECT = "maestro-cdp"
BRANCH = "production"
ENDPOINT = "primary"
DATABASE = "maestro_cdp"


def get_connection_details():
    """Get Lakebase connection details from Databricks CLI."""
    branch_path = f"projects/{PROJECT}/branches/{BRANCH}"
    endpoint_path = f"{branch_path}/endpoints/{ENDPOINT}"

    host = json.loads(subprocess.run(
        ["databricks", "postgres", "list-endpoints", branch_path,
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True
    ).stdout)[0]["status"]["hosts"]["host"]

    token = json.loads(subprocess.run(
        ["databricks", "postgres", "generate-database-credential", endpoint_path,
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True
    ).stdout)["token"]

    email = json.loads(subprocess.run(
        ["databricks", "current-user", "me",
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True
    ).stdout)["userName"]

    return host, token, email


def test_psycopg2_connection():
    """Test direct psycopg2 connection to Lakebase."""
    print("=== Test 1: psycopg2 connection ===")
    host, token, email = get_connection_details()

    conn = psycopg2.connect(
        host=host, port=5432, database=DATABASE,
        user=email, password=token, sslmode="require"
    )
    cur = conn.cursor()
    cur.execute("SELECT journey_id, customer_id, current_step, status FROM journey_state;")
    rows = cur.fetchall()
    print(f"  Rows in journey_state: {len(rows)}")
    for row in rows:
        print(f"  {row}")
    conn.close()
    print("  PASS\n")


def test_sqlalchemy_connection():
    """Test SQLAlchemy connection to Lakebase."""
    print("=== Test 2: SQLAlchemy connection ===")
    from sqlalchemy import create_engine, text

    host, token, email = get_connection_details()
    url = f"postgresql://{email}:{quote_plus(token)}@{host}:5432/{DATABASE}?sslmode=require"
    engine = create_engine(url)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM journey_state"))
        count = result.scalar()
        print(f"  journey_state row count: {count}")
    print("  PASS\n")


def test_dbos_checkpoint():
    """Test DBOS workflow with Lakebase as the backing store."""
    print("=== Test 3: DBOS checkpointing ===")
    from dbos import DBOS, DBOSConfig, SetWorkflowID
    from sqlalchemy import create_engine, text

    host, token, email = get_connection_details()
    db_url = f"postgresql://{email}:{quote_plus(token)}@{host}:5432/{DATABASE}?sslmode=require"

    config = DBOSConfig(
        name="maestro-cdp",
        system_database_url=db_url,
        application_database_url=db_url,
    )

    DBOS(config=config)

    @DBOS.workflow()
    def persist_journey_workflow(customer_id: str, step: str, due_ts: str, blob: dict) -> str:
        journey_id = f"jrn_{customer_id}_test"
        save_journey_state(journey_id, customer_id, step, due_ts, blob)
        return journey_id

    @DBOS.step()
    def save_journey_state(journey_id, customer_id, step, due_ts, blob):
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO journey_state (journey_id, customer_id, current_step, next_action_due_ts, state_blob, status)
                VALUES (:jid, :cid, :step, :due, CAST(:blob AS jsonb), 'pending')
                ON CONFLICT (journey_id) DO UPDATE SET
                    current_step = :step,
                    next_action_due_ts = :due,
                    state_blob = CAST(:blob AS jsonb),
                    updated_at = NOW()
            """), {
                "jid": journey_id, "cid": customer_id,
                "step": step, "due": due_ts,
                "blob": json.dumps(blob)
            })
            conn.commit()

    DBOS.launch()

    # Run the workflow
    with SetWorkflowID("test-dbos-checkpoint-002"):
        jid = persist_journey_workflow(
            customer_id="cust_test_001",
            step="awaiting_send",
            due_ts="2026-05-10T09:00:00-05:00",
            blob={"test": True, "channel": "email"}
        )

    print(f"  Journey persisted: {jid}")

    # Verify the row exists
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT journey_id, status FROM journey_state WHERE journey_id = :jid"
        ), {"jid": jid})
        row = result.fetchone()
        print(f"  Verified in Lakebase: {row}")

    DBOS.destroy()
    print("  PASS\n")


if __name__ == "__main__":
    test_psycopg2_connection()
    test_sqlalchemy_connection()
    test_dbos_checkpoint()
    print("All tests passed!")
