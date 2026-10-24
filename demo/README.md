# demo/

This directory contains the live demonstration materials for the MLOps report.

## Contents

| File / Folder | Purpose |
|---|---|
| `docker-compose.yml` | Spin up a local MLflow + MinIO stack for demo |
| `train_demo.py` | A minimal training script logged to MLflow |
| `serve_demo.py` | A minimal FastAPI serving script |
| `screenshots/` | Screenshots used in the slides |

## Quick start

```bash
# 1. Start the stack
docker compose up -d

# 2. Run the demo training job
python train_demo.py

# 3. Open MLflow UI
open http://localhost:5000

# 4. Start the serving endpoint
python serve_demo.py
```

> **Note**: Docker and Python 3.10+ are required.
