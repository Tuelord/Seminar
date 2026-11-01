# 🏛️ Michelangelo Mini Demo

> A miniature reproduction of [Uber's Michelangelo ML platform](https://github.com/michelangelo-ai/michelangelo),
> demonstrating the full ML lifecycle: **Feature Store → Training → Serving → Monitoring**.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MICHELANGELO MINI                           │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   OFFLINE     │    │   TRAINING   │    │   ONLINE SERVING     │  │
│  │              │    │              │    │                      │  │
│  │ Synthetic    │    │ XGBoost      │    │ FastAPI              │  │
│  │ Taxi Data    │──▶│ Regression   │    │  ├─ /predict (Feast) │  │
│  │      │       │    │      │       │    │  ├─ /predict_raw     │  │
│  │      ▼       │    │      ▼       │    │  └─ /model_info      │  │
│  │  Parquet     │    │   MLflow     │    │         │             │  │
│  │      │       │    │  Registry    │───▶│  Load by alias       │  │
│  │      ▼       │    │  "champion"  │    │  "champion"          │  │
│  │   Feast      │    │              │    │         │             │  │
│  │  (SQLite)    │───────────────────────▶│  Feature lookup      │  │
│  └──────────────┘    └──────────────┘    └──────────┬───────────┘  │
│                                                      │              │
│  ┌──────────────────────────────────────────────────▼──────────┐   │
│  │                      MONITORING                              │   │
│  │  prediction_log.csv  ──▶  monitor.py  ──▶  MAE / RMSE / R²  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Contents

| File | Layer | Purpose |
|---|---|---|
| `docker-compose.yml` | Infra | MLflow Tracking Server (artifacts in a local volume) |
| `generate_features.py` | Offline | Create synthetic taxi data → Parquet → Feast materialize |
| `feature_repo/` | Offline | Feast feature store definitions + config |
| `train.py` | Training | XGBoost → MLflow → register model → set alias `champion` |
| `serve.py` | Online | FastAPI: load model by alias, Feast feature lookup, prediction log |
| `monitor.py` | Monitoring | Compare predictions vs actuals → MAE report |
| `run_demo.py` | All | End-to-end orchestrator (runs everything in sequence) |
| `requirements.txt` | — | Python dependencies |

## Prerequisites

- **Docker** (with Docker Compose)
- **Python 3.10–3.13** (tested with 3.12; Python 3.14 fails on `import feast`)

## Quick Start

### Option A: Fully automated (recommended)

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full demo (all 7 phases)
python run_demo.py
```

### Option B: Step by step

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate features and materialize to Feast
python generate_features.py

# 4. Train the model (logged to MLflow, alias "champion")
python train.py

# 5. Start the serving API (background)
python serve.py &

# 6. Send predictions
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"trip_id": 42}'

# Or with raw features:
curl -X POST http://localhost:8000/predict_raw \
     -H "Content-Type: application/json" \
     -d '{"trip_distance": 5.2, "pickup_hour": 17, "pickup_weekday": 2, "passenger_count": 2}'

# 7. Run monitoring
python monitor.py
```

## 🎯 Key Feature: Zero-Downtime Model Swap

The main highlight of this demo is the **alias-based model swap**:

```bash
# Train a new, improved model → alias "champion" is updated
python train.py --n_estimators 200 --max_depth 8

# The serving API automatically detects the alias change
# and hot-swaps the model. No restart, no code changes!

# Verify:
curl http://localhost:8000/model_info
# → {"model_name": "taxi-fare-model", "alias": "champion", "version": "2", ...}
```

The background watcher in `serve.py` polls MLflow every 15 seconds.
When the `champion` alias points to a new version, the model is reloaded
transparently.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/model_info` | Current model version & alias |
| `POST` | `/predict` | Predict using Feast features `{"trip_id": 42}` |
| `POST` | `/predict_raw` | Predict with raw features |
| `GET` | `/docs` | Swagger UI (auto-generated) |

## MLflow UI

Open [http://localhost:5001](http://localhost:5001) to view experiments,
runs, metrics, and the model registry.

## Mapping to Michelangelo Architecture

| Michelangelo Concept | This Demo |
|---|---|
| Feature Store (Palette) | Feast + SQLite online store |
| Offline feature pipeline | `generate_features.py` → Parquet → `feast materialize` |
| Training pipeline | `train.py` → XGBoost + MLflow |
| Model Registry | MLflow Model Registry with aliases |
| Online serving (Cassandra) | FastAPI + Feast online store |
| Model deployment | Alias swap (`champion` → new version) |
| Monitoring | `monitor.py` (MAE comparison) |

