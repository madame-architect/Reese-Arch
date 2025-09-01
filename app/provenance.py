from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .settings import CACHE_FILE, RUNS_DIR


@dataclass
class Provenance:
    plan_hash: str
    dataset_hash: str
    seed: int
    start_time: float
    end_time: float


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache() -> Dict[str, str]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(cache: Dict[str, str]) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))


def cache_get_or_set(key: str, run_id: Optional[str] = None) -> Optional[str]:
    cache = load_cache()
    if key in cache:
        return cache[key]
    if run_id:
        cache[key] = run_id
        save_cache(cache)
    return None


def create_manifest(run_dir: Path, prov: Provenance) -> Path:
    manifest: Dict[str, Any] = {
        "plan_hash": prov.plan_hash,
        "dataset_hash": prov.dataset_hash,
        "seed": prov.seed,
        "start_time": prov.start_time,
        "end_time": prov.end_time,
        "python": sys.version,
        "platform": platform.platform(),
    }
    try:
        pip = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode()
        manifest["pip_freeze"] = pip.splitlines()
    except Exception:  # pragma: no cover
        manifest["pip_freeze"] = []
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2))
    return path
