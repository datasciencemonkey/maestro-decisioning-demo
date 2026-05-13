"""Phase 0+1: Schema validation tests — no network required."""

from datetime import datetime
from zoneinfo import ZoneInfo

from maestro.models import (
    CartAbandonedEvent,
    CartItem,
    ContributingSignal,
    Decision,
    DecisionArtifact,
)
from maestro.synthetic import (
    CINDY_CAP_STATUS,
    CINDY_CAMPAIGNS,
    CINDY_CART,
    CINDY_EVENT,
    CINDY_FEASIBILITY,
    CINDY_PROFILE,
    CINDY_PROPENSITY,
    CINDY_SEND_TIME,
    CINDY_TICKETS,
)

CT = ZoneInfo("America/Chicago")


def test_cart_abandoned_event_roundtrip():
    json_str = CINDY_EVENT.model_dump_json()
    restored = CartAbandonedEvent.model_validate_json(json_str)
    assert restored.customer_id == "cust_88241"
    assert restored.cart_total == 42.00
    assert restored.tier1_clearance is True
    assert len(restored.items) == 1


def test_profile_story_coherence():
    p = CINDY_PROFILE
    assert p.pet_name == "Whiskers"
    assert p.pet_type == "tabby kitten"
    assert p.timezone == "America/Chicago"
    assert p.preferred_channel == "email"
    assert p.consent_email is True
    assert p.consent_sms is False
    assert p.is_repeat_buyer is True
    assert p.loyalty_tier == "gold"
    assert p.quiet_hours_start == 21
    assert p.quiet_hours_end == 7


def test_cart_story_coherence():
    c = CINDY_CART
    assert c.cart_id == "cart_77a3f"
    assert c.total == 42.00
    assert c.items[0].product_id == "pb_welcome_home_24pp"


def test_frequency_cap_breach():
    cap = CINDY_CAP_STATUS
    assert cap.status == "breach"
    assert cap.cap == 2
    assert cap.current + cap.queued >= cap.cap


def test_campaigns_count():
    assert len(CINDY_CAMPAIGNS) == 4
    names = {c.name for c in CINDY_CAMPAIGNS}
    assert "Spring Seasonal Promo" in names
    assert "Abandoned Cart Recovery" in names


def test_support_tickets_clean():
    assert CINDY_TICKETS == []


def test_propensity_score():
    assert CINDY_PROPENSITY.score == 0.81
    assert CINDY_PROPENSITY.intent == "cart_recovery"


def test_send_time_adjusted_for_quiet_hours():
    st = CINDY_SEND_TIME
    assert st.adjusted_for_quiet_hours is True
    assert st.optimal_ts.hour == 8
    assert st.optimal_ts.day == 10  # next day


def test_feasibility():
    f = CINDY_FEASIBILITY
    assert f.feasible is True
    assert f.production_days == 4


def test_decision_artifact_schema():
    """Verify DecisionArtifact matches spec section 9."""
    artifact = DecisionArtifact(
        decision_id="dec_a3f88241",
        customer_id="cust_88241",
        journey_id="jrn_88241_a3f",
        trigger_event_id="evt_cart_abandoned_77a3f",
        verdict="re-prioritize",
        decisions=[
            Decision(type="suppress_from", target="Spring Seasonal Promo", reason="frequency_cap_breach"),
            Decision(type="prioritize_in", target="Abandoned Cart Recovery", weight=0.81),
            Decision(type="tone", value="warm, personal, Whiskers context"),
            Decision(type="send_time", value="2026-05-10T08:00:00-05:00", reason="quiet hours adjusted"),
            Decision(type="channel", value="email", reason="consent + preferred"),
        ],
        contributing_signals=[
            ContributingSignal(signal="frequency_cap", value="breach", weight=1.0),
            ContributingSignal(signal="propensity", value=0.81, weight=0.7),
            ContributingSignal(signal="support_tickets", value="none", weight=0.3),
            ContributingSignal(signal="production_feasibility", value="feasible", weight=0.4),
        ],
        rationale="Frequency cap breach blocks Spring Seasonal. Propensity high (0.81), support clean, production feasible.",
        trace_id="tr_abc123",
        created_at=datetime(2026, 5, 9, 20, 18, 1, 687000, tzinfo=CT),
    )
    dumped = artifact.model_dump()
    assert dumped["verdict"] == "re-prioritize"
    assert len(dumped["decisions"]) == 5
    assert len(dumped["contributing_signals"]) == 4
    assert dumped["rationale"].startswith("Frequency cap")
    # Verify suppress_from is present
    suppress = [d for d in dumped["decisions"] if d["type"] == "suppress_from"]
    assert len(suppress) == 1
    assert "Spring Seasonal" in suppress[0]["target"]


def test_email_content_model():
    from maestro.models import EmailContent
    email = EmailContent(
        subject="Whiskers is waiting!",
        body_html="<h1>Hi Cindy</h1><p>Your photo book misses you.</p>",
        body_text="Hi Cindy, your photo book misses you.",
        hero_image_url="/whiskers.jpg",
        cta_text="Complete Your Order",
        cta_url="https://fluttershy.com/cart/resume",
    )
    assert email.subject == "Whiskers is waiting!"
    assert "Cindy" in email.body_html
    assert email.cta_text == "Complete Your Order"


def test_re_evaluation_result_proceed():
    from maestro.models import ReEvaluationResult
    result = ReEvaluationResult(
        action="proceed",
        reason="No changes detected since decision",
        changes_detected=[],
        updated_artifact=None,
    )
    assert result.action == "proceed"
    assert result.changes_detected == []


def test_re_evaluation_result_abort():
    from maestro.models import ReEvaluationResult
    result = ReEvaluationResult(
        action="abort",
        reason="Customer completed purchase during sleep window",
        changes_detected=["purchase_completed"],
        updated_artifact=None,
    )
    assert result.action == "abort"
    assert "purchase_completed" in result.changes_detected
