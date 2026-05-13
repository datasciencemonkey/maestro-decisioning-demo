"""Re-evaluation step — checks for context changes after DBOS sleep.

After the durable sleep, re-reads customer signals to detect if anything
changed during the wait window. In demo: synthetic data is unchanged, so
always returns "proceed". In production: would detect purchase completion,
new support tickets, or frequency cap changes.
"""

from __future__ import annotations

import json

from maestro.synthetic import (
    CAP_STATUSES,
    CARTS,
    PROFILES,
    TICKETS,
)


def re_evaluate_context(journey_id: str, artifact_json: str) -> dict:
    """Re-check customer context after sleep window.

    Compares current state against the original decision signals.
    Returns dict with: action, reason, changes_detected, updated_artifact.
    """
    artifact = json.loads(artifact_json)
    customer_id = artifact.get("customer_id", "")
    changes: list[str] = []

    # Check 1: Has the customer completed the purchase?
    cart = CARTS.get(customer_id)
    if cart and hasattr(cart, "status") and cart.status == "completed":
        changes.append("purchase_completed")

    # Check 2: Any new support tickets?
    tickets = TICKETS.get(customer_id, [])
    original_signals = artifact.get("contributing_signals", [])
    original_ticket_signal = next(
        (s for s in original_signals if s.get("signal") == "support_tickets"), None
    )
    if tickets and (not original_ticket_signal or original_ticket_signal.get("value") == "none recent"):
        changes.append("new_support_ticket")

    # Check 3: Frequency cap changed?
    cap_key = (customer_id, "email")
    cap = CAP_STATUSES.get(cap_key)
    if cap and cap.status == "ok":
        # Cap was breach at decision time but now ok — something changed
        original_cap = next(
            (s for s in original_signals if "frequency" in s.get("signal", "")), None
        )
        if original_cap and original_cap.get("value") == "breach":
            changes.append("frequency_cap_resolved")

    # Check 4: Profile still exists and consented?
    profile = PROFILES.get(customer_id)
    if not profile or not profile.consent_email:
        changes.append("consent_revoked")

    # Determine action
    if not changes:
        return {
            "action": "proceed",
            "reason": "No changes detected since decision — proceeding with email composition",
            "changes_detected": [],
            "updated_artifact": None,
        }

    if "purchase_completed" in changes or "consent_revoked" in changes:
        return {
            "action": "abort",
            "reason": f"Cannot proceed: {', '.join(changes)}",
            "changes_detected": changes,
            "updated_artifact": None,
        }

    return {
        "action": "adjust",
        "reason": f"Context changed: {', '.join(changes)} — adjusting decision",
        "changes_detected": changes,
        "updated_artifact": artifact_json,  # In production: would re-run agent
    }
