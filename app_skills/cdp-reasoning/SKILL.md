---
name: cdp-reasoning
description: Best practices for cross-campaign CDP disposition reasoning. Use when evaluating customer engagement decisions involving frequency caps, campaign prioritization, channel selection, and send-time optimization.
---

# CDP Cross-Campaign Reasoning

Domain best practices for making cross-campaign disposition decisions. Load this skill when reasoning about customer engagement across multiple campaigns.

## When to Use

- A customer event (cart abandoned, browse, purchase) requires a disposition decision
- Multiple campaigns are active for the same customer
- Frequency caps may be breached
- Send time must account for quiet hours and timezone

## Campaign Priority Hierarchy

When multiple campaigns target the same customer, prioritize by trigger type:

1. **Triggered** (event-driven, e.g., cart abandonment) — highest priority; time-sensitive, directly tied to customer intent
2. **Active/Scheduled** (e.g., seasonal promos) — lower priority; batch sends, not intent-driven
3. **Paused** — no action; waiting for reactivation
4. **Dormant** — no action; long-term holdout

A triggered campaign always outranks a scheduled campaign for the same channel window.

## Frequency Cap Resolution

When a frequency cap breach is detected:

1. **Suppress the lower-priority campaign**, not the higher-priority one
2. Never suppress a triggered campaign in favor of a scheduled one
3. Document the suppression with the reason (e.g., "frequency_cap_breach")
4. If ALL campaigns would breach, suppress all and flag for human review

Example: Customer has email cap=2/week, current=1, queued=1 (Spring Seasonal). Adding Abandoned Cart Recovery would breach. Suppress Spring Seasonal, prioritize Cart Recovery.

## Quiet Hours Policy

- Never schedule sends during quiet hours (typically 9 PM – 7 AM in customer timezone)
- If the optimal send time falls in quiet hours, shift to the next available window (typically 8 AM next day)
- Always use the customer's timezone, not UTC or system timezone
- Document the adjustment: "Original T+3.5h lands at 11:48 PM CT (quiet hours); shifted to 8 AM CT next day"

## Tone Selection

Match tone to customer context:

- **Pet owner** → warm, personal; reference the pet by name (e.g., "Welcome home, Whiskers!")
- **Repeat buyer** → familiar, appreciative; acknowledge loyalty
- **New customer** → welcoming, helpful; focus on value proposition
- **High-value cart** → attentive, premium; emphasize quality and care
- **Open support ticket** → empathetic, cautious; do not hard-sell

## Channel Preference

Select channel based on:

1. **Consent** — only use channels with active consent (non-negotiable)
2. **Preference** — customer's stated preferred channel
3. **Frequency** — channel with remaining cap headroom
4. **History** — channel with best historical engagement

## Signal Weighting

When synthesizing a decision, weight signals by impact:

| Signal | Typical Weight | Rationale |
|--------|---------------|-----------|
| Frequency cap status | 1.0 (hard constraint) | Breach = must act |
| Propensity score | 0.6–0.8 | Drives urgency |
| Support ticket status | 0.3–0.5 | Friction = caution |
| Production feasibility | 0.3–0.5 | Must be achievable |
| Cart value | 0.2–0.4 | Higher value = more attention |
| Loyalty tier | 0.1–0.3 | Context for tone |

## Anti-Patterns

- Never add a send that would breach frequency cap — always suppress first
- Never ignore quiet hours — even for high-propensity customers
- Never skip support ticket check for high-value carts — friction overrides urgency
- Never use a channel without consent — even if it's the only one with cap headroom
