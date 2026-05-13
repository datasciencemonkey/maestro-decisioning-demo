"""Integration test for the unified Beat 2/2.5/3 flow.

Tests the complete chain: models -> re-evaluate -> email agent -> send record.
Does NOT test DBOS workflow (requires Lakebase) or LLM calls (requires AI Gateway).
"""

import json


def test_full_chain_models():
    """All new models can be instantiated with valid data."""
    from maestro.models import EmailContent, ReEvaluationResult

    email = EmailContent(
        subject="Test",
        body_html="<p>Hi</p>",
        body_text="Hi",
        hero_image_url="/whiskers.jpg",
        cta_text="Order",
        cta_url="https://example.com",
    )
    assert email.subject == "Test"

    result = ReEvaluationResult(
        action="proceed", reason="OK", changes_detected=[], updated_artifact=None
    )
    assert result.action == "proceed"


def test_re_evaluate_then_send():
    """Re-evaluate returns proceed, then build_send_record creates valid record."""
    from maestro.re_evaluate import re_evaluate_context
    from maestro.send import build_send_record

    artifact = {
        "customer_id": "cust_88241",
        "decisions": [{"type": "tone", "value": "warm"}],
        "contributing_signals": [],
    }
    artifact_json = json.dumps(artifact)

    eval_result = re_evaluate_context("jrn_test", artifact_json)
    assert eval_result["action"] == "proceed"

    email_data = json.dumps({
        "subject": "Whiskers!",
        "body_html": "<p>Hi</p>",
        "body_text": "Hi",
        "hero_image_url": "/whiskers.jpg",
        "cta_text": "Order",
        "cta_url": "https://example.com",
    })
    record = build_send_record("jrn_test", "cust_88241", email_data)
    assert record["status"] == "delivered"
    assert record["subject"] == "Whiskers!"


def test_copywriter_prompt_builds():
    """Copywriter prompt includes all necessary context."""
    from maestro.email_agent import build_email_prompt
    from maestro.synthetic import CINDY_CART, CINDY_PROFILE

    artifact = {
        "customer_id": "cust_88241",
        "decisions": [{"type": "tone", "value": "warm + personal"}],
    }
    prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
    assert "Cindy" in prompt
    assert "Whiskers" in prompt
    assert "42" in prompt


def test_workflow_imports():
    """Unified workflow and all steps import correctly."""
    from maestro.workflow import (
        compose_email_step,
        persist_decision_step,
        re_evaluate_step,
        run_agent_step,
        save_journey_step,
        simulate_send_step,
        unified_journey_workflow,
        update_journey_status_step,
    )
    assert callable(unified_journey_workflow)
    assert callable(compose_email_step)
    assert callable(simulate_send_step)
    assert callable(re_evaluate_step)
    assert callable(run_agent_step)
    assert callable(persist_decision_step)
    assert callable(save_journey_step)
    assert callable(update_journey_status_step)


def test_app_phases_endpoint_exists():
    """The /api/workflow/{id}/phases endpoint is registered."""
    from maestro.app import app

    routes = [r.path for r in app.routes]
    assert "/api/workflow/{workflow_id}/phases" in routes
