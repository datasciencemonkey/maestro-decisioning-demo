"""Phase 4: Agent integration tests — requires live LLM via AI Gateway."""

import os
import time

import pytest

from maestro.synthetic import CINDY_EVENT

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


@pytest.fixture(scope="module")
def model():
    """Bootstrap the AI Gateway model (once per test module)."""
    for key in list(os.environ):
        if key.startswith("OTEL_"):
            del os.environ[key]

    import mlflow
    from databricks.sdk import WorkspaceClient
    from databricks_openai import AsyncDatabricksOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    w = WorkspaceClient(profile="9cefok")
    os.environ["DATABRICKS_HOST"] = w.config.host
    os.environ["DATABRICKS_TOKEN"] = (
        w.config.authenticate()["Authorization"].replace("Bearer ", "")
    )
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
    mlflow.pydantic_ai.autolog()

    client = AsyncDatabricksOpenAI(workspace_client=w)
    provider = OpenAIProvider(openai_client=client)
    return OpenAIChatModel("databricks-claude-sonnet-4-6", provider=provider)


async def test_agent_produces_decision(model):
    """Agent produces a valid DecisionArtifact for Cindy."""
    from maestro.agent import run_maestro

    start = time.perf_counter()
    result = await run_maestro(CINDY_EVENT, model)
    elapsed = time.perf_counter() - start

    # Basic structure
    assert result.customer_id == "cust_88241"
    assert result.verdict is not None and len(result.verdict) > 0
    assert len(result.decisions) >= 3
    assert len(result.contributing_signals) >= 2
    assert result.rationale is not None and len(result.rationale) > 20

    # Latency
    if elapsed > 2.0:
        pytest.warns(UserWarning, match="latency")
        print(f"WARNING: latency {elapsed:.1f}s exceeds 2.0s ceiling")
    print(f"Latency: {elapsed:.2f}s")


async def test_suppresses_spring_seasonal(model):
    """Agent suppresses Spring Seasonal due to frequency cap breach."""
    from maestro.agent import run_maestro

    result = await run_maestro(CINDY_EVENT, model)

    suppress_decisions = [
        d for d in result.decisions if d.type == "suppress_from"
    ]
    assert len(suppress_decisions) >= 1, "Agent must suppress at least one campaign"

    targets = " ".join(
        (d.target or "").lower() for d in suppress_decisions
    )
    assert any(
        term in targets
        for term in ["spring", "seasonal", "campaign_sp", "sp_2026"]
    ), f"Expected Spring Seasonal suppression, got targets: {targets}"


async def test_prioritizes_cart_recovery(model):
    """Agent prioritizes Abandoned Cart Recovery."""
    from maestro.agent import run_maestro

    result = await run_maestro(CINDY_EVENT, model)

    prioritize_decisions = [
        d for d in result.decisions if d.type == "prioritize_in"
    ]
    assert len(prioritize_decisions) >= 1, "Agent must prioritize a campaign"

    targets = " ".join(
        (d.target or "").lower() for d in prioritize_decisions
    )
    assert any(
        term in targets
        for term in ["cart", "abandon", "recovery", "campaign_acr", "acr_88241"]
    ), f"Expected cart recovery prioritization, got: {targets}"


async def test_rationale_mentions_frequency(model):
    """Rationale references the frequency cap breach."""
    from maestro.agent import run_maestro

    result = await run_maestro(CINDY_EVENT, model)

    rationale_lower = result.rationale.lower()
    assert any(
        term in rationale_lower
        for term in ["frequency", "cap", "breach", "limit"]
    ), f"Rationale should mention frequency cap: {result.rationale}"
