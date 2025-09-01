import json
from fastapi.testclient import TestClient

from app.main import app
from scripts.make_synth_data import main as make_data

client = TestClient(app)


def setup_module(module):
    make_data()


def test_run_and_idempotent(tmp_path):
    plan = {
        "question": "demo",
        "dataset": {"uri": "local://data/data.parquet", "dict": "local://data/data_dict.yaml"},
        "cohorts": {
            "baseline": {"and": [{"col": "score", "op": ">=", "val": 26}]},
            "proposed": {"and": [{"col": "score", "op": ">=", "val": 24}]},
        },
        "endpoint": {"type": "continuous", "value": "endpoint_value"},
        "analysis": {
            "stats": ["mean_diff"],
            "power": {"method": "normal_approx", "alpha": 0.05, "n_per_arm": 50, "target": 0.8},
        },
        "fairness": {"subgroups": ["sex"]},
        "policy": {"autotune": {"enable": True, "steps": []}},
        "privacy": {"small_cell_k": 2},
        "seed": 0,
    }
    resp = client.post("/run", json={"plan_json": plan}, headers={"Idempotency-Key": "abc"})
    assert resp.status_code == 200
    run_id = resp.json()["run_id"]
    resp2 = client.post("/run", json={"plan_json": plan}, headers={"Idempotency-Key": "abc"})
    assert resp2.json()["run_id"] == run_id
