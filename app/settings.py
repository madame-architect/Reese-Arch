from __future__ import annotations

from pathlib import Path

ALLOWED_INPUT_PREFIX = "local://data/"
ALLOWED_OUTPUT_PREFIX = "local://runs/"
SMALL_CELL_DEFAULT = 10
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RUNS_DIR = ROOT_DIR / "runs"
CACHE_FILE = RUNS_DIR / "cache.json"
