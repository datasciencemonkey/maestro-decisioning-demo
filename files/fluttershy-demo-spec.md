# Fluttershy Agentic CDP Demo — Specification

**Status:** Phase A locked, Phase B/C scoped, Build sequencing committed
**Owner:** AI Practice Lead, Databricks
**Audience for this doc:** Practice team, field engineering, demo build squad
**Last reviewed:** Working session, May 2026
**Companion artifacts:** `fluttershy-demo-design-doc.md`, `fluttershy-demo-storyboard.html`

---

## 1. Executive Summary

We are building a scripted, synthetic-data demo that proves Databricks is the **agentic CDP** — your customer data platform IS your data platform, your agents reason across every governed domain, and journey state is durable on the same platform as your analytical state. Phase A is a 15-minute "Land" demo for customers and field engineers. Phase B and C are 30 and 45-minute expansions. The thesis is replacement, not composable. The competition is Salesforce Data Cloud and Adobe RT-CDP.

The strongest single beat is the **agentic disposition core** — the moment a `cart_abandoned` event triggers an agent that reasons across profile, behavior, photo, production calendar, campaigns, support tickets, propensity, and consent — pauses durably for eleven hours via DBOS on Lakebase — then resumes and sends a multimodal segment-of-1 email through a partner ESP. This is what no other CDP can structurally do. Everything else in the demo exists to set up or pay off this beat.

---

## 2. Objectives

### 2.1 Strategic objective
Establish Databricks as the agentic CDP category leader, by demonstrating capabilities that are structurally outside what Adobe RT-CDP and Salesforce Data Cloud can deliver — not because our AI is better, but because their walled gardens end at the marketing schema while ours covers the entire enterprise data estate under one governance plane.

### 2.2 Audience objectives
- **Customers (primary for Phase A):** marketing leaders see cross-campaign reasoning + multimodal + durability and recognize this as a generational change. Data/AI leaders see the architectural elegance of one governance plane and recognize this as future-proof.
- **Field engineers (primary for Phase B/C, secondary for A):** see a deployable Asset Bundle, deep architecture, full MLflow lineage. Can confidently sell, replicate, and extend the pattern in customer environments.

### 2.3 Phasing objective
- **Phase A (15 min, Land):** open the door. Customer says "tell me more."
- **Phase B (30 min, Expand 1):** prove ML depth. Agent builds the propensity model itself.
- **Phase C (45 min, Expand 2):** prove agent-as-product. Agent talks to Cindy directly. Field engineer architectural deep-dive.

### 2.4 Technical objective
Ship the agentic disposition core as a reusable, well-contracted Databricks-native pattern. The surface (browser, ops dashboard, email preview) is configurable; the core is the moat.

---

## 3. Assumptions

| # | Assumption | Implication |
|---|---|---|
| 1 | Identity resolution is out of scope — the customer is a known, authenticated user at demo start | We can drop the "stitching" beat covered by a separate Databricks demo |
| 2 | Synthetic data only — this is not a customer POC | Cost, IP risk, and data residency concerns are bounded |
| 3 | Print-on-demand business model — Fluttershy is Shutterfly-shaped (no SKU inventory) | "Inventory" is replaced by `production_calendar` (lead times by product type & shipping option) |
| 4 | Activation is intentionally a partner — Braze, SendGrid, or whichever ESP the customer uses | We are not building an ESP; we are positioning ESP-agnosticism as a feature |
| 5 | Foundation models accessed via AI Gateway — Claude, Llama, or customer choice | Stack is provider-abstracted. Per-customer model preference does not break the demo |
| 6 | Demo is scripted with deterministic-replay fallback for any live model call | A network blip or auth failure during a customer meeting cannot collapse the live demo |
| 7 | All durable agent state lives inside the Databricks governance plane (Lakebase, not external Postgres) | The "one governance plane" thesis is structurally true, not just rhetorical |
| 8 | The customer (e.g. Fluttershy) brings their existing brand, product catalog, and customer data — Databricks is the *platform*, not the brand | Our demo is illustrative of what a brand can build *on Databricks*, not a Databricks-branded consumer product |

---

## 4. Outcomes & Success Criteria

### 4.1 Demo reception (qualitative)

| Audience | Target reception | Signal |
|---|---|---|
| Marketing leader at CDP-curious customer | 9/10 | "How do we get this into our environment?" within 48h |
| Data/AI leader at same customer | 9/10 | Asks for Phase B and architectural deep-dive |
| Field engineer | 7/10 from Phase A alone, 9/10 with B/C | Can articulate the thesis to a customer without slides |
| Adobe / Salesforce account team in the room | Visibly annoyed | Indirect: they coach the customer harder afterward |

### 4.2 Demo reception (quantitative — for tracking)
- Pipeline created within 30 days of demo: track per delivery
- Repeat customer requests for re-runs: track per delivery
- Field-engineer self-serve replication time: target ≤ 1 hour from Asset Bundle deploy

### 4.3 Business outcome
Phase A becomes the standard top-of-funnel demo for Databricks AI Practice. Asset Bundle is replicated by field engineers across the global team within one quarter of GA.

---

## 5. Constraints

| # | Constraint | Why |
|---|---|---|
| 1 | 15-minute Phase A runtime; hard ceiling 17:30 | Customer attention; agenda budgets in customer meetings |
| 2 | Synthetic data only; no real customer data | Privacy, IP, and reproducibility |
| 3 | No copyrighted brand imagery (Shutterfly, Disney, real cats from stock services without license) | Legal and reputational |
| 4 | Tier 1 streaming hygiene must exist (events filtered before agent disposition) | Cost defensibility for technical buyers; see §7 |
| 5 | Beat 3 (Activation) limited to 3 visible UI elements; rest are verbal callouts | Pacing. Six on-screen elements would rush |
| 6 | Live model calls require deterministic-replay fallback | Network/auth failures during live demo cannot collapse the narrative |
| 7 | All durable state must be inside the Databricks governance plane | The thesis fails if DBOS lands on external Postgres |
| 8 | Phase A does NOT show agent-built ML models or live customer chat | Those are Phase B and Phase C respectively. Don't leak the reveal |

---

## 6. Tech Choices

| Layer | Choice | Rationale |
|---|---|---|
| Agent authoring | **Pydantic AI** | Mature support for skills, multi-agent, MCP tools. Customer choice of framework is itself part of the "open framework on Databricks" pitch. |
| Agent wrapping | **MLflow ResponsesAgent** | Gives AI Playground, Agent Eval, Agent Monitoring out of the box. Connects Pydantic AI to the Databricks-native observability story. |
| Agent serving | **Mosaic AI + Databricks Apps** | Native serving surface; Apps gives the UI hosting story for free in Phase B/C. |
| Durability | **DBOS on Lakebase** | Workflow-level durability + Postgres-compatible OLTP in same governance plane as analytical state. THE structural moat. |
| Tools | **Unity Catalog Functions + MCP servers** | UC Functions for typed business logic with native UC governance; MCP for partner integrations (ESP send, etc) |
| Foundation models | **Claude / Llama via AI Gateway** | Provider-abstracted; customer selects. Gateway logs every call for audit. |
| Vector search | **Mosaic AI Vector Search**, auto-synced from Delta | Multimodal magic for Beat 1 (cat photo embedding) and Beat 3 (visually-similar stock cat selection) |
| ML | **AutoML → MLflow Registry → Model Serving** | Phase B reveals the agent built this in-flow |
| Observability | **MLflow Tracing throughout, OpenTelemetry-compatible** | Single trace spans agent + tool calls + model inference + journey state |

**Explicitly NOT chosen:**
- External Postgres (Supabase, Neon, RDS) — would fragment governance
- LangGraph as primary authoring framework — Pydantic AI's typed-tool ergonomics fit our story; LangGraph remains an "or this" alternative for customers
- Temporal or Airflow for workflow durability — DBOS on Lakebase is structurally tighter for the "one governance plane" thesis
- Building our own ESP — explicit non-goal; activation is the only function we let leave the platform

---

## 7. Disposition Tiering (the core's design contract)

The agent is the disposition engine — but every event hitting the agent is a real cost. To make the architecture defensible at customer scale, we layer dispositions in three tiers.

### 7.1 Tier 1 — Hygiene (microseconds, near-free)
Streaming SQL at the Delta layer drops events that are not real or not actionable: bots, dupes, opt-outs, hard "do not contact" states, race conditions where the order has already completed, hard-cap breaches on frequency. This is not deciding *whether to act* — it is deciding *whether the event is real*.

### 7.2 Tier 2 — Agent disposition (seconds, expensive)
Everything that survives Tier 1 hits the agent. Propensity score, frequency caps, support tickets, production calendar, consent — all are *inputs* to reasoning, not gates before it. The agent is the disposition engine, not a downstream system that a rule engine deigns to invoke. **This is the demo's hero capability.**

### 7.3 Tier 3 — Disposition intensity (the agent's actual decision)
The agent does not decide "act / don't act." It decides intervention intensity calibrated to funnel depth and signal richness:

| Funnel depth | Disposition intensity (typical) |
|---|---|
| Add-to-cart bounce | In-app personalization next visit (zero send cost) |
| Cart abandon mid-checkout | Email at optimal send time |
| Payment-page abandon | Email + offer + possible discount unlock |
| Multi-day no-engagement after cart | Channel escalation per consent; agent reconsiders entirely |

### 7.4 Why this matters for the demo and beyond
The Beat 2 reasoning trace IS the magic. A pre-filter for "recoverability" before the agent recreates the Salesforce/Adobe rule-engine-gates-AI pattern and undermines our thesis. Tier 1 catches noise; Tier 3 calibrates intensity. Both are visible in the trace; neither pre-empts the agent.

We will show one inline trace line in Beat 2 confirming Tier 1 hygiene ran (`tier1_hygiene: passed (2,847 events dropped this min · 312 to agent)`) — invisible to non-technical viewers, signals to technical buyers that we are not naive about cost.

---

## 8. Storyline & Beat Structure

### 8.1 Phase A — The 15-minute Land

| Beat | Length | Hero capability |
|---|---|---|
| Setup | 1:00 | Audience meets Cindy + Whiskers; architecture flash |
| 1. Browser | 3:00 | Real-time multimodal personalization (photo → embedding → re-rank) |
| 2. Reason | 5:45 | Cross-campaign agentic reasoning over data outside the marketing stack |
| 2.5. Durability | 0:45 | Journey paused 11h 42m on DBOS/Lakebase, agent rehydrated context |
| 3. Activate | 3:30 | Segment-of-1 multimodal email composed, vector-search visual match, partner ESP send |
| Close | 1:00 | Architecture replacement chart + Phase B tease |
| **Total** | **15:00** | **Hard ceiling 17:30** |

> **The differentiation lives in Beats 2 and 2.5.** Beats 1, 3, and Close are setup and payoff. The other beats can be redesigned, re-skinned, or re-paced without breaking the thesis. Beats 2 and 2.5 *are* the thesis. **Build them first; gate everything else on them.** See §11.2 and the Beat 2 build brief.

### 8.2 The narrative spine (one sentence per beat)
1. **Browser** — multimodal personalization happens live.
2. **Reason** — the agent reaches into domains no other CDP can touch.
3. **Durability** — and holds the journey across time without leaving the platform.
4. **Activate** — to deliver a segment of one.
5. **Close** — that's seven CDP functions replaced, one kept by choice.

### 8.3 Phase B — Expand 1 (30 min, +15)
- Agent invokes AutoML on a Delta feature set, registers the model in MLflow, deploys it to Model Serving, then uses it. The "score 0.81" from Beat 2 retroactively becomes "the agent built this an hour ago."
- Journey complications: Cindy doesn't open the 8 AM email. DBOS wakes the journey 24h later; the agent re-reasons with current context — switches creative, drops 10% off, escalates to SMS only if consent permits.

### 8.4 Phase C — Expand 2 (45 min, +15)
- Cindy opens a chat in the order-status surface. The same agent (different surface) talks to her, knows her full context, can update the order, schedule a redo, write back to her profile — all governed.
- Architecture deep-dive for field engineers: MLflow trace walk, AI Gateway logs, UC audit logs, Asset Bundle deploy.

---

## 9. Storyline Traceability — Original Notes vs. Current Spec

The original IMG_1083 notes specified a Shutterfly-flavored agentic personalization demo. Below is a faithful trace of how each original element maps to the current Phase A and beyond.

### 9.1 Direct matches (original element → current beat)

| Original element | Current beat | Match quality |
|---|---|---|
| Part 1 / 1a — "identified who Cindy is" | Setup + Beat 1 (Cindy is known authenticated user) | Direct |
| Part 1 / 1b — "NBA / recommendations while browsing" | Beat 1 — NBA panel + product re-rank | Direct |
| Part 1 / 1b — "understood Cindy's browsing cat options / uploaded cat photo" | Beat 1 — photo upload triggers embedding + re-rank | Direct, deepened with Vector Search auto-sync from Delta |
| Part 1 — "Cindy abandoned cart" | Beat 1 → Beat 2 transition | Direct |
| Part 2 / 2a — "agent grab everything about Cindy and recommend cross-campaign prioritization" | Beat 2 — full reasoning trace | Direct, deepened with production calendar, frequency cap, support tickets, propensity, send time |
| Part 2 — "decided to target Cindy for abandoned cart over seasonal promotion" | Beat 2 — Spring Seasonal suppressed, Abandoned Cart prioritized | Direct |
| Part 2 — "remove Cindy from seasonal promotion campaign" | Beat 2 — campaign panel animates the suppression | Direct |
| Part 3 — "agent triggered send email (segment = 1) via partner send email API" | Beat 3 — agent composes + sends via Braze MCP | Direct |
| Part 3 — "personalize the email with cat stock photos of the same kind of cat" | Beat 3 — Vector Search returns top-3 visually-similar tabby kittens, agent selects best | Direct, deepened with explicit Vector Search story |

### 9.2 Original "TBD" elements

| Original TBD | Current placement |
|---|---|
| Part A — "agent decided we need a propensity model? Or agent builds the model" | **Phase B** — fully exercised: feature engineering, AutoML, MLflow registration, Model Serving deploy, in-flow use |
| Part B — "talk to my customer via the agent. Talk to Cindy" | **Phase C** — agent-as-product on order-status surface |

### 9.3 Additions to the original storyline

These were not in the original notes but emerged from working sessions and are now part of the spec:

| Addition | Why |
|---|---|
| **Cindy/Whiskers character arc** — kitten name in profile from prior order, kitten reference photo is new, builds "Welcome Home" book | Narrative spine. One sentence in setup, paid off three times (Beat 1 photo upload, Beat 3 email subject "Whiskers' Welcome Home album," Phase C "agent talks about Whiskers"). Makes the demo emotionally resonant rather than only technically impressive. |
| **Beat 2.5 — Durability Bridge** (DBOS on Lakebase) | The hero structural moat. Beat 2's "send at 8 AM" creates a tension the audience feels but doesn't articulate. Resolving it with durable journey state inside the same governance plane is the move that makes Salesforce/Adobe journey-builder stories sound dated. |
| **Tier 1/2/3 disposition layering** | Cost defensibility for technical buyers. Without it, the architecture is naive at customer scale. |
| **Production calendar** (replacing "inventory") | Print-on-demand business model fit. Anyone from POD/marketplace would have spotted "inventory" as wrong. |
| **Specific tech stack lock** | The original notes did not specify framework or runtime. Pydantic AI + MLflow ResponsesAgent + DBOS-on-Lakebase + Mosaic AI Vector Search are now committed. |
| **MLflow trace visualization as the demo's hero asset** | The original notes did not call this out, but the trace IS the magic of Beat 2 and must be invested in heavily. |
| **Replacement-not-composable framing** | The original notes did not frame posture vs. competitors. We are explicitly replacement: Databricks owns 7 of 8 CDP functions, activation is partner-by-choice. |

### 9.4 Refinements / sharpenings of original elements

| Original phrasing | Refinement |
|---|---|
| "abandoned cart" | All add-to-cart bounce events post-Tier-1 hygiene flow to the agent. The agent disposes them at calibrated intensity per Tier 3 (in-app vs. email vs. email+offer). |
| "stock cat photos of the same kind of cat" | Mosaic AI Vector Search returns top-3 visually-similar stock kittens from an 8.4k image catalog (image embedding similarity). Agent selects the one with highest similarity score. |
| "send email API" | MCP tool call to Braze (or whichever ESP). Partner-agnostic. AI Gateway logs the model call; UC audits the data access; activation is governed end-to-end even though the send leaves the platform. |
| "Part A: agent decided we need this classic propensity model?? And do feature engineering. Or agent builds a model for us" | Phase A scopes this to "agent calls a pre-existing propensity model serving endpoint." Phase B reveals the agent built that model itself in a prior turn — full feature engineering, AutoML, registration, deployment. |

### 9.5 Match assessment
The current Phase A is a faithful, deepened, and de-risked rendering of the original storyline. Every original beat has a direct corresponding beat in the current script. The two original TBD items are correctly deferred to Phase B and C. The additions (Whiskers arc, Durability Bridge, Tier model, replacement framing, stack lock) strengthen the narrative without contradicting any original element.

---

## 10. Cost & Economics (back-of-envelope)

For a customer-the-size-of-Fluttershy with ~10M end users:

| Variable | Order-of-magnitude estimate |
|---|---|
| Daily active users with carts | ~3-5% of total = 300k–500k |
| Daily abandon events | ~70% of carts created = ~210k–350k |
| Tier 1 hygiene retention rate | ~60-80% of events flow to Tier 2 |
| Tier 2 agent dispositions/day | ~125k–280k |
| Cost per disposition (multi-step reasoning, ~3-5k input tokens, ~500 output, plus tool calls) | ~$0.005–$0.02 |
| **Daily agent compute cost for the brand** | **~$625–$5,600/day** |
| Annualized | ~$230k–$2M/year |

### 10.1 What this number means
- **Per end user, this is $0.0001–$0.001 per shopper per year** — economically trivial for a brand with cart-recovery uplift in the percentage points.
- This is *just* agent compute. Tool calls (Vector Search, Model Serving), storage, and Lakebase OLTP are additional but materially smaller.
- **Tier 1 hygiene is what makes this defensible.** Without it, costs scale linearly with raw event volume rather than with actionable events.

### 10.2 What we will NOT do in the demo
Quote a specific dollar number. Customer traffic profiles vary by 10x. We will instead build a **calculator** the field can use in deal motion, taking the customer's actual `daily_active_users`, `cart_creation_rate`, and `abandon_rate` as inputs.

### 10.3 Calculator inputs (to be built)
- `daily_active_users`
- `cart_creation_rate` (% of DAU who create a cart)
- `abandon_rate` (% of carts that abandon)
- `tier1_drop_rate` (% of events filtered by hygiene; default 30%)
- `cost_per_disposition_low` ($0.005 default)
- `cost_per_disposition_high` ($0.02 default)
- `model_used` (selects token cost defaults)

Output: low/high daily, monthly, annual cost per brand. Cost-per-shopper. Comparison to incremental revenue from a 5% cart-recovery uplift.

---

## 11. Build Plan & Sequencing

### 11.1 Sequencing principle
**Build the agentic disposition core first.** The surface (browser, ops dashboard, email preview) is configurable; the core is the moat. Define output contracts up front so a UI — any UI — can render the core's outputs human-legibly later.

### 11.2 Build phases

| Phase | Deliverable | Duration | Parallel |
|---|---|---|---|
| 1. Synthetic data | UC tables populated, Vector Search index built, journey_state schema in Lakebase | 1 week | — |
| **2. Beat 2 + Beat 2.5 — the differentiation core** | Pydantic AI authoring, MLflow ResponsesAgent wrapping, tool implementations, DBOS persistence + resumption, full output contracts. **This is the build's gate. Phase 4 does not start until Beat 2 acceptance criteria pass.** | 2-3 weeks | with 3 |
| 3. Trace rendering | The MLflow trace UI — annotated, drillable, narratable. The demo's highest-risk single component. | 1 week | with 2 |
| 4. Surface layer (Beats 1, 3) | Browser + ops dashboard + email preview, all reading from real agent outputs | 2 weeks | — |
| 5. Polish & rehearse | Pre-warm endpoints, deterministic-replay fallback, scripted execution timing, asset bundle | 1 week | — |
| **Total** | | **~7 weeks** | |

### 11.3 Output contracts the core MUST emit (regardless of which surface consumes them)

These contracts make the surface a thin rendering layer.

**Tool call trace event:**
```
{
  trace_id, span_id, parent_span_id,
  tool_name, tool_inputs, tool_outputs,
  latency_ms, tokens_in, tokens_out, cost_usd,
  uc_lineage_refs, mlflow_run_id, timestamp
}
```

**Decision artifact:**
```
{
  decision_id, customer_id, journey_id,
  verdict (e.g. "re-prioritize"),
  decisions: [{type: "suppress_from", target: "Spring Seasonal"}, ...],
  contributing_signals: [{signal, value, weight}, ...],
  optimal_send_time, channel, tone,
  trace_id (link to reasoning)
}
```

**Journey state row (Lakebase):**
```
journey_state (
  journey_id PK, customer_id, current_step,
  next_action_due_ts, state_blob JSONB,
  status (pending, in_progress, completed, failed),
  created_at, updated_at, last_resumed_at
)
```

**Composed output (pre-render):**
```
{
  output_id, customer_id, decision_id,
  channel: "email",
  payload: {subject, body, image_refs: [...], cta_url},
  send_time, esp: "braze",
  approved_at, sent_at, send_receipt
}
```

Email skin renders from this. SMS skin renders from this. In-app card renders from this. The agent does not bake HTML.

### 11.4 What to start writing this week (Beat 2 substrate)

These three deliverables are the substrate for Beat 2's reasoning loop. Everything else builds on them. The agent's reasoning loop *itself* — which tools to call, in what order, and how to combine — is the actual Beat 2 build, but it cannot start until these are in place.

1. The `journey_state` table schema in Lakebase, with one example row hand-inserted, and a notebook that queries it.
2. The agent's tool contract definitions in Pydantic — typed inputs, typed outputs, MLflow-traced. Even before the agent exists, the tools should be callable and produce trace events.
3. The DBOS workflow definition — `persist_journey_state` and `resume_journey` as proper DBOS-decorated functions, with a unit test that proves a state survives a process restart.

### 11.5 Placeholder browser surface during phase 2

Even while the polished surface is deferred, a stripped-down placeholder browser fires real events into the event stream when a button is clicked. This makes the `cart_abandoned` event *real* and *traceable* end to end during phase 2 development. Doesn't need to be beautiful. Needs to fire real telemetry into Delta.

### 11.6 Beat 2 acceptance gate (must pass before Phase 4)

The Beat 2 build is gated by an explicit acceptance review. **Phase 4 (surface layer) does not start until these criteria pass.** Full criteria are documented in `beat-2-build-brief.md` §11. Summary:

**Concrete (testable):**
- All tool calls emit structured trace events matching the §11.3 contract
- Decision artifact JSON validates against schema and persists to Lakebase
- Total reasoning latency ≤ 1.5s (target), ≤ 2.0s (ceiling) on warm path
- Trace shows at least one branching decision (agent decides tool order based on prior outputs, not as fixed sequence)
- Trace shows at least one signal contradiction reconciled
- DBOS persist_journey_state confirmed via Lakebase row inspection
- Trace replays deterministically from recorded run

**Qualitative (review by practice lead + 2 reviewers):**
- Non-technical viewer reads the trace and articulates the agent's reasoning without technical guidance
- Reasoning reads as judgment, not as a script
- At least one viewer in user testing says some version of "that's actually thinking"

**Auto-block conditions:**
- Trace looks like a fixed script of tool calls (no branching, no judgment visible)
- Decision artifact reads as a templated output, not a reasoned conclusion
- Latency exceeds 2.5s on warm path

---

## 12. Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | Activation partner: name Braze explicitly in script, or stay generic? | Practice Lead | Phase 4 build |
| 2 | Synthetic dataset: build new vs fork existing demo dataset? | TBD | Phase 1 build |
| 3 | Foundation model for live demo: Claude or Llama? (Gateway abstracts but the demo may call it out) | TBD | Phase 5 polish |
| 4 | Cindy's reference cat photo — generate AI-synthetic or license stock? | TBD | Phase 1 build |
| 5 | Demo environment: shared workspace or per-rep? | Field ops | Phase 5 |
| 6 | Cost calculator: standalone tool, embedded in Asset Bundle, or sales-engineering spreadsheet? | Practice Lead + Field | Post-Phase A GA |
| 7 | Phase B AutoML model: real training run on synthetic data, or pre-trained for demo determinism? | TBD | Phase B planning |
| 8 | Asset Bundle structure: one bundle for Phase A, one per phase, or modular? | Field engineering | Phase 5 |

---

## Appendix A — Synthetic Data Model

All tables in Unity Catalog under `fluttershy_demo.cdp`.

| Table | Purpose | Phase |
|---|---|---|
| `customers` | Profile (incl. `pet_name`, `pet_type`, `consent_status`, `preferred_channel`, `quiet_hours_tz`) | A |
| `events` | Streaming behavioral events (page views, uploads, cart actions, abandons) | A |
| `orders`, `order_items` | Transaction history + open carts | A |
| `products`, `product_images` | Catalog + image refs for embedding | A |
| `product_image_embeddings` | Mosaic AI Vector Search index, auto-synced from Delta | A |
| `campaigns`, `campaign_membership`, `campaign_priority` | Active campaigns, segment membership, frequency caps | A |
| `production_calendar` | Lead times by product type and shipping option | A |
| `support_tickets` | Open + recent tickets per customer | A |
| `consent` | Opt-ins, channel prefs, quiet hours, GDPR/CPRA flags | A |
| `propensity_scores` | Model serving endpoint output cache | A |
| **`journey_state`** | DBOS-backed durable state. Written in Beat 2, read on resume in Beat 3. | A |
| `feedback_labels` | Agent eval / human review labels | B |
| `feature_store_*` | Feature engineering artifacts produced by Phase B AutoML | B |

---

## Appendix B — Agent Tools and Skills

> **Architectural distinction.** Most entries below are **tools** — typed, deterministic function calls that read from UC, hit a serving endpoint, or invoke an MCP server. They have no agency. A handful are **skills** — composite paths that involve agent reasoning (prompt construction, context assembly, output validation). The reasoning *loop itself* — which tools to call, in what order, and how to combine — is the most important "skill" and is not enumerated below because it *is* the agent.
>
> This distinction matters: tools are weeks-of-engineering, skills are months-of-prompt-and-eval-design. Don't conflate the build effort.

### B.1 Tools (deterministic substrate)

These are typed function calls, MLflow-traced, governed under UC. No LLM in the loop.

| Tool | Signature | Storage / source |
|---|---|---|
| `read_profile` | `(customer_id) -> Profile` | UC `customers` |
| `read_cart` | `(customer_id) -> Cart` | UC `orders` (open) + `order_items` |
| `check_production_feasibility` | `(product_id, ship_by) -> Feasibility` | UC `production_calendar` |
| `list_active_campaigns` | `(customer_id) -> [Campaign]` | UC `campaigns` + `campaign_membership` |
| `check_frequency_cap` | `(customer_id, channel, window_days) -> CapStatus` | UC `campaigns` aggregation |
| `read_support_tickets` | `(customer_id, lookback_days) -> [Ticket]` | UC `support_tickets` |
| `score_propensity` | `(customer_id, intent) -> Score` | Model Serving endpoint |
| `find_visually_similar_images` | `(image_uri, top_k) -> [ImageMatch]` | Mosaic AI Vector Search |
| `send_via_partner` | `(esp, draft) -> SendReceipt` | MCP tool to Braze/SendGrid/etc |

### B.2 Skills (agent reasoning paths — Phase A)

These wrap LLM reasoning around tool calls. Prompt engineering and eval loop are part of the build.

| Skill | Signature | Reasoning involved |
|---|---|---|
| `compose_email` | `(template, context) -> EmailDraft` | Foundation Model API call. Prompt construction, brand voice, output validation, retry logic. |
| `persist_journey_state` | `(customer_id, step, due_ts, blob) -> JourneyHandle` | Decides which subset of state to serialize, formats for DBOS, writes to Lakebase. |
| `resume_journey` | `(journey_id) -> RehydratedContext` | DBOS-triggered. Reads Lakebase, decides which fields to rehydrate into agent working memory, re-establishes context. |

### B.3 The unenumerated skill — the reasoning loop

Not a tool. Not in any table. The agent's system prompt, working memory, tool-selection logic, and output structuring is **the demo's actual differentiation.** Acceptance criteria for this skill are in `beat-2-build-brief.md` §11.

### B.4 Phase B additional skills/tools

- `engineer_features(spec) -> FeatureSet` *(skill — feature design + prompt construction)*
- `train_with_automl(features, target, time_budget) -> ModelCandidate` *(tool — wraps AutoML API)*
- `register_model(candidate) -> ModelVersion` *(tool — MLflow Registry write)*
- `deploy_model(version, endpoint) -> ServingEndpoint` *(tool — Model Serving API)*
- `decide_intervention_intensity(funnel_depth, signals) -> Intensity` *(skill — Tier 3 reasoning)*

### B.5 Phase C additional skills/tools

- `respond_to_customer(channel, message_thread) -> AgentReply` *(skill — full conversational reasoning)*
- `update_order(order_id, mutation) -> OrderHandle` *(tool — UC + transactional write)*
- `write_back_profile(customer_id, attributes) -> WriteAck` *(tool — UC write with consent check)*

---

*End of specification.*
