# Fluttershy Agentic CDP Demo — Design Doc

**Owner:** AI Practice Lead, Databricks
**Status:** Phase A locked, Phase B/C scoped
**Audience:** Customers + Databricks field engineers
**Vehicle:** Scripted synthetic-data demo (no real customer data, no real ESP integration in Phase A)

---

## 1. Strategic Frame

**Thesis (the spine of every beat):**
> *The composable, agent-native CDP: your customer data platform IS your data platform. Agents reason across marketing, product, ops, supply chain, and finance in one governance plane — with full ML lifecycle, multimodal data, and durable agent state included.*

**Posture:** Replacement, not composable. Databricks owns profiles, segments, journey state, decisioning, ML, multimodal personalization, agent orchestration, and governance. Activation is the only function that leaves the platform (Braze / partner ESP). That is intentional — we are not an ESP.

**Why this is differentiated:** Adobe RT-CDP and Salesforce Data Cloud sell *AI bolted onto a CDP*. Their walled garden ends at the marketing schema. We sell *agents native to the data platform you already have*, which means agents reach into inventory, support, supply chain, finance, and any other governed domain — and reason across all of it in one trace.

**Out of scope for Phase A:** identity resolution (covered by separate demo), bake-off vs. competitors (deferred), live customer-facing agent (Phase C).

---

## 2. The Land-and-Expand Plan

| Phase | Length | Audience emphasis | Hero capabilities |
|---|---|---|---|
| **A — Land** | 15 min | Customers (primary), field (secondary) | Real-time multimodal, cross-campaign reasoning, segment-of-1 activation |
| **B — Expand 1** | 30 min | Both | Adds: agent invokes AutoML + serves model, multi-day journey orchestration |
| **C — Expand 2** | 45 min | Field engineers (primary) | Adds: agent talks back to Cindy, deeper architecture, governance walk |

This doc fully specs Phase A. Phase B and C are sketched in §10.

---

## 3. The Cindy Character Arc

One sentence in setup, sourced once, paid off three times.

> *Cindy recently adopted a new tabby kitten named Whiskers. She's back on Fluttershy today building a "Welcome Home, Whiskers" photo book. The cat's name is in her profile from a previous order; the kitten reference photo she's about to upload is new.*

Why this matters: it sources the cat name (used in Beat 3 copy), explains the photo upload sequence (Beat 1), makes the segment-of-1 stock-cat match emotionally satisfying (Beat 3), and sets the runway for Phase C ("agent talks to Cindy about Whiskers"). Cost: one sentence. Value: makes the entire demo emotionally resonant instead of merely technically impressive.

---

## 4. Phase A — The 15-Minute Demo (Locked Script)

### Setup (1 min)

**Spoken:** "Meet Cindy — a known customer, cat parent, back on Fluttershy today building a photo book for her new kitten Whiskers. Everything you're about to see runs on Databricks. One platform, one governance plane, one agent."

**On screen:** Architecture diagram lights up the components that will be exercised. Hold for 5 seconds.

---

### Beat 1 — Real-time multimodal personalization (3 min)

**POV:** Cindy's browser. Camera narrated: *"Let's look over Cindy's shoulder."*

**Sequence:**
1. Cindy lands on Fluttershy, browses cat-themed photo book templates.
2. She uploads a reference photo of Whiskers (a tabby kitten).
3. NBA panel updates *live* with cat-matched template recommendations. Tabby-pattern templates surface to the top.
4. She adds a "Welcome Home" template to cart.
5. She abandons cart and closes the tab.

**Under the hood (visible on screen as a small annotation panel):**
- Web events stream to Delta via Auto Loader / DLT
- Image embedding generated, written to Vector Search (auto-synced from Delta)
- Pydantic AI agent reads UC profile + behavioral stream + product vector index
- MLflow trace updates in real time, visible in the corner

**Moat line:** *"Her photo, her behavior, her profile — one governance plane. No bolted-on vector DB, no ETL between systems."*

---

### Beat 2 — Cross-campaign agentic reasoning (the hero — 6 min)

**POV cut:** *"Now let's switch to the marketing ops view."* Camera transitions to a dark dashboard. Narration explicit so audience tracks the cut.

**Setup on screen:** A "Spring Seasonal Promotion" campaign is queued for tomorrow morning, 9 AM. Cindy is in its segment. The cart-abandon event from Beat 1 just fired. The agent activates.

**Agent reasons across (each step visible in the trace as it executes):**

1. **Profile** — UC `customers` table. Whiskers, recent kitten adoption, repeat buyer, opens email.
2. **Cart contents** — UC `orders` (open) + `order_items`. "Welcome Home" tabby template, $42.
3. **Production lead time** — UC `production_calendar`. *"If we send the offer now, can it ship by her implied deadline?"* Yes — 4-day production, standard shipping.
4. **Active campaigns + frequency caps** — UC `campaigns` + `campaign_membership`. Cindy is in Spring Seasonal (sends tomorrow). Frequency cap = 2/week. Sending both = cap breach.
5. **Support tickets** — UC `support_tickets`. No recent friction. Safe to engage.
6. **Propensity score** — Model serving endpoint `cindy_abandon_recover_v3`. Score: 0.81. *(Phase B will reveal the agent built this model itself.)*
7. **Optimal send time** — Model output: peak conversion T+3.5h post-abandon for Cindy's behavioral cohort.

**Decision rendered on screen:**
- ✅ Suppress Cindy from Spring Seasonal Promotion
- ✅ Prioritize Abandoned Cart Recovery
- ✅ Tone: warm + personal (kitten context)
- ✅ Send: T+3.5h (≈ 11:30 PM her local time → adjusted to 8 AM next morning by quiet-hours policy)
- ✅ Channel: email (her preferred channel from `consent` table)

Full MLflow reasoning trace visible. Each step clickable to drill into the underlying data the agent saw.

**Moat lines:**
- *"No other CDP reaches into production scheduling and support tickets. Their walled garden ends at the marketing schema."*
- *"Every step of this reasoning is governed, logged, and replayable — same lineage as your batch ETL."*

---

### Beat 2.5 — Durability bridge (45 sec)

**Why this beat exists:** Beat 2 ended with "send at 8 AM tomorrow." That decision creates a tension the audience feels but doesn't articulate: *what holds the journey across 11+ hours, across infra restarts, without losing context?* This beat resolves it before the question gets asked.

**On screen (compressed visual moment, not a separate dashboard):**

1. A `journey_state` card slides into the decision panel: *journey_id, current_step=`awaiting_send`, next_action_due_ts=`2026-05-10T08:00 CT`, persisted to Lakebase via DBOS.*
2. Time-lapse animation: clock advances 8:18 PM → 8:00 AM. Caption: "11h 42m · journey paused, agent idle, state durable."
3. Resumption card flips: *DBOS triggered · workflow resumed · agent rehydrated context from Lakebase.*

**Spoken (15 sec):** *"The agent isn't sitting in memory waiting. Journey state is persisted via DBOS to Lakebase — Postgres-compatible, governed under the same Unity Catalog as our analytical tables. Eleven hours later, the workflow wakes up, the agent rehydrates Cindy's full context, and we're ready to send. No external workflow engine, no separate operational database, no governance fragmentation."*

**Moat line:** *"One governance plane covers analytical state, agent state, and ML lifecycle. Try that on any other stack."*

**Why this lands hard:** This is the beat that field engineers will quote back to customers. It's also the beat that makes Salesforce/Adobe journey-builder stories sound like 2018. Worth the 45 seconds.

---

### Beat 3 — Segment-of-1 multimodal activation (3:30 — tightened from 4:00)

**POV:** Split view — agent panel on the left (dark), email preview on the right (light).

**Three visible elements (others called out verbally to keep timing tight):**

1. **Email copy generates live** — Foundation Model API call. Subject line writes itself: *"Whiskers' Welcome Home album is waiting 🐾"*. Body copy types in: *"That tabby template you started capturing Whiskers in..."*
2. **Visually-similar cats panel** — Vector Search returns top-3 stock photos of tabby kittens that visually match Whiskers' uploaded reference. One is selected and inserted into the email.
3. **Email preview renders** — Final composed email, ready to send.

**Verbal callouts (not on screen, but said aloud):**
- *"This send goes through an MCP tool call to Braze — or whichever ESP the customer uses. We're not locking you in."*
- *"AI Gateway logs the model call. Unity Catalog audits the data access. The activation is governed end-to-end."*

**Moat line:** *"Segment of one. Multimodal. Governed. Activation-agnostic. Your ESP, our brain."*

---

### Close (1 min)

**On screen:** Architecture diagram returns. Components light up to show what got replaced:
- ✅ Customer 360 → Lakehouse + UC
- ✅ Real-time decisioning → Pydantic AI agent + Mosaic AI
- ✅ ML scoring → MLflow + Model Serving
- ✅ Multimodal personalization → Foundation Models + Vector Search
- ✅ Journey state → DBOS on Lakebase
- ✅ Agent runtime → Mosaic AI + Databricks Apps
- ⬜ Activation → *intentionally* partner (Braze / SendGrid / etc.)

**Spoken close:** *"In 15 minutes, one agent reasoned across Cindy's profile, behavior, photo upload, your production calendar, your campaigns, your support tickets, your ML models — paused for eleven hours, durably — and made a single, governed, multimodal decision. That's not a CDP with AI bolted on. That's the agentic CDP, native to your data platform."*

**Tease Phase B:** *"In our next session, we'll show you how the agent built that propensity model itself — full feature engineering, AutoML, registration, deployment — and how the journey handles complications when Cindy doesn't open the first email."*

---

## 5. Synthetic Data Model

All tables in Unity Catalog under `fluttershy_demo.cdp`. Designed for Phase A but provisions for B/C added now to avoid retrofit.

| Table | Purpose | Phase |
|---|---|---|
| `customers` | Profile (incl. `pet_name`, `pet_type`, `consent_status`, `preferred_channel`, `quiet_hours_tz`) | A |
| `events` | Streaming behavioral events (page views, uploads, cart actions) | A |
| `orders`, `order_items` | Transaction history + open carts | A |
| `products`, `product_images` | Catalog + image refs for embedding | A |
| `product_image_embeddings` | Vector Search index, auto-synced | A |
| `campaigns`, `campaign_membership`, `campaign_priority` | Active campaigns, segment membership, frequency caps | A |
| `production_calendar` | Lead times by product type & shipping option (replaces "inventory" — fits print-on-demand model) | A |
| `support_tickets` | Open + recent tickets per customer | A |
| `consent` | Opt-ins, channel prefs, quiet hours, GDPR/CPRA flags | A |
| `propensity_scores` | Model serving endpoint output cache | A |
| **`journey_state`** | DBOS-backed durable state · written in Beat 2.5, read on resume | A (exercised) |
| `feedback_labels` | Agent eval / human review labels | B |

`journey_state` schema sketch: `(customer_id, journey_id, current_step, state_blob, next_action_due_ts, last_updated)` with DBOS transactions writing through Lakebase Postgres, mirrored to Delta for analytics.

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  UNITY CATALOG GOVERNANCE PLANE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ Delta Tables │  │ Vector Search│  │ Lakebase (Postgres) │    │
│  │ (analytical) │  │ (multimodal) │  │ (operational, DBOS) │    │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬──────────┘    │
│         │                 │                     │               │
│         └─────────────────┼─────────────────────┘               │
│                           │                                     │
│                  ┌────────▼─────────┐                           │
│                  │   Pydantic AI    │ ◄── MLflow Tracing         │
│                  │      Agent       │                           │
│                  │ (ResponsesAgent  │ ◄── AI Gateway             │
│                  │   wrapped)       │                           │
│                  └────────┬─────────┘                           │
│                           │                                     │
│   ┌───────────────────────┼───────────────────────┐             │
│   │                       │                       │             │
│   ▼                       ▼                       ▼             │
│ Foundation         Model Serving           UC Functions /       │
│ Model APIs         (propensity,            MCP Tools            │
│ (claude/llama)     embeddings)             (incl. Braze)        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ Databricks    │
                   │ Apps (UI)     │
                   └───────────────┘
```

**Component choices:**
- **Agent authoring:** Pydantic AI (skills, multi-agent, MCP tools)
- **Wrapping:** MLflow `ResponsesAgent` interface — gives us AI Playground, Agent Eval, Agent Monitoring out of the box
- **Serving:** Mosaic AI Model Serving + Databricks Apps for the UI
- **Durability:** DBOS on Lakebase (single governance plane with analytical state)
- **Tools:** UC Functions for typed business logic; MCP for Braze and similar partner APIs
- **Models:** Foundation Model APIs through AI Gateway (Claude / Llama, customer choice)
- **Vector:** Mosaic AI Vector Search auto-synced from Delta product images
- **ML:** AutoML → MLflow Registry → Model Serving (Phase B reveals agent did this)
- **Observability:** MLflow Tracing throughout, OpenTelemetry-compatible

---

## 7. Agent Design

**Single supervisor agent** with skill-based routing. Phase A keeps this single-agent for clarity; Phase B will introduce sub-agents.

**Skills (Pydantic AI):**
- `read_profile(customer_id) -> Profile`
- `read_cart(customer_id) -> Cart`
- `check_production_feasibility(product_id, ship_by) -> Feasibility`
- `list_active_campaigns(customer_id) -> [Campaign]`
- `check_frequency_cap(customer_id, channel) -> CapStatus`
- `read_support_tickets(customer_id, lookback_days) -> [Ticket]`
- `score_propensity(customer_id, intent) -> Score` *(Phase B reveals this is dynamic)*
- `find_visually_similar_images(image_uri, top_k) -> [ImageMatch]`
- `compose_email(template, context) -> EmailDraft`
- `send_via_partner(esp, draft) -> SendReceipt` *(MCP tool)*
- `persist_journey_state(customer_id, step, due_ts, blob) -> JourneyHandle` *(DBOS → Lakebase)*
- `resume_journey(journey_id) -> RehydratedContext` *(DBOS-triggered)*

**Tools all live in UC Functions or MCP servers — UC governance applies to every tool call.**

---

## 8. Production / Execution Notes

### The five mistakes already corrected

1. ~~Inventory~~ → **Production lead time** (fits print-on-demand business model — anyone from POD/marketplace would have spotted "inventory" as wrong in 4 seconds).
2. **Photo upload sequence** is now explicit (browse → upload reference → build → add to cart → abandon).
3. **"Whiskers" is sourced** in setup as a profile field from a previous order. No mystery context.
4. **"4 hours" anchored** in propensity model output ("peak conversion T+3.5h for cohort"), then quiet-hours policy adjusts it to 8 AM.
5. **POV shifts narrated** — "let's look over her shoulder" / "let's switch to marketing ops" / "split view: agent on left, email on right."

### Execution risks to watch

- **The MLflow trace UI in Beat 2 is the demo's emotional and technical peak.** If it looks like raw JSON or unreadable logs, the wow collapses. Invest serious time in trace presentation: annotated, paced, narrated, drillable. Don't discover this is broken three days before the demo.
- **The durability time-lapse in Beat 2.5 must look effortless.** The risk is the audience reads it as a literal pause and gets restless. Keep the animation under 8 seconds, narrate over it, and have the resumption card pre-loaded so it pops in immediately.
- **Beat 3 timing.** Six visible elements would rush; we cut to three on-screen with the rest as verbal callouts. Hold this discipline.
- **Cindy's cat photo.** Need a real-looking but synthetic / royalty-free tabby kitten image. No copyrighted material. Generate one or use a clearly-licensed stock asset.
- **Live model calls during the demo.** Pre-warm endpoints. Have a deterministic-replay fallback for the agent reasoning (recorded trace) in case of network/auth issues during a customer meeting.

### Aesthetic direction

- **Beat 1 must look like a real e-commerce site**, not a magazine or design portfolio. Conventions to honor: utility bar with free-shipping promo, search bar in header, category nav, breadcrumb, filter sidebar, product cards with star ratings + price + Add-to-Cart, cart drawer with shipping estimate, urgency badges (Bestseller, Tabby Match). Reference points: Minted and Artifact Uprising for the premium-photo-product brand voice; Shutterfly and Mixbook for shopping mechanics. Marketing leaders watch e-commerce sites all day — they will spot magazine-tone and lose trust in the rest of the demo.
- **Beat 2 should feel like a serious operations console**, not a chat interface. Dense data, dark theme, monospace traces, real timestamps, drillable rows.
- **Beat 3 split-screen** — agent panel left (operational, dark), customer-facing email preview right (brand, light). The contrast is the whole point.

### Repeatability for field engineers

Whole demo ships as a Databricks Asset Bundle. A field engineer can `databricks bundle deploy` into a customer's workspace and have a working version running in under an hour. This is not a Phase A on-screen beat, but it *is* a Phase A deliverable.

---

## 9. Predicted Reception

| Audience | Score | Notes |
|---|---|---|
| Marketing leader at a CDP-curious customer | 9/10 | Cross-campaign + multimodal land hard. Will ask about ID resolution — point to the other demo. |
| Data/AI leader at the same customer | 9/10 | The "one governance plane" line lands. Will want Phase B for the ML story. |
| Field engineer | 7/10 from Phase A alone | They need Phase B/C depth. That's intentional — Phase A is for selling, B/C is for enabling. |
| Adobe/Salesforce account team in the room | Annoyed. | That's the right reaction. |

The 9/10 customer score assumes nailed live execution. The script supports it; delivery has to.

---

## 10. Phase B and C — sketches only

**Phase B (30 min, adds 15):**
- **Agent built the propensity model.** The "score 0.81" in Beat 2 retroactively becomes "the agent built this an hour ago" — full reveal: feature engineering on Delta, AutoML run, MLflow registration, deployment to Model Serving, then in-flow inference. The full ML lifecycle, agent-orchestrated.
- **Journey complications.** Cindy doesn't open the 8 AM email. DBOS wakes the journey 24h later — but the agent now decides differently: switch creative, drop a 10% offer, escalate channel to SMS only if `consent` permits. Demonstrates the journey logic isn't a fixed workflow — it's an agent reasoning at every wake-up with full current context.

**Phase C (45 min, adds 15):**
- Cindy opens a chat in the order-status view; the same agent (different surface) talks to her, knows her full context, can update the order, schedule a redo, and write back to her profile — all governed.
- Architecture deep-dive for field engineers, including a walk through MLflow traces, AI Gateway logs, UC audit logs, and the Asset Bundle that ships the whole thing.

---

## 11. Open Questions

| # | Question | Owner | Phase |
|---|---|---|---|
| 1 | Activation partner: name Braze explicitly in the script, or stay generic "partner ESP"? | Practice Lead | A |
| 2 | Synthetic dataset — build new, or fork an existing demo dataset? | TBD | A |
| 3 | Foundation model choice for live demo — Claude or Llama? (UI Gateway abstracts but the demo might call it out) | TBD | A |
| 4 | Real cat photo asset for Cindy's upload — generate or license? | TBD | A |
| 5 | Demo environment — shared workspace or per-rep? | Field ops | A |

---

## Appendix A — Beat-level timing budget

| Beat | Target | Hard ceiling |
|---|---|---|
| Setup | 1:00 | 1:15 |
| Beat 1 | 3:00 | 3:30 |
| Beat 2 | 5:45 | 6:30 |
| **Beat 2.5 — Durability** | **0:45** | **1:00** |
| Beat 3 | 3:30 | 4:00 |
| Close | 1:00 | 1:15 |
| **Total** | **15:00** | **17:30** |

**Where the 45 seconds came from:** trimmed Beat 2 by 15s (cut the second moat line — it lands as repetition after the durability moat line) and Beat 3 by 30s (one fewer verbal callout, slightly faster typing animation). Beat 2.5 is net-zero on total runtime, but pulls a Phase B capability into the sales motion.

If overrun looks likely, drop the second moat line in Beat 2 and the AI Gateway / UC verbal callout in Beat 3. Never cut on Beat 2's reasoning trace dwell or the time-lapse animation in 2.5 — they are the demo's two emotional peaks.
