"""
train.py — Model Training Layer
=================================
Michelangelo Mini Demo · Step 2

This script simulates the **training pipeline** of the Michelangelo
architecture:

  1. Reads the feature + label Parquet produced by generate_features.py.
  2. Trains an XGBoost regression model to predict taxi fare amounts.
  3. Logs parameters, metrics, and the model artifact to MLflow.
  4. Registers the model in the MLflow Model Registry and sets the
     alias ``champion`` so the serving layer can load it by alias.

Usage:
    python train.py                          # train with default hyper-params
    python train.py --n_estimators 200       # override hyper-params
"""

import argparse
import os

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# ── Configuration ────────────────────────────────────────────────────────────
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DEMO_DIR, "data")
LABELS_PATH = os.path.join(DATA_DIR, "taxi_labels.parquet")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = "taxi-fare-demo"
MODEL_NAME = "taxi-fare-model"


def parse_args():
    parser = argparse.ArgumentParser(description="Train XGBoost taxi fare model")
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=6)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Connect to MLflow ────────────────────────────────────────────────
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

    # ── Load data ────────────────────────────────────────────────────────
    print("━" * 60)
    print("STEP 1 ▸ Loading training data …")
    df = pd.read_parquet(LABELS_PATH)
    feature_cols = ["trip_distance", "pickup_hour", "pickup_weekday", "passenger_count"]
    X = df[feature_cols]
    y = df["fare_amount"]
    print(f"   ✔ {len(df)} rows loaded.  Features: {feature_cols}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed,
    )

    # ── Train ────────────────────────────────────────────────────────────
    print()
    print("STEP 2 ▸ Training XGBoost model …")
    params = {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "learning_rate": args.learning_rate,
        "random_state": args.seed,
        "objective": "reg:squarederror",
    }

    with mlflow.start_run() as run:
        mlflow.log_params(params)

        model = XGBRegressor(**params)
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        # ── Evaluate ─────────────────────────────────────────────────
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = r2_score(y_test, y_pred)

        mlflow.log_metrics({"mae": mae, "rmse": rmse, "r2": r2})
        print(f"   ✔ MAE  = {mae:.4f}")
        print(f"   ✔ RMSE = {rmse:.4f}")
        print(f"   ✔ R²   = {r2:.4f}")

        # ── Log model to MLflow ──────────────────────────────────────
        print()
        print("STEP 3 ▸ Logging model to MLflow …")
        mlflow.xgboost.log_model(
            model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
        )
        print(f"   ✔ Model logged under run {run.info.run_id}")

    # ── Set "champion" alias ─────────────────────────────────────────────
    print()
    print("STEP 4 ▸ Setting alias 'champion' on latest version …")

    # Get the latest version that was just registered
    latest_versions = client.search_model_versions(
        f"name='{MODEL_NAME}'", order_by=["version_number DESC"], max_results=1,
    )
    if latest_versions:
        version = latest_versions[0].version
        client.set_registered_model_alias(MODEL_NAME, "champion", version)
        print(f"   ✔ Alias 'champion' → v{version}")
    else:
        print("   ⚠ No model version found — alias not set.")

    print()
    print("━" * 60)
    print("Training complete.  Model registered and alias set.")
    print(f"MLflow UI: {MLFLOW_TRACKING_URI}")
    print("━" * 60)


if __name__ == "__main__":
    main()
