"""CDP domain tools for the Maestro agent.

Each tool is an async function returning a typed Pydantic model.
Phase A: returns synthetic data from maestro.synthetic lookups.
Phase B+: will query UC tables via Databricks SQL.
"""

from maestro.models import (
    Campaign, CapStatus, Cart, Feasibility, JourneyHandle,
    Profile, Score, SendTimestamp, Ticket,
)
from maestro.synthetic import (
    CAMPAIGNS, CAP_STATUSES, CARTS, FEASIBILITIES,
    PROFILES, PROPENSITY_SCORES, SEND_TIMES, TICKETS,
)


async def read_profile(customer_id: str) -> Profile:
    """Read customer profile from UC customers table.

    Returns demographics, pet info, timezone, channel preferences,
    consent status, and loyalty tier.
    """
    if customer_id in PROFILES:
        return PROFILES[customer_id]
    raise ValueError(f"Unknown customer: {customer_id}")


async def read_cart(customer_id: str) -> Cart:
    """Read the abandoned cart contents from UC orders + order_items tables.

    Returns cart items, total value, and abandonment timestamp.
    """
    if customer_id in CARTS:
        return CARTS[customer_id]
    raise ValueError(f"No abandoned cart for customer: {customer_id}")


async def check_production_feasibility(product_id: str, ship_by: str) -> Feasibility:
    """Check if a product can be produced and shipped by the requested date.

    Queries the UC production_calendar table for lead times and capacity.

    Args:
        product_id: The product identifier (e.g., pb_welcome_home_24pp)
        ship_by: ISO date string for requested ship-by date
    """
    if product_id in FEASIBILITIES:
        return FEASIBILITIES[product_id]
    raise ValueError(f"Unknown product: {product_id}")


async def list_active_campaigns(customer_id: str) -> list[Campaign]:
    """List all active campaigns the customer is enrolled in.

    Queries UC campaigns + campaign_membership tables. Returns campaigns
    with their status (active, triggered, paused, dormant), scheduled
    send times, and channels.
    """
    if customer_id in CAMPAIGNS:
        return CAMPAIGNS[customer_id]
    return []


async def check_frequency_cap(customer_id: str, channel: str, window_days: int) -> CapStatus:
    """Check if sending on the given channel would breach the frequency cap.

    Aggregates recent + queued sends from UC campaigns for the customer
    within the specified window.

    Args:
        customer_id: The customer identifier
        channel: Communication channel (email, sms, push)
        window_days: Rolling window in days to check (typically 7)
    """
    key = (customer_id, channel)
    if key in CAP_STATUSES:
        return CAP_STATUSES[key]
    # Default: no cap data means OK
    return CapStatus(
        customer_id=customer_id, channel=channel,
        cap=3, current=0, queued=0, status="ok", window_days=window_days,
    )


async def read_support_tickets(customer_id: str, lookback_days: int) -> list[Ticket]:
    """Read recent support tickets for friction detection.

    Queries UC support_tickets table for the last N days.

    Args:
        customer_id: The customer identifier
        lookback_days: Number of days to look back (typically 30)
    """
    if customer_id in TICKETS:
        return TICKETS[customer_id]
    return []


async def score_propensity(customer_id: str, intent: str) -> Score:
    """Score the customer's likelihood of converting on the given intent.

    Calls the Model Serving endpoint (Phase A: returns cached synthetic score).

    Args:
        customer_id: The customer identifier
        intent: The conversion intent (e.g., cart_recovery, seasonal_purchase)
    """
    key = (customer_id, intent)
    if key in PROPENSITY_SCORES:
        return PROPENSITY_SCORES[key]
    # Default: moderate propensity
    return Score(
        customer_id=customer_id, intent=intent,
        score=0.5, model_version="default", confidence=0.5,
    )


async def optimal_send_time(customer_id: str, cohort: str, propensity: float) -> SendTimestamp:
    """Calculate the optimal send time for this customer.

    Uses the send-time model output, adjusted for quiet hours
    and customer timezone.

    Args:
        customer_id: The customer identifier
        cohort: Engagement cohort (e.g., morning_engaged)
        propensity: The propensity score (for urgency weighting)
    """
    if customer_id in SEND_TIMES:
        return SEND_TIMES[customer_id]
    raise ValueError(f"No send time data for customer: {customer_id}")


async def persist_journey_state(
    customer_id: str, step: str, due_ts: str, blob: dict
) -> JourneyHandle:
    """Persist journey state to Lakebase for durable execution.

    Creates or updates a row in the journey_state table. This is the
    handoff point to Beat 2.5 -- the DBOS workflow will pick up from here.

    Args:
        customer_id: The customer identifier
        step: Current journey step (e.g., awaiting_send)
        due_ts: ISO timestamp for when the next action is due
        blob: JSON-serializable state blob (decision artifact, context)
    """
    import uuid
    journey_id = f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}"

    # Phase A: return handle without actual DB write
    # (DB write happens in the DBOS workflow layer in workflow.py)
    return JourneyHandle(
        journey_id=journey_id,
        customer_id=customer_id,
        step=step,
        due_ts=due_ts,
        status="pending",
    )
