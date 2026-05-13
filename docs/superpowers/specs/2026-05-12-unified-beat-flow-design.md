# Unified Beat 2 / 2.5 / 3 Flow — Design Spec

**Date:** 2026-05-12
**Status:** Draft — pending user approval
**Scope:** Unify agent reasoning, DBOS durable workflow, and email composition into a single auto-cascading flow with cinematic UI reveals and Databricks-aligned theming.

---

## 1. Problem

Today Beat 2 (agent reasoning) and Beat 2.5 (DBOS workflow) are disconnected:
- `POST /api/run` runs the agent independently, returns DecisionArtifact
- User manually clicks "Run DBOS Workflow" to start persistence + sleep
- No Beat 3 (email composition) exists at all
- The workflow completes by marking `status = 'completed'` and does nothing after waking

The demo feels like two separate features stitched together. The audience loses the narrative thread.

## 2. Solution

One DBOS workflow that owns the entire lifecycle from agent reasoning through email delivery. One trigger (cart abandon). The frontend auto-cascades through narrated phases — the audience watches the full arc unfold without clicking anything.

## 3. Flow Architecture

```
Cart abandon (Beat 1 CartDrawer)
  → POST /api/workflow
  → Single DBOS workflow with 6 steps:

  Step 1: run_agent_step()
    Maestro reasoning agent, 9 tools, produces DecisionArtifact.
    UI: AgentNarrative (9-domain typewriter) → 3-panel reveal.

  Step 2: persist_decision_step()
    Writes DecisionArtifact to Lakebase `decisions` table.
    Writes journey_state row with due_ts from agent's send_time decision.
    UI: "Decision locked — persisted to Lakebase" badge.

  Step 3: DBOS.sleep(random 15–20s)
    Simulates waiting for optimal send window.
    Duration randomized to prove the agent determined the timing.
    UI: Countdown timer — "Optimal window: 8:00 AM CT — simulating 17s wait..."

  Step 4: re_evaluate_step()
    Re-checks context after sleep: has customer converted? New tickets?
    Frequency cap changed? Another campaign fired?
    Output: "proceed" / "abort" / "adjust".
    For demo: always proceeds (synthetic data unchanged), but the audience
    sees the check — proves the agent isn't blindly executing a stale decision.
    UI: "Rehydrating context... checking for changes since decision"

  Step 5: compose_email_step()
    Dedicated copywriter agent composes personalized email.
    Input: DecisionArtifact + Profile + Cart + Whiskers image ref.
    Output: EmailContent (subject, body_html, hero_image_url, cta_text).
    Only runs if Step 4 returns "proceed" or "adjust".
    UI: Cinematic email preview reveal.

  Step 6: simulate_send_step()
    Writes to `sent_emails` table. Marks journey complete.
    UI: "Delivered" badge with confetti.
```

## 4. Backend Changes

### 4.1 Revised Workflow (`src/maestro/workflow.py`)

Replace the current fragmented workflow with a single unified workflow:

```python
@DBOS.workflow()
def unified_journey_workflow(event_json: str, delay_seconds: int) -> dict:
    # Step 1: Agent reasoning
    artifact_json = run_agent_step(event_json)

    # Step 2: Persist decision + journey state
    journey_id = persist_decision_step(artifact_json)
    save_journey_step(journey_id, artifact_json, delay_seconds)

    # Step 3: Durable sleep (simulates optimal send window)
    DBOS.sleep(delay_seconds)

    # Step 4: Re-evaluate context
    evaluation = re_evaluate_step(journey_id, artifact_json)

    # Step 5: Compose email (if proceed/adjust)
    email_json = None
    if evaluation["action"] in ("proceed", "adjust"):
        context = artifact_json if evaluation["action"] == "proceed" else evaluation["updated_artifact"]
        email_json = compose_email_step(context)

    # Step 6: Simulate send
    if email_json:
        simulate_send_step(journey_id, email_json)

    update_journey_status_step(journey_id, "completed")
    return {"journey_id": journey_id, "email": email_json}
```

### 4.2 New DBOS Steps

**`re_evaluate_step()`:**
- Re-reads profile, cap status, support tickets from synthetic data
- Compares against original decision signals
- Returns `{"action": "proceed"}` for demo (no changes in synthetic data)
- In production: would detect purchase completion, new tickets, cap breaches

**`compose_email_step()`:**
- Invokes the copywriter agent (see 4.3)
- Returns `EmailContent` as JSON

**`simulate_send_step()`:**
- Inserts row into `sent_emails` table
- Updates `journey_state.status = 'sent'`

### 4.3 Copywriter Agent

A small dedicated Pydantic AI agent for email composition:

```python
copywriter_agent = Agent(
    model=MODEL,
    output_type=EmailContent,
    system_prompt="""You are a DTC email copywriter for Fluttershy, a pet photo products brand.
Write warm, personal cart recovery emails. Use the customer's pet name naturally.
Tone: {tone_from_decision}. Keep subject under 50 chars. Body under 100 words.
Include a clear CTA. Never use urgency tactics or guilt."""
)
```

**Input context (via RunContext deps):**
- DecisionArtifact (verdict, tone, channel decisions)
- Profile (name, pet_name, pet_type, tier)
- Cart (product name, price, image)
- hero_image_url: `/whiskers.jpg`

### 4.4 New Models

```python
class EmailContent(BaseModel):
    subject: str          # "Whiskers is waiting for their photo book!"
    body_html: str        # Rendered HTML with Fluttershy branding
    body_text: str        # Plain-text fallback
    hero_image_url: str   # "/whiskers.jpg"
    cta_text: str         # "Complete Your Order"
    cta_url: str          # "https://fluttershy.com/cart/resume"

class ReEvaluationResult(BaseModel):
    action: str           # "proceed" | "abort" | "adjust"
    reason: str           # Human-readable explanation
    changes_detected: list[str]  # What changed (empty for demo)
    updated_artifact: str | None  # Updated JSON if "adjust"
```

### 4.5 New Database Table

```sql
CREATE TABLE sent_emails (
    email_id TEXT PRIMARY KEY,
    journey_id TEXT REFERENCES journey_state(journey_id),
    customer_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    channel TEXT DEFAULT 'email',
    status TEXT DEFAULT 'delivered',
    sent_at TIMESTAMP DEFAULT NOW()
);
```

### 4.6 Revised API Endpoints

**`POST /api/workflow` (revised):**
- Accepts cart_abandoned event directly (no pre-computed decision)
- Starts `unified_journey_workflow` with `random.randint(15, 20)` delay
- Returns `{"workflow_id": ..., "journey_id": ...}`

**`GET /api/workflow/{id}/phases` (new):**
- Returns current phase + data for each completed phase
- Frontend polls this every 2s

```json
{
  "current_phase": "composing_email",
  "phases": {
    "agent": {"status": "done", "data": {"artifact": {...}, "campaigns": [...]}},
    "persist": {"status": "done"},
    "sleep": {"status": "done", "duration_s": 17},
    "re_evaluate": {"status": "done", "data": {"action": "proceed", "reason": "No changes detected"}},
    "email": {"status": "in_progress"},
    "send": {"status": "pending"}
  }
}
```

**Keep `POST /api/run` unchanged** — useful for testing agent reasoning in isolation. But Beat2Page no longer calls it. The unified workflow subsumes the agent call. No deprecation needed — it's a valid standalone tool.

## 5. Frontend Changes

### 5.1 Beat2Page State Machine

Replace the current load-once-and-display pattern with a phase-driven state machine:

```
idle → narrative → panels → workflow_persist → workflow_sleep →
  re_evaluate → composing_email → email_preview → delivered
```

- `idle`: Page mounted, about to trigger
- `narrative`: AgentNarrative playing (9-step typewriter)
- `panels`: 3-panel layout revealed (campaigns, trace, decision)
- `workflow_persist`: "Decision locked" badge animates in
- `workflow_sleep`: Countdown timer (15–20s)
- `re_evaluate`: "Checking for changes..." spinner
- `composing_email`: "Composing personalized outreach..." spinner
- `email_preview`: Cinematic email card reveal
- `delivered`: "Delivered" badge with confetti

Auto-advances between phases. Brief narrator pauses at beat boundaries (panels → workflow, sleep → email).

### 5.2 Trigger Change

Currently: Beat2Page auto-calls `POST /api/run` on mount.
New: Beat2Page auto-calls `POST /api/workflow` on mount, then polls `/api/workflow/{id}/phases`.

The AgentNarrative still plays during Step 1. When the `agent` phase returns `done`, the 3-panel layout reveals. The page continues polling as subsequent phases complete.

### 5.3 EmailPreview Component (New)

**Location:** `frontend/src/beat2/components/EmailPreview.tsx`

A branded email card that appears below the WorkflowTimeline with a cinematic reveal:

**Reveal animation sequence:**
1. WorkflowTimeline "Complete" step pulses gold
2. A gold divider line draws itself across the page (CSS `scaleX` from 0 to 1)
3. Email card scales up from 0.8 with spring physics (Framer Motion)
4. Fluttershy branded header fades in (logo + "Fluttershy Pet Photo Co.")
5. Whiskers hero image loads with blur-to-sharp transition (CSS filter)
6. Agent-composed subject line typewriters in (serif font, gold color)
7. Body copy fades in paragraph by paragraph (staggered 200ms)
8. CTA button slides up from below with bounce
9. Brief 1.5s pause
10. "Delivered" badge drops in from above with scale bounce
11. Subtle confetti particles burst from the badge (CSS keyframes, no library)
12. `sent_emails` row fades in as a mini data-table below the card

**Email card structure:**
```
┌──────────────────────────────────────────────┐
│  [Fluttershy logo]   Fluttershy Pet Photo Co │  ← cream header
├──────────────────────────────────────────────┤
│                                              │
│           [Whiskers hero image]              │  ← tabby kitten, rounded corners
│                                              │
│  Hi Cindy,                                   │
│                                              │
│  {agent-composed warm copy mentioning         │  ← DM Sans, espresso text
│   Whiskers and the photo book}               │
│                                              │
│        ┌──────────────────────┐              │
│        │  Complete Your Order │              │  ← gold CTA button
│        └──────────────────────┘              │
│                                              │
│  Free shipping on orders over $35            │  ← muted subtext
├──────────────────────────────────────────────┤
│  Fluttershy · Unsubscribe · Privacy          │  ← footer
└──────────────────────────────────────────────┘
```

**Outer frame:** Databricks-themed border with cyan "Composed by Agent" label.

### 5.4 Sleep Countdown

Replace the current static "Sleep 15s" step in WorkflowTimeline with a live countdown:
- Shows remaining seconds (e.g., "17s... 16s... 15s...")
- Gold progress bar filling left to right
- Label: "Optimal send window: 8:00 AM CT"
- Pulsing gold dot on the active timeline step

### 5.5 Re-evaluation UI

After sleep completes, before email:
- Brief "Rehydrating context..." message with spinning loader
- Checkmarks appear: "Purchase status: unchanged", "Support tickets: none", "Frequency cap: clear"
- "Proceeding to compose" confirmation
- Auto-advances to email composition

### 5.6 Whiskers Image

Static asset: `frontend/public/whiskers.jpg`
A cute tabby kitten photo. Referenced from Beat 1's UploadModal narrative — "remember when Cindy uploaded Whiskers' photo? The agent used it to personalize the email."

Need to source/add a royalty-free tabby kitten image to the repo.

## 6. Theming Audit

### 6.1 Databricks Alignment

**Activate unused Databricks tokens across all components:**
- `--color-databricks-cyan` (#40D1F5) — secondary accents, active step indicators, info badges
- `--color-databricks-red` (#EB1600) — light mode CTAs, suppression badges, alert states
- `--color-databricks-navy` (#0B2026) — light mode text, header backgrounds

**Light mode = Databricks professional:**
- Navy text, red primary CTAs, cyan secondary accents, white cards
- Beat 2 header uses navy background with white text

**Dark mode = Cinematic ops with Databricks structure:**
- Gold primary, espresso backgrounds, cream text
- Cyan appears as secondary glow on active workflow steps
- Timeline connector lines use cyan in dark mode

### 6.2 New Status Color Tokens

```css
--color-status-suppressed: #EB1600;            /* Databricks red */
--color-status-priority: #C4A87A;              /* Gold — the win state */
--color-status-active: #40D1F5;                /* Databricks cyan */
--color-status-dormant: var(--color-muted-foreground);
--color-status-triggered: #22C55E;             /* Green — sent/delivered */
```

### 6.3 Component Fixes

Replace all hardcoded hex values with CSS variables:

| Component | Fix |
|-----------|-----|
| CampaignPanel | Replace Tailwind `green-500/red-500` badges → status tokens |
| DecisionPanel | Replace inline `#22C55E` → `var(--color-status-triggered)` |
| WorkflowTimeline | Replace `orange-500` → `var(--color-gold)`, add cyan for active step |
| ReasoningTrace | Replace hardcoded tool colors → semantic tokens |
| Beat2Page | Replace `bg-[var(--color-gold)]/10` → proper token reference |
| CustomerCard | Ensure gold gradient uses variable, not hardcoded |

### 6.4 Typography Enforcement

- All UI text: `font-family: var(--font-sans)` (DM Sans)
- Narrator text + email preview headings: `font-family: var(--font-serif)` (DM Serif Display)
- Explicit `font-family` on every component — don't rely on Tailwind defaults
- Font sizes: follow existing scale (10px labels, 11px badges, 13px body, 15px headings)

### 6.5 Email Preview Theming

**Inner card (Fluttershy brand):**
- Background: `var(--color-cream)` / `#EDE4D8`
- Text: `var(--color-espresso)` / `#2C1810`
- CTA button: `var(--color-gold)` with espresso text
- Header: Cream background with Fluttershy wordmark
- Footer: Muted mocha text

**Outer frame (Databricks platform):**
- Border: `var(--color-border)` (adapts light/dark)
- "Composed by Agent" label: `var(--color-databricks-cyan)` text
- "Delivered" badge: `var(--color-status-triggered)` (green)

## 7. Data Flow

```
CartDrawer (Beat 1)
  │
  ├─ POST /api/events ─────────── stores event in memory (unchanged)
  │
  └─ navigate('/beat2')
       │
       Beat2Page mounts
       │
       ├─ POST /api/workflow { event, delay: random(15,20) }
       │    │
       │    └─ unified_journey_workflow starts
       │         │
       │         ├─ run_agent_step() ──────────── DecisionArtifact
       │         ├─ persist_decision_step() ───── Lakebase: decisions
       │         ├─ save_journey_step() ────────── Lakebase: journey_state
       │         ├─ DBOS.sleep(15-20s) ─────────── durable timer
       │         ├─ re_evaluate_step() ─────────── context check
       │         ├─ compose_email_step() ───────── copywriter agent → EmailContent
       │         └─ simulate_send_step() ───────── Lakebase: sent_emails
       │
       └─ polls GET /api/workflow/{id}/phases every 2s
            │
            └─ UI advances through state machine as phases complete
```

## 8. File Changes Summary

| File | Action | What |
|------|--------|------|
| `src/maestro/workflow.py` | **Rewrite** | Unified 6-step workflow |
| `src/maestro/app.py` | **Edit** | Revise `/api/workflow`, add `/api/workflow/{id}/phases`, deprecate `/api/run` |
| `src/maestro/models.py` | **Edit** | Add `EmailContent`, `ReEvaluationResult` models |
| `src/maestro/email_agent.py` | **New** | Copywriter agent |
| `src/maestro/synthetic.py` | **Edit** | Add re-evaluation synthetic data (unchanged signals) |
| `data/seed_tables.sql` | **Edit** | Add `sent_emails` table DDL |
| `frontend/src/beat2/Beat2Page.tsx` | **Rewrite** | Phase-driven state machine, auto-cascade |
| `frontend/src/beat2/components/EmailPreview.tsx` | **New** | Cinematic email card with branded layout |
| `frontend/src/beat2/components/WorkflowTimeline.tsx` | **Edit** | Live countdown, re-evaluate step, auto-trigger |
| `frontend/src/beat2/components/CampaignPanel.tsx` | **Edit** | Theme token fixes |
| `frontend/src/beat2/components/DecisionPanel.tsx` | **Edit** | Theme token fixes |
| `frontend/src/beat2/components/ReasoningTrace.tsx` | **Edit** | Theme token fixes |
| `frontend/src/beat2/components/CustomerCard.tsx` | **Edit** | Theme token fixes |
| `frontend/src/index.css` | **Edit** | Add status tokens, enforce typography |
| `frontend/public/whiskers.jpg` | **New** | Tabby kitten hero image |
| `tests/test_email_agent.py` | **New** | Copywriter agent tests |
| `tests/test_unified_workflow.py` | **New** | End-to-end workflow tests |

## 9. Acceptance Criteria

1. **Single trigger:** Cart abandon → one workflow → all beats complete automatically
2. **Agent reasoning visible:** 9-domain narrative + 3-panel layout still shows during Step 1
3. **Durable sleep:** Random 15-20s, survives process restart (DBOS guarantee)
4. **Re-evaluation check:** Audience sees the agent verify context before composing
5. **Email preview:** Cinematic reveal with Fluttershy branding, Whiskers hero, agent-composed copy
6. **Simulated send:** "Delivered" badge + `sent_emails` row in Lakebase
7. **Theming:** All components use CSS variable tokens, status colors are semantic, light/dark parity verified, Databricks cyan activated
8. **Typography:** DM Sans for UI, DM Serif Display for narrator/email headings
9. **No manual clicks:** Everything auto-cascades after cart abandon (narrated pauses, not user clicks)
10. **Latency:** Agent reasoning < 2.5s, email composition < 2s, total flow < 30s (excluding sleep)

## 10. Out of Scope

- Real email provider integration (SendGrid/SES) — simulate only
- Email open/click tracking
- Fallback channels (SMS/push)
- Workflow history dashboard
- Decision artifact browser
- Beat 1 store visual changes (beyond CartDrawer trigger fix)
- Mobile responsiveness audit
