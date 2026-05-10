#!/usr/bin/env python
"""Train a propensity model using Databricks AutoML.

Beat 2.5+ stub — demonstrates the pattern without calling real APIs.
Replace the stub functions with actual Databricks SDK calls when ready.

Usage:
    uv run python skills/automl-propensity/scripts/train_propensity.py \
        --campaign-type cart_recovery
"""

import argparse
import json
import sys


def train_propensity_model(
    campaign_type: str,
    training_table: str,
    target_column: str,
    profile: str,
) -> dict:
    """Stub: Train a propensity model via Databricks AutoML.

    In production, this would:
    1. from databricks.sdk import WorkspaceClient
    2. w = WorkspaceClient(profile=profile)
    3. experiment = w.experiments.create_automl_experiment(
           experiment_name=f"propensity_{campaign_type}",
           dataset_name=training_table,
           target_col=target_column,
           problem_type="classification",
           timeout_minutes=30,
       )
    4. Wait for experiment completion
    5. Select best model run
    6. Register model: w.model_registry.create_model(
           name=f"maestro_cdp.models.propensity_{campaign_type}",
           source=f"runs:/{best_run_id}/model",
       )
    7. Create serving endpoint: w.serving_endpoints.create(
           name=f"propensity-{campaign_type}",
           config=EndpointCoreConfigInput(served_models=[...]),
       )
    """
    model_name = f"maestro_cdp.models.propensity_{campaign_type}"
    endpoint_name = f"propensity-{campaign_type}"

    print(f"[STUB] Would train AutoML model for campaign_type={campaign_type}")
    print(f"[STUB] Training table: {training_table}")
    print(f"[STUB] Target column: {target_column}")
    print(f"[STUB] Profile: {profile}")
    print(f"[STUB] Model would be registered as: {model_name}")
    print(f"[STUB] Serving endpoint would be: {endpoint_name}")

    return {
        "model_name": model_name,
        "endpoint_name": endpoint_name,
        "experiment_url": f"https://fevm-serverless-9cefok.cloud.databricks.com/#mlflow/experiments/propensity_{campaign_type}",
        "accuracy": 0.847,
        "status": "stub_complete",
    }


def main():
    parser = argparse.ArgumentParser(description="Train propensity model via AutoML")
    parser.add_argument("--campaign-type", required=True, help="Campaign type (e.g., cart_recovery)")
    parser.add_argument("--training-table", default="maestro_cdp.features.customer_events",
                        help="UC table with training data")
    parser.add_argument("--target-column", default="converted", help="Target column name")
    parser.add_argument("--profile", default="9cefok", help="Databricks CLI profile")
    args = parser.parse_args()

    result = train_propensity_model(
        campaign_type=args.campaign_type,
        training_table=args.training_table,
        target_column=args.target_column,
        profile=args.profile,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
