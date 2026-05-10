"""Hardcoded demo data for Cindy (cust_88241).

Provides a coherent story: repeat buyer, gold-tier, abandoned a photo book,
frequency-cap breach forces the agent to suppress Spring Seasonal in favour
of Abandoned Cart Recovery.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from maestro.models import (
    Campaign,
    CapStatus,
    Cart,
    CartAbandonedEvent,
    CartItem,
    Feasibility,
    Profile,
    Score,
    SendTimestamp,
    Ticket,
)

CT = ZoneInfo("America/Chicago")

# ── Profile ─────────────────────────────────────────────────────────────────

CINDY_PROFILE = Profile(
    customer_id="cust_88241",
    name="Cindy Chen",
    email="cindy.chen@example.com",
    pet_name="Whiskers",
    pet_type="tabby kitten",
    timezone="America/Chicago",
    preferred_channel="email",
    consent_email=True,
    consent_sms=False,
    is_repeat_buyer=True,
    loyalty_tier="gold",
    quiet_hours_start=21,
    quiet_hours_end=7,
)

# ── Cart ────────────────────────────────────────────────────────────────────

CINDY_CART = Cart(
    cart_id="cart_77a3f",
    customer_id="cust_88241",
    items=[CartItem(product_id="pb_welcome_home_24pp", qty=1, price=42.00)],
    total=42.00,
    created_at=datetime(2026, 5, 9, 19, 45, 0, tzinfo=CT),
    abandoned_at=datetime(2026, 5, 9, 20, 18, 0, tzinfo=CT),
)

# ── Production feasibility ──────────────────────────────────────────────────

CINDY_FEASIBILITY = Feasibility(
    product_id="pb_welcome_home_24pp",
    feasible=True,
    production_days=4,
    ship_by_achievable=True,
    reason="Standard production; 4-day turnaround within capacity.",
)

# ── Active campaigns ────────────────────────────────────────────────────────

CINDY_CAMPAIGNS = [
    Campaign(
        campaign_id="campaign_sp_2026",
        name="Spring Seasonal Promo",
        campaign_type="seasonal",
        status="active",
        scheduled_send=datetime(2026, 5, 10, 9, 0, 0, tzinfo=CT),
        channel="email",
    ),
    Campaign(
        campaign_id="campaign_acr_88241",
        name="Abandoned Cart Recovery",
        campaign_type="trigger",
        status="triggered",
        scheduled_send=None,
        channel="email",
    ),
    Campaign(
        campaign_id="campaign_vip_q2",
        name="VIP Loyalty Reload",
        campaign_type="loyalty",
        status="paused",
        scheduled_send=None,
        channel="email",
    ),
    Campaign(
        campaign_id="campaign_react_90d",
        name="Reactivation 90d",
        campaign_type="winback",
        status="dormant",
        scheduled_send=None,
        channel="email",
    ),
]

# ── Frequency cap ───────────────────────────────────────────────────────────

CINDY_CAP_STATUS = CapStatus(
    customer_id="cust_88241",
    channel="email",
    cap=2,
    current=1,
    queued=1,
    status="breach",
    window_days=7,
)

# ── Support tickets (clean history) ─────────────────────────────────────────

CINDY_TICKETS: list[Ticket] = []

# ── Propensity score ────────────────────────────────────────────────────────

CINDY_PROPENSITY = Score(
    customer_id="cust_88241",
    intent="cart_recovery",
    score=0.81,
    model_version="v3",
    confidence=0.89,
)

# ── Optimal send time ──────────────────────────────────────────────────────

CINDY_SEND_TIME = SendTimestamp(
    customer_id="cust_88241",
    optimal_ts=datetime(2026, 5, 10, 8, 0, 0, tzinfo=CT),
    cohort="morning_engaged",
    adjusted_for_quiet_hours=True,
    original_ts=datetime(2026, 5, 9, 23, 48, 0, tzinfo=CT),
    reason="Original T+3.5h lands at 11:48 PM CT (quiet hours); shifted to 8 AM CT next day.",
)

# ── Trigger event ───────────────────────────────────────────────────────────

CINDY_EVENT = CartAbandonedEvent(
    customer_id="cust_88241",
    cart_id="cart_77a3f",
    abandoned_at=datetime(2026, 5, 9, 20, 18, 0, tzinfo=CT),
    cart_total=42.00,
    items=[CartItem(product_id="pb_welcome_home_24pp", qty=1, price=42.00)],
    source_session_id="sess_a1b2c3",
    tier1_clearance=True,
)

# ── Lookup dicts (keyed the way agent tools will query) ─────────────────────

PROFILES = {"cust_88241": CINDY_PROFILE}
CARTS = {"cust_88241": CINDY_CART}
FEASIBILITIES = {"pb_welcome_home_24pp": CINDY_FEASIBILITY}
CAMPAIGNS = {"cust_88241": CINDY_CAMPAIGNS}
CAP_STATUSES = {("cust_88241", "email"): CINDY_CAP_STATUS}
TICKETS = {"cust_88241": CINDY_TICKETS}
PROPENSITY_SCORES = {("cust_88241", "cart_recovery"): CINDY_PROPENSITY}
SEND_TIMES = {"cust_88241": CINDY_SEND_TIME}
