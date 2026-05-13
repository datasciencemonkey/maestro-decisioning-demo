# tests/test_re_evaluate.py
import json


def test_re_evaluate_no_changes():
    """Re-evaluation with unchanged synthetic data should return 'proceed'."""
    from maestro.re_evaluate import re_evaluate_context

    artifact = {
        "customer_id": "cust_88241",
        "decisions": [
            {"type": "suppress_from", "target": "campaign_sp_2026"},
            {"type": "channel", "target": "email"},
        ],
        "contributing_signals": [
            {"signal": "frequency_cap", "value": "breach", "weight": 1.0},
        ],
    }
    result = re_evaluate_context("jrn_test", json.dumps(artifact))
    assert result["action"] == "proceed"
    assert result["changes_detected"] == []
    assert "No changes" in result["reason"]


def test_re_evaluate_returns_valid_structure():
    """Result should have all required keys."""
    from maestro.re_evaluate import re_evaluate_context

    artifact = {"customer_id": "cust_88241", "decisions": [], "contributing_signals": []}
    result = re_evaluate_context("jrn_test", json.dumps(artifact))
    assert "action" in result
    assert "reason" in result
    assert "changes_detected" in result
    assert result["action"] in ("proceed", "abort", "adjust")
