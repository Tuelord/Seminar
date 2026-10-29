"""
run_demo.py — End-to-End Demo Orchestrator
=============================================
Michelangelo Mini Demo

Runs all four layers in sequence and demonstrates the alias-swap feature:

  Step 1: Offline   — generate_features.py
  Step 2: Train v1  — train.py (n_estimators=100, alias=champion)
  Step 3: Serve     — serve.py (started in background)
  Step 4: Predict   — send sample requests to the API
  Step 5: Train v2  — train.py (n_estimators=200, alias=champion)
  Step 6: Predict   — model hot-swapped, new predictions
  Step 7: Monitor   — monitor.py (compare predictions vs actuals)

Prerequisites:
    docker compose up -d   # MLflow + MinIO
    pip install -r requirements.txt

Usage:
    python run_demo.py
"""

import json
import os
import subprocess
import sys
import time

import requests

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "http://localhost:8000"


def run_script(name: str, extra_args: list[str] | None = None):
    """Run a Python script and stream its output."""
    cmd = [sys.executable, os.path.join(DEMO_DIR, name)]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, cwd=DEMO_DIR)
    if result.returncode != 0:
        print(f"⚠  {name} exited with code {result.returncode}")
        sys.exit(1)


def wait_for_api(timeout: int = 30):
    """Block until the serving API is ready."""
    print("[demo] Waiting for API to be ready …")
    for _ in range(timeout):
        try:
            r = requests.get(f"{API_BASE}/health", timeout=2)
            if r.status_code == 200:
                print("[demo] ✔ API is ready.")
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    print("[demo] ⚠ API did not become ready in time.")
    sys.exit(1)


def send_predictions(trip_ids: list[int], label: str):
    """Send prediction requests and print results."""
    print(f"\n[demo] Sending {len(trip_ids)} predictions ({label}) …")
    for tid in trip_ids:
        try:
            r = requests.post(
                f"{API_BASE}/predict",
                json={"trip_id": tid},
                timeout=5,
            )
            data = r.json()
            print(
                f"   trip_id={tid:>5}  →  "
                f"predicted_fare=${data.get('predicted_fare', '?'):>7}  "
                f"(model v{data.get('model_version', '?')})"
            )
        except Exception as exc:
            print(f"   trip_id={tid}  →  ERROR: {exc}")


def main():
    print("=" * 60)
    print("   MICHELANGELO MINI DEMO — End-to-End Walkthrough")
    print("=" * 60)

    # ── Clean previous log ───────────────────────────────────────────────
    log_path = os.path.join(DEMO_DIR, "data", "prediction_log.csv")
    if os.path.isfile(log_path):
        os.remove(log_path)

    # ── Step 1: Offline features ─────────────────────────────────────────
    print("\n" + "═" * 60)
    print("PHASE 1 — OFFLINE FEATURE ENGINEERING")
    print("═" * 60)
    run_script("generate_features.py")

    # ── Step 2: Train first model (v1) ───────────────────────────────────
    print("\n" + "═" * 60)
    print("PHASE 2 — TRAIN MODEL v1  (n_estimators=100)")
    print("═" * 60)
    run_script("train.py", ["--n_estimators", "100", "--max_depth", "4"])

    # ── Step 3: Start serving ────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("PHASE 3 — START ONLINE SERVING")
    print("═" * 60)
    serve_proc = subprocess.Popen(
        [sys.executable, os.path.join(DEMO_DIR, "serve.py")],
        cwd=DEMO_DIR,
    )
    wait_for_api()

    try:
        # ── Step 4: Predict with v1 ─────────────────────────────────
        print("\n" + "═" * 60)
        print("PHASE 4 — PREDICTIONS WITH MODEL v1")
        print("═" * 60)
        sample_ids = list(range(1, 21))  # trip_id 1..20
        send_predictions(sample_ids, "model v1")

        # ── Step 5: Train improved model (v2) ───────────────────────
        print("\n" + "═" * 60)
        print("PHASE 5 — TRAIN IMPROVED MODEL v2  (n_estimators=200)")
        print("═" * 60)
        run_script("train.py", ["--n_estimators", "200", "--max_depth", "6"])

        # Wait for the watcher to detect the alias change
        print("\n[demo] Waiting for model watcher to detect alias change …")
        time.sleep(20)

        # Verify the swap
        info = requests.get(f"{API_BASE}/model_info").json()
        print(f"[demo] ✔ Serving API now uses model v{info.get('version', '?')}")

        # ── Step 6: Predict with v2 ─────────────────────────────────
        print("\n" + "═" * 60)
        print("PHASE 6 — PREDICTIONS WITH MODEL v2  (after alias swap)")
        print("═" * 60)
        send_predictions(sample_ids, "model v2")

        # ── Step 7: Monitor ─────────────────────────────────────────
        print("\n" + "═" * 60)
        print("PHASE 7 — MONITORING (predictions vs actuals)")
        print("═" * 60)
        run_script("monitor.py")

    finally:
        # ── Cleanup ─────────────────────────────────────────────────
        print("\n[demo] Stopping serving process …")
        serve_proc.terminate()
        serve_proc.wait(timeout=5)

    print("\n" + "=" * 60)
    print("   DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("Key takeaway:")
    print("  → We retrained the model (v1 → v2) and changed the alias.")
    print("  → The serving API automatically picked up the new model.")
    print("  → No code changes, no restart, no downtime.")
    print()


if __name__ == "__main__":
    main()
