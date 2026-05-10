"""
Seed Lakebase tables for Maestro CDP demo.

Reads seed_tables.sql and executes it against the maestro_cdp database
on Lakebase (managed PostgreSQL on Databricks).

Usage:
    uv run python data/seed_tables.py
"""

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

import psycopg2

PROFILE = "9cefok"
PROJECT = "maestro-cdp"
DATABASE = "maestro_cdp"

TABLES = [
    "customers",
    "orders",
    "order_items",
    "production_calendar",
    "campaigns",
    "campaign_membership",
    "support_tickets",
    "consent",
    "propensity_scores",
]


def get_lakebase_conn_params() -> dict:
    """Get Lakebase connection parameters from Databricks CLI credentials."""
    host = json.loads(subprocess.run(
        ["databricks", "postgres", "list-endpoints",
         f"projects/{PROJECT}/branches/production",
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)[0]["status"]["hosts"]["host"]

    token = json.loads(subprocess.run(
        ["databricks", "postgres", "generate-database-credential",
         f"projects/{PROJECT}/branches/production/endpoints/primary",
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["token"]

    email = json.loads(subprocess.run(
        ["databricks", "current-user", "me",
         "--profile", PROFILE, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["userName"]

    return dict(host=host, port=5432, database=DATABASE,
                user=email, password=token, sslmode="require")


def run_seed(sql_path: Path) -> None:
    """Connect to Lakebase, execute seed SQL, and print row counts."""
    print(f"Reading SQL from {sql_path}")
    sql_text = sql_path.read_text()

    print("Obtaining Lakebase credentials...")
    params = get_lakebase_conn_params()
    print("Connecting to Lakebase...")

    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()

    # Strip SQL line-comments before splitting so embedded semicolons
    # inside comments (e.g. "-- foo; bar") don't create bogus fragments.
    clean_lines = []
    for line in sql_text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("--"):
            continue
        clean_lines.append(line)
    clean_sql = "\n".join(clean_lines)

    # Split on semicolons, skip empty statements
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
    total = len(statements)
    print(f"Executing {total} SQL statements...\n")

    for i, stmt in enumerate(statements, 1):
        try:
            cur.execute(stmt)
            print(f"  [{i}/{total}] OK")
        except psycopg2.Error as exc:
            print(f"  [{i}/{total}] ERROR: {exc.pgerror or exc}")
            # Continue to next statement rather than aborting
            conn.rollback()
            conn.autocommit = True

    # Print row counts
    print("\n--- Table Row Counts ---")
    for table in TABLES:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table:25s} {count:>6d} rows")
        except psycopg2.Error as exc:
            print(f"  {table:25s} ERROR: {exc.pgerror or exc}")
            conn.rollback()
            conn.autocommit = True

    cur.close()
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    sql_file = Path(__file__).parent / "seed_tables.sql"
    if not sql_file.exists():
        print(f"ERROR: {sql_file} not found", file=sys.stderr)
        sys.exit(1)
    run_seed(sql_file)
