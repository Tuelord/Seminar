"""
generate_features.py — Offline Feature Engineering Layer
=========================================================
Michelangelo Mini Demo · Step 1

This script simulates the **offline feature pipeline** of the Michelangelo
architecture:

  1. Generates synthetic NYC-style taxi trip data.
  2. Saves features + labels to a Parquet file (offline store).
  3. Runs `feast apply` to register feature definitions.
  4. Runs `feast materialize` to push features into the online store (SQLite).

Usage:
    python generate_features.py
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ── Configuration ────────────────────────────────────────────────────────────
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DEMO_DIR, "data")
FEATURE_REPO_DIR = os.path.join(DEMO_DIR, "feature_repo")
PARQUET_PATH = os.path.join(DATA_DIR, "taxi_features.parquet")
LABELS_PATH = os.path.join(DATA_DIR, "taxi_labels.parquet")

NUM_TRIPS = 10_000
RANDOM_SEED = 42


def generate_synthetic_taxi_data(n: int, seed: int) -> pd.DataFrame:
    """
    Create a realistic synthetic taxi dataset.

    Fare formula (hidden ground truth):
        fare = base_fare
             + per_mile_rate × distance × rush_hour_multiplier
             + passenger_surcharge
             + noise

    This gives XGBoost meaningful patterns to learn.
    """
    rng = np.random.default_rng(seed)

    # ── Raw features ─────────────────────────────────────────────────────
    trip_ids = np.arange(1, n + 1)
    trip_distance = rng.exponential(scale=3.0, size=n).clip(0.3, 35.0)
    pickup_hour = rng.integers(0, 24, size=n)
    pickup_weekday = rng.integers(0, 7, size=n)  # 0=Mon … 6=Sun
    passenger_count = rng.integers(1, 7, size=n)

    # Timestamps spread over the last 90 days
    base_ts = datetime(2024, 6, 1)
    event_timestamp = [
        base_ts + timedelta(seconds=int(rng.integers(0, 90 * 86400)))
        for _ in range(n)
    ]

    # ── Fare calculation (ground truth) ──────────────────────────────────
    base_fare = 2.50
    per_mile = 2.50
    rush_hour_mult = np.where(
        ((pickup_hour >= 7) & (pickup_hour <= 9))
        | ((pickup_hour >= 17) & (pickup_hour <= 19)),
        1.35,   # 35 % surcharge during rush hour
        1.00,
    )
    weekend_discount = np.where(pickup_weekday >= 5, 0.90, 1.00)
    passenger_surcharge = (passenger_count - 1) * 0.50
    noise = rng.normal(0, 1.5, size=n)

    fare_amount = (
        base_fare
        + per_mile * trip_distance * rush_hour_mult * weekend_discount
        + passenger_surcharge
        + noise
    ).clip(2.50, None).round(2)

    df = pd.DataFrame(
        {
            "trip_id": trip_ids,
            "event_timestamp": event_timestamp,
            "trip_distance": trip_distance.round(2),
            "pickup_hour": pickup_hour,
            "pickup_weekday": pickup_weekday,
            "passenger_count": passenger_count,
            "fare_amount": fare_amount,
        }
    )
    return df


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── 1. Generate data ─────────────────────────────────────────────────
    print("━" * 60)
    print("STEP 1 ▸ Generating synthetic taxi trip data …")
    df = generate_synthetic_taxi_data(NUM_TRIPS, RANDOM_SEED)

    # Save features (without label) for Feast
    feature_cols = [
        "trip_id",
        "event_timestamp",
        "trip_distance",
        "pickup_hour",
        "pickup_weekday",
        "passenger_count",
    ]
    df[feature_cols].to_parquet(PARQUET_PATH, index=False)
    print(f"   ✔ Features saved → {PARQUET_PATH}  ({len(df)} rows)")

    # Save full dataset (with labels) for training & monitoring
    df.to_parquet(LABELS_PATH, index=False)
    print(f"   ✔ Labels   saved → {LABELS_PATH}")

    # ── 2. Feast apply ───────────────────────────────────────────────────
    print()
    print("STEP 2 ▸ Registering feature definitions (feast apply) …")
    subprocess.run(
        [sys.executable, "-m", "feast", "apply"],
        cwd=FEATURE_REPO_DIR,
        check=True,
    )
    print("   ✔ Feast feature definitions applied.")

    # ── 3. Feast materialize ─────────────────────────────────────────────
    print()
    print("STEP 3 ▸ Materializing features to online store (feast materialize) …")
    start_date = "2024-01-01T00:00:00"
    end_date = "2024-12-31T23:59:59"
    subprocess.run(
        [
            sys.executable, "-m", "feast",
            "materialize", start_date, end_date,
        ],
        cwd=FEATURE_REPO_DIR,
        check=True,
    )
    print("   ✔ Features materialized to SQLite online store.")

    print()
    print("━" * 60)
    print("Offline layer complete.  Features are ready for training & serving.")
    print("━" * 60)


if __name__ == "__main__":
    main()
