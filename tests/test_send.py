"""Tests for simulated email send."""
import json


def test_build_send_record():
    """Verify send record has all required fields."""
    from maestro.send import build_send_record

    email_data = {
        "subject": "Whiskers misses you!",
        "body_html": "<h1>Hi</h1>",
        "body_text": "Hi",
        "hero_image_url": "/whiskers.jpg",
        "cta_text": "Order Now",
        "cta_url": "https://fluttershy.com/cart/resume",
    }
    record = build_send_record("jrn_test_123", "cust_88241", json.dumps(email_data))
    assert record["journey_id"] == "jrn_test_123"
    assert record["customer_id"] == "cust_88241"
    assert record["subject"] == "Whiskers misses you!"
    assert record["status"] == "delivered"
    assert "email_id" in record
    assert record["email_id"].startswith("eml_")
