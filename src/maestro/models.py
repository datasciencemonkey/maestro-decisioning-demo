"""Pydantic models for the Maestro CDP agent loop."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


# ── Input Event ──────────────────────────────────────────────────────────────


class CartItem(BaseModel):
    product_id: str
    qty: int
    price: float


class CartAbandonedEvent(BaseModel):
    event_type: Literal["cart_abandoned"] = "cart_abandoned"
    customer_id: str
    cart_id: str
    abandoned_at: datetime
    cart_total: float
    items: list[CartItem]
    source_session_id: str | None = None
    tier1_clearance: bool = True


# ── Tool Return Types ────────────────────────────────────────────────────────


class Profile(BaseModel):
    customer_id: str
    name: str
    email: str
    pet_name: str | None = None
    pet_type: str | None = None
    timezone: str
    preferred_channel: str
    consent_email: bool
    consent_sms: bool
    is_repeat_buyer: bool
    loyalty_tier: str
    quiet_hours_start: int  # hour 0-23
    quiet_hours_end: int  # hour 0-23


class Cart(BaseModel):
    cart_id: str
    customer_id: str
    items: list[CartItem]
    total: float
    created_at: datetime
    abandoned_at: datetime


class Feasibility(BaseModel):
    product_id: str
    feasible: bool
    production_days: int
    ship_by_achievable: bool
    reason: str


class Campaign(BaseModel):
    campaign_id: str
    name: str
    campaign_type: str
    status: Literal["active", "triggered", "paused", "dormant"]
    scheduled_send: datetime | None = None
    channel: str


class CapStatus(BaseModel):
    customer_id: str
    channel: str
    cap: int
    current: int
    queued: int
    status: Literal["ok", "warning", "breach"]
    window_days: int


class Ticket(BaseModel):
    ticket_id: str
    customer_id: str
    subject: str
    status: str
    priority: str
    created_at: datetime
    resolved_at: datetime | None = None


class Score(BaseModel):
    customer_id: str
    intent: str
    score: float
    model_version: str
    confidence: float


class SendTimestamp(BaseModel):
    customer_id: str
    optimal_ts: datetime
    cohort: str
    adjusted_for_quiet_hours: bool
    original_ts: datetime
    reason: str


class JourneyHandle(BaseModel):
    journey_id: str
    customer_id: str
    step: str
    due_ts: str
    status: Literal["pending", "in_progress", "completed", "failed"]


# ── Decision Output ──────────────────────────────────────────────────────────


class Decision(BaseModel):
    type: str  # suppress_from, prioritize_in, tone, send_time, channel
    target: str | None = None
    value: str | None = None
    weight: float | None = None
    reason: str | None = None


class ContributingSignal(BaseModel):
    signal: str
    value: Any
    weight: float


class DecisionArtifact(BaseModel):
    decision_id: str
    customer_id: str
    journey_id: str
    trigger_event_id: str
    verdict: str
    decisions: list[Decision]
    contributing_signals: list[ContributingSignal]
    rationale: str
    trace_id: str | None = None
    created_at: datetime


# ── Email Output (Beat 3) ──────────────────────────────────────────────────


class EmailContent(BaseModel):
    subject: str
    body_html: str
    body_text: str
    hero_image_url: str
    cta_text: str
    cta_url: str


class ReEvaluationResult(BaseModel):
    action: Literal["proceed", "abort", "adjust"]
    reason: str
    changes_detected: list[str]
    updated_artifact: str | None = None
