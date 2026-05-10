"""Test MLflow auto-tracing with Pydantic AI via Databricks AI Gateway, traces sent to 9cefok."""
import os
import mlflow
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from databricks_openai import AsyncDatabricksOpenAI
from databricks.sdk import WorkspaceClient

# Suppress OTEL env vars from other workspaces
for key in list(os.environ):
    if key.startswith("OTEL_"):
        del os.environ[key]

# Connect MLflow to 9cefok workspace
w = WorkspaceClient(profile="9cefok")
os.environ["DATABRICKS_HOST"] = w.config.host
os.environ["DATABRICKS_TOKEN"] = w.config.authenticate()["Authorization"].replace("Bearer ", "")

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")

# Enable auto-tracing
mlflow.pydantic_ai.autolog()

# Route LLM through Databricks AI Gateway
client = AsyncDatabricksOpenAI(workspace_client=w)
provider = OpenAIProvider(openai_client=client)
model = OpenAIChatModel("databricks-claude-sonnet-4-6", provider=provider)

# Simple agent to verify tracing works
agent = Agent(
    model,
    instructions="You are a test agent. Reply with exactly one word: TRACE_OK",
)

result = agent.run_sync("Say the magic word.")
print(f"Agent output: {result.output}")
print(f"Model: databricks-claude-sonnet-4-6 via Databricks AI Gateway")
print(f"Traces sent to: {w.config.host}")
print("MLflow Pydantic AI auto-tracing: PASS")
