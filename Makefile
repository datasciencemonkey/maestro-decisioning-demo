.PHONY: test-local test-dev test-all seed deploy sync

# ── Local tests (no network dependencies except AI Gateway) ──────────────
test-local:
	uv run pytest tests/test_models.py tests/test_tools.py -v

# ── Dev tests (against deployed app + workspace services) ────────────────
test-dev:
	uv run pytest tests/test_system.py tests/test_app_endpoints.py -v -s

# ── All tests ────────────────────────────────────────────────────────────
test-all: test-local test-dev

# ── Seed Lakebase tables ─────────────────────────────────────────────────
seed:
	uv run python data/seed_tables.py

# ── Sync to workspace and deploy ─────────────────────────────────────────
sync:
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/app.py --file src/maestro/app.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/bootstrap.py --file src/maestro/bootstrap.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/agent.py --file src/maestro/agent.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/models.py --file src/maestro/models.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/synthetic.py --file src/maestro/synthetic.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/tools.py --file src/maestro/tools.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/workflow.py --file src/maestro/workflow.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/src/maestro/__init__.py --file src/maestro/__init__.py --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/app.yaml --file app.yaml --format AUTO --overwrite --profile 9cefok
	databricks workspace import /Users/sathish.gangichetty@databricks.com/maestro-cdp-app/pyproject.toml --file pyproject.toml --format AUTO --overwrite --profile 9cefok

deploy: sync
	databricks apps deploy maestro-cdp-demo --no-wait --profile 9cefok

# ── Run demo locally ─────────────────────────────────────────────────────
demo:
	uv run python scripts/run_demo.py --agent-only

demo-full:
	uv run python scripts/run_demo.py --delay 10
