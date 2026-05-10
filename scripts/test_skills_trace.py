"""Test pydantic-ai-skills with MLflow tracing through Databricks AI Gateway."""
import os
for key in list(os.environ):
    if key.startswith("OTEL_"):
        del os.environ[key]

import asyncio
import mlflow
from databricks.sdk import WorkspaceClient
from databricks_openai import AsyncDatabricksOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai_skills import SkillsCapability

# --- Workspace + MLflow ---
w = WorkspaceClient(profile="9cefok")
os.environ["DATABRICKS_HOST"] = w.config.host
os.environ["DATABRICKS_TOKEN"] = w.config.authenticate()["Authorization"].replace("Bearer ", "")
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Users/sathish.gangichetty@databricks.com/maestro-cdp")
mlflow.pydantic_ai.autolog()

# --- LLM via AI Gateway ---
client = AsyncDatabricksOpenAI(workspace_client=w)
provider = OpenAIProvider(openai_client=client)
model = OpenAIChatModel("databricks-claude-sonnet-4-6", provider=provider)

# --- Agent with Skills ---
agent = Agent(
    model,
    instructions="You are a helpful assistant with access to skills. Use them when relevant.",
    capabilities=[SkillsCapability(directories=["./skills"])],
)


async def main():
    result = await agent.run("Please greet Sathish warmly.")
    print(f"\n--- Agent Response ---\n{result.output}")
    print(f"\n--- Usage ---\nTokens: {result.usage()}")


if __name__ == "__main__":
    asyncio.run(main())
