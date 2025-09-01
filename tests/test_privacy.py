import pandas as pd

from app.executor import small_cell


def test_small_cell():
    df = pd.DataFrame({"n": [5, 20], "pct": [1.0, 2.0]})
    out = small_cell(df, 10)
    assert pd.isna(out.loc[0, "n"])
    assert out.loc[1, "n"] == 20
