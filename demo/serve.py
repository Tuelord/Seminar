"""
serve.py — Online Serving Layer
==================================
Michelangelo Mini Demo · Step 3

This script simulates the **online serving layer** of the Michelangelo
architecture:

  1. Loads the XGBoost model from MLflow by its ``champion`` alias.
  2. Connects to the Feast online store for real-time feature retrieval.
  3. Exposes a FastAPI REST endpoint for predictions.
  4. Logs every prediction to ``data/prediction_log.csv`` (for monitoring).
  5. Runs a background watcher that detects alias changes in MLflow and
     hot-swaps the model — **zero downtime, zero code changes**.

Endpoints:
    GET  /health          → liveness probe
    POST /predict         → predict using Feast features  { "trip_id": 42 }
    POST /predict_raw     → predict with raw features     { "trip_distance": …, … }
    GET  /model_info      → currently loaded model version

Usage:
    python serve.py
    # curl http://localhost:8000/predict -d '{"trip_id": 42}'
"""

import csv
import os
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from feast import FeatureStore
from mlflow import MlflowClient
from pydantic import BaseModel

# ── Configuration ────────────────────────────────────────────────────────────
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DEMO_DIR, "data")
FEATURE_REPO_DIR = os.path.join(DEMO_DIR, "feature_repo")
LOG_PATH = os.path.join(DATA_DIR, "prediction_log.csv")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
MODEL_NAME = os.getenv("MODEL_NAME", "taxi-fare-model")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "champion")
WATCH_INTERVAL = int(os.getenv("MODEL_WATCH_INTERVAL", "15"))  # seconds

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# ── Global state ─────────────────────────────────────────────────────────────
_model = None
_model_version: Optional[str] = None
_feast_store: Optional[FeatureStore] = None
_lock = threading.Lock()


# ── Model loader ─────────────────────────────────────────────────────────────
def _load_model():
    """Load (or reload) the model referenced by the current alias."""
    global _model, _model_version
    client = MlflowClient()
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        new_version = mv.version
    except Exception:
        # Alias not found — try loading latest
        new_version = None

    uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    print(f"[serve] Loading model from {uri} …")
    model = mlflow.pyfunc.load_model(uri)
    with _lock:
        _model = model
        _model_version = new_version or "unknown"
    print(f"[serve] ✔ Model v{_model_version} loaded.")


# ── Background watcher ──────────────────────────────────────────────────────
def _model_watcher():
    """
    Periodically check whether the 'champion' alias points to a different
    model version.  If it does → hot-swap the model with zero downtime.
    """
    client = MlflowClient()
    while True:
        time.sleep(WATCH_INTERVAL)
        try:
            mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
            if mv.version != _model_version:
                print(
                    f"[serve] ⚡ Alias '{MODEL_ALIAS}' changed: "
                    f"v{_model_version} → v{mv.version}.  Reloading …"
                )
                _load_model()
        except Exception as exc:
            # Swallow errors — watcher should be resilient
            print(f"[serve] ⚠ Watcher error: {exc}")


# ── Feast store ──────────────────────────────────────────────────────────────
def _init_feast():
    global _feast_store
    _feast_store = FeatureStore(repo_path=FEATURE_REPO_DIR)
    print("[serve] ✔ Feast online store connected.")


# ── Prediction logger ───────────────────────────────────────────────────────
def _log_prediction(trip_id: int, predicted_fare: float):
    """Append each prediction to a CSV file for offline monitoring."""
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "trip_id", "predicted_fare", "model_version"])
        writer.writerow([
            datetime.utcnow().isoformat(),
            trip_id,
            round(predicted_fare, 2),
            _model_version,
        ])


# ── FastAPI app ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    # Startup
    _init_feast()
    _load_model()
    watcher = threading.Thread(target=_model_watcher, daemon=True)
    watcher.start()
    print(f"[serve] Model watcher started (interval={WATCH_INTERVAL}s)")
    yield
    # Shutdown — nothing to clean up


app = FastAPI(
    title="Michelangelo Mini — Taxi Fare Prediction",
    description=(
        "Online serving layer that loads the XGBoost model from MLflow "
        "(by alias) and retrieves features from Feast in real time."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response schemas ───────────────────────────────────────────────
class PredictByIdRequest(BaseModel):
    trip_id: int


class PredictRawRequest(BaseModel):
    trip_distance: float
    pickup_hour: int
    pickup_weekday: int
    passenger_count: int


class PredictResponse(BaseModel):
    trip_id: Optional[int] = None
    predicted_fare: float
    model_name: str
    model_version: str


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Liveness & readiness probe."""
    return {
        "status": "ok",
        "model_loaded": _model is not None,
        "model_version": _model_version,
    }


@app.get("/model_info")
def model_info():
    """Return metadata about the currently loaded model."""
    return {
        "model_name": MODEL_NAME,
        "alias": MODEL_ALIAS,
        "version": _model_version,
        "tracking_uri": MLFLOW_TRACKING_URI,
    }


@app.post("/predict", response_model=PredictResponse)
def predict_by_id(req: PredictByIdRequest):
    """
    Predict fare using features fetched from the Feast **online store**.

    This mirrors the Michelangelo online serving flow:
      request → Feast feature lookup → model inference → response + log.
    """
    if _model is None:
        raise HTTPException(503, "Model not loaded. Run train.py first.")

    # Fetch features from Feast
    try:
        features = _feast_store.get_online_features(
            features=[
                "trip_features:trip_distance",
                "trip_features:pickup_hour",
                "trip_features:pickup_weekday",
                "trip_features:passenger_count",
            ],
            entity_rows=[{"trip_id": req.trip_id}],
        ).to_dict()
    except Exception as exc:
        raise HTTPException(
            500, f"Feature lookup failed for trip_id={req.trip_id}: {exc}"
        )

    # Validate
    if features["trip_distance"][0] is None:
        raise HTTPException(
            404,
            f"trip_id={req.trip_id} not found in Feast online store. "
            "Run generate_features.py first.",
        )

    # Build input DataFrame (column order must match training)
    X = pd.DataFrame(
        {
            "trip_distance":  [features["trip_distance"][0]],
            "pickup_hour":    [features["pickup_hour"][0]],
            "pickup_weekday": [features["pickup_weekday"][0]],
            "passenger_count": [features["passenger_count"][0]],
        }
    )

    with _lock:
        pred = float(_model.predict(X)[0])

    _log_prediction(req.trip_id, pred)

    return PredictResponse(
        trip_id=req.trip_id,
        predicted_fare=round(pred, 2),
        model_name=MODEL_NAME,
        model_version=_model_version or "unknown",
    )


@app.post("/predict_raw", response_model=PredictResponse)
def predict_raw(req: PredictRawRequest):
    """
    Predict fare from raw features supplied in the request body.
    Useful for testing without Feast.
    """
    if _model is None:
        raise HTTPException(503, "Model not loaded. Run train.py first.")

    X = pd.DataFrame([req.model_dump()])

    with _lock:
        pred = float(_model.predict(X)[0])

    return PredictResponse(
        predicted_fare=round(pred, 2),
        model_name=MODEL_NAME,
        model_version=_model_version or "unknown",
    )


# ── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
