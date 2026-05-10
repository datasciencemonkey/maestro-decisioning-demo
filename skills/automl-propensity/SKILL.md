---
name: automl-propensity
description: Train and deploy propensity models using Databricks AutoML. Use when the agent needs campaign-specific propensity scores and no Model Serving endpoint exists yet, or when retraining is needed for a new campaign type.
---

# AutoML Propensity Model Training

Spawn a Databricks AutoML workflow to train a propensity model for a specific campaign type (e.g., cart_recovery, seasonal_purchase, loyalty_renewal). The trained model is registered in Unity Catalog and deployed to a Model Serving endpoint.

## When to Use

- No propensity model exists for a campaign type
- Existing model is stale (>30 days since last training)
- New campaign type requires its own propensity scoring
- Agent needs real-time propensity scoring instead of cached scores

## What It Does

1. Submits an AutoML classification experiment on customer behavior data
2. Selects the best model from the experiment
3. Registers the model in UC: `maestro_cdp.models.propensity_{campaign_type}`
4. Creates or updates a Model Serving endpoint
5. Returns the endpoint name for `score_propensity` tool to call

## Scripts

### `train_propensity.py`

Train a propensity model for a given campaign type.

**Arguments:**
- `--campaign-type` (required): The campaign type to train for (e.g., cart_recovery)
- `--training-table` (optional): UC table with training data (default: maestro_cdp.features.customer_events)
- `--target-column` (optional): Target column name (default: converted)
- `--profile` (optional): Databricks CLI profile (default: 9cefok)

**Output:** JSON with model_name, endpoint_name, experiment_url, accuracy

## Beat 2 vs Beat 2.5+

- **Beat 2:** `score_propensity` returns cached synthetic scores (0.81 for Cindy). This skill is discoverable but not invoked.
- **Beat 2.5+:** Agent can invoke this skill to train real models. Once the endpoint is live, `score_propensity` calls it instead of returning cached data.

## Prerequisites

- Databricks workspace with ML Runtime
- Feature table with customer behavior data
- Unity Catalog with model registry enabled
