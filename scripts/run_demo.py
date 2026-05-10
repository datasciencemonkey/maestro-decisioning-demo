"""Beat 2 + 2.5 Demo — End-to-end run.

Runs the full Maestro CDP agent loop:
1. Cart abandoned event fires for Cindy (cust_88241)
2. Agent reasons across 9 domains → produces DecisionArtifact
3. Decision + journey state persisted to Lakebase
4. DBOS durable sleep (configurable delay)
5. Resume: rehydrate context, mark completed

Usage:
    uv run python scripts/run_demo.py
    uv run python scripts/run_demo.py --delay 5   # short sleep for testing
    uv run python scripts/run_demo.py --agent-only # skip DBOS workflow, just run agent
"""

import argparse
import asyncio
import json
import os
import time

for key in list(os.environ):
    if key.startswith("OTEL_"):
        del os.environ[key]


def run_agent_only():
    """Run just the agent (Beat 2) without DBOS workflow."""
    from maestro.bootstrap import bootstrap
    from maestro.agent import run_maestro
    from maestro.synthetic import CINDY_EVENT

    print("=" * 60)
    print("MAESTRO CDP — Beat 2 Agent Demo")
    print("=" * 60)

    print("\n[1/3] Bootstrapping workspace, MLflow, AI Gateway...")
    model, db_url = bootstrap()

    print(f"[2/3] Running agent for {CINDY_EVENT.customer_id}...")
    print(f"      Cart: ${CINDY_EVENT.cart_total:.2f} — {CINDY_EVENT.cart_id}")
    print(f"      Abandoned at: {CINDY_EVENT.abandoned_at.isoformat()}")

    start = time.perf_counter()
    result = asyncio.run(run_maestro(CINDY_EVENT, model, db_url))
    elapsed = time.perf_counter() - start

    print(f"\n[3/3] Decision rendered in {elapsed:.2f}s")
    print("=" * 60)
    print(f"  Verdict:  {result.verdict}")
    print(f"  Customer: {result.customer_id}")
    print(f"  Journey:  {result.journey_id}")
    print()

    print("  Decisions:")
    for d in result.decisions:
        label = d.type.replace("_", " ").title()
        value = d.target or d.value or ""
        reason = f" ({d.reason})" if d.reason else ""
        print(f"    [{label}] {value}{reason}")

    print()
    print("  Contributing Signals:")
    for s in result.contributing_signals:
        print(f"    {s.signal}: {s.value} (weight={s.weight})")

    print()
    print("  Rationale:")
    print(f"    {result.rationale}")

    print()
    if elapsed <= 1.5:
        print(f"  Latency: {elapsed:.2f}s — TARGET MET")
    elif elapsed <= 2.0:
        print(f"  Latency: {elapsed:.2f}s — within ceiling")
    else:
        print(f"  Latency: {elapsed:.2f}s — OVER CEILING (target ≤2.0s)")

    print("=" * 60)
    return result


def run_full_workflow(delay_seconds: int):
    """Run full Beat 2 + 2.5 with DBOS workflow."""
    from urllib.parse import quote_plus

    from dbos import DBOS, DBOSConfig

    from maestro.bootstrap import get_lakebase_conn_params
    from maestro.synthetic import CINDY_EVENT

    # Import workflow to register DBOS decorators
    from maestro.workflow import journey_workflow

    print("=" * 60)
    print("MAESTRO CDP — Beat 2 + 2.5 Full Demo")
    print("=" * 60)

    print(f"\n[1/4] Initializing DBOS on Lakebase...")
    params = get_lakebase_conn_params()
    db_url = (
        f"postgresql://{params['user']}:{quote_plus(params['password'])}"
        f"@{params['host']}:{params['port']}/{params['database']}?sslmode=require"
    )

    config = DBOSConfig(
        name="maestro-cdp",
        system_database_url=db_url,
        application_database_url=db_url,
    )
    DBOS(config=config)
    DBOS.launch()

    print(f"[2/4] Starting journey workflow (delay={delay_seconds}s)...")
    event_json = CINDY_EVENT.model_dump_json()

    start = time.perf_counter()
    journey_id = journey_workflow(event_json, delay_seconds)
    elapsed = time.perf_counter() - start

    print(f"\n[3/4] Journey completed: {journey_id}")
    print(f"      Total time: {elapsed:.2f}s (includes {delay_seconds}s sleep)")

    # Verify in Lakebase
    import psycopg2
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(
        "SELECT current_step, status FROM journey_state WHERE journey_id = %s",
        (journey_id,),
    )
    row = cur.fetchone()
    if row:
        print(f"      Lakebase: step={row[0]}, status={row[1]}")
    cur.close()
    conn.close()

    print(f"\n[4/4] Shutting down DBOS...")
    DBOS.destroy()

    print("=" * 60)
    print("Demo complete.")
    return journey_id


def main():
    parser = argparse.ArgumentParser(description="Maestro CDP Demo")
    parser.add_argument("--delay", type=int, default=5,
                        help="DBOS sleep delay in seconds (default: 5)")
    parser.add_argument("--agent-only", action="store_true",
                        help="Run just the agent (Beat 2) without DBOS workflow")
    args = parser.parse_args()

    if args.agent_only:
        run_agent_only()
    else:
        run_full_workflow(args.delay)


if __name__ == "__main__":
    main()
