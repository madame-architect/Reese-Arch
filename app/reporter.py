from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from .settings import ROOT_DIR

env = Environment(loader=FileSystemLoader(str(ROOT_DIR / "app" / "templates")))


def render_card(plan_yaml: str, results: Dict[str, Any], run_dir: Path) -> Dict[str, str]:
    tpl = env.get_template("evidence_card.md.j2")
    md = tpl.render(plan_yaml=plan_yaml, results=results)
    md_path = run_dir / "evidence_card.md"
    md_path.write_text(md)
    pdf_path = run_dir / "evidence_card.pdf"
    pdf = ""
    if shutil.which("pandoc"):
        import subprocess

        subprocess.run(["pandoc", md_path, "-o", pdf_path], check=False)
        pdf = str(pdf_path)
    return {"card_md": str(md_path), "card_pdf": pdf}
