from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from .types import EndpointType, FilterOp


class DataSpec(BaseModel):
    uri: str
    dict: str


class Filter(BaseModel):
    """Recursive filter object."""

    and_: Optional[List["Filter"]] = Field(default=None, alias="and")
    or_: Optional[List["Filter"]] = Field(default=None, alias="or")
    not_: Optional["Filter"] = Field(default=None, alias="not")
    col: Optional[str] = None
    op: Optional[FilterOp] = None
    val: Optional[Union[str, int, float, List[Union[str, int, float]]]] = None

    @validator("val", pre=True)
    def _val(cls, v):
        return v

    @validator("op", always=True)
    def _check(cls, v, values):
        if values.get("col") is not None and v is None:
            raise ValueError("op required when col provided")
        return v


Filter.model_rebuild()


class PowerSpec(BaseModel):
    method: str
    alpha: float
    n_per_arm: int
    target: float
    effect_assumed: Optional[float] = None
    p1_assumed: Optional[float] = None
    p2_assumed: Optional[float] = None
    assumed_hr: Optional[float] = None


class AnalysisSpec(BaseModel):
    stats: List[str]
    power: PowerSpec


class EndpointSpec(BaseModel):
    type: EndpointType
    value: Union[str, Dict[str, str]]


class PolicySpec(BaseModel):
    class AutotuneStep(BaseModel):
        param: str
        op: str
        factor: float
        max_times: int = 1

    class Autotune(BaseModel):
        enable: bool = False
        steps: List[AutotuneStep] = []

    autotune: Autotune = Autotune()


class PlanModel(BaseModel):
    question: str
    dataset: DataSpec
    cohorts: Dict[str, Filter]
    endpoint: EndpointSpec
    analysis: AnalysisSpec
    fairness: Dict[str, List[str]] = Field(default_factory=dict)
    policy: PolicySpec = PolicySpec()
    privacy: Dict[str, int] = Field(default_factory=lambda: {"small_cell_k": 10})
    seed: int = 0


class DataDictColumn(BaseModel):
    role: str
    endpoint_type: Optional[str] = None
    type: Optional[str] = None
    categories: Optional[List[str]] = None


class DataDict(BaseModel):
    dataset_id: str
    files: List[Dict[str, str]]
    columns: Dict[str, DataDictColumn]
