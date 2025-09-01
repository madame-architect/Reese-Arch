from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

import uvicorn
import yaml
from fastapi import FastAPI, Header, HTTPException

from .executor import execute, finalize
from .logging_utils import configure as log_config
from .planner import from_question
from .provenance import cache_get_or_set
from .reporter import render_card
from .schemas import PlanModel
from .settings import RUNS_DIR
from .validator import load_datadict, load_plan, load_plan_str, resolve_input

log_config()
app = FastAPI(title="Agentic MVP")


@app.post("/plan")
def plan(body: Dict[str, Any]):
    question = body.get("question")
    defaults = body.get("defaults")
    return from_question(question, defaults)


@app.post("/run")
def run(body: Dict[str, Any], idempotency_key: str | None = Header(default=None)):
    plan_yaml = body.get("plan_yaml")
    plan_json = body.get("plan_json")
    if plan_yaml:
        plan = load_plan_str(plan_yaml)
        plan_text = plan_yaml
    elif plan_json:
        plan = load_plan(plan_json)
        plan_text = yaml.safe_dump(plan_json)
    else:
        raise HTTPException(400, "plan required")

    dct_path = resolve_input(plan.dataset.dict)
    dct = load_datadict(dct_path)
    key = json.dumps([plan.model_dump_json(), dct_path.stat().st_mtime, idempotency_key])
    run_id = cache_get_or_set(key)
    run_dir = RUNS_DIR / (run_id or uuid.uuid4().hex)
    if run_id:
        res_path = run_dir / "results.json"
        if not res_path.exists():
            raise HTTPException(500, "cached run missing")
        results = json.loads(res_path.read_text())
        notes = ["cached"]
    else:
        results, notes = execute(plan, dct, run_dir)
        cache_get_or_set(key, run_dir.name)
    finalize(plan, dct_path, run_dir, results, plan.seed)
    card = render_card(plan_text, results, run_dir)
    return {
        "run_id": run_dir.name,
        "final_plan_yaml": plan_text,
        "results_json_path": str(run_dir / "results.json"),
        "card_md": card["card_md"],
        "card_pdf": card["card_pdf"],
        "manifest": str(run_dir / "manifest.json"),
        "notes": notes,
    }


@app.post("/render")
def render(body: Dict[str, Any]):
    plan_yaml = body["plan_yaml"]
    results = body["results_json"]
    run_id = body["run_id"]
    run_dir = RUNS_DIR / run_id
    return render_card(plan_yaml, results, run_dir)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8080)
