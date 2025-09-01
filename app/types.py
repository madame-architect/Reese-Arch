from __future__ import annotations

from enum import Enum
from typing import Literal


class EndpointType(str, Enum):
    """Supported endpoint types."""

    continuous = "continuous"
    binary = "binary"
    time_to_event = "time_to_event"


class FilterOp(str, Enum):
    """Allowed filter operators."""

    eq = "=="
    ne = "!="
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="
    isin = "in"
    notin = "not_in"
    between = "between"


LogicalOp = Literal["and", "or", "not"]
