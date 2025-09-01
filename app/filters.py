from __future__ import annotations

import operator
from typing import Any, Dict, Iterable

import pandas as pd

from .types import FilterOp


def _apply_predicate(df: pd.DataFrame, pred: Dict[str, Any]) -> pd.Series:
    col = pred["col"]
    op = pred["op"]
    val = pred["val"]
    series = df[col]
    ops = {
        FilterOp.eq: operator.eq,
        FilterOp.ne: operator.ne,
        FilterOp.gt: operator.gt,
        FilterOp.ge: operator.ge,
        FilterOp.lt: operator.lt,
        FilterOp.le: operator.le,
    }
    if op in ops:
        return ops[FilterOp(op)](series, val)
    if op == FilterOp.isin:
        return series.isin(val if isinstance(val, Iterable) else [val])
    if op == FilterOp.notin:
        return ~series.isin(val if isinstance(val, Iterable) else [val])
    if op == FilterOp.between:
        low, high = val
        return series.between(low, high)
    raise ValueError(f"unknown op {op}")


def evaluate(df: pd.DataFrame, filt: Dict[str, Any]) -> pd.Series:
    if "and" in filt:
        masks = [evaluate(df, f) for f in filt["and"]]
        return pd.concat(masks, axis=1).all(axis=1)
    if "or" in filt:
        masks = [evaluate(df, f) for f in filt["or"]]
        return pd.concat(masks, axis=1).any(axis=1)
    if "not" in filt:
        return ~evaluate(df, filt["not"])
    return _apply_predicate(df, filt)
