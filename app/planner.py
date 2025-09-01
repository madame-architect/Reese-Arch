from __future__ import annotations

from typing import Any, Dict

import yaml

from .schemas import PlanModel

DEFAULT_PLAN = {
    "question": "Impact of relaxing a threshold",
    "dataset": {"uri": "local://data/data.parquet", "dict": "local://data/data_dict.yaml"},
    "cohorts": {
        "baseline": {"and": []},
        "proposed": {"and": []},
    },
    "endpoint": {"type": "continuous", "value": "endpoint_value"},
    "analysis": {
        "stats": ["mean_diff"],
        "power": {"method": "normal_approx", "alpha": 0.05, "n_per_arm": 150, "target": 0.8},
    },
    "fairness": {"subgroups": ["sex", "age_band"]},
    "policy": {"autotune": {"enable": True, "steps": []}},
    "privacy": {"small_cell_k": 10},
    "seed": 0,
}


def from_question(question: str | None, defaults: Dict[str, Any] | None = None) -> Dict[str, Any]:
    plan = DEFAULT_PLAN.copy()
    if question:
        plan["question"] = question
    if defaults:
        plan.update(defaults)
    PlanModel.model_validate(plan)
    return {"plan_yaml": yaml.safe_dump(plan), "plan_json": plan}
