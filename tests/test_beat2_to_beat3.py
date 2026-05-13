"""Comprehensive tests for the full Beat 2 -> 2.5 -> 3 chain.

Covers: models, synthetic data integrity, re-evaluation logic, email agent,
send record, API endpoints, workflow imports, and signal value safety.

Does NOT duplicate tests from: test_unified_flow.py, test_models.py,
test_re_evaluate.py, test_email_agent.py, test_send.py.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

CT = ZoneInfo("America/Chicago")


# ────────────────────────────────────────────────────────────────────────────
# 1. Models — not duplicating existing coverage
# ────────────────────────────────────────────────────────────────────────────


class TestEmailContentAllFields:
    def test_all_fields_are_stored_correctly(self):
        from maestro.models import EmailContent

        email = EmailContent(
            subject="Whiskers left something behind",
            body_html="<h1>Hi Cindy</h1><p>Come back.</p>",
            body_text="Hi Cindy, come back.",
            hero_image_url="https://cdn.fluttershy.com/whiskers.jpg",
            cta_text="Finish Your Order",
            cta_url="https://fluttershy.com/cart/resume?cid=cust_88241",
        )
        assert email.subject == "Whiskers left something behind"
        assert email.body_html == "<h1>Hi Cindy</h1><p>Come back.</p>"
        assert email.body_text == "Hi Cindy, come back."
        assert email.hero_image_url == "https://cdn.fluttershy.com/whiskers.jpg"
        assert email.cta_text == "Finish Your Order"
        assert email.cta_url == "https://fluttershy.com/cart/resume?cid=cust_88241"

    def test_email_content_serialises_to_json(self):
        from maestro.models import EmailContent

        email = EmailContent(
            subject="S",
            body_html="<p>B</p>",
            body_text="B",
            hero_image_url="/img.jpg",
            cta_text="Go",
            cta_url="https://example.com",
        )
        dumped = json.loads(email.model_dump_json())
        assert dumped["subject"] == "S"
        assert dumped["cta_url"] == "https://example.com"

    def test_email_content_missing_field_raises_validation_error(self):
        from pydantic import ValidationError

        from maestro.models import EmailContent

        with pytest.raises(ValidationError):
            EmailContent(
                subject="No body",
                body_html="<p>hi</p>",
                # missing body_text, hero_image_url, cta_text, cta_url
            )


class TestReEvaluationResultAllActionTypes:
    def test_proceed_action_has_empty_changes(self):
        from maestro.models import ReEvaluationResult

        r = ReEvaluationResult(
            action="proceed",
            reason="All signals unchanged",
            changes_detected=[],
            updated_artifact=None,
        )
        assert r.action == "proceed"
        assert r.changes_detected == []
        assert r.updated_artifact is None

    def test_abort_action_carries_reason(self):
        from maestro.models import ReEvaluationResult

        r = ReEvaluationResult(
            action="abort",
            reason="consent_revoked",
            changes_detected=["consent_revoked"],
            updated_artifact=None,
        )
        assert r.action == "abort"
        assert "consent_revoked" in r.changes_detected

    def test_adjust_action_carries_updated_artifact(self):
        from maestro.models import ReEvaluationResult

        artifact = '{"customer_id": "cust_88241"}'
        r = ReEvaluationResult(
            action="adjust",
            reason="frequency_cap_resolved",
            changes_detected=["frequency_cap_resolved"],
            updated_artifact=artifact,
        )
        assert r.action == "adjust"
        assert r.updated_artifact == artifact

    def test_invalid_action_type_raises_validation_error(self):
        from pydantic import ValidationError

        from maestro.models import ReEvaluationResult

        with pytest.raises(ValidationError):
            ReEvaluationResult(
                action="unknown_action",
                reason="bad",
                changes_detected=[],
                updated_artifact=None,
            )


class TestDecisionArtifactWithObjectSignalValues:
    """Guard against the crash bug: signal values that are dicts/objects."""

    def test_contributing_signal_accepts_dict_value(self):
        from maestro.models import ContributingSignal

        cap_dict = {"status": "breach", "current": 1, "queued": 1, "cap": 2}
        signal = ContributingSignal(signal="frequency_cap", value=cap_dict, weight=1.0)
        assert signal.value == cap_dict
        assert signal.value["status"] == "breach"

    def test_decision_artifact_with_object_signal_values_roundtrips(self):
        from maestro.models import ContributingSignal, Decision, DecisionArtifact

        cap_dict = {"status": "breach", "current": 1, "queued": 1, "cap": 2}
        artifact = DecisionArtifact(
            decision_id="dec_obj_test",
            customer_id="cust_88241",
            journey_id="jrn_obj_test",
            trigger_event_id="evt_test",
            verdict="re-prioritize",
            decisions=[
                Decision(type="suppress_from", target="Spring Seasonal Promo"),
            ],
            contributing_signals=[
                ContributingSignal(signal="frequency_cap", value=cap_dict, weight=1.0),
                ContributingSignal(signal="propensity", value=0.81, weight=0.7),
            ],
            rationale="Object signal value test.",
            created_at=datetime(2026, 5, 9, 20, 18, 0, tzinfo=CT),
        )
        dumped = artifact.model_dump()
        # Object-valued signal preserved
        assert dumped["contributing_signals"][0]["value"] == cap_dict
        # JSON serialisation must not crash
        serialised = artifact.model_dump_json()
        restored = json.loads(serialised)
        assert restored["contributing_signals"][0]["value"]["status"] == "breach"

    def test_stringifying_object_signal_value_does_not_crash(self):
        from maestro.models import ContributingSignal

        cap_dict = {"status": "breach", "current": 1, "queued": 1, "cap": 2}
        signal = ContributingSignal(signal="frequency_cap", value=cap_dict, weight=1.0)
        # This is the operation the UI does — must not raise
        result = str(signal.value)
        assert "breach" in result


# ────────────────────────────────────────────────────────────────────────────
# 2. Synthetic Data Integrity
# ────────────────────────────────────────────────────────────────────────────


class TestSyntheticLookupDicts:
    def test_profiles_dict_contains_cindy(self):
        from maestro.synthetic import PROFILES

        assert "cust_88241" in PROFILES

    def test_carts_dict_contains_cindy(self):
        from maestro.synthetic import CARTS

        assert "cust_88241" in CARTS

    def test_feasibilities_dict_contains_photo_book(self):
        from maestro.synthetic import FEASIBILITIES

        assert "pb_welcome_home_24pp" in FEASIBILITIES

    def test_campaigns_dict_contains_cindy(self):
        from maestro.synthetic import CAMPAIGNS

        assert "cust_88241" in CAMPAIGNS

    def test_cap_statuses_keyed_by_customer_and_channel(self):
        from maestro.synthetic import CAP_STATUSES

        assert ("cust_88241", "email") in CAP_STATUSES

    def test_tickets_dict_contains_cindy(self):
        from maestro.synthetic import TICKETS

        assert "cust_88241" in TICKETS

    def test_propensity_scores_keyed_by_customer_and_intent(self):
        from maestro.synthetic import PROPENSITY_SCORES

        assert ("cust_88241", "cart_recovery") in PROPENSITY_SCORES

    def test_send_times_dict_contains_cindy(self):
        from maestro.synthetic import SEND_TIMES

        assert "cust_88241" in SEND_TIMES


class TestSyntheticCapStatus:
    def test_cap_status_is_breach(self):
        from maestro.synthetic import CINDY_CAP_STATUS

        assert CINDY_CAP_STATUS.status == "breach"

    def test_cap_is_two_and_slots_are_full(self):
        from maestro.synthetic import CINDY_CAP_STATUS

        assert CINDY_CAP_STATUS.cap == 2
        assert CINDY_CAP_STATUS.current + CINDY_CAP_STATUS.queued >= CINDY_CAP_STATUS.cap


class TestSyntheticCampaigns:
    def test_campaigns_list_has_four_entries(self):
        from maestro.synthetic import CINDY_CAMPAIGNS

        assert len(CINDY_CAMPAIGNS) == 4

    def test_spring_seasonal_status_is_active(self):
        from maestro.synthetic import CINDY_CAMPAIGNS

        spring = next(c for c in CINDY_CAMPAIGNS if "Spring" in c.name)
        assert spring.status == "active"

    def test_abandoned_cart_recovery_status_is_triggered(self):
        from maestro.synthetic import CINDY_CAMPAIGNS

        acr = next(c for c in CINDY_CAMPAIGNS if "Abandoned" in c.name)
        assert acr.status == "triggered"

    def test_vip_loyalty_status_is_paused(self):
        from maestro.synthetic import CINDY_CAMPAIGNS

        vip = next(c for c in CINDY_CAMPAIGNS if "VIP" in c.name)
        assert vip.status == "paused"

    def test_reactivation_status_is_dormant(self):
        from maestro.synthetic import CINDY_CAMPAIGNS

        react = next(c for c in CINDY_CAMPAIGNS if "Reactivation" in c.name)
        assert react.status == "dormant"


class TestSyntheticSendTime:
    def test_send_time_adjusted_for_quiet_hours_flag_is_true(self):
        from maestro.synthetic import CINDY_SEND_TIME

        assert CINDY_SEND_TIME.adjusted_for_quiet_hours is True

    def test_send_time_is_8am_ct(self):
        from maestro.synthetic import CINDY_SEND_TIME

        # 8 AM CT
        assert CINDY_SEND_TIME.optimal_ts.hour == 8

    def test_send_time_original_was_during_quiet_hours(self):
        from maestro.synthetic import CINDY_SEND_TIME

        # Original was at 23:48 — well inside quiet hours (21-7)
        assert CINDY_SEND_TIME.original_ts.hour >= 21 or CINDY_SEND_TIME.original_ts.hour < 7


# ────────────────────────────────────────────────────────────────────────────
# 3. Re-evaluation Logic
# ────────────────────────────────────────────────────────────────────────────


class TestReEvaluateProceeds:
    def test_proceeds_when_no_changes_in_demo_data(self):
        from maestro.re_evaluate import re_evaluate_context

        artifact = {
            "customer_id": "cust_88241",
            "decisions": [],
            "contributing_signals": [
                {"signal": "frequency_cap", "value": "breach", "weight": 1.0}
            ],
        }
        result = re_evaluate_context("jrn_abc", json.dumps(artifact))
        assert result["action"] == "proceed"

    def test_proceed_result_has_empty_changes_list(self):
        from maestro.re_evaluate import re_evaluate_context

        artifact = {"customer_id": "cust_88241", "decisions": [], "contributing_signals": []}
        result = re_evaluate_context("jrn_abc", json.dumps(artifact))
        assert result["changes_detected"] == []

    def test_proceed_result_updated_artifact_is_none(self):
        from maestro.re_evaluate import re_evaluate_context

        artifact = {"customer_id": "cust_88241", "decisions": [], "contributing_signals": []}
        result = re_evaluate_context("jrn_abc", json.dumps(artifact))
        assert result["updated_artifact"] is None


class TestReEvaluateAborts:
    def test_aborts_when_cart_has_completed_status(self):
        """Mocking a cart with status='completed' should trigger abort."""
        from maestro.re_evaluate import re_evaluate_context

        mock_cart = MagicMock()
        mock_cart.status = "completed"

        artifact = {
            "customer_id": "cust_88241",
            "decisions": [],
            "contributing_signals": [],
        }

        with patch("maestro.re_evaluate.CARTS", {"cust_88241": mock_cart}):
            result = re_evaluate_context("jrn_abc", json.dumps(artifact))

        assert result["action"] == "abort"
        assert "purchase_completed" in result["changes_detected"]

    def test_aborts_when_consent_revoked(self):
        """Mocking a profile with consent_email=False should trigger abort."""
        from maestro.re_evaluate import re_evaluate_context

        mock_profile = MagicMock()
        mock_profile.consent_email = False

        artifact = {
            "customer_id": "cust_88241",
            "decisions": [],
            "contributing_signals": [],
        }

        with patch("maestro.re_evaluate.PROFILES", {"cust_88241": mock_profile}):
            result = re_evaluate_context("jrn_abc", json.dumps(artifact))

        assert result["action"] == "abort"
        assert "consent_revoked" in result["changes_detected"]

    def test_abort_reason_includes_change_name(self):
        from maestro.re_evaluate import re_evaluate_context

        mock_profile = MagicMock()
        mock_profile.consent_email = False

        artifact = {"customer_id": "cust_88241", "decisions": [], "contributing_signals": []}
        with patch("maestro.re_evaluate.PROFILES", {"cust_88241": mock_profile}):
            result = re_evaluate_context("jrn_abc", json.dumps(artifact))

        assert "consent_revoked" in result["reason"]


class TestReEvaluateAdjusts:
    def test_adjusts_when_new_support_ticket_appears(self):
        """A new ticket that wasn't in the original signals should cause adjust."""
        from maestro.re_evaluate import re_evaluate_context

        mock_ticket = MagicMock()

        artifact = {
            "customer_id": "cust_88241",
            "decisions": [],
            "contributing_signals": [
                {"signal": "support_tickets", "value": "none recent", "weight": 0.3}
            ],
        }

        with patch("maestro.re_evaluate.TICKETS", {"cust_88241": [mock_ticket]}):
            result = re_evaluate_context("jrn_abc", json.dumps(artifact))

        assert result["action"] == "adjust"
        assert "new_support_ticket" in result["changes_detected"]


# ────────────────────────────────────────────────────────────────────────────
# 4. Email Agent
# ────────────────────────────────────────────────────────────────────────────


class TestBuildEmailPrompt:
    def test_prompt_includes_customer_name(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {"customer_id": "cust_88241", "decisions": []}
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "Cindy" in prompt

    def test_prompt_includes_pet_name(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {"customer_id": "cust_88241", "decisions": []}
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "Whiskers" in prompt

    def test_prompt_includes_product_id(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {"customer_id": "cust_88241", "decisions": []}
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "pb_welcome_home_24pp" in prompt

    def test_prompt_includes_price(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {"customer_id": "cust_88241", "decisions": []}
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "42" in prompt

    def test_prompt_uses_tone_from_decisions(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {
            "customer_id": "cust_88241",
            "decisions": [{"type": "tone", "value": "empathetic"}],
        }
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "empathetic" in prompt

    def test_prompt_defaults_to_warm_personal_when_no_tone_decision(self):
        from maestro.email_agent import build_email_prompt
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        artifact = {"customer_id": "cust_88241", "decisions": []}
        prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
        assert "warm" in prompt.lower() or "personal" in prompt.lower()


class TestCopywriterPromptConstraints:
    def test_prompt_mentions_50_char_subject_limit(self):
        from maestro.email_agent import COPYWRITER_PROMPT

        assert "50" in COPYWRITER_PROMPT

    def test_prompt_mentions_100_word_body_limit(self):
        from maestro.email_agent import COPYWRITER_PROMPT

        assert "100" in COPYWRITER_PROMPT

    def test_prompt_prohibits_urgency_tactics(self):
        from maestro.email_agent import COPYWRITER_PROMPT

        assert "urgency" in COPYWRITER_PROMPT.lower() or "countdown" in COPYWRITER_PROMPT.lower()

    def test_prompt_mentions_fluttershy_brand(self):
        from maestro.email_agent import COPYWRITER_PROMPT

        assert "Fluttershy" in COPYWRITER_PROMPT


class TestCopywriterDeps:
    def test_copywriter_deps_dataclass_instantiation(self):
        from maestro.email_agent import CopywriterDeps
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        deps = CopywriterDeps(
            customer_id="cust_88241",
            profile=CINDY_PROFILE,
            cart=CINDY_CART,
            tone="warm + personal",
            hero_image_url="/whiskers.jpg",
        )
        assert deps.customer_id == "cust_88241"
        assert deps.tone == "warm + personal"
        assert deps.hero_image_url == "/whiskers.jpg"
        assert deps.profile.pet_name == "Whiskers"

    def test_copywriter_deps_stores_cart_reference(self):
        from maestro.email_agent import CopywriterDeps
        from maestro.synthetic import CINDY_CART, CINDY_PROFILE

        deps = CopywriterDeps(
            customer_id="cust_88241",
            profile=CINDY_PROFILE,
            cart=CINDY_CART,
            tone="professional",
            hero_image_url="/img.jpg",
        )
        assert deps.cart.total == 42.00


# ────────────────────────────────────────────────────────────────────────────
# 5. Send Record
# ────────────────────────────────────────────────────────────────────────────


class TestBuildSendRecord:
    def _make_email_json(self, subject="Whiskers!") -> str:
        return json.dumps({
            "subject": subject,
            "body_html": "<h1>Hi</h1>",
            "body_text": "Hi",
            "hero_image_url": "/whiskers.jpg",
            "cta_text": "Order",
            "cta_url": "https://fluttershy.com",
        })

    def test_email_id_starts_with_eml_prefix(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_88241", self._make_email_json())
        assert record["email_id"].startswith("eml_")

    def test_status_is_delivered(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_88241", self._make_email_json())
        assert record["status"] == "delivered"

    def test_all_required_fields_present(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_88241", self._make_email_json())
        required = {"email_id", "journey_id", "customer_id", "subject", "body_html",
                    "channel", "status", "sent_at"}
        assert required.issubset(record.keys())

    def test_journey_id_preserved(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_special_99", "cust_88241", self._make_email_json())
        assert record["journey_id"] == "jrn_special_99"

    def test_customer_id_preserved(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_00001", self._make_email_json())
        assert record["customer_id"] == "cust_00001"

    def test_channel_is_email(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_88241", self._make_email_json())
        assert record["channel"] == "email"

    def test_subject_copied_from_email_content(self):
        from maestro.send import build_send_record

        record = build_send_record("jrn_x", "cust_88241", self._make_email_json("Unique subject!"))
        assert record["subject"] == "Unique subject!"

    def test_email_id_is_unique_across_two_calls(self):
        from maestro.send import build_send_record

        r1 = build_send_record("jrn_x", "cust_88241", self._make_email_json())
        r2 = build_send_record("jrn_y", "cust_88241", self._make_email_json())
        assert r1["email_id"] != r2["email_id"]

    def test_handles_minimal_email_content_shape(self):
        """Works even when optional email fields are absent."""
        from maestro.send import build_send_record

        minimal = json.dumps({"subject": "min", "body_html": "<p>x</p>"})
        record = build_send_record("jrn_z", "cust_88241", minimal)
        assert record["subject"] == "min"
        assert record["status"] == "delivered"


# ────────────────────────────────────────────────────────────────────────────
# 6. API Endpoints (FastAPI TestClient — no DBOS, no LLM)
# ────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def client():
    """TestClient with DBOS + LLM init patched out."""
    # Patch DBOS and WorkspaceClient before importing app
    with (
        patch("maestro.app._get_db_config", return_value=None),
        patch("maestro.app.DBOS", MagicMock()),
        patch("databricks.sdk.WorkspaceClient", MagicMock()),
        patch("databricks_openai.AsyncDatabricksOpenAI", MagicMock()),
    ):
        # Re-import inside patch context so module-level code is patched
        import importlib

        import maestro.app as app_module
        importlib.reload(app_module)
        from fastapi.testclient import TestClient
        yield TestClient(app_module.app)


class TestHealthEndpoint:
    def test_get_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_get_health_returns_ok_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_get_health_returns_service_name(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "maestro-cdp"


class TestEventsEndpoint:
    def test_post_cart_abandoned_event_returns_200(self, client):
        payload = {
            "event_type": "cart_abandoned",
            "customer_id": "cust_88241",
            "cart_id": "cart_77a3f",
        }
        response = client.post("/api/events", json=payload)
        assert response.status_code == 200

    def test_post_cart_abandoned_returns_received_status(self, client):
        payload = {
            "event_type": "cart_abandoned",
            "customer_id": "cust_88241",
        }
        response = client.post("/api/events", json=payload)
        data = response.json()
        assert data["status"] == "received"

    def test_post_cart_abandoned_echoes_event_type(self, client):
        payload = {"event_type": "cart_abandoned", "customer_id": "cust_88241"}
        response = client.post("/api/events", json=payload)
        assert response.json()["event_type"] == "cart_abandoned"

    def test_post_unknown_event_type_returns_400(self, client):
        payload = {"event_type": "purchase_completed", "customer_id": "cust_88241"}
        response = client.post("/api/events", json=payload)
        assert response.status_code == 400

    def test_post_unknown_event_type_includes_error_detail(self, client):
        payload = {"event_type": "page_view", "customer_id": "cust_88241"}
        response = client.post("/api/events", json=payload)
        detail = response.json()["detail"]
        assert "page_view" in detail or "Unknown" in detail


class TestWorkflowEndpoints:
    def test_post_workflow_raises_when_dbos_start_fails(self, client):
        """When DBOS.start_workflow_async raises, endpoint returns 500."""
        import maestro.app as app_module

        orig = app_module.DBOS
        mock_dbos = MagicMock()
        mock_dbos.start_workflow_async.side_effect = RuntimeError("DBOS not available")
        app_module.DBOS = mock_dbos
        try:
            # raise_server_exceptions=False makes TestClient return the HTTP
            # response (500) instead of re-raising the server-side exception.
            from fastapi.testclient import TestClient
            safe_client = TestClient(app_module.app, raise_server_exceptions=False)
            response = safe_client.post("/api/workflow", json={"delay": 5})
            assert response.status_code == 500
        finally:
            app_module.DBOS = orig

    def test_get_workflow_phases_unknown_id_returns_404(self, client):
        """Unknown workflow IDs should return 404."""
        response = client.get("/api/workflow/nonexistent-workflow-id-xyz/phases")
        assert response.status_code == 404


def _make_mock_artifact(verdict: str = "re-prioritize", decision_id: str = "dec_test"):
    """Helper: build a DecisionArtifact that the /api/run endpoint can return."""
    from maestro.models import ContributingSignal, Decision, DecisionArtifact

    return DecisionArtifact(
        decision_id=decision_id,
        customer_id="cust_88241",
        journey_id="jrn_test",
        trigger_event_id="evt_test",
        verdict=verdict,
        decisions=[
            Decision(type="suppress_from", target="Spring Seasonal Promo"),
            Decision(type="prioritize_in", target="Abandoned Cart Recovery"),
        ],
        contributing_signals=[
            ContributingSignal(signal="frequency_cap", value="breach", weight=1.0),
            ContributingSignal(signal="propensity", value=0.81, weight=0.7),
        ],
        rationale="Test rationale.",
        created_at=datetime(2026, 5, 9, 20, 18, 0, tzinfo=CT),
    )


class TestRunEndpoint:
    def test_post_run_calls_agent_and_returns_artifact(self, client):
        """POST /api/run returns artifact dict with required fields."""
        # run_maestro is imported locally inside the endpoint, patch at source
        import asyncio

        async def _fake_run(*args, **kwargs):
            return _make_mock_artifact("re-prioritize")

        with patch("maestro.agent.run_maestro", side_effect=_fake_run):
            response = client.post("/api/run")

        assert response.status_code == 200
        data = response.json()
        assert "artifact" in data
        assert data["artifact"]["verdict"] == "re-prioritize"
        assert data["artifact"]["customer_id"] == "cust_88241"

    def test_post_run_returns_campaigns_list(self, client):
        async def _fake_run(*args, **kwargs):
            return _make_mock_artifact("proceed", "dec_test2")

        with patch("maestro.agent.run_maestro", side_effect=_fake_run):
            response = client.post("/api/run")

        data = response.json()
        assert "campaigns" in data
        assert isinstance(data["campaigns"], list)

    def test_post_run_returns_latency_field(self, client):
        async def _fake_run(*args, **kwargs):
            return _make_mock_artifact("proceed", "dec_lat")

        with patch("maestro.agent.run_maestro", side_effect=_fake_run):
            response = client.post("/api/run")

        data = response.json()
        assert "latency_s" in data
        assert data["latency_s"] >= 0


# ────────────────────────────────────────────────────────────────────────────
# 7. Workflow Imports
# ────────────────────────────────────────────────────────────────────────────


class TestWorkflowImports:
    def test_unified_journey_workflow_is_callable(self):
        from maestro.workflow import unified_journey_workflow

        assert callable(unified_journey_workflow)

    def test_backward_compatible_alias_journey_workflow_exists(self):
        from maestro.workflow import journey_workflow, unified_journey_workflow

        assert journey_workflow is unified_journey_workflow

    def test_backward_compatible_alias_save_decision_step_exists(self):
        from maestro.workflow import persist_decision_step, save_decision_step

        assert save_decision_step is persist_decision_step

    def test_run_agent_step_is_callable(self):
        from maestro.workflow import run_agent_step

        assert callable(run_agent_step)

    def test_compose_email_step_is_callable(self):
        from maestro.workflow import compose_email_step

        assert callable(compose_email_step)

    def test_persist_decision_step_is_callable(self):
        from maestro.workflow import persist_decision_step

        assert callable(persist_decision_step)

    def test_save_journey_step_is_callable(self):
        from maestro.workflow import save_journey_step

        assert callable(save_journey_step)

    def test_re_evaluate_step_is_callable(self):
        from maestro.workflow import re_evaluate_step

        assert callable(re_evaluate_step)

    def test_simulate_send_step_is_callable(self):
        from maestro.workflow import simulate_send_step

        assert callable(simulate_send_step)

    def test_update_journey_status_step_is_callable(self):
        from maestro.workflow import update_journey_status_step

        assert callable(update_journey_status_step)

    def test_rehydrate_journey_step_is_callable(self):
        from maestro.workflow import rehydrate_journey_step

        assert callable(rehydrate_journey_step)


# ────────────────────────────────────────────────────────────────────────────
# 8. Signal Value Safety
# ────────────────────────────────────────────────────────────────────────────


class TestSignalValueSafety:
    def test_string_signal_value_renders_safely(self):
        from maestro.models import ContributingSignal

        signal = ContributingSignal(signal="frequency_cap", value="breach", weight=1.0)
        rendered = str(signal.value)
        assert rendered == "breach"

    def test_numeric_signal_value_renders_safely(self):
        from maestro.models import ContributingSignal

        signal = ContributingSignal(signal="propensity", value=0.81, weight=0.7)
        rendered = str(signal.value)
        assert "0.81" in rendered

    def test_dict_signal_value_renders_safely_without_crash(self):
        from maestro.models import ContributingSignal

        cap_dict = {"status": "breach", "current": 1, "queued": 1, "cap": 2}
        signal = ContributingSignal(signal="frequency_cap", value=cap_dict, weight=1.0)
        # Must not raise
        rendered = str(signal.value)
        assert isinstance(rendered, str)

    def test_none_signal_value_renders_safely(self):
        from maestro.models import ContributingSignal

        signal = ContributingSignal(signal="support_tickets", value=None, weight=0.3)
        rendered = str(signal.value)
        assert rendered == "None"

    def test_list_signal_value_renders_safely(self):
        from maestro.models import ContributingSignal

        signal = ContributingSignal(signal="campaigns", value=["a", "b"], weight=0.5)
        rendered = str(signal.value)
        assert isinstance(rendered, str)

    def test_artifact_with_mixed_signal_types_serialises_without_crash(self):
        from maestro.models import ContributingSignal, Decision, DecisionArtifact

        artifact = DecisionArtifact(
            decision_id="dec_safe",
            customer_id="cust_88241",
            journey_id="jrn_safe",
            trigger_event_id="evt_safe",
            verdict="re-prioritize",
            decisions=[Decision(type="channel", value="email")],
            contributing_signals=[
                ContributingSignal(signal="frequency_cap",
                                   value={"status": "breach", "cap": 2}, weight=1.0),
                ContributingSignal(signal="propensity", value=0.81, weight=0.7),
                ContributingSignal(signal="support_tickets", value="none recent", weight=0.3),
                ContributingSignal(signal="campaigns", value=["c1", "c2"], weight=0.5),
            ],
            rationale="Mixed signal types.",
            created_at=datetime(2026, 5, 9, 20, 18, 0, tzinfo=CT),
        )
        # Both model_dump and model_dump_json must complete without raising
        dumped = artifact.model_dump()
        json_str = artifact.model_dump_json()
        restored = json.loads(json_str)
        assert restored["verdict"] == "re-prioritize"
        assert len(restored["contributing_signals"]) == 4
