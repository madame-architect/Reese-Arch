import pandas as pd

from app.filters import evaluate


def test_and_or_not():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    filt = {"and": [{"col": "a", "op": ">", "val": 1}, {"not": {"col": "b", "op": "==", "val": 5}}]}
    mask = evaluate(df, filt)
    assert mask.tolist() == [False, False, True]
