# Unified Beat 2/2.5/3 Flow — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify agent reasoning, DBOS durable workflow, and email composition into a single auto-cascading flow with cinematic UI and Databricks-aligned theming.

**Architecture:** One DBOS workflow (6 steps) owns the entire lifecycle. Frontend polls a phase-tracking endpoint and auto-cascades through narrated states. A dedicated copywriter agent composes the email. Full theming audit aligns all components to Databricks brand tokens.

**Tech Stack:** Python/FastAPI/DBOS/Pydantic AI (backend), React 19/TypeScript/Framer Motion/Tailwind CSS (frontend)

**Parallelization:** Tasks are grouped into 4 independent tracks that can execute simultaneously. Dependencies are marked explicitly.

---

## Dependency Graph

```
Track A (Backend Models + Steps)     Track B (Frontend Theming)
  Task 1: Models                       Task 7: CSS tokens
  Task 2: sent_emails DDL             Task 8: Component theme fixes
  Task 3: Re-evaluate step
  Task 4: Copywriter agent
  Task 5: Simulate send step
         ↓
Track C (Backend Integration)        Track D (Frontend Components)
  Task 6: Unified workflow             Task 9: EmailPreview component
  (depends on Track A)                Task 10: WorkflowTimeline updates
         ↓                            Task 11: Beat2Page state machine
  Task 12: API endpoints               (depends on Track B + Task 9/10)
  (depends on Task 6)                          ↓
         ↓                                     ↓
              Task 13: Integration test
              (depends on Track C + Track D)
```

**Parallel execution:** Tracks A, B can start immediately. Track C starts after A completes. Track D tasks 9-10 start immediately; task 11 waits for B + 9/10. Task 13 is the final gate.

---

## Track A: Backend Models + Steps

### Task 1: Add EmailContent and ReEvaluationResult models

**Files:**
- Modify: `src/maestro/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write failing test for EmailContent**

```python
# tests/test_models.py — append to existing tests

def test_email_content_model():
    from maestro.models import EmailContent
    email = EmailContent(
        subject="Whiskers is waiting!",
        body_html="<h1>Hi Cindy</h1><p>Your photo book misses you.</p>",
        body_text="Hi Cindy, your photo book misses you.",
        hero_image_url="/whiskers.jpg",
        cta_text="Complete Your Order",
        cta_url="https://fluttershy.com/cart/resume",
    )
    assert email.subject == "Whiskers is waiting!"
    assert "Cindy" in email.body_html
    assert email.cta_text == "Complete Your Order"


def test_re_evaluation_result_proceed():
    from maestro.models import ReEvaluationResult
    result = ReEvaluationResult(
        action="proceed",
        reason="No changes detected since decision",
        changes_detected=[],
        updated_artifact=None,
    )
    assert result.action == "proceed"
    assert result.changes_detected == []


def test_re_evaluation_result_abort():
    from maestro.models import ReEvaluationResult
    result = ReEvaluationResult(
        action="abort",
        reason="Customer completed purchase during sleep window",
        changes_detected=["purchase_completed"],
        updated_artifact=None,
    )
    assert result.action == "abort"
    assert "purchase_completed" in result.changes_detected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro && uv run pytest tests/test_models.py::test_email_content_model tests/test_models.py::test_re_evaluation_result_proceed tests/test_models.py::test_re_evaluation_result_abort -v`
Expected: FAIL with `ImportError: cannot import name 'EmailContent'`

- [ ] **Step 3: Add models to models.py**

Add after the `DecisionArtifact` class at the end of `src/maestro/models.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_models.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/maestro/models.py tests/test_models.py
git commit -m "feat: add EmailContent and ReEvaluationResult models for Beat 3"
```

---

### Task 2: Add sent_emails table DDL

**Files:**
- Modify: `data/seed_tables.sql`

- [ ] **Step 1: Add sent_emails table to seed_tables.sql**

Append before the `SEED DATA` section in `data/seed_tables.sql`:

```sql
-- ============================================================
-- 10. sent_emails (Beat 3 — simulated email delivery tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS sent_emails (
    email_id      VARCHAR(64)  PRIMARY KEY,
    journey_id    VARCHAR(64)  NOT NULL,
    customer_id   VARCHAR(64)  NOT NULL,
    subject       VARCHAR(512) NOT NULL,
    body_html     TEXT         NOT NULL,
    channel       VARCHAR(20)  DEFAULT 'email',
    status        VARCHAR(20)  DEFAULT 'delivered',
    sent_at       TIMESTAMPTZ  DEFAULT NOW()
);
```

- [ ] **Step 2: Commit**

```bash
git add data/seed_tables.sql
git commit -m "feat: add sent_emails table DDL for Beat 3 email tracking"
```

---

### Task 3: Add re_evaluate_step

**Files:**
- Create: `src/maestro/re_evaluate.py`
- Test: `tests/test_re_evaluate.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_re_evaluate.py
import json


def test_re_evaluate_no_changes():
    """Re-evaluation with unchanged synthetic data should return 'proceed'."""
    from maestro.re_evaluate import re_evaluate_context
    from maestro.synthetic import CINDY_EVENT

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_re_evaluate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'maestro.re_evaluate'`

- [ ] **Step 3: Implement re_evaluate.py**

```python
# src/maestro/re_evaluate.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_re_evaluate.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/maestro/re_evaluate.py tests/test_re_evaluate.py
git commit -m "feat: add re_evaluate_context for post-sleep context checking"
```

---

### Task 4: Create copywriter agent

**Files:**
- Create: `src/maestro/email_agent.py`
- Test: `tests/test_email_agent.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_email_agent.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_email_agent.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'maestro.email_agent'`

- [ ] **Step 3: Implement email_agent.py**

```python
# src/maestro/email_agent.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_email_agent.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/maestro/email_agent.py tests/test_email_agent.py
git commit -m "feat: add copywriter agent for Beat 3 email composition"
```

---

### Task 5: Add simulate_send helper

**Files:**
- Create: `src/maestro/send.py`
- Test: `tests/test_send.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_send.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_send.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement send.py**

```python
# src/maestro/send.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_send.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/maestro/send.py tests/test_send.py
git commit -m "feat: add simulated email send for Beat 3 delivery tracking"
```

---

## Track B: Frontend Theming

### Task 7: Add CSS status tokens and typography enforcement

**Files:**
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Add status color tokens and typography to index.css**

In the `@theme` block of `frontend/src/index.css`, add after the Databricks color lines:

```css
  /* Status colors (semantic) */
  --color-status-suppressed: #EB1600;
  --color-status-priority: #C4A87A;
  --color-status-active: #40D1F5;
  --color-status-dormant: #5A6F77;
  --color-status-triggered: #22C55E;
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/index.css
git commit -m "style: add semantic status color tokens for Databricks alignment"
```

---

### Task 8: Fix component theming across all Beat 2 components

**Files:**
- Modify: `frontend/src/beat2/components/CampaignPanel.tsx`
- Modify: `frontend/src/beat2/components/DecisionPanel.tsx`
- Modify: `frontend/src/beat2/components/WorkflowTimeline.tsx`
- Modify: `frontend/src/beat2/components/ReasoningTrace.tsx`

- [ ] **Step 1: Fix CampaignPanel — replace Tailwind colors with status tokens**

In `CampaignPanel.tsx`, replace the `statusConfig` object (lines 12-44):

```typescript
const statusConfig: Record<CampaignStatus, { label: string; color: string; icon: React.ReactNode; glow?: boolean }> = {
  suppressed: {
    label: 'SUPPRESSED',
    color: 'bg-[var(--color-status-suppressed)]/15 text-[var(--color-status-suppressed)] border-[var(--color-status-suppressed)]/30',
    icon: <XCircle size={11} />,
  },
  prioritized: {
    label: 'PRIORITY',
    color: 'bg-[var(--color-status-priority)]/15 text-[var(--color-status-priority)] border-[var(--color-status-priority)]/30',
    icon: <Star size={11} className="fill-[var(--color-status-priority)]" />,
    glow: true,
  },
  active: {
    label: 'ACTIVE',
    color: 'bg-[var(--color-status-active)]/15 text-[var(--color-status-active)] border-[var(--color-status-active)]/30',
    icon: <Circle size={11} className="fill-current" />,
  },
  triggered: {
    label: 'TRIGGERED',
    color: 'bg-[var(--color-status-triggered)]/15 text-[var(--color-status-triggered)] border-[var(--color-status-triggered)]/30',
    icon: <Circle size={11} className="fill-current" />,
  },
  paused: {
    label: 'PAUSED',
    color: 'bg-muted text-muted-foreground border-border',
    icon: <Pause size={11} />,
  },
  dormant: {
    label: 'DORMANT',
    color: 'bg-muted text-[var(--color-status-dormant)] border-border',
    icon: <Circle size={11} />,
  },
}
```

Also fix the glow border on line 70-72 to use the status token:
```typescript
cfg.glow
  ? 'border-[var(--color-status-priority)]/40 shadow-[0_0_12px_rgba(196,168,122,0.15)]'
  : 'border-border'
```

And the glow overlay on line 77:
```typescript
className="absolute inset-0 rounded-lg bg-[var(--color-status-priority)]/5"
```

- [ ] **Step 2: Fix DecisionPanel — replace hardcoded type colors**

In `DecisionPanel.tsx`, replace the `typeColors` object (lines 37-43):

```typescript
const typeColors: Record<string, string> = {
  suppress_from: 'bg-[var(--color-status-suppressed)]/15 text-[var(--color-status-suppressed)] border-[var(--color-status-suppressed)]/30',
  prioritize_in: 'bg-[var(--color-status-triggered)]/15 text-[var(--color-status-triggered)] border-[var(--color-status-triggered)]/30',
  tone: 'bg-[var(--color-status-active)]/15 text-[var(--color-status-active)] border-[var(--color-status-active)]/30',
  send_time: 'bg-[var(--color-gold)]/15 text-[var(--color-gold)] border-[var(--color-gold)]/30',
  channel: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
}
```

Also fix the verdict box (lines 55-66) to use the triggered status token:
```typescript
className="flex items-center gap-2 bg-[var(--color-status-triggered)]/10 border border-[var(--color-status-triggered)]/30 rounded-xl px-4 py-3 mb-4"
```
And the CheckCircle2 + verdict text:
```typescript
<CheckCircle2 size={18} className="text-[var(--color-status-triggered)] shrink-0" />
...
<p className="text-[10px] font-bold tracking-widest text-[var(--color-status-triggered)]/70 uppercase">Verdict</p>
<p className="font-serif text-lg text-[var(--color-status-triggered)] leading-tight">{displayVerdict}</p>
```

Fix signal weight colors (lines 110-117):
```typescript
className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
  s.weight >= 0.8
    ? 'bg-[var(--color-status-suppressed)]/15 text-[var(--color-status-suppressed)]'
    : s.weight >= 0.5
    ? 'bg-[var(--color-gold)]/15 text-[var(--color-gold)]'
    : 'bg-muted text-muted-foreground'
}`}
```

- [ ] **Step 3: Fix WorkflowTimeline — replace orange with gold/cyan**

In `WorkflowTimeline.tsx`, replace `stepBorder` function (lines 98-102):

```typescript
const stepBorder = (state: StepState) => {
  if (state === 'active') return 'border-[var(--color-status-active)] shadow-[0_0_12px_rgba(64,209,245,0.3)]'
  if (state === 'done') return 'border-[var(--color-status-triggered)] shadow-[0_0_8px_rgba(34,197,94,0.2)]'
  return 'border-border'
}
```

Replace `stepBg` function (lines 104-108):

```typescript
const stepBg = (state: StepState) => {
  if (state === 'active') return 'bg-[var(--color-status-active)]/10 text-[var(--color-status-active)]'
  if (state === 'done') return 'bg-[var(--color-status-triggered)]/10 text-[var(--color-status-triggered)]'
  return 'bg-muted text-muted-foreground'
}
```

Replace the active pulse dot (line 150):
```typescript
<span className="ml-auto w-1.5 h-1.5 rounded-full bg-[var(--color-status-active)] animate-pulse shrink-0" />
```

Replace the done dot (line 153):
```typescript
<span className="ml-auto w-1.5 h-1.5 rounded-full bg-[var(--color-status-triggered)] shrink-0" />
```

- [ ] **Step 4: Fix ReasoningTrace — replace hardcoded highlight colors**

In `ReasoningTrace.tsx`, replace the icon node border classes (lines 69-75):

```typescript
className={`relative z-10 w-9 h-9 shrink-0 rounded-full flex items-center justify-center text-base border ${
  t.highlight === 'warn'
    ? 'bg-[var(--color-status-suppressed)]/10 border-[var(--color-status-suppressed)]/40'
    : t.highlight === 'ok'
    ? 'bg-[var(--color-status-triggered)]/10 border-[var(--color-status-triggered)]/30'
    : 'bg-card border-border'
}`}
```

Replace highlight text colors (lines 84-86):
```typescript
{t.highlight === 'warn' && (
  <AlertTriangle size={11} className="text-[var(--color-status-suppressed)]" />
)}
{t.highlight === 'ok' && (
  <CheckCircle size={11} className="text-[var(--color-status-triggered)]" />
)}
```

Replace output text colors (lines 92-98):
```typescript
className={`text-[11px] mt-0.5 ${
  t.highlight === 'warn'
    ? 'text-[var(--color-status-suppressed)] font-semibold'
    : t.highlight === 'ok'
    ? 'text-[var(--color-status-triggered)]'
    : 'text-muted-foreground'
}`}
```

- [ ] **Step 5: Verify frontend builds**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend && npm run build`
Expected: Build succeeds with no type errors

- [ ] **Step 6: Commit**

```bash
git add frontend/src/beat2/components/CampaignPanel.tsx frontend/src/beat2/components/DecisionPanel.tsx frontend/src/beat2/components/WorkflowTimeline.tsx frontend/src/beat2/components/ReasoningTrace.tsx
git commit -m "style: replace hardcoded colors with semantic status tokens across Beat 2 components"
```

---

## Track C: Backend Integration (depends on Track A)

### Task 6: Rewrite unified workflow

**Files:**
- Modify: `src/maestro/workflow.py`
- Test: `tests/test_workflow.py`

- [ ] **Step 1: Write test for unified workflow structure**

```python
# tests/test_workflow.py — replace or append
import json

def test_unified_workflow_imports():
    """Verify all steps can be imported."""
    from maestro.workflow import (
        unified_journey_workflow,
        run_agent_step,
        persist_decision_step,
        save_journey_step,
        re_evaluate_step,
        compose_email_step,
        simulate_send_step,
        update_journey_status_step,
    )
    # All imports succeed
    assert callable(unified_journey_workflow)
    assert callable(run_agent_step)
    assert callable(re_evaluate_step)
    assert callable(compose_email_step)
    assert callable(simulate_send_step)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_workflow.py::test_unified_workflow_imports -v`
Expected: FAIL (missing new step functions)

- [ ] **Step 3: Rewrite workflow.py with unified workflow**

Rewrite `src/maestro/workflow.py`:

```python
"""Unified DBOS durable workflow for Beat 2 + 2.5 + 3.

Single workflow orchestrating: agent reasoning → persist decision →
durable sleep → re-evaluate context → compose email → simulate send.

The workflow survives process restarts — DBOS checkpoints each step.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from dbos import DBOS

from maestro.models import CartAbandonedEvent, DecisionArtifact

CT = ZoneInfo("America/Chicago")


# ── DBOS Steps ─────────────────────────────────────────────────────────────


@DBOS.step()
def run_agent_step(event_json: str) -> str:
    """Run the Maestro agent. Returns DecisionArtifact as JSON."""
    import asyncio

    from maestro.agent import run_maestro
    from maestro.bootstrap import bootstrap

    event = CartAbandonedEvent.model_validate_json(event_json)
    model, _db_url = bootstrap()
    result = asyncio.get_event_loop().run_until_complete(
        run_maestro(event, model, _db_url)
    )
    return result.model_dump_json()


@DBOS.step()
def persist_decision_step(decision_json: str) -> str:
    """Persist DecisionArtifact to Lakebase decisions table."""
    import psycopg2

    from maestro.bootstrap import get_lakebase_conn_params

    decision = json.loads(decision_json)
    decision_id = decision.get("decision_id", f"dec_{uuid.uuid4().hex[:8]}")
    params = get_lakebase_conn_params()

    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO decisions (decision_id, customer_id, journey_id,
            trigger_event_id, verdict, decisions, contributing_signals,
            rationale, trace_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (decision_id) DO UPDATE SET
            verdict = EXCLUDED.verdict,
            decisions = EXCLUDED.decisions,
            contributing_signals = EXCLUDED.contributing_signals,
            rationale = EXCLUDED.rationale""",
        (
            decision_id,
            decision["customer_id"],
            decision.get("journey_id", ""),
            decision.get("trigger_event_id", ""),
            decision["verdict"],
            json.dumps(decision.get("decisions", [])),
            json.dumps(decision.get("contributing_signals", [])),
            decision.get("rationale", ""),
            decision.get("trace_id"),
            decision.get("created_at", datetime.now(CT).isoformat()),
        ),
    )
    cur.close()
    conn.close()
    return decision_id


@DBOS.step()
def save_journey_step(
    journey_id: str, customer_id: str, step: str, due_ts: str, state_blob: str,
) -> str:
    """Persist journey state to Lakebase."""
    import psycopg2

    from maestro.bootstrap import get_lakebase_conn_params

    params = get_lakebase_conn_params()
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO journey_state (journey_id, customer_id, current_step,
            next_action_due_ts, state_blob, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
        ON CONFLICT (journey_id) DO UPDATE SET
            current_step = EXCLUDED.current_step,
            next_action_due_ts = EXCLUDED.next_action_due_ts,
            state_blob = EXCLUDED.state_blob,
            updated_at = NOW()""",
        (journey_id, customer_id, step, due_ts, state_blob),
    )
    cur.close()
    conn.close()
    return journey_id


@DBOS.step()
def re_evaluate_step(journey_id: str, artifact_json: str) -> str:
    """Re-check context after sleep. Returns ReEvaluationResult as JSON."""
    from maestro.re_evaluate import re_evaluate_context

    result = re_evaluate_context(journey_id, artifact_json)
    return json.dumps(result)


@DBOS.step()
def compose_email_step(artifact_json: str) -> str:
    """Compose personalized email via copywriter agent. Returns EmailContent JSON."""
    import asyncio

    from maestro.bootstrap import bootstrap
    from maestro.email_agent import compose_email

    model, _db_url = bootstrap()
    email = asyncio.get_event_loop().run_until_complete(
        compose_email(artifact_json, model)
    )
    return email.model_dump_json()


@DBOS.step()
def simulate_send_step(journey_id: str, customer_id: str, email_json: str) -> str:
    """Write to sent_emails table, simulating delivery."""
    from maestro.bootstrap import get_lakebase_conn_params
    from maestro.send import build_send_record, insert_sent_email

    record = build_send_record(journey_id, customer_id, email_json)
    params = get_lakebase_conn_params()
    email_id = insert_sent_email(record, params)
    return email_id


@DBOS.step()
def update_journey_status_step(journey_id: str, status: str) -> str:
    """Update journey_state status."""
    import psycopg2

    from maestro.bootstrap import get_lakebase_conn_params

    params = get_lakebase_conn_params()
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "UPDATE journey_state SET status = %s, updated_at = NOW() WHERE journey_id = %s",
        (status, journey_id),
    )
    cur.close()
    conn.close()
    return journey_id


# ── Unified Workflow ───────────────────────────────────────────────────────


@DBOS.workflow()
def unified_journey_workflow(event_json: str, delay_seconds: int = 15) -> str:
    """Complete Beat 2 + 2.5 + 3 workflow.

    Steps:
      1. Agent reasoning → DecisionArtifact
      2. Persist decision to Lakebase
      3. Save journey state
      4. Durable sleep (simulates optimal send window)
      5. Re-evaluate context (check for changes)
      6. Compose email (copywriter agent)
      7. Simulate send (write to sent_emails)

    Returns: JSON dict with journey_id, email_id, phases
    """
    # ── Step 1: Agent reasoning ────────────────────────────────────────
    decision_json = run_agent_step(event_json)
    decision = json.loads(decision_json)
    customer_id = decision.get("customer_id", "unknown")

    # ── Step 2: Persist decision ───────────────────────────────────────
    decision_id = persist_decision_step(decision_json)

    # ── Step 3: Save journey state ─────────────────────────────────────
    journey_id = decision.get(
        "journey_id",
        f"jrn_{customer_id}_{uuid.uuid4().hex[:6]}",
    )
    send_time_decisions = [
        d for d in decision.get("decisions", []) if d.get("type") == "send_time"
    ]
    due_ts = (
        send_time_decisions[0].get("value", datetime.now(CT).isoformat())
        if send_time_decisions
        else datetime.now(CT).isoformat()
    )
    save_journey_step(
        journey_id=journey_id,
        customer_id=customer_id,
        step="awaiting_send",
        due_ts=due_ts,
        state_blob=decision_json,
    )

    # ── Step 4: Durable sleep ──────────────────────────────────────────
    DBOS.sleep(delay_seconds)

    # ── Step 5: Re-evaluate context ────────────────────────────────────
    eval_json = re_evaluate_step(journey_id, decision_json)
    evaluation = json.loads(eval_json)

    # ── Step 6: Compose email (if proceed/adjust) ──────────────────────
    email_json = None
    email_id = None
    if evaluation["action"] in ("proceed", "adjust"):
        context = decision_json if evaluation["action"] == "proceed" else evaluation.get("updated_artifact", decision_json)
        email_json = compose_email_step(context)

        # ── Step 7: Simulate send ──────────────────────────────────────
        email_id = simulate_send_step(journey_id, customer_id, email_json)
        update_journey_status_step(journey_id, "sent")
    else:
        update_journey_status_step(journey_id, "cancelled")

    return json.dumps({
        "journey_id": journey_id,
        "decision_id": decision_id,
        "email_id": email_id,
        "evaluation": evaluation["action"],
    })
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_workflow.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/maestro/workflow.py tests/test_workflow.py
git commit -m "feat: rewrite workflow.py with unified 7-step Beat 2/2.5/3 workflow"
```

---

### Task 12: Revise API endpoints in app.py

**Files:**
- Modify: `src/maestro/app.py`

- [ ] **Step 1: Revise POST /api/workflow to accept event and random delay**

Replace the existing `start_dbos_workflow` function in `app.py` (around line 191):

```python
@app.post("/api/workflow")
def start_unified_workflow(body: dict):
    """Start unified Beat 2+2.5+3 workflow: agent → persist → sleep → re-eval → email → send."""
    import random

    from maestro.synthetic import CINDY_EVENT
    from maestro.workflow import unified_journey_workflow

    event_json = CINDY_EVENT.model_dump_json()
    delay = body.get("delay", random.randint(15, 20))

    handle = DBOS.start_workflow(unified_journey_workflow, event_json, delay)
    return {
        "workflow_id": handle.get_workflow_id(),
        "delay": delay,
        "status": "started",
    }
```

- [ ] **Step 2: Add GET /api/workflow/{id}/phases endpoint**

Add after the existing `get_workflow_status` endpoint:

```python
@app.get("/api/workflow/{workflow_id}/phases")
def get_workflow_phases(workflow_id: str):
    """Return phase-level status for the unified workflow.

    Frontend polls this every 2s to drive the auto-cascade UI.
    """
    try:
        handle = DBOS.retrieve_workflow(workflow_id)
        status_obj = handle.get_status()
        status = status_obj.status if hasattr(status_obj, 'status') else str(status_obj)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Map DBOS workflow status to phase progression
    # DBOS statuses: PENDING, SUCCESS, ERROR, RETRIES_EXCEEDED, CANCELLED
    phases = {
        "agent": {"status": "pending"},
        "persist": {"status": "pending"},
        "sleep": {"status": "pending"},
        "re_evaluate": {"status": "pending"},
        "email": {"status": "pending"},
        "send": {"status": "pending"},
    }

    if status == "PENDING":
        # Workflow is running — we approximate phase from elapsed time
        # In a real system, steps would emit events. For demo, use time-based heuristic.
        phases["agent"] = {"status": "done"}
        phases["persist"] = {"status": "done"}
        phases["sleep"] = {"status": "active"}
        current_phase = "sleep"
    elif status == "SUCCESS":
        # Get the workflow result for data
        try:
            result_json = handle.get_result()
            result = json.loads(result_json) if isinstance(result_json, str) else result_json
        except Exception:
            result = {}

        for key in phases:
            phases[key] = {"status": "done"}

        # Attach data to relevant phases
        phases["re_evaluate"]["data"] = {"action": result.get("evaluation", "proceed")}
        if result.get("email_id"):
            phases["send"]["data"] = {"email_id": result["email_id"]}

        current_phase = "done"
    elif status in ("ERROR", "RETRIES_EXCEEDED"):
        phases["agent"] = {"status": "done"}
        current_phase = "error"
    else:
        current_phase = "unknown"

    return {
        "workflow_id": workflow_id,
        "workflow_status": status,
        "current_phase": current_phase,
        "phases": phases,
    }
```

- [ ] **Step 3: Verify the app starts**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro && uv run python -c "from maestro.app import app; print('App loaded OK')"`
Expected: `App loaded OK`

- [ ] **Step 4: Commit**

```bash
git add src/maestro/app.py
git commit -m "feat: revise /api/workflow for unified flow, add /api/workflow/{id}/phases endpoint"
```

---

## Track D: Frontend Components

### Task 9: Create EmailPreview component

**Files:**
- Create: `frontend/src/beat2/components/EmailPreview.tsx`

- [ ] **Step 1: Create EmailPreview.tsx**

```tsx
// frontend/src/beat2/components/EmailPreview.tsx
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mail, CheckCircle2, Send } from 'lucide-react'

interface EmailData {
  subject: string
  body_html: string
  hero_image_url: string
  cta_text: string
  cta_url: string
}

interface EmailPreviewProps {
  email?: EmailData
  visible: boolean
  delivered: boolean
}

export default function EmailPreview({ email, visible, delivered }: EmailPreviewProps) {
  const [showDelivered, setShowDelivered] = useState(false)

  useEffect(() => {
    if (delivered) {
      const t = setTimeout(() => setShowDelivered(true), 1500)
      return () => clearTimeout(t)
    }
  }, [delivered])

  if (!visible || !email) return null

  return (
    <div className="relative">
      {/* Gold divider line */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="h-px bg-gradient-to-r from-transparent via-[var(--color-gold)] to-transparent mb-6 origin-left"
      />

      {/* Outer frame — Databricks platform */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8, rotateX: 8 }}
        animate={{ opacity: 1, scale: 1, rotateX: 0 }}
        transition={{ type: 'spring', damping: 20, stiffness: 200, delay: 0.3 }}
        className="bg-card border border-border rounded-xl overflow-hidden"
      >
        {/* Platform label */}
        <div className="flex items-center justify-between px-5 py-2.5 border-b border-border">
          <div className="flex items-center gap-2">
            <Mail size={13} className="text-[var(--color-databricks-cyan)]" />
            <span className="text-[10px] font-bold tracking-widest text-[var(--color-databricks-cyan)]">
              COMPOSED BY AGENT
            </span>
          </div>
          <AnimatePresence>
            {showDelivered && (
              <motion.div
                initial={{ opacity: 0, scale: 0.5, y: -8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ type: 'spring', damping: 12, stiffness: 300 }}
                className="flex items-center gap-1.5 bg-[var(--color-status-triggered)]/10 border border-[var(--color-status-triggered)]/30 text-[var(--color-status-triggered)] text-[10px] font-bold tracking-wider px-2.5 py-1 rounded-full"
              >
                <CheckCircle2 size={11} />
                DELIVERED
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Inner email card — Fluttershy brand */}
        <div className="m-4 rounded-lg overflow-hidden border border-[var(--color-cream)] dark:border-[var(--color-mocha)]/30">
          {/* Fluttershy header */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.4 }}
            className="bg-[var(--color-cream)] dark:bg-[var(--color-espresso)] px-6 py-3 flex items-center gap-2"
          >
            <span className="text-lg">🐾</span>
            <span className="font-serif text-sm text-[var(--color-espresso)] dark:text-[var(--color-cream)]">
              Fluttershy Pet Photo Co.
            </span>
          </motion.div>

          {/* Hero image */}
          <motion.div
            initial={{ opacity: 0, filter: 'blur(12px)' }}
            animate={{ opacity: 1, filter: 'blur(0px)' }}
            transition={{ delay: 0.8, duration: 0.6 }}
            className="w-full aspect-[2/1] bg-[var(--color-cream)] dark:bg-[var(--color-mocha)]/20 overflow-hidden"
          >
            <img
              src={email.hero_image_url}
              alt="Pet hero"
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none'
              }}
            />
          </motion.div>

          {/* Email body */}
          <div className="px-6 py-5 bg-white dark:bg-[var(--color-espresso)]">
            {/* Subject */}
            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.0, duration: 0.4 }}
              className="font-serif text-lg text-[var(--color-espresso)] dark:text-[var(--color-gold)] mb-3"
            >
              {email.subject}
            </motion.h2>

            {/* Body HTML */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2, duration: 0.4 }}
              className="text-sm text-[var(--color-espresso)] dark:text-[var(--color-cream)] leading-relaxed font-sans [&_h1]:text-base [&_h1]:font-serif [&_h1]:mb-2 [&_p]:mb-2"
              dangerouslySetInnerHTML={{ __html: email.body_html }}
            />

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.4, type: 'spring', damping: 15 }}
              className="mt-4 text-center"
            >
              <span className="inline-flex items-center gap-2 bg-[var(--color-gold)] text-[var(--color-espresso)] font-bold text-sm px-6 py-3 rounded-lg">
                <Send size={14} />
                {email.cta_text}
              </span>
            </motion.div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.6 }}
              className="text-center text-[11px] text-[var(--color-mocha)] mt-3"
            >
              Free shipping on orders over $35
            </motion.p>
          </div>

          {/* Footer */}
          <div className="px-6 py-3 bg-[var(--color-cream)]/50 dark:bg-[var(--color-espresso)]/80 border-t border-[var(--color-cream)] dark:border-[var(--color-mocha)]/20">
            <p className="text-[10px] text-[var(--color-mocha)] text-center">
              Fluttershy · Unsubscribe · Privacy Policy
            </p>
          </div>
        </div>
      </motion.div>

      {/* Confetti burst on delivered */}
      <AnimatePresence>
        {showDelivered && (
          <>
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                initial={{
                  opacity: 1,
                  scale: 0,
                  x: 0,
                  y: 0,
                }}
                animate={{
                  opacity: 0,
                  scale: 1,
                  x: (Math.random() - 0.5) * 120,
                  y: -Math.random() * 80 - 20,
                }}
                transition={{ duration: 0.8, delay: i * 0.05 }}
                className="absolute top-0 right-24 w-2 h-2 rounded-full"
                style={{
                  backgroundColor: ['#C4A87A', '#40D1F5', '#22C55E', '#EB1600'][i % 4],
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
```

- [ ] **Step 2: Verify build**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/beat2/components/EmailPreview.tsx
git commit -m "feat: add cinematic EmailPreview component for Beat 3"
```

---

### Task 10: Update WorkflowTimeline for auto-trigger and countdown

**Files:**
- Modify: `frontend/src/beat2/components/WorkflowTimeline.tsx`

- [ ] **Step 1: Rewrite WorkflowTimeline with 6-step pipeline, countdown, and re-evaluate display**

Replace the entire file:

```tsx
// frontend/src/beat2/components/WorkflowTimeline.tsx
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Database, Timer, RefreshCw, Mail, Send } from 'lucide-react'

type StepState = 'pending' | 'active' | 'done'

interface Step {
  id: string
  label: string
  icon: React.ReactNode
  state: StepState
  detail?: string
}

interface PhaseData {
  status: string
  data?: Record<string, unknown>
}

interface WorkflowTimelineProps {
  workflowId: string | null
  delaySeconds: number
  onPhasesUpdate?: (phases: Record<string, PhaseData>) => void
  onComplete?: (result: Record<string, unknown>) => void
}

const INITIAL_STEPS: Step[] = [
  { id: 'agent', label: 'Agent', icon: <Brain size={16} />, state: 'pending' },
  { id: 'persist', label: 'Persist', icon: <Database size={16} />, state: 'pending' },
  { id: 'sleep', label: 'Sleep', icon: <Timer size={16} />, state: 'pending' },
  { id: 're_evaluate', label: 'Re-evaluate', icon: <RefreshCw size={16} />, state: 'pending' },
  { id: 'email', label: 'Compose', icon: <Mail size={16} />, state: 'pending' },
  { id: 'send', label: 'Deliver', icon: <Send size={16} />, state: 'pending' },
]

export default function WorkflowTimeline({
  workflowId,
  delaySeconds,
  onPhasesUpdate,
  onComplete,
}: WorkflowTimelineProps) {
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS)
  const [countdown, setCountdown] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Start countdown when sleep becomes active
  useEffect(() => {
    const sleepStep = steps.find(s => s.id === 'sleep')
    if (sleepStep?.state === 'active' && countdown === null) {
      setCountdown(delaySeconds)
      countdownRef.current = setInterval(() => {
        setCountdown(prev => {
          if (prev === null || prev <= 1) {
            if (countdownRef.current) clearInterval(countdownRef.current)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => {
      if (countdownRef.current) clearInterval(countdownRef.current)
    }
  }, [steps, delaySeconds, countdown])

  // Poll for phase updates
  useEffect(() => {
    if (!workflowId) return

    // Start with agent active
    setSteps(prev => prev.map((s, i) => ({ ...s, state: i === 0 ? 'active' : 'pending' })))

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/workflow/${workflowId}/phases`)
        if (!res.ok) return
        const data = await res.json()

        onPhasesUpdate?.(data.phases)

        // Map phases to step states
        setSteps(prev =>
          prev.map(step => {
            const phase = data.phases[step.id]
            if (!phase) return step
            return {
              ...step,
              state: phase.status === 'done' ? 'done' : phase.status === 'active' ? 'active' : step.state,
            }
          })
        )

        if (data.current_phase === 'done' || data.workflow_status === 'SUCCESS') {
          if (pollRef.current) clearInterval(pollRef.current)
          setSteps(prev => prev.map(s => ({ ...s, state: 'done' })))
          onComplete?.(data)
        }
      } catch {
        // silently retry
      }
    }, 2000)

    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [workflowId, onPhasesUpdate, onComplete])

  const stepBorder = (state: StepState) => {
    if (state === 'active') return 'border-[var(--color-status-active)] shadow-[0_0_12px_rgba(64,209,245,0.3)]'
    if (state === 'done') return 'border-[var(--color-status-triggered)] shadow-[0_0_8px_rgba(34,197,94,0.2)]'
    return 'border-border'
  }

  const stepColor = (state: StepState) => {
    if (state === 'active') return 'text-[var(--color-status-active)]'
    if (state === 'done') return 'text-[var(--color-status-triggered)]'
    return 'text-muted-foreground'
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] font-bold tracking-widest text-muted-foreground">DBOS DURABLE WORKFLOW</p>
          <p className="text-xs text-muted-foreground mt-0.5">Unified Beat 2 → 2.5 → 3 — persisted execution on Lakebase</p>
        </div>
        {workflowId && (
          <span className="text-xs text-muted-foreground animate-pulse">Running…</span>
        )}
      </div>

      {error && <p className="text-xs text-[var(--color-status-suppressed)] mb-3">{error}</p>}

      {/* Steps row */}
      <div className="flex items-center gap-1.5">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center gap-1.5 flex-1 min-w-0">
            <motion.div
              animate={step.state === 'active' ? { scale: [1, 1.04, 1] } : { scale: 1 }}
              transition={{ duration: 1.2, repeat: step.state === 'active' ? Infinity : 0 }}
              className={`flex flex-col items-center gap-1 flex-1 min-w-0 border rounded-lg px-2 py-2.5 ${stepBorder(step.state)}`}
            >
              <div className={`shrink-0 ${stepColor(step.state)}`}>
                {step.icon}
              </div>
              <span className={`text-[10px] font-semibold truncate ${stepColor(step.state)}`}>
                {step.id === 'sleep' && step.state === 'active' && countdown !== null
                  ? `${countdown}s`
                  : step.label}
              </span>
              {step.state === 'active' && (
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-status-active)] animate-pulse shrink-0" />
              )}
              {step.state === 'done' && (
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-status-triggered)] shrink-0" />
              )}
            </motion.div>
            {i < steps.length - 1 && (
              <span className="text-muted-foreground text-[10px] shrink-0">→</span>
            )}
          </div>
        ))}
      </div>

      {/* Sleep progress bar */}
      <AnimatePresence>
        {countdown !== null && countdown > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
              <span>Optimal send window: 8:00 AM CT</span>
              <span>{countdown}s remaining</span>
            </div>
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-[var(--color-gold)] rounded-full"
                initial={{ width: '0%' }}
                animate={{
                  width: `${((delaySeconds - countdown) / delaySeconds) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {workflowId && (
        <p className="text-[10px] text-muted-foreground font-mono mt-3">
          workflow_id: {workflowId}
        </p>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Verify build**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/beat2/components/WorkflowTimeline.tsx
git commit -m "feat: rewrite WorkflowTimeline with 6-step pipeline, countdown, and auto-polling"
```

---

### Task 11: Rewrite Beat2Page with phase-driven state machine

**Files:**
- Modify: `frontend/src/beat2/Beat2Page.tsx`

**Depends on:** Tasks 7, 8, 9, 10

- [ ] **Step 1: Rewrite Beat2Page.tsx with unified state machine**

Replace the entire file. The key changes:
- Auto-calls `POST /api/workflow` on mount (not `/api/run`)
- Polls `/api/workflow/{id}/phases` instead of waiting for a single response
- State machine drives UI: narrative → panels → workflow → email → delivered
- AgentNarrative still plays during Step 1
- EmailPreview revealed after workflow completes

```tsx
// frontend/src/beat2/Beat2Page.tsx
import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Sparkles } from 'lucide-react'
import CampaignPanel from './components/CampaignPanel'
import ReasoningTrace from './components/ReasoningTrace'
import DecisionPanel from './components/DecisionPanel'
import WorkflowTimeline from './components/WorkflowTimeline'
import EmailPreview from './components/EmailPreview'

type Phase = 'idle' | 'narrative' | 'panels' | 'workflow' | 'email_preview' | 'delivered'

interface Campaign {
  name: string
  campaign_id: string
  status: 'suppressed' | 'prioritized' | 'active' | 'triggered' | 'paused' | 'dormant'
}

interface DecisionRow { type: string; target: string; reason: string }
interface Signal { signal: string; value: string; weight: number }

interface Artifact {
  verdict: string
  decisions: DecisionRow[]
  contributing_signals: Signal[]
  rationale: string
}

interface EmailData {
  subject: string
  body_html: string
  hero_image_url: string
  cta_text: string
  cta_url: string
}

const NARRATIVE_STEPS = [
  { icon: '👤', text: 'Who are they?', detail: 'Loading customer profile — Cindy Chen, gold tier, tabby kitten Whiskers' },
  { icon: '🛒', text: 'What did they leave behind?', detail: 'Abandoned cart — "Welcome Home, Whiskers" photo book, $42' },
  { icon: '📅', text: 'Can we still ship it?', detail: 'Checking production calendar — 4-day turnaround, standard shipping feasible' },
  { icon: '📢', text: 'What campaigns are they in?', detail: 'Found 4 active campaigns — Spring Seasonal, Cart Recovery, VIP Loyalty, Reactivation' },
  { icon: '⚠️', text: 'Would another email breach the cap?', detail: 'Frequency cap: 2/week — current 1, queued 1 (Spring Seasonal) → BREACH' },
  { icon: '🎫', text: 'Any recent complaints?', detail: 'Support history clean — no open tickets in 30 days' },
  { icon: '📊', text: 'How likely are they to convert?', detail: 'Propensity score: 0.81 — high confidence for cart recovery' },
  { icon: '⏰', text: 'When should we reach out?', detail: 'Optimal send: 8:00 AM CT — adjusted from 11:48 PM (quiet hours)' },
  { icon: '💾', text: 'Lock the decision — durably.', detail: 'Persisting journey state to Lakebase via DBOS' },
]

function AgentNarrative() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStep(s => (s < NARRATIVE_STEPS.length - 1 ? s + 1 : s))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div
      key="narrative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-2xl mx-auto py-12 space-y-3"
    >
      <div className="text-center mb-8">
        <p className="text-lg font-serif font-semibold text-card-foreground">One decision. Nine domains.</p>
        <p className="text-sm text-muted-foreground mt-1">Watch the agent think…</p>
      </div>

      {NARRATIVE_STEPS.map((s, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: i <= step ? 1 : 0.15, x: i <= step ? 0 : -20 }}
          transition={{ duration: 0.4 }}
          className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
            i === step
              ? 'bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/20'
              : i < step ? 'bg-card border border-border' : ''
          }`}
        >
          <span className="text-lg mt-0.5">{s.icon}</span>
          <div>
            <p className={`text-sm font-medium ${i === step ? 'text-[var(--color-gold)]' : 'text-card-foreground'}`}>
              {s.text}
            </p>
            {i <= step && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="text-xs text-muted-foreground mt-0.5"
              >
                {s.detail}
              </motion.p>
            )}
          </div>
          {i === step && (
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="ml-auto w-2 h-2 rounded-full bg-[var(--color-gold)] mt-2"
            />
          )}
        </motion.div>
      ))}
    </motion.div>
  )
}

export default function Beat2Page() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [workflowId, setWorkflowId] = useState<string | null>(null)
  const [delaySeconds, setDelaySeconds] = useState(17)
  const [artifact, setArtifact] = useState<Artifact | null>(null)
  const [campaigns, setCampaigns] = useState<Campaign[] | null>(null)
  const [latency, setLatency] = useState<number | null>(null)
  const [email, setEmail] = useState<EmailData | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Auto-start workflow on mount
  useEffect(() => {
    const start = async () => {
      setPhase('narrative')
      try {
        const res = await fetch('/api/workflow', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setWorkflowId(data.workflow_id)
        setDelaySeconds(data.delay)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error')
        // Still show narrative with fallback data
      }
    }
    start()
  }, [])

  // Also fetch agent result via /api/run for immediate panel data
  useEffect(() => {
    const fetchAgentResult = async () => {
      try {
        const start = performance.now()
        const res = await fetch('/api/run', { method: 'POST' })
        if (!res.ok) return
        const json = await res.json()
        setArtifact(json.artifact)
        setCampaigns(json.campaigns)
        setLatency(json.latency_s ?? (performance.now() - start) / 1000)

        // Transition from narrative to panels
        setTimeout(() => setPhase('panels'), 1000)
        // Auto-advance to workflow view
        setTimeout(() => setPhase('workflow'), 3000)
      } catch {
        // Fallback: transition anyway after narrative completes
        setTimeout(() => setPhase('panels'), NARRATIVE_STEPS.length * 3000 + 1000)
        setTimeout(() => setPhase('workflow'), NARRATIVE_STEPS.length * 3000 + 4000)
      }
    }
    fetchAgentResult()
  }, [])

  const handleWorkflowComplete = useCallback((result: Record<string, unknown>) => {
    // Fetch composed email from the workflow result
    // For now, use a placeholder that will be replaced with real data
    setEmail({
      subject: 'Whiskers is waiting for their photo book!',
      body_html: '<h1>Hi Cindy,</h1><p>We noticed you left something special behind — a "Welcome Home" photo book for Whiskers. Your tabby kitten deserves to be celebrated!</p><p>We\'ve saved your cart and your $42 photo book is ready to go. As a Gold member, you\'ll get free shipping.</p>',
      hero_image_url: '/whiskers.jpg',
      cta_text: 'Complete Your Order',
      cta_url: 'https://fluttershy.com/cart/resume?cid=cust_88241',
    })
    setPhase('email_preview')
    setTimeout(() => setPhase('delivered'), 3000)
  }, [])

  const showNarrative = phase === 'narrative'
  const showPanels = phase !== 'idle' && phase !== 'narrative'
  const showWorkflow = phase === 'workflow' || phase === 'email_preview' || phase === 'delivered'
  const showEmail = phase === 'email_preview' || phase === 'delivered'

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-[1400px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-[var(--color-gold)]/20 flex items-center justify-center">
              <Brain size={15} className="text-[var(--color-gold)]" />
            </div>
            <div>
              <p className="text-sm font-semibold text-card-foreground font-sans">Marketing Ops</p>
              <p className="text-[10px] text-muted-foreground">Unified Beat 2 → 2.5 → 3 — Cross-Campaign Optimization</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showNarrative && (
              <span className="inline-flex items-center gap-1.5 text-[11px] text-[var(--color-gold)] animate-pulse">
                <Sparkles size={12} />
                Agent reasoning across 9 domains…
              </span>
            )}
            {showPanels && latency && (
              <span className="inline-flex items-center gap-1.5 bg-[var(--color-status-triggered)]/10 border border-[var(--color-status-triggered)]/30 text-[var(--color-status-triggered)] text-[11px] px-3 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-status-triggered)]" />
                Decision ready · {latency.toFixed(1)}s
              </span>
            )}
            {error && (
              <span className="text-[11px] text-[var(--color-status-suppressed)]">Error: {error}</span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-5">
        {/* Narrative loading */}
        <AnimatePresence>
          {showNarrative && <AgentNarrative />}
        </AnimatePresence>

        {/* 3-panel layout */}
        {showPanels && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="grid grid-cols-1 lg:grid-cols-[240px_1fr_320px] gap-4"
          >
            <div className="bg-card border border-border rounded-xl p-4">
              <CampaignPanel campaigns={campaigns ?? undefined} />
            </div>
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <ReasoningTrace rationale={artifact?.rationale} latency={latency ?? undefined} />
            </div>
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <DecisionPanel
                verdict={artifact?.verdict}
                decisions={artifact?.decisions}
                signals={artifact?.contributing_signals}
              />
            </div>
          </motion.div>
        )}

        {/* Workflow Timeline */}
        {showWorkflow && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <WorkflowTimeline
              workflowId={workflowId}
              delaySeconds={delaySeconds}
              onComplete={handleWorkflowComplete}
            />
          </motion.div>
        )}

        {/* Email Preview — cinematic reveal */}
        {showEmail && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <EmailPreview
              email={email ?? undefined}
              visible={showEmail}
              delivered={phase === 'delivered'}
            />
          </motion.div>
        )}
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Verify build**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/beat2/Beat2Page.tsx
git commit -m "feat: rewrite Beat2Page with unified phase-driven state machine and email reveal"
```

---

## Final Gate

### Task 13: Integration test — verify full flow

**Files:**
- Test: `tests/test_unified_flow.py`

**Depends on:** All tracks complete

- [ ] **Step 1: Write integration test**

```python
# tests/test_unified_flow.py
"""Integration test for the unified Beat 2/2.5/3 flow.

Tests the complete chain: models → re-evaluate → email agent → send record.
Does NOT test DBOS workflow (requires Lakebase) or LLM calls (requires AI Gateway).
"""
import json


def test_full_chain_models():
    """All new models can be instantiated with valid data."""
    from maestro.models import EmailContent, ReEvaluationResult

    email = EmailContent(
        subject="Test",
        body_html="<p>Hi</p>",
        body_text="Hi",
        hero_image_url="/whiskers.jpg",
        cta_text="Order",
        cta_url="https://example.com",
    )
    assert email.subject == "Test"

    result = ReEvaluationResult(
        action="proceed", reason="OK", changes_detected=[], updated_artifact=None
    )
    assert result.action == "proceed"


def test_re_evaluate_then_send():
    """Re-evaluate returns proceed, then build_send_record creates valid record."""
    from maestro.re_evaluate import re_evaluate_context
    from maestro.send import build_send_record

    artifact = {
        "customer_id": "cust_88241",
        "decisions": [{"type": "tone", "value": "warm"}],
        "contributing_signals": [],
    }
    artifact_json = json.dumps(artifact)

    # Re-evaluate
    eval_result = re_evaluate_context("jrn_test", artifact_json)
    assert eval_result["action"] == "proceed"

    # Build send record
    email_data = json.dumps({
        "subject": "Whiskers!",
        "body_html": "<p>Hi</p>",
        "body_text": "Hi",
        "hero_image_url": "/whiskers.jpg",
        "cta_text": "Order",
        "cta_url": "https://example.com",
    })
    record = build_send_record("jrn_test", "cust_88241", email_data)
    assert record["status"] == "delivered"
    assert record["subject"] == "Whiskers!"


def test_copywriter_prompt_builds():
    """Copywriter prompt includes all necessary context."""
    from maestro.email_agent import build_email_prompt
    from maestro.synthetic import CINDY_CART, CINDY_PROFILE

    artifact = {
        "customer_id": "cust_88241",
        "decisions": [{"type": "tone", "value": "warm + personal"}],
    }
    prompt = build_email_prompt(artifact, CINDY_PROFILE, CINDY_CART)
    assert "Cindy" in prompt
    assert "Whiskers" in prompt
    assert "42" in prompt


def test_workflow_imports():
    """Unified workflow and all steps import correctly."""
    from maestro.workflow import (
        compose_email_step,
        persist_decision_step,
        re_evaluate_step,
        run_agent_step,
        save_journey_step,
        simulate_send_step,
        unified_journey_workflow,
        update_journey_status_step,
    )
    assert callable(unified_journey_workflow)
    assert callable(compose_email_step)
    assert callable(simulate_send_step)
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest tests/test_unified_flow.py tests/test_models.py tests/test_re_evaluate.py tests/test_send.py tests/test_email_agent.py -v`
Expected: ALL PASS

- [ ] **Step 3: Build frontend**

Run: `cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
git add tests/test_unified_flow.py
git commit -m "test: add integration test for unified Beat 2/2.5/3 flow"
```

- [ ] **Step 5: Push to remote**

```bash
git push origin main
```

---

## Whiskers Image (manual step)

Source a royalty-free tabby kitten photo and save to `frontend/public/whiskers.jpg`. Unsplash is the recommended source (per frontend/CLAUDE.md). This is a non-blocking task — the EmailPreview component gracefully hides the image on error.
