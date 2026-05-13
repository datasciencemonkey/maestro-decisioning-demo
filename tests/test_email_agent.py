"""Tests for the copywriter email agent."""
import json

import pytest


def test_email_agent_creates_valid_prompt():
    """Verify the copywriter agent builds the right prompt from context."""
    from maestro.email_agent import build_email_prompt
    from maestro.synthetic import CINDY_PROFILE, CINDY_CART

    artifact = {
        "customer_id": "cust_88241",
        "verdict": "re-prioritize",
        "decisions": [
            {"type": "tone", "value": "warm + personal", "reason": "Pet context"},
            {"type": "channel", "target": "email"},
        ],
    }

    prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
    assert "Cindy" in prompt
    assert "Whiskers" in prompt
    assert "photo book" in prompt.lower() or "42" in prompt
    assert "warm" in prompt.lower()


def test_email_content_model_from_dict():
    """Verify EmailContent can be built from a typical agent output."""
    from maestro.models import EmailContent

    data = {
        "subject": "Whiskers misses their photo book!",
        "body_html": "<h1>Hi Cindy</h1><p>We saved your cart.</p>",
        "body_text": "Hi Cindy, we saved your cart.",
        "hero_image_url": "/whiskers.jpg",
        "cta_text": "Complete Your Order",
        "cta_url": "https://fluttershy.com/cart/resume",
    }
    email = EmailContent(**data)
    assert email.subject == "Whiskers misses their photo book!"
    assert len(email.body_text) > 0


def test_copywriter_system_prompt():
    """Verify the system prompt includes brand and constraints."""
    from maestro.email_agent import COPYWRITER_PROMPT

    assert "Fluttershy" in COPYWRITER_PROMPT
    assert "50 char" in COPYWRITER_PROMPT.lower() or "50" in COPYWRITER_PROMPT
    assert "100 word" in COPYWRITER_PROMPT.lower() or "100" in COPYWRITER_PROMPT
