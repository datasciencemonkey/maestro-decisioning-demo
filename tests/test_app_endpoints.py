"""Systematic endpoint tests for the deployed Databricks App.

Tests each endpoint independently to identify exactly which parts work
and which fail. Run locally against the live app URL.

Usage:
    uv run pytest tests/test_app_endpoints.py -v -s
"""

import os
import time

import pytest
import requests
from databricks.sdk import WorkspaceClient

APP_URL = "https://maestro-cdp-demo-7474645105283837.aws.databricksapps.com"
PROFILE = "9cefok"


@pytest.fixture(scope="module")
def auth_headers():
    """Get auth headers for the deployed app using workspace token."""
    w = WorkspaceClient(profile=PROFILE)
    token = w.config.authenticate().get("Authorization", "").replace("Bearer ", "")
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoint:
    """Test /health — should work without any LLM or DB dependencies."""

    def test_health_returns_200(self, auth_headers):
        r = requests.get(f"{APP_URL}/health", headers=auth_headers, timeout=10)
        print(f"  /health → {r.status_code}: {r.text[:200]}")
        assert r.status_code == 200

    def test_health_returns_json(self, auth_headers):
        r = requests.get(f"{APP_URL}/health", headers=auth_headers, timeout=10)
        data = r.json()
        assert data["status"] == "ok"
        assert data["service"] == "maestro-cdp"


class TestIndexEndpoint:
    """Test / — should return the HTML demo page."""

    def test_index_returns_html(self, auth_headers):
        r = requests.get(f"{APP_URL}/", headers=auth_headers, timeout=10)
        print(f"  / → {r.status_code}, content-type: {r.headers.get('content-type', 'N/A')}")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_index_contains_demo_ui(self, auth_headers):
        r = requests.get(f"{APP_URL}/", headers=auth_headers, timeout=10)
        assert "Maestro CDP" in r.text
        assert "Run Cart Recovery for Cindy" in r.text


class TestAgentEndpoint:
    """Test /api/run — the core agent endpoint. Most likely to fail."""

    def test_run_returns_response(self, auth_headers):
        """Just check we get a response (200 or detailed error, not a crash)."""
        r = requests.post(f"{APP_URL}/api/run", headers=auth_headers, timeout=120)
        print(f"  /api/run → {r.status_code}: {r.text[:500]}")
        # We expect either 200 (success) or 500 with a JSON error detail
        assert r.status_code in (200, 500)
        # If 500, the error should be JSON with a detail field (our error handling)
        if r.status_code == 500:
            data = r.json()
            assert "detail" in data, f"500 without detail: {r.text[:200]}"
            print(f"  Error detail: {data['detail'][:300]}")
            pytest.fail(f"Agent endpoint failed: {data['detail'][:200]}")

    def test_run_returns_valid_artifact(self, auth_headers):
        """If the agent succeeds, validate the response structure."""
        r = requests.post(f"{APP_URL}/api/run", headers=auth_headers, timeout=120)
        if r.status_code != 200:
            pytest.skip(f"Agent returned {r.status_code}, skipping structure validation")
        data = r.json()
        assert "artifact" in data
        assert "campaigns" in data
        assert "latency_s" in data
        artifact = data["artifact"]
        assert artifact["customer_id"] == "cust_88241"
        assert artifact["verdict"] is not None
        assert len(artifact["decisions"]) >= 3
        assert len(artifact["contributing_signals"]) >= 2
        assert len(artifact["rationale"]) > 20
        print(f"  Verdict: {artifact['verdict']}")
        print(f"  Decisions: {len(artifact['decisions'])}")
        print(f"  Latency: {data['latency_s']:.2f}s")

    def test_run_suppresses_spring_seasonal(self, auth_headers):
        """Agent must suppress Spring Seasonal due to frequency cap breach."""
        r = requests.post(f"{APP_URL}/api/run", headers=auth_headers, timeout=120)
        if r.status_code != 200:
            pytest.skip(f"Agent returned {r.status_code}")
        decisions = r.json()["artifact"]["decisions"]
        suppress = [d for d in decisions if d["type"] == "suppress_from"]
        assert len(suppress) >= 1, "No suppress_from decision found"
        targets = " ".join((d.get("target") or "").lower() for d in suppress)
        assert any(t in targets for t in ["spring", "seasonal", "campaign_sp", "sp_2026"]), \
            f"Expected Spring Seasonal suppression, got: {targets}"
