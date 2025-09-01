import pytest

from app.validator import load_plan, load_plan_str


def test_invalid_plan_missing():
    with pytest.raises(Exception):
        load_plan({})
