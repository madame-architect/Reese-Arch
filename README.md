# Agentic MVP

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_synth_data.py
uvicorn app.main:app --reload --port 8080
```

## Example
```bash
curl -X POST http://localhost:8080/plan -H "Content-Type: application/json" -d '{}'
```

Artifacts are written under `runs/<run_id>/`.
