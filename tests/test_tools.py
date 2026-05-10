"""Phase 3: Tool contract tests -- no LLM required."""

import pytest
from maestro.tools import (
    read_profile, read_cart, check_production_feasibility,
    list_active_campaigns, check_frequency_cap, read_support_tickets,
    score_propensity, optimal_send_time, persist_journey_state,
)


pytestmark = pytest.mark.asyncio


async def test_read_profile():
    p = await read_profile("cust_88241")
    assert p.name == "Cindy Chen"
    assert p.pet_name == "Whiskers"
    assert p.timezone == "America/Chicago"


async def test_read_profile_unknown():
    with pytest.raises(ValueError, match="Unknown customer"):
        await read_profile("cust_unknown")


async def test_read_cart():
    c = await read_cart("cust_88241")
    assert c.total == 42.00
    assert c.items[0].product_id == "pb_welcome_home_24pp"


async def test_check_production_feasibility():
    f = await check_production_feasibility("pb_welcome_home_24pp", "2026-05-15")
    assert f.feasible is True
    assert f.production_days == 4


async def test_list_active_campaigns():
    camps = await list_active_campaigns("cust_88241")
    assert len(camps) == 4
    names = {c.name for c in camps}
    assert "Spring Seasonal Promo" in names
    assert "Abandoned Cart Recovery" in names


async def test_check_frequency_cap_breach():
    cap = await check_frequency_cap("cust_88241", "email", 7)
    assert cap.status == "breach"
    assert cap.cap == 2
    assert cap.current + cap.queued >= cap.cap


async def test_check_frequency_cap_default():
    cap = await check_frequency_cap("cust_unknown", "email", 7)
    assert cap.status == "ok"


async def test_read_support_tickets_clean():
    tickets = await read_support_tickets("cust_88241", 30)
    assert tickets == []


async def test_score_propensity():
    s = await score_propensity("cust_88241", "cart_recovery")
    assert s.score == 0.81
    assert s.intent == "cart_recovery"


async def test_score_propensity_default():
    s = await score_propensity("cust_unknown", "some_intent")
    assert s.score == 0.5


async def test_optimal_send_time():
    st = await optimal_send_time("cust_88241", "morning_engaged", 0.81)
    assert st.optimal_ts.hour == 8
    assert st.adjusted_for_quiet_hours is True


async def test_persist_journey_state():
    h = await persist_journey_state(
        "cust_88241", "awaiting_send",
        "2026-05-10T08:00:00-05:00", {"test": True}
    )
    assert h.customer_id == "cust_88241"
    assert h.step == "awaiting_send"
    assert h.status == "pending"
    assert h.journey_id.startswith("jrn_cust_88241_")
