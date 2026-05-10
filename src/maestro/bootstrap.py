"""Shared bootstrap for Maestro CDP demo.

Initializes workspace auth, MLflow tracing, AI Gateway model,
Lakebase connection, and DBOS. Import and call bootstrap() once
at the start of any script or test.
"""

import os
import json
import subprocess
from urllib.parse import quote_plus


def _clear_otel_env():
    """Remove stale OTEL_* env vars from other workspaces."""
    for key in list(os.environ):
        if key.startswith("OTEL_"):
            del os.environ[key]


def get_lakebase_url(database: str = "maestro_cdp", profile: str = "9cefok") -> str:
    """Build a Lakebase PostgreSQL connection URL."""
    project = "maestro-cdp"
    branch_path = f"projects/{project}/branches/production"
    endpoint_path = f"{branch_path}/endpoints/primary"

    host = json.loads(subprocess.run(
        ["databricks", "postgres", "list-endpoints", branch_path,
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)[0]["status"]["hosts"]["host"]

    token = json.loads(subprocess.run(
        ["databricks", "postgres", "generate-database-credential", endpoint_path,
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["token"]

    email = json.loads(subprocess.run(
        ["databricks", "current-user", "me",
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["userName"]

    return f"postgresql://{email}:{quote_plus(token)}@{host}:5432/{database}?sslmode=require"


def get_lakebase_conn_params(database: str = "maestro_cdp", profile: str = "9cefok") -> dict:
    """Get Lakebase connection params as a dict (for psycopg2.connect(**params))."""
    project = "maestro-cdp"
    branch_path = f"projects/{project}/branches/production"
    endpoint_path = f"{branch_path}/endpoints/primary"

    host = json.loads(subprocess.run(
        ["databricks", "postgres", "list-endpoints", branch_path,
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)[0]["status"]["hosts"]["host"]

    token = json.loads(subprocess.run(
        ["databricks", "postgres", "generate-database-credential", endpoint_path,
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["token"]

    email = json.loads(subprocess.run(
        ["databricks", "current-user", "me",
         "--profile", profile, "--output", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)["userName"]

    return dict(host=host, port=5432, database=database,
                user=email, password=token, sslmode="require")


def bootstrap(profile: str = "9cefok"):
    """Initialize workspace, MLflow, AI Gateway model, and Lakebase.

    Returns:
        tuple: (model, db_url) where model is an OpenAIChatModel
               routed through Databricks AI Gateway, and db_url is
               the Lakebase PostgreSQL connection string.
    """
    _clear_otel_env()

    import mlflow
    from databricks.sdk import WorkspaceClient
    from databricks_openai import AsyncDatabricksOpenAI
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    # Workspace auth
    w = WorkspaceClient(profile=profile)
    os.environ["DATABRICKS_HOST"] = w.config.host
    os.environ["DATABRICKS_TOKEN"] = w.config.authenticate()["Authorization"].replace("Bearer ", "")

    # MLflow tracing
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
    mlflow.pydantic_ai.autolog()

    # LLM via AI Gateway (custom endpoint at /ai-gateway/mlflow/v1)
    from openai import AsyncOpenAI
    from pydantic_ai.profiles.openai import OpenAIModelProfile

    host = w.config.host.rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    token = os.environ["DATABRICKS_TOKEN"]
    client = AsyncOpenAI(
        api_key=token,
        base_url=f"{host}/ai-gateway/mlflow/v1",
    )
    provider = OpenAIProvider(openai_client=client)
    # AI Gateway doesn't support strict tool definitions
    profile = OpenAIModelProfile(openai_supports_strict_tool_definition=False)
    model = OpenAIChatModel("maestro-endpoint", provider=provider, profile=profile)

    # Lakebase URL
    db_url = get_lakebase_url(profile=profile)

    return model, db_url
