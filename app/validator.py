from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml

from .schemas import DataDict, PlanModel
from .settings import ALLOWED_INPUT_PREFIX, DATA_DIR, RUNS_DIR


def _ensure_local(uri: str, prefix: str) -> Path:
    if not uri.startswith(prefix):
        raise ValueError("invalid uri")
    rel = uri[len(prefix) :]
    path = (DATA_DIR if prefix.endswith("/data/") else RUNS_DIR) / rel
    if ".." in Path(rel).parts:
        raise ValueError("path traversal")
    return path


def resolve_input(uri: str) -> Path:
    return _ensure_local(uri, ALLOWED_INPUT_PREFIX)


def resolve_output(uri: str) -> Path:
    return _ensure_local(uri, ALLOWED_INPUT_PREFIX.replace("data", "runs"))


def load_plan(data: Dict[str, Any]) -> PlanModel:
    return PlanModel.model_validate(data)


def load_plan_str(text: str) -> PlanModel:
    data = yaml.safe_load(text)
    return load_plan(data)


def load_datadict(path: Path) -> DataDict:
    return DataDict.model_validate(yaml.safe_load(path.read_text()))


def validate_filters(plan: PlanModel, dct: DataDict) -> None:
    cols = dct.columns.keys()
    for filt in plan.cohorts.values():
        _validate_filter_recursive(filt.model_dump(), cols)


def _validate_filter_recursive(filt: Dict[str, Any], cols) -> None:
    if "and" in filt:
        for f in filt["and"]:
            _validate_filter_recursive(f, cols)
    elif "or" in filt:
        for f in filt["or"]:
            _validate_filter_recursive(f, cols)
    elif "not" in filt:
        _validate_filter_recursive(filt["not"], cols)
    else:
        col = filt["col"]
        if col not in cols:
            raise ValueError(f"unknown column {col}")
