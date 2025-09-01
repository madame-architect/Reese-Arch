from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from scipy import stats

from .filters import evaluate
from .provenance import Provenance, create_manifest, sha256_file, sha256_text
from .schemas import DataDict, PlanModel
from .settings import RUNS_DIR, SMALL_CELL_DEFAULT


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def apply_cohort(df: pd.DataFrame, filt: Dict[str, Any]) -> pd.DataFrame:
    mask = evaluate(df, filt)
    return df[mask]


def cont_stats(a: pd.Series, b: pd.Series) -> Dict[str, Any]:
    mean_a, mean_b = a.mean(), b.mean()
    sd_a, sd_b = a.std(ddof=1), b.std(ddof=1)
    delta = mean_b - mean_a
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * sd_a**2 + (n2 - 1) * sd_b**2) / (n1 + n2 - 2))
    se = sp * np.sqrt(1 / n1 + 1 / n2)
    z = stats.norm.ppf(0.975)
    ci_low = delta - z * se
    ci_high = delta + z * se
    return {
        "mean_baseline": mean_a,
        "mean_proposed": mean_b,
        "delta": delta,
        "ci": [ci_low, ci_high],
        "sp": sp,
    }


def bin_stats(a: pd.Series, b: pd.Series) -> Dict[str, Any]:
    p1, p2 = a.mean(), b.mean()
    delta = p2 - p1
    n1, n2 = len(a), len(b)
    z = stats.norm.ppf(0.975)
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    ci_low = delta - z * se
    ci_high = delta + z * se
    return {
        "p1": p1,
        "p2": p2,
        "delta": delta,
        "ci": [ci_low, ci_high],
    }


def km_summary(time_a, event_a, time_b, event_b) -> Dict[str, Any]:
    km = KaplanMeierFitter()
    km.fit(time_a, event_a)
    med_a = km.median_survival_time_
    km.fit(time_b, event_b)
    med_b = km.median_survival_time_
    return {"median_baseline": med_a, "median_proposed": med_b}


def power_normal(effect: float, sp: float, n: int, alpha: float) -> float:
    se = sp * np.sqrt(2 / n)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    return stats.norm.cdf(abs(effect) / se - z_alpha)


def power_chi2(p1: float, p2: float, n: int, alpha: float) -> float:
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    return stats.norm.cdf(abs(p2 - p1) / se - z_alpha)


def small_cell(df: pd.DataFrame, k: int) -> pd.DataFrame:
    mask = df["n"] < k
    df.loc[mask, ["n", "pct"]] = None
    return df


def fairness(df_a: pd.DataFrame, df_b: pd.DataFrame, subs: List[str], k: int):
    out: Dict[str, Any] = {}
    for col in subs:
        tbl_a = df_a[col].value_counts(normalize=False).rename("baseline")
        tbl_b = df_b[col].value_counts(normalize=False).rename("proposed")
        comp = pd.concat([tbl_a, tbl_b], axis=1).fillna(0).astype(int)
        comp["delta"] = comp["proposed"] - comp["baseline"]
        comp = comp.reset_index().rename(columns={"index": col})
        comp["pct"] = comp["proposed"] / len(df_b) * 100
        comp["n"] = comp["proposed"]
        comp = small_cell(comp, k).drop(columns=["n"])
        out[col] = comp.to_dict(orient="records")
    return out

def execute(plan: PlanModel, dct: DataDict, run_dir: Path) -> Tuple[Dict[str, Any], List[str]]:
    df = pd.read_parquet(dct.files[0]["path"])
    notes: List[str] = []
    set_seed(plan.seed)
    cohorts = {name: apply_cohort(df, filt.model_dump(by_alias=True, exclude_none=True)) for name, filt in plan.cohorts.items()}
    baseline, proposed = cohorts["baseline"], cohorts["proposed"]
    endpoint = plan.endpoint
    results: Dict[str, Any] = {"n_baseline": len(baseline), "n_proposed": len(proposed)}

    if endpoint.type == "continuous":
        res = cont_stats(baseline[endpoint.value], proposed[endpoint.value])
        results["stats"] = res
        effect = plan.analysis.power.effect_assumed or res["delta"]
        pwr = power_normal(effect, res["sp"], plan.analysis.power.n_per_arm, plan.analysis.power.alpha)
    elif endpoint.type == "binary":
        res = bin_stats(baseline[endpoint.value], proposed[endpoint.value])
        results["stats"] = res
        p1 = plan.analysis.power.p1_assumed or res["p1"]
        p2 = plan.analysis.power.p2_assumed or res["p2"]
        pwr = power_chi2(p1, p2, plan.analysis.power.n_per_arm, plan.analysis.power.alpha)
    else:
        val = endpoint.value
        res = km_summary(
            baseline[val["time"]], baseline[val["event"]], proposed[val["time"]], proposed[val["event"]]
        )
        results["stats"] = res
        pwr = 0.0  # placeholder
    results["power"] = pwr

    if pwr < plan.analysis.power.target and plan.policy.autotune.enable:
        new_n = int(plan.analysis.power.n_per_arm * 1.15)
        plan.analysis.power.n_per_arm = new_n
        notes.append("autotune applied: n_per_arm -> {}".format(new_n))
        if endpoint.type == "continuous":
            pwr = power_normal(effect, res["sp"], new_n, plan.analysis.power.alpha)
        elif endpoint.type == "binary":
            pwr = power_chi2(p1, p2, new_n, plan.analysis.power.alpha)
        results["power"] = pwr

    subs = plan.fairness.get("subgroups", [])
    results["fairness"] = fairness(
        baseline, proposed, subs, plan.privacy.get("small_cell_k", SMALL_CELL_DEFAULT)
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    res_path = run_dir / "results.json"
    res_path.write_text(json.dumps(results, indent=2))
    return results, notes


def finalize(plan: PlanModel, dct_path: Path, run_dir: Path, results: Dict[str, Any], seed: int) -> Provenance:
    plan_hash = sha256_text(plan.model_dump_json())
    dataset_hash = sha256_file(dct_path.parent / dct_path.name.replace("data_dict.yaml", "data.parquet"))
    end = time.time()
    prov = Provenance(plan_hash, dataset_hash, seed, 0.0, end)
    create_manifest(run_dir, prov)
    return prov
