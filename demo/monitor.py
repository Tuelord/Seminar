"""
monitor.py — Monitoring Layer
================================
Michelangelo Mini Demo · Step 4

This script simulates the **monitoring pipeline** of the Michelangelo
architecture:

  1. Reads the prediction log written by serve.py.
  2. Joins predicted fares with actual fares from the ground-truth Parquet.
  3. Computes and prints MAE (Mean Absolute Error) and other metrics.
  4. Optionally breaks down metrics per model version (to compare before/after
     an alias swap).

Usage:
    python monitor.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ── Paths ────────────────────────────────────────────────────────────────────
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DEMO_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "prediction_log.csv")
LABELS_PATH = os.path.join(DATA_DIR, "taxi_labels.parquet")


def main() -> None:
    # ── 1. Load prediction log ───────────────────────────────────────────
    if not os.path.isfile(LOG_PATH):
        print("⚠  No prediction log found.  Run serve.py and send some requests first.")
        sys.exit(1)

    log_df = pd.read_csv(LOG_PATH)
    print("━" * 60)
    print(f"MONITORING REPORT — {len(log_df)} predictions logged")
    print("━" * 60)

    # ── 2. Load ground truth ─────────────────────────────────────────────
    if not os.path.isfile(LABELS_PATH):
        print("⚠  Ground truth file not found.  Run generate_features.py first.")
        sys.exit(1)

    truth_df = pd.read_parquet(LABELS_PATH)[["trip_id", "fare_amount"]]

    # ── 3. Join ──────────────────────────────────────────────────────────
    merged = log_df.merge(truth_df, on="trip_id", how="inner")
    if merged.empty:
        print("⚠  No matching trip_ids between log and ground truth.")
        sys.exit(1)

    y_true = merged["fare_amount"]
    y_pred = merged["predicted_fare"]

    # ── 4. Aggregate metrics ─────────────────────────────────────────────
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)

    print()
    print("Overall Metrics:")
    print(f"  MAE  = {mae:.4f}  (average absolute error in $)")
    print(f"  RMSE = {rmse:.4f}")
    print(f"  R²   = {r2:.4f}")
    print(f"  Predictions matched: {len(merged)} / {len(log_df)}")

    # ── 5. Per-model-version breakdown ───────────────────────────────────
    if "model_version" in merged.columns:
        versions = merged["model_version"].unique()
        if len(versions) > 1:
            print()
            print("Per-Model-Version Breakdown:")
            print(f"  {'Version':<12} {'MAE':>8} {'RMSE':>8} {'R²':>8} {'Count':>7}")
            print(f"  {'─' * 12} {'─' * 8} {'─' * 8} {'─' * 8} {'─' * 7}")
            for ver in sorted(versions, key=str):
                mask = merged["model_version"] == ver
                v_true = merged.loc[mask, "fare_amount"]
                v_pred = merged.loc[mask, "predicted_fare"]
                v_mae = mean_absolute_error(v_true, v_pred)
                v_rmse = float(np.sqrt(mean_squared_error(v_true, v_pred)))
                v_r2 = r2_score(v_true, v_pred) if len(v_true) > 1 else float("nan")
                print(
                    f"  v{str(ver):<11} {v_mae:>8.4f} {v_rmse:>8.4f} "
                    f"{v_r2:>8.4f} {mask.sum():>7}"
                )

    print()
    print("━" * 60)
    print("Monitoring complete.")
    print("━" * 60)


if __name__ == "__main__":
    main()
