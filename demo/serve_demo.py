"""
demo/serve_demo.py
------------------
Minimal FastAPI model-serving script for the MLOps demo.
Loads the latest model registered in MLflow and exposes a /predict endpoint.

Owner: Member G (Ky thuat)

Usage:
    pip install fastapi uvicorn mlflow scikit-learn
    python serve_demo.py
    # Then: curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
    #            -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
"""

import os
import mlflow
import mlflow.sklearn
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# ── MLflow tracking server (same as train_demo.py) ──────────────────────────
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris-classifier")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# ── Load model at startup ────────────────────────────────────────────────────
print(f"[serve] Loading model '{MODEL_NAME}' from {MLFLOW_TRACKING_URI} ...")
try:
    model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/latest")
    print("[serve] Model loaded successfully.")
except Exception as exc:
    print(f"[serve] WARNING: Could not load model — {exc}")
    print("[serve] Run train_demo.py first to register a model.")
    model = None

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="MLOps Demo — Iris Classifier",
    description=(
        "A minimal REST API that serves an MLflow-tracked scikit-learn model. "
        "Part of the Software Architecture report demo."
    ),
    version="1.0.0",
)


class PredictRequest(BaseModel):
    features: List[float]  # Expects 4 Iris feature values


class PredictResponse(BaseModel):
    prediction: int
    label: str
    model_name: str


LABELS = {0: "setosa", 1: "versicolor", 2: "virginica"}


@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Run inference on a single Iris sample.

    Body example:
        {"features": [5.1, 3.5, 1.4, 0.2]}
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run train_demo.py first.",
        )
    if len(req.features) != 4:
        raise HTTPException(
            status_code=422,
            detail="Expected exactly 4 feature values (sepal_length, sepal_width, petal_length, petal_width).",
        )

    X = np.array(req.features).reshape(1, -1)
    pred = int(model.predict(X)[0])
    return PredictResponse(
        prediction=pred,
        label=LABELS.get(pred, "unknown"),
        model_name=MODEL_NAME,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
