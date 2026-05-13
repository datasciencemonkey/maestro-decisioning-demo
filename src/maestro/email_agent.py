"""Copywriter agent — composes personalized cart recovery emails.

Separate from the reasoning agent. Takes the DecisionArtifact context
and produces branded email content with Fluttershy theming.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from maestro.models import Cart, EmailContent, Profile


# ── System Prompt ──────────────────────────────────────────────────────────

COPYWRITER_PROMPT = """\
You are a DTC email copywriter for Fluttershy, a premium pet photo products brand.

Write a warm, personal cart recovery email. Rules:
  - Subject line: under 50 characters, mention the pet by name if available
  - Body: under 100 words, conversational, mention the specific product left behind
  - Tone: {tone} — match the customer's relationship with the brand
  - Use the pet's name naturally (not forced). If no pet, focus on the product.
  - Include one clear CTA. Never use urgency tactics, guilt, or countdown timers.
  - The hero image URL is: {hero_image_url}
  - CTA URL is: https://fluttershy.com/cart/resume?cid={customer_id}

Write the body_html as a simple HTML fragment (no full document, no <html> tags).
Use <h1> for greeting, <p> for body, styled simply. The email template wrapper
handles the outer chrome.
"""


# ── Dependencies ───────────────────────────────────────────────────────────


@dataclass
class CopywriterDeps:
    customer_id: str
    profile: Profile
    cart: Cart
    tone: str
    hero_image_url: str


# ── Agent Construction ─────────────────────────────────────────────────────


def create_copywriter_agent(model) -> Agent[CopywriterDeps, EmailContent]:
    """Create the copywriter agent."""
    return Agent(
        model,
        output_type=EmailContent,
        deps_type=CopywriterDeps,
        instructions=COPYWRITER_PROMPT,
        name="fluttershy-copywriter",
        retries=1,
    )


# ── Prompt Builder ─────────────────────────────────────────────────────────


def build_email_prompt(artifact: dict, profile: Profile, cart: Cart) -> str:
    """Build the user prompt for the copywriter agent from decision context."""
    decisions = artifact.get("decisions", [])
    tone_decision = next((d for d in decisions if d.get("type") == "tone"), None)
    tone = tone_decision.get("value", "warm + personal") if tone_decision else "warm + personal"

    items_desc = ", ".join(
        f"{item.product_id} (${item.price:.2f})" for item in cart.items
    )

    return (
        f"Write a cart recovery email for {profile.name} "
        f"(customer ID: {profile.customer_id}).\n\n"
        f"Pet: {profile.pet_name or 'none'} ({profile.pet_type or 'n/a'})\n"
        f"Loyalty tier: {profile.loyalty_tier}\n"
        f"Cart items: {items_desc}\n"
        f"Cart total: ${cart.total:.2f}\n"
        f"Tone: {tone}\n"
        f"Hero image: /whiskers.jpg\n"
        f"CTA URL: https://fluttershy.com/cart/resume?cid={profile.customer_id}\n"
    )


# ── Runner ─────────────────────────────────────────────────────────────────


async def compose_email(
    artifact_json: str,
    model,
) -> EmailContent:
    """Compose a personalized email from the decision artifact context.

    Uses synthetic data to look up profile/cart, then runs the copywriter agent.
    """
    from maestro.synthetic import CARTS, PROFILES

    artifact = json.loads(artifact_json)
    customer_id = artifact.get("customer_id", "cust_88241")
    profile = PROFILES.get(customer_id)
    cart = CARTS.get(customer_id)

    if not profile or not cart:
        raise ValueError(f"No profile/cart for customer: {customer_id}")

    decisions = artifact.get("decisions", [])
    tone_decision = next((d for d in decisions if d.get("type") == "tone"), None)
    tone = tone_decision.get("value", "warm + personal") if tone_decision else "warm + personal"

    agent = create_copywriter_agent(model)
    deps = CopywriterDeps(
        customer_id=customer_id,
        profile=profile,
        cart=cart,
        tone=tone,
        hero_image_url="/whiskers.jpg",
    )
    prompt = build_email_prompt(artifact, profile, cart)
    result = await agent.run(prompt, deps=deps)
    return result.output
