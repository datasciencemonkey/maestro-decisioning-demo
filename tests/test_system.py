"""Systematic system tests covering all 5 layers of the Maestro CDP demo.

Layer 1: AI Gateway — can we hit databricks-claude-sonnet-4-6?
Layer 2: Tool calls — do all 9 tools respond correctly?
Layer 3: MLflow traces — do traces land in the configured experiment?
Layer 4: App deployment — is the Databricks App serving?
Layer 5: DBOS workflow — persist, sleep(8s), resume, verify state

Run:
    uv run pytest tests/test_system.py -v -s
    uv run pytest tests/test_system.py -v -s -k "gateway"   # just layer 1
    uv run pytest tests/test_system.py -v -s -k "workflow"  # just layer 5
"""

import asyncio
import json
import os
import time

import psycopg2
import pytest

pytestmark = pytest.mark.integration

# ── Shared fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def workspace():
    """Authenticated workspace client."""
    for key in list(os.environ):
        if key.startswith("OTEL_"):
            del os.environ[key]

    from databricks.sdk import WorkspaceClient
    return WorkspaceClient(profile="9cefok")


@pytest.fixture(scope="module")
def model(workspace):
    """AI Gateway model via custom maestro-endpoint."""
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    from pydantic_ai.profiles.openai import OpenAIModelProfile

    host = workspace.config.host.rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    token = workspace.config.authenticate()["Authorization"].replace("Bearer ", "")
    client = AsyncOpenAI(api_key=token, base_url=f"{host}/ai-gateway/mlflow/v1")
    provider = OpenAIProvider(openai_client=client)
    profile = OpenAIModelProfile(openai_supports_strict_tool_definition=False)
    return OpenAIChatModel("maestro-endpoint", provider=provider, profile=profile)


@pytest.fixture(scope="module")
def db_params():
    """Lakebase connection params."""
    from maestro.bootstrap import get_lakebase_conn_params
    return get_lakebase_conn_params()


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 1: AI Gateway
# ═══════════════════════════════════════════════════════════════════════════


class TestLayer1Gateway:
    """Verify we can hit the databricks-claude-sonnet-4-6 on AI Gateway."""

    def test_gateway_endpoint_exists(self, workspace):
        """The maestro-endpoint AI Gateway endpoint is accessible."""
        from openai import OpenAI

        host = workspace.config.host.rstrip("/")
        if not host.startswith("http"):
            host = f"https://{host}"
        token = workspace.config.authenticate()["Authorization"].replace("Bearer ", "")
        client = OpenAI(api_key=token, base_url=f"{host}/ai-gateway/mlflow/v1")
        r = client.chat.completions.create(
            model="maestro-endpoint",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        assert r.choices[0].message.content is not None
        print(f"  maestro-endpoint responded: {r.choices[0].message.content[:20]}")

    @pytest.mark.asyncio
    async def test_gateway_responds(self, model):
        """A simple prompt returns a response through AI Gateway."""
        from pydantic_ai import Agent

        agent = Agent(model, instructions="Reply with exactly: GATEWAY_OK")
        result = await agent.run("Test")
        assert result.output is not None
        print(f"  Gateway response: {result.output[:50]}")

    @pytest.mark.asyncio
    async def test_gateway_latency(self, model):
        """Measure round-trip latency to AI Gateway."""
        from pydantic_ai import Agent

        agent = Agent(model, instructions="Reply with one word: OK")
        start = time.perf_counter()
        await agent.run("Ping")
        elapsed = time.perf_counter() - start
        print(f"  Gateway latency: {elapsed:.2f}s")
        assert elapsed < 30, f"Gateway latency too high: {elapsed:.1f}s"


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 2: Tool calls (all 9 tools respond correctly)
# ═══════════════════════════════════════════════════════════════════════════


class TestLayer2Tools:
    """Verify all 9 tools return valid typed responses for Cindy."""

    @pytest.mark.asyncio
    async def test_all_tools_respond(self):
        """Call each tool and verify return type is correct."""
        from maestro import tools

        results = {}
        results["profile"] = await tools.read_profile("cust_88241")
        assert results["profile"].name == "Cindy Chen"

        results["cart"] = await tools.read_cart("cust_88241")
        assert results["cart"].total == 42.00

        results["feasibility"] = await tools.check_production_feasibility(
            "pb_welcome_home_24pp", "2026-05-15"
        )
        assert results["feasibility"].feasible is True

        results["campaigns"] = await tools.list_active_campaigns("cust_88241")
        assert len(results["campaigns"]) == 4

        results["cap"] = await tools.check_frequency_cap("cust_88241", "email", 7)
        assert results["cap"].status == "breach"

        results["tickets"] = await tools.read_support_tickets("cust_88241", 30)
        assert results["tickets"] == []

        results["propensity"] = await tools.score_propensity("cust_88241", "cart_recovery")
        assert results["propensity"].score == 0.81

        results["send_time"] = await tools.optimal_send_time(
            "cust_88241", "morning_engaged", 0.81
        )
        assert results["send_time"].optimal_ts.hour == 8

        results["persist"] = await tools.persist_journey_state(
            "cust_88241", "awaiting_send", "2026-05-10T08:00:00-05:00", {"test": True}
        )
        assert results["persist"].status == "pending"

        print(f"  All 9 tools responded correctly")
        for name, r in results.items():
            print(f"    {name}: {type(r).__name__}")


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 3: MLflow traces
# ═══════════════════════════════════════════════════════════════════════════


class TestLayer3Traces:
    """Verify traces land in the configured MLflow experiment."""

    def test_mlflow_experiment_exists(self, workspace):
        """The maestro-cdp experiment exists on the workspace."""
        os.environ.setdefault("DATABRICKS_HOST", workspace.config.host)
        token = workspace.config.authenticate().get("Authorization", "").replace("Bearer ", "")
        if token:
            os.environ.setdefault("DATABRICKS_TOKEN", token)

        import mlflow
        mlflow.set_tracking_uri("databricks")
        exp = mlflow.get_experiment_by_name(
            "/Users/sathish.gangichetty@databricks.com/maestro-cdp"
        )
        assert exp is not None, "MLflow experiment not found"
        print(f"  Experiment ID: {exp.experiment_id}")

    @pytest.mark.asyncio
    async def test_trace_captured_after_agent_run(self, model):
        """Run the agent and verify a trace appears in MLflow."""
        import mlflow

        os.environ.setdefault("DATABRICKS_HOST",
            os.environ.get("DATABRICKS_HOST", "https://fevm-serverless-9cefok.cloud.databricks.com"))
        mlflow.set_tracking_uri("databricks")
        mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
        mlflow.pydantic_ai.autolog()

        from maestro.agent import run_maestro
        from maestro.synthetic import CINDY_EVENT

        result = await run_maestro(CINDY_EVENT, model)
        assert result.verdict is not None

        # Give trace export a moment to flush
        time.sleep(3)

        traces = mlflow.search_traces(max_results=1)
        assert len(traces) > 0, "No traces found after agent run"
        print(f"  Latest trace: {traces.iloc[0].get('trace_id', 'N/A')}")


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 4: App deployment
# ═══════════════════════════════════════════════════════════════════════════


class TestLayer4App:
    """Verify the Databricks App is deployed and serving."""

    APP_URL = "https://maestro-cdp-demo-7474645105283837.aws.databricksapps.com"

    def test_app_compute_active(self, workspace):
        """App compute is in ACTIVE state."""
        import subprocess
        result = subprocess.run(
            ["databricks", "apps", "get", "maestro-cdp-demo",
             "--profile", "9cefok", "-o", "json"],
            capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        assert data["compute_status"]["state"] == "ACTIVE", \
            f"Compute state: {data['compute_status']['state']}"

    def test_app_status_running(self, workspace):
        """App status is RUNNING."""
        import subprocess
        result = subprocess.run(
            ["databricks", "apps", "get", "maestro-cdp-demo",
             "--profile", "9cefok", "-o", "json"],
            capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        assert data["app_status"]["state"] == "RUNNING", \
            f"App state: {data['app_status']['state']}"

    def test_health_endpoint(self, workspace):
        """Health endpoint responds with 200."""
        import requests
        token = workspace.config.authenticate().get("Authorization", "").replace("Bearer ", "")
        r = requests.get(f"{self.APP_URL}/health",
                         headers={"Authorization": f"Bearer {token}"}, timeout=10)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        print(f"  Health: {r.json()}")


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 5: DBOS workflow (persist → sleep 8s → resume)
# ═══════════════════════════════════════════════════════════════════════════


class TestLayer5Workflow:
    """Verify DBOS workflow: persist, sleep(8s), resume, state check."""

    @pytest.fixture(autouse=True)
    def setup_dbos(self, db_params):
        """Initialize DBOS for workflow tests."""
        from urllib.parse import quote_plus
        from dbos import DBOS, DBOSConfig

        db_url = (
            f"postgresql://{db_params['user']}:{quote_plus(db_params['password'])}"
            f"@{db_params['host']}:{db_params['port']}/{db_params['database']}"
            f"?sslmode=require"
        )
        config = DBOSConfig(
            name="maestro-cdp-test-system",
            system_database_url=db_url,
            application_database_url=db_url,
        )
        DBOS(config=config)
        DBOS.launch()
        yield DBOS
        DBOS.destroy()

    def test_workflow_persist_sleep_resume(self, db_params):
        """Full workflow: save state → sleep 8s → rehydrate → mark completed."""
        from dbos import DBOS

        from maestro.workflow import (
            rehydrate_journey_step,
            save_journey_step,
            update_journey_status_step,
        )

        journey_id = "jrn_system_test_001"
        test_decision = {
            "verdict": "re-prioritize",
            "customer_id": "cust_88241",
            "decisions": [{"type": "suppress_from", "target": "Spring Seasonal"}],
        }

        # Define a test workflow that exercises persist → sleep → resume
        @DBOS.workflow()
        def test_journey_workflow():
            # Step 1: Persist
            save_journey_step(
                journey_id=journey_id,
                customer_id="cust_88241",
                step="awaiting_send",
                due_ts="2026-05-10T08:00:00-05:00",
                state_blob=json.dumps(test_decision),
            )
            # Step 2: Durable sleep (8 seconds)
            DBOS.sleep(8)
            # Step 3: Rehydrate
            state_json = rehydrate_journey_step(journey_id)
            # Step 4: Mark completed
            update_journey_status_step(journey_id, "completed")
            return state_json

        print("  [1/2] Running workflow: persist → sleep(8s) → rehydrate → complete...")
        state_json = test_journey_workflow()
        state = json.loads(state_json)
        assert state["verdict"] == "re-prioritize"
        assert state["customer_id"] == "cust_88241"

        # Verify final state in Lakebase
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute(
            "SELECT status, current_step FROM journey_state WHERE journey_id = %s",
            (journey_id,),
        )
        row = cur.fetchone()
        assert row is not None, "Journey state not found after workflow"
        assert row[0] == "completed"
        print(f"  [2/2] Verified in Lakebase: status={row[0]}, step={row[1]}")

        # Cleanup
        cur.execute("DELETE FROM journey_state WHERE journey_id = %s", (journey_id,))
        conn.commit()
        cur.close()
        conn.close()
        print("  Full workflow verified: persist → sleep(8s) → rehydrate → complete")
