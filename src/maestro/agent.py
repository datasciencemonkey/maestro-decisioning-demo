"""Maestro CDP agent — cross-campaign disposition reasoning.

Single supervisor agent that reasons across 9 domains given a
cart_abandoned event. Produces a structured DecisionArtifact
with verdict, decisions, contributing signals, and rationale.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai_skills import SkillsCapability

from maestro.models import (
    Campaign,
    CapStatus,
    Cart,
    CartAbandonedEvent,
    DecisionArtifact,
    Feasibility,
    JourneyHandle,
    Profile,
    Score,
    SendTimestamp,
    Ticket,
)
from maestro.synthetic import (
    CAMPAIGNS,
    CAP_STATUSES,
    CARTS,
    FEASIBILITIES,
    PROFILES,
    PROPENSITY_SCORES,
    SEND_TIMES,
    TICKETS,
)

# ── Dependencies ────────────────────────────────────────────────────────────


@dataclass
class MaestroDeps:
    """Runtime dependencies injected into every tool via RunContext."""

    customer_id: str
    event: CartAbandonedEvent
    db_url: str | None = None


# ── System Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are the agentic CDP disposition engine for Fluttershy, a print-on-demand
photo product brand. A cart_abandoned event has fired.

YOUR GOAL: Decide how to engage this customer for cart recovery, balancing:
  • Their context (profile, cart, support history)
  • Operational constraints (production calendar, frequency caps, consent)
  • Likelihood of conversion (propensity score)
  • Optimal timing (send-time model + quiet-hours policy)

REASONING APPROACH — this is critical:
  1. Start by understanding WHO the customer is (profile) and WHAT they left
     behind (cart). These inform every subsequent decision.
  2. Check operational constraints — can we even fulfill this order? Are there
     campaign conflicts? Would another send breach frequency caps?
  3. Assess likelihood and timing — how likely is recovery? When should we act?
  4. YOU DECIDE the order of tool calls based on what you learn. When a tool's
     output makes a subsequent tool unnecessary, SKIP it and explain why.
  5. When two signals contradict (e.g., customer is in an active campaign AND
     frequency cap would breach), reconcile them explicitly — state the
     conflict, your resolution, and why.

DECISION OUTPUT:
When you have enough information, produce a DecisionArtifact with:
  • verdict: your overall recommendation (e.g., "re-prioritize", "suppress",
    "proceed", "defer")
  • decisions: specific actions — each with type, target/value, and reason:
    - suppress_from: remove customer from a lower-priority campaign
    - prioritize_in: elevate a campaign for this customer
    - tone: communication style (warm/personal, professional, empathetic)
    - send_time: when to send, with timezone
    - channel: communication channel (email, sms, push)
  • contributing_signals: each signal that influenced your decision, with weight
  • rationale: one paragraph, human-legible, explaining your reasoning chain

After deciding, call persist_journey_state with the decided send_time as due_ts
to hand off to the durable journey workflow.

IMPORTANT CONSTRAINTS:
  • Never schedule sends during quiet hours (typically 9 PM – 7 AM customer tz)
  • Never breach frequency caps — suppress lower-priority campaigns instead
  • Never use a channel without active consent
  • A triggered campaign always outranks a scheduled campaign

CDP DOMAIN KNOWLEDGE:
  Campaign Priority: triggered > active/scheduled > paused > dormant
  Frequency Cap Resolution: suppress lower-priority campaign, never the triggered one
  Quiet Hours: 9 PM – 7 AM in customer timezone; shift to next 8 AM
  Tone: pet owner → warm/personal with pet name; repeat buyer → familiar; new → welcoming
  Channel: consent is non-negotiable; prefer customer's stated preference
  Signal Weights: frequency_cap=1.0 (hard), propensity=0.6-0.8, support=0.3-0.5, feasibility=0.3-0.5
"""


# ── Agent Construction ──────────────────────────────────────────────────────


def create_agent(model) -> Agent[MaestroDeps, DecisionArtifact]:
    """Create the Maestro CDP agent with all tools registered."""

    maestro_agent = Agent(
        model,
        output_type=DecisionArtifact,
        deps_type=MaestroDeps,
        instructions=SYSTEM_PROMPT,
        name="maestro-cdp",
        retries=1,
        capabilities=[SkillsCapability(directories=["./app_skills"])],
    )

    # ── Tool Registration ───────────────────────────────────────────────

    @maestro_agent.tool
    async def read_profile(
        ctx: RunContext[MaestroDeps], customer_id: str
    ) -> Profile:
        """Read the customer profile — demographics, pet info, timezone,
        channel preferences, consent status, and loyalty tier."""
        if customer_id in PROFILES:
            return PROFILES[customer_id]
        raise ValueError(f"Unknown customer: {customer_id}")

    @maestro_agent.tool
    async def read_cart(
        ctx: RunContext[MaestroDeps], customer_id: str
    ) -> Cart:
        """Read the abandoned cart — items, total value, and when it was
        abandoned."""
        if customer_id in CARTS:
            return CARTS[customer_id]
        raise ValueError(f"No abandoned cart for: {customer_id}")

    @maestro_agent.tool
    async def check_production_feasibility(
        ctx: RunContext[MaestroDeps], product_id: str, ship_by: str
    ) -> Feasibility:
        """Check if a product can be produced and shipped by the requested
        date. Returns production days and feasibility status."""
        if product_id in FEASIBILITIES:
            return FEASIBILITIES[product_id]
        raise ValueError(f"Unknown product: {product_id}")

    @maestro_agent.tool
    async def list_active_campaigns(
        ctx: RunContext[MaestroDeps], customer_id: str
    ) -> list[Campaign]:
        """List all campaigns this customer is enrolled in — with status
        (active, triggered, paused, dormant), scheduled sends, and channels."""
        return CAMPAIGNS.get(customer_id, [])

    @maestro_agent.tool
    async def check_frequency_cap(
        ctx: RunContext[MaestroDeps],
        customer_id: str,
        channel: str,
        window_days: int,
    ) -> CapStatus:
        """Check if sending on this channel would breach the frequency cap.
        Returns current count, queued count, cap limit, and breach status."""
        key = (customer_id, channel)
        if key in CAP_STATUSES:
            return CAP_STATUSES[key]
        return CapStatus(
            customer_id=customer_id, channel=channel,
            cap=3, current=0, queued=0, status="ok", window_days=window_days,
        )

    @maestro_agent.tool
    async def read_support_tickets(
        ctx: RunContext[MaestroDeps],
        customer_id: str,
        lookback_days: int,
    ) -> list[Ticket]:
        """Read recent support tickets to detect friction. Empty list means
        no recent issues — a positive signal for engagement."""
        return TICKETS.get(customer_id, [])

    @maestro_agent.tool
    async def score_propensity(
        ctx: RunContext[MaestroDeps], customer_id: str, intent: str
    ) -> Score:
        """Score the customer's likelihood of converting on the given intent.
        Returns a 0-1 propensity score from the model serving endpoint."""
        key = (customer_id, intent)
        if key in PROPENSITY_SCORES:
            return PROPENSITY_SCORES[key]
        return Score(
            customer_id=customer_id, intent=intent,
            score=0.5, model_version="default", confidence=0.5,
        )

    @maestro_agent.tool
    async def optimal_send_time(
        ctx: RunContext[MaestroDeps],
        customer_id: str,
        cohort: str,
        propensity: float,
    ) -> SendTimestamp:
        """Calculate the optimal send time, adjusted for quiet hours and
        customer timezone. Returns the recommended timestamp with reasoning."""
        if customer_id in SEND_TIMES:
            return SEND_TIMES[customer_id]
        raise ValueError(f"No send time data for: {customer_id}")

    @maestro_agent.tool
    async def persist_journey_state(
        ctx: RunContext[MaestroDeps],
        customer_id: str,
        step: str,
        due_ts: str,
        blob: dict,
    ) -> JourneyHandle:
        """Persist journey state to Lakebase for durable execution. This
        creates the handoff point for the DBOS workflow to pick up later."""
        import uuid

        journey_id = f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}"
        return JourneyHandle(
            journey_id=journey_id,
            customer_id=customer_id,
            step=step,
            due_ts=due_ts,
            status="pending",
        )

    return maestro_agent


# ── Runner ──────────────────────────────────────────────────────────────────


async def run_maestro(
    event: CartAbandonedEvent,
    model,
    db_url: str | None = None,
) -> DecisionArtifact:
    """Run the Maestro agent on a cart_abandoned event.

    Returns a structured DecisionArtifact with verdict, decisions,
    contributing signals, and rationale.
    """
    agent = create_agent(model)
    deps = MaestroDeps(
        customer_id=event.customer_id,
        event=event,
        db_url=db_url,
    )

    prompt = (
        f"Cart abandoned event for customer {event.customer_id}. "
        f"Cart ID: {event.cart_id}. "
        f"Items: {[item.model_dump() for item in event.items]}. "
        f"Total: ${event.cart_total:.2f}. "
        f"Abandoned at: {event.abandoned_at.isoformat()}. "
        f"Evaluate this customer for cart recovery disposition."
    )

    result = await agent.run(prompt, deps=deps)
    return result.output
