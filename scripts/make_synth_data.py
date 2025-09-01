from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    rng = np.random.default_rng(0)
    n = 600
    ids = np.arange(n)
    age = rng.integers(50, 85, n)
    score = rng.normal(25, 5, n)
    sex = rng.choice(["F", "M"], size=n)
    age_band = pd.cut(age, bins=[0, 65, 75, 120], labels=["<65", "65-74", "75+"])
    endpoint_value = rng.normal(0, 1, n) + (score - 25) * 0.1
    event_flag = rng.binomial(1, 0.25, n)
    event_time = rng.exponential(12, n)
    df = pd.DataFrame(
        {
            "id": ids,
            "age": age,
            "score": score,
            "sex": sex,
            "age_band": age_band.astype(str),
            "endpoint_value": endpoint_value,
            "event_time": event_time,
            "event_flag": event_flag,
        }
    )
    DATA.mkdir(exist_ok=True)
    df.to_parquet(DATA / "data.parquet")
    data_dict = {
        "dataset_id": "ds_demo",
        "files": [{"path": str(DATA / "data.parquet")}],
        "columns": {
            "id": {"role": "id"},
            "age": {"role": "cohort_field", "type": "int"},
            "score": {"role": "cohort_field", "type": "float"},
            "sex": {"role": "subgroup_field", "categories": ["F", "M"]},
            "age_band": {"role": "subgroup_field", "categories": ["<65", "65-74", "75+"]},
            "endpoint_value": {"role": "endpoint", "endpoint_type": "continuous"},
            "event_time": {"role": "endpoint", "endpoint_type": "time_to_event"},
            "event_flag": {"role": "endpoint_flag"},
        },
    }
    (DATA / "data_dict.yaml").write_text(yaml.safe_dump(data_dict))


if __name__ == "__main__":
    main()
