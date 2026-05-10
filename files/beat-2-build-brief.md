# Beat 2 — Build Brief

**Status:** Build target #1 — start here
**Owner:** Build squad lead
**Companions:** `fluttershy-demo-spec.md` (§7 tiering, §11 build plan, Appendix B tools/skills), `fluttershy-demo-design-doc.md` (Beat 2 narrative)

---

## 1. Beat at a Glance

When a `cart_abandoned` event clears Tier 1 hygiene, the agent reasons across nine domains — profile, cart, production calendar, active campaigns, frequency caps, support tickets, propensity, consent, optimal send time — then renders a structured decision (suppress from Spring Seasonal; prioritize Abandoned Cart Recovery; warm tone with Whiskers context; send 8 AM CT; email channel). Total runtime ≤ 1.5s target / 2.0s ceiling. Reasoning is rendered to a viewer-readable trace in the marketing ops UI.

**This is the demo's only differentiation moment.** Every other beat sets it up or pays it off. Acceptance gate (§11) is strict — Phase 4 does not start until this passes.

---

## 2. Objective

Build an agent that, given a `cart_abandoned` event, reasons across the nine domains above and produces:

1. A complete MLflow trace readable by a non-technical viewer as intelligent decision-making
2. A structured decision artifact persisted to Lakebase
3. A `journey_state` row that DBOS can resume on schedule

The reasoning loop must demonstrably:
- **Branch** based on tool outputs (not run as a fixed script)
- **Reconcile** contradicting signals
- **Justify** its decisions in human-legible form

If the trace reads as a sequential list of tool calls with no judgment, this beat fails review.

---

## 3. Scope

### In scope
- Single supervisor agent (Pydantic AI), single-turn reasoning loop
- All Phase A tools (see §5)
- MLflow trace emission for every tool call
- Decision artifact persistence to Lakebase + Delta mirror
- Marketing ops UI panel (campaigns left / trace center / decision right)
- Deterministic-replay capability for live demo
- DBOS `persist_journey_state` only — Beat 2 ends with the row written; Beat 2.5 handles resumption

### Out of scope (deferred to other beats / phases)
- Multi-agent / sub-agent decomposition → Phase B
- Agent-built propensity model → Phase B (Phase A calls a pre-existing endpoint)
- Human-in-the-loop approval → Phase B
- A/B testing variants → Phase B
- SMS / push channel → Phase B
- Browser surface (cart_abandoned event source) → Beat 1 build brief
- DBOS resumption + clock advance → Beat 2.5 build brief
- Email composition + send → Beat 3 build brief
- Tier 1 streaming hygiene → infrastructure-level, separate work item

---

## 4. Inputs

### 4.1 Triggering event

```json
{
  "event_type": "cart_abandoned",
  "customer_id": "cust_88241",
  "cart_id": "cart_77a3f",
  "abandoned_at": "2026-05-09T20:18:00-05:00",
  "cart_total": 42.00,
  "items": [
    {"product_id": "pb_welcome_home_24pp", "qty": 1, "price": 42.00}
  ],
  "source_session_id": "sess_...",
  "tier1_clearance": true
}
```

`tier1_clearance: true` confirms Tier 1 hygiene already filtered bots/dupes/opt-outs/race conditions. Agent does not re-validate.

### 4.2 Reference data (UC tables read via tools)
- `customers` — Cindy's profile (incl. `pet_name=Whiskers`, `pet_type=tabby`, `tz=America/Chicago`)
- `orders` + `order_items` — open cart contents
- `production_calendar` — lead times by product
- `campaigns` + `campaign_membership` — active campaigns + Cindy's segment membership
- `support_tickets` — last 30 days
- `consent` — channel prefs, quiet hours

All accessed via tool calls (§5), never pre-loaded into agent context.

### 4.3 External services
- Model Serving endpoint `cindy_abandon_recover_v3` (propensity)
- Optimal-send-time service (TBD: tool call vs. inline calculation — see §12)
- Foundation Model API via AI Gateway (for the reasoning loop itself)

---

## 5. Tool Calls

All tools typed (Pydantic), MLflow-traced, governed under UC. Full signatures in spec Appendix B.1.

### 5.1 Tools the agent has access to

| # | Tool | Purpose in Beat 2 |
|---|---|---|
| 1 | `read_profile(customer_id) → Profile` | Establish customer context |
| 2 | `read_cart(customer_id) → Cart` | What's in the abandoned cart |
| 3 | `check_production_feasibility(product_id, ship_by) → Feasibility` | Can it still ship in time? |
| 4 | `list_active_campaigns(customer_id) → [Campaign]` | What's queued for this customer? |
| 5 | `check_frequency_cap(customer_id, channel, window_days) → CapStatus` | Would another send breach? |
| 6 | `read_support_tickets(customer_id, lookback_days) → [Ticket]` | Any open friction? |
| 7 | `score_propensity(customer_id, intent) → Score` | Likelihood of recovery |
| 8 | `optimal_send_time(customer_id, cohort, propensity) → SendTimestamp` | When to send |
| 9 | `persist_journey_state(customer_id, step, due_ts, blob) → JourneyHandle` | Hand off to Beat 2.5 |

### 5.2 Typical call sequence (the agent decides; this is illustrative, not enforced)

```
+0.000s  trigger received
+0.041s  read_profile
+0.083s  read_cart
+0.142s  check_production_feasibility
+0.198s  list_active_campaigns
+0.221s  check_frequency_cap          ← BREACH detected on Spring Seasonal
+0.245s  read_support_tickets         ← clean
+0.401s  score_propensity             ← 0.81
+0.512s  optimal_send_time            ← T+3.5h, quiet-hours-adjusted to 8:00 AM CT
+0.643s  persist_journey_state        ← jrn_88241_a3f committed
+0.687s  decision rendered
```

**Critical:** the agent decides which tools to call and in what order. The system prompt must guide reasoning, not enforce a script. See §6.

---

## 6. The Reasoning Loop (the actual differentiation)

### 6.1 What the agent must demonstrate
The reasoning loop is the only thing in Beat 2 that competitors structurally cannot replicate. The acceptance gate (§11) is built around demonstrable reasoning, not tool-call enumeration. Specifically the agent must:

- **Choose tool order based on prior outputs.** Example: call `check_frequency_cap` before `score_propensity` — because if the cap is already breached, the propensity score is moot for this channel and the agent should consider channel switch or suppression.
- **Reconcile contradicting signals.** Example: Cindy is in Spring Seasonal (active campaign) AND frequency cap breach is imminent → suppress, don't add. The reconciliation must appear in the trace.
- **Apply judgment-based shortcuts.** Example: skip support tickets if cart total is below a recoverability threshold. Or expand the lookback window for tickets if propensity is low.
- **Justify its decisions.** Decision artifact must include a `rationale` field with a human-legible summary.

### 6.2 System prompt structure (sketch — to be tuned with eval loop)

```
You are an agentic CDP disposition engine for Fluttershy, a print-on-demand
photo product brand. A cart_abandoned event has fired for {customer_id}.

Your goal: decide how to engage this customer for cart recovery, balancing:
  - Their context (profile, cart, support history)
  - Operational constraints (production calendar, frequency caps, consent)
  - Likelihood of conversion (propensity)
  - Optimal timing (send-time model + quiet-hours policy)

You have access to the following tools:
  read_profile, read_cart, check_production_feasibility,
  list_active_campaigns, check_frequency_cap, read_support_tickets,
  score_propensity, optimal_send_time, persist_journey_state

Reason step by step. Call tools as needed; you decide the order. When a
tool's output makes a subsequent tool unnecessary, skip it and explain why
in your reasoning trace. When two signals contradict, reconcile them
explicitly.

When you have enough information to decide, output a structured
DecisionArtifact (see schema) with:
  - verdict
  - decisions[] (suppress, prioritize, tone, send_time, channel)
  - contributing_signals[] (each with weight)
  - rationale (one paragraph, human-legible)

Then call persist_journey_state with the decided send_time as due_ts.
```

### 6.3 Implementation notes
- Pydantic AI `@agent.tool` registration for all tools
- All tool functions async; agent loop async
- Response format = structured `DecisionArtifact` (Pydantic model — see §9)
- Max iterations: 12 (safety cap; should typically converge in 6-8)
- Foundation model: see §12 open questions

### 6.4 What this is NOT
- A LangChain-style sequential chain
- A fixed pipeline with conditional branches
- A rules engine wrapped in an LLM call

If any of those are easier to build, they are also easier to dismiss in customer review. Build the agent.

---

## 7. UI Elements (Marketing Ops Panel)

Three regions, all reading from real agent outputs (no mocks). Visual reference in `fluttershy-demo-storyboard.html` Scene 2.

### 7.1 Active campaigns panel (left, ~240px)
- List of campaigns Cindy is in: Spring Seasonal Promo, Abandoned Cart Recovery, VIP Loyalty Reload, Reactivation 90d
- Per-campaign states: `default` / `flagged` / `suppressed` / `prioritized`
- Animations driven by trace events:
  - Spring Seasonal → `flagged` when `check_frequency_cap` returns BREACH
  - Spring Seasonal → `suppressed` when decision artifact lands with `suppress_from`
  - Abandoned Cart → `prioritized` when decision artifact lands with `prioritize_in`
- Source: `campaigns` table + decision artifact

### 7.2 Reasoning trace (center, flexible)
- Customer summary card at top: name, customer_id, profile snippet (pet, tz, repeat-buyer status)
- "Thinking..." indicator while agent is mid-reasoning (cyan pulse)
- Trace lines stream in as tool calls fire — each line shows: timestamp, tool icon, tool name, key inputs, key outputs (collapsed by default)
- Each line expandable to show full input/output JSON (Phase A: collapsed only is acceptable; Phase B: expandable)
- After completion: "Decision rendered · {latency}ms · {N} tool calls" status (green)
- Source: MLflow trace events streamed to UI

### 7.3 Decision panel (right, ~320px)
- Verdict header: e.g. "Re-prioritize Cindy"
- Decision rows (5): Suppress from / Prioritize / Tone / Send time / Channel
- Each row: label + value, animated in 200ms intervals after trace completes
- Persistence card at bottom: `journey_id`, `due_ts`, `storage: DBOS · Lakebase`
- Source: decision artifact JSON

### 7.4 Pacing
- Trace lines stream at ~950ms intervals to match real reasoning latency (live)
- In replay mode, identical pacing
- Total Beat 2 runtime: 5:45 target, 6:30 ceiling
- Beat 2.5 (durability bridge) takes over after Beat 2 closes — see Beat 2.5 brief

---

## 8. Trace Event Spec

Every tool call emits one trace event to MLflow. Schema:

```json
{
  "trace_id": "tr_abc123",
  "span_id": "sp_def456",
  "parent_span_id": "sp_root",
  "tool_name": "check_frequency_cap",
  "tool_inputs": {
    "customer_id": "cust_88241",
    "channel": "email",
    "window_days": 7
  },
  "tool_outputs": {
    "cap": 2,
    "current": 1,
    "queued": 1,
    "status": "breach"
  },
  "latency_ms": 23,
  "tokens_in": null,
  "tokens_out": null,
  "cost_usd": 0.0,
  "uc_lineage_refs": ["fluttershy_demo.cdp.campaigns@v37"],
  "mlflow_run_id": "run_xyz",
  "timestamp": "2026-05-09T20:18:01.245-05:00"
}
```

For Foundation Model API calls within the reasoning loop itself, additionally populate `tokens_in`, `tokens_out`, `cost_usd`.

For `persist_journey_state`, additionally include the journey_id and due_ts in `tool_outputs` so the trace UI can render the persistence card.

---

## 9. Decision Artifact Spec

Persisted to UC `decisions` table (Delta) and mirrored to Lakebase for operational reads. Schema:

```json
{
  "decision_id": "dec_a3f88241",
  "customer_id": "cust_88241",
  "journey_id": "jrn_88241_a3f",
  "trigger_event_id": "evt_cart_abandoned_77a3f",
  "verdict": "re-prioritize",
  "decisions": [
    {
      "type": "suppress_from",
      "target": "Spring Seasonal Promo",
      "reason": "frequency_cap_breach"
    },
    {
      "type": "prioritize_in",
      "target": "Abandoned Cart Recovery",
      "weight": 0.81
    },
    {
      "type": "tone",
      "value": "warm, personal, Whiskers context"
    },
    {
      "type": "send_time",
      "value": "2026-05-10T08:00:00-05:00",
      "reason": "T+3.5h adjusted for quiet hours (America/Chicago)"
    },
    {
      "type": "channel",
      "value": "email",
      "reason": "consent + preferred"
    }
  ],
  "contributing_signals": [
    {"signal": "frequency_cap", "value": "breach", "weight": 1.0},
    {"signal": "propensity", "value": 0.81, "weight": 0.7},
    {"signal": "support_tickets", "value": "none", "weight": 0.3},
    {"signal": "production_feasibility", "value": "feasible", "weight": 0.4}
  ],
  "rationale": "Frequency cap breach blocks Spring Seasonal. Propensity high (0.81), support clean, production feasible. Optimal send is T+3.5h, adjusted to 8 AM CT for quiet hours. Channel email per consent.",
  "trace_id": "tr_abc123",
  "created_at": "2026-05-09T20:18:01.687-05:00"
}
```

The `rationale` field is what the decision panel renders verbatim (or summarized) for the audience. Quality of this field is part of the acceptance review.

---

## 10. Live Execution & Failure Modes

### 10.1 Pre-warm checklist (run before every live demo)
- [ ] Model Serving endpoint (propensity) — health-check 30s before start
- [ ] Mosaic AI Vector Search endpoint — pre-warm (used in Beat 3, but warm now to mask Beat 3 latency)
- [ ] Foundation Model API gateway — send no-op prompt to pay cold-start
- [ ] DBOS worker — confirm running and connected to Lakebase
- [ ] UC connection — confirm authenticated session

### 10.2 Deterministic-replay fallback
- Maintain a recorded "golden" trace from a successful run, stored alongside the demo asset bundle
- If any of the following triggers, switch to replay mode automatically:
  - Live run latency exceeds 3s
  - Tool call returns error
  - Foundation Model API rate-limited
- Switch must be invisible to the audience — UI animates the recorded trace at the same pace as the live run would
- Practice lead can also force replay mode via a hotkey before the demo starts (for high-stakes meetings)

### 10.3 Failure modes (graceful degradation)

| Failure | Behavior |
|---|---|
| Model Serving propensity endpoint unavailable | Use cached score from `propensity_scores` table; flag in trace |
| Foundation Model API rate-limited | Fall back to deterministic replay |
| UC tool returns no rows | Log warning, continue (don't crash agent) |
| DBOS persist failure | Log + alert; emit `decision_artifact` without journey_id; Beat 2.5 will surface failure |
| Reasoning loop exceeds max iterations (12) | Return partial decision with `verdict: "incomplete"`, flag for human review |
| Latency exceeds 2.5s warm path | Log to monitoring; if happens twice in rehearsal, fail acceptance review |

---

## 11. Acceptance Criteria

**Phase 4 (surface layer build) does not start until all criteria below pass.** Practice lead + 2 reviewers must sign off.

### 11.1 Concrete (testable, automatable)

- [ ] All 9 tool calls emit structured trace events matching the §8 contract
- [ ] Trace renders in the MLflow trace UI without raw JSON visible to a non-technical viewer (annotations, icons, friendly labels)
- [ ] Decision artifact JSON validates against the §9 schema
- [ ] Decision artifact persists to UC `decisions` table AND mirrors to Lakebase
- [ ] Total agent reasoning latency ≤ 1.5s target / 2.0s ceiling on warm path, measured over 20 runs
- [ ] **Frequency cap breach test case:** given a cart_abandoned event for a customer at email cap=2/2 with a queued seasonal send, the agent's decision artifact MUST include `{"type": "suppress_from", "target": "Spring Seasonal"}`. Hard requirement.
- [ ] **Branching decision visible in trace:** the agent decides tool order based on prior outputs in at least one observable case. Example: skipping `read_support_tickets` when cart total is below threshold, or expanding lookback when propensity is low. Document at least one such case in the build review.
- [ ] **Signal contradiction reconciled in trace:** the agent surfaces and resolves at least one conflict. Example: "active campaign + cap breach → suppress, not skip." The reconciliation must be visible in the trace, not buried in the rationale.
- [ ] DBOS `persist_journey_state` confirmed via Lakebase row inspection — query the row by `journey_id`, verify `due_ts` and `state_blob`
- [ ] Trace replays deterministically from recorded run (replay mode parity with live)
- [ ] All UC reads logged to UC audit log (verify via `system.access.audit`)
- [ ] All Foundation Model calls logged to AI Gateway

### 11.2 Qualitative (review gate — practice lead + 2 reviewers)

- [ ] A non-technical viewer (PM or marketer who hasn't seen the demo) reads the trace and articulates the agent's reasoning in their own words, without technical guidance
- [ ] The reasoning reads as judgment, not as a script. Reviewers can identify at least one moment that "looks like thinking"
- [ ] The decision panel summarizes the rationale clearly enough to defend in a customer Q&A
- [ ] At least one reviewer in user testing says some version of *"that's actually thinking"* unprompted
- [ ] A reviewer with Salesforce or Adobe RT-CDP experience confirms this is structurally outside what those platforms do

### 11.3 Auto-block conditions (FAIL — do not pass review)

- Trace looks like a fixed script of tool calls (no branching, no judgment visible in any run)
- Decision artifact reads as a templated output with values filled in, not a reasoned conclusion
- Latency exceeds 2.5s on warm path more than once in rehearsal
- Replay mode is visibly different from live mode (different pacing, different content, missing animations)
- Customer-architect-grade reviewer dismisses it as "function-calling LLM with extra steps"

---

## 12. Open Questions for Beat 2

| # | Question | Recommendation | Resolve by |
|---|---|---|---|
| 1 | Foundation model: Claude or Llama? | Claude for the live demo (reasoning quality); Llama as documented alternative. Spec leaves open. | Build week 2 |
| 2 | System prompt: hand-tuned or eval-loop-driven? | Eval-loop-driven. Hand-tuning is fragile. Build a small eval set of 20-30 abandoned-cart scenarios with expected verdicts. | Build week 1 |
| 3 | Tool call ordering: enforced via prompt, or fully agent-decided? | Fully agent-decided with system-prompt *guidance.* Enforced ordering kills the differentiation. | Build week 1 |
| 4 | Failed tool call recovery: retry, skip, or abort? | Skip + flag in trace. Retry adds latency; abort kills the demo. | Build week 2 |
| 5 | Trace UI: build custom, or use MLflow native? | Build custom for the demo surface. MLflow native is for engineers. Spec §11.3 calls this the highest-risk component. | Build week 1 |
| 6 | Decision storage: only Lakebase, or also Delta? | Both. DBOS writes to Lakebase (operational), mirror to Delta for analytics. | Build week 1 |
| 7 | `optimal_send_time` — separate tool or inline calculation? | Tool. Easier to swap algorithms; cleaner trace event. | Build week 1 |
| 8 | Synthetic test scenarios — how many for eval set? | 20-30 covering: clean cart-recovery happy path, frequency cap breach, support ticket open, low-propensity skip, payment-page abandon, multi-day no-engagement | Build week 1 |

---

*End of brief.*
