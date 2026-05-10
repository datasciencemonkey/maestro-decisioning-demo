# Fluttershy Agentic CDP Demo — Build Team Handoff

**Date:** May 2026
**From:** AI Practice Lead, Databricks
**For:** Build squad (engineers, designer, demo coordinator)
**Status:** Phase A locked · Ready for build · Beat 2 = your starting target

---

## What this package is

A complete strategic + execution spec for a 15-minute scripted demo proving Databricks is the agentic CDP. Three artifacts you'll already-built (spec, design doc, animated storyboard) plus a build brief for Beat 2, which is where you start.

This is not a customer POC. It is a synthetic-data scripted demo, intended to (a) sell to customers and (b) be replicable by field engineers in customer workspaces via a Databricks Asset Bundle.

The demo's competitive positioning is **replacement, not composable** — Databricks owns 7 of 8 CDP functions, with activation intentionally delegated to a partner ESP (Braze, SendGrid, etc).

---

## Read in this order

| Order | File | What it gives you | Time |
|---|---|---|---|
| 0 | `00-README.md` | This file. Orientation. | 5 min |
| 1 | `fluttershy-demo-spec.md` *or* `.html` | Strategic context — objectives, assumptions, outcomes, constraints, tech choices, disposition tiering, storyline, cost economics, build plan, open questions | 30 min |
| 2 | `fluttershy-demo-design-doc.md` | Phase A locked script — beat-by-beat with timing, POV, on-screen elements, spoken lines | 20 min |
| 3 | `fluttershy-demo-storyboard.html` | Animated visual reference. Open in a browser. Press space to step through scenes. | 10 min interactive |
| 4 | `beat-2-build-brief.md` *or* `.html` | **Your build target.** Everything you need to start coding Beat 2. | 20 min |

The MD and HTML versions of the spec and build brief are content-identical. Use whichever you prefer — engineers tend to like the MD in their editor; design and demo-coordination folks tend to like the HTML.

---

## Key decisions already made

Don't relitigate without practice-lead signoff. These are committed.

- **Stack:** Pydantic AI (authoring) → MLflow ResponsesAgent (wrapping) → Mosaic AI + Databricks Apps (serving) → DBOS on Lakebase (durability) → UC Functions + MCP (tools) → Foundation Model APIs via AI Gateway → Mosaic AI Vector Search.
- **Posture:** replacement, not composable. We do not ship an ESP.
- **Phase A is 15 min** with hard ceiling 17:30. Phase B (30 min) and Phase C (45 min) are scoped, not built.
- **Beat 2 is the differentiation.** Build it first. Phase 4 (surface layer) gates on Beat 2 acceptance.
- **All durable agent state lives in Lakebase.** No external Postgres. This is structural to the thesis.
- **Production calendar replaces "inventory."** Fluttershy is print-on-demand.
- **Cindy / Whiskers character arc is the narrative spine.** Don't drop it for a "more generic" customer story.

---

## Where to start (week 1)

Three concrete deliverables. Every other week of build assumes these exist.

1. **`journey_state` schema in Lakebase** — table created, one example row hand-inserted, notebook that queries it. Owner: data engineer.
2. **Pydantic tool contracts** — typed inputs, typed outputs, MLflow-traced. The 9 tools listed in `beat-2-build-brief.md` §5.1. Even before the agent exists, the tools should be callable and produce trace events. Owner: agent engineer.
3. **DBOS workflow definition** — `persist_journey_state` and `resume_journey` as DBOS-decorated functions, with a unit test that proves state survives a process restart. Owner: agent engineer.

Once these three are done, the agent reasoning loop (the actual Beat 2 build) can start. The build brief §6 has the system prompt sketch and implementation notes.

---

## Beat 2 acceptance gate

Phase 4 (surface layer — Beats 1, 3) does not start until Beat 2 passes review. This is non-negotiable. Full criteria in `beat-2-build-brief.md` §11. Highlights:

**Concrete (testable):**
- Trace shows ≥1 branching decision (agent decides tool order based on prior outputs)
- Trace shows ≥1 signal contradiction reconciled
- Frequency cap breach test: agent suppresses Spring Seasonal in decision artifact
- Latency ≤ 1.5s target / 2.0s ceiling, warm path
- DBOS persistence confirmed via Lakebase row inspection

**Qualitative (practice lead + 2 reviewers):**
- Non-technical viewer reads the trace and articulates the reasoning unaided
- Reasoning reads as judgment, not script
- ≥1 viewer says some version of *"that's actually thinking"*

**Auto-block conditions:** Trace looks like a fixed script · Decision artifact reads as templated · Latency >2.5s · Replay visibly differs from live.

If you hit auto-block, rework. Don't paper over.

---

## What's NOT in this package yet

These are scoped but not yet drafted. Will follow the same template as the Beat 2 build brief.

- **Beat 1 build brief** — browser surface, photo upload, live re-rank, abandon event firing
- **Beat 2.5 build brief** — DBOS resumption, time-lapse animation, journey rehydration
- **Beat 3 build brief** — email composition, vector search, partner ESP send
- **Phase B build briefs** — agent-built propensity model, journey complications
- **Phase C build briefs** — agent-as-product on order-status surface, architecture deep-dive
- **Cost calculator spec** — for sales-engineering deal motion
- **Asset Bundle structure** — for field-engineer replication
- **Synthetic dataset specification** — depends on open question (build vs fork)

Practice lead will draft these in priority order as the build progresses. Beat 1 brief lands before Phase 4 starts; Beat 2.5 and Beat 3 briefs land while Phase 2 is still in progress so the team can prepare.

---

## File index

| File | Purpose |
|---|---|
| `00-README.md` | This handoff index |
| `fluttershy-demo-spec.md` | Strategic spec (12 sections + 2 appendices) |
| `fluttershy-demo-spec.html` | Rendered spec — sticky TOC, document layout, print-friendly |
| `fluttershy-demo-design-doc.md` | Phase A locked script with beat-level detail |
| `fluttershy-demo-storyboard.html` | Animated 5-scene visual reference |
| `beat-2-build-brief.md` | Beat 2 build target — structured, with acceptance criteria |
| `beat-2-build-brief.html` | Rendered build brief |

---

## Open questions you'll hit

See spec §12 for the full list. Highlights you'll likely encounter in week 1:

1. **Activation partner — name Braze, or stay generic?** Practice lead's call. If unsure, build for "ESP-agnostic" and decide late.
2. **Synthetic dataset — build new or fork existing?** Depends on what's already in the practice's demo workspace. Check before scoping.
3. **Foundation model for live demo — Claude or Llama?** AI Gateway abstracts, but the demo may call it out by name. Default Claude for reasoning quality.
4. **Cindy's reference cat photo — AI-synthetic or licensed stock?** Cannot use unlicensed real photos. Recommend AI-synthetic to avoid license tracking.
5. **Beat 2 reasoning model — same as Beat 3 compose, or different?** Default same; revisit if cost-per-disposition pushes back.

---

## Communication

For questions on:

- **Strategic / scope changes** → Practice Lead. Do not change posture, stack, or beat structure without signoff.
- **Technical implementation** → Build squad lead, with practice lead in CC for anything that touches contracts.
- **Demo coordination** (rehearsals, customer scheduling) → Practice ops.

Standing weekly review during build phase. Beat 2 acceptance review is a separate scheduled session with practice lead + 2 reviewers, not a standing meeting.

---

## A note on what makes this demo land

If you take one thing from this package, take this: **the demo lives or dies on Beat 2's reasoning trace looking like real reasoning.** Not on the polish of the browser surface, not on the email design, not on the architecture diagram. The trace.

A senior data architect at a customer can dismiss everything else as wrappers. They cannot dismiss a trace that shows the agent making judgment calls — choosing tool order, reconciling contradictions, applying shortcuts — because no system they've seen does that within their governance plane.

Build the trace as if it's the only thing the customer will remember. Because it is.

---

*— AI Practice Lead*
