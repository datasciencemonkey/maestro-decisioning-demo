"""Simulated email send — writes to sent_emails table.

In production this would call SendGrid/SES. For the demo,
we write a row to Lakebase to prove the lifecycle completed.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone


def build_send_record(journey_id: str, customer_id: str, email_json: str) -> dict:
    """Build a sent_emails record from composed email content."""
    email = json.loads(email_json)
    return {
        "email_id": f"eml_{uuid.uuid4().hex[:8]}",
        "journey_id": journey_id,
        "customer_id": customer_id,
        "subject": email["subject"],
        "body_html": email["body_html"],
        "channel": "email",
        "status": "delivered",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }


def insert_sent_email(record: dict, conn_params: dict) -> str:
    """Insert a sent_emails row into Lakebase. Returns email_id."""
    import psycopg2

    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sent_emails (email_id, journey_id, customer_id, subject,
            body_html, channel, status, sent_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email_id) DO NOTHING""",
        (
            record["email_id"],
            record["journey_id"],
            record["customer_id"],
            record["subject"],
            record["body_html"],
            record["channel"],
            record["status"],
            record["sent_at"],
        ),
    )
    cur.close()
    conn.close()
    return record["email_id"]
