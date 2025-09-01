.PHONY: venv data run test

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

data:
	python scripts/make_synth_data.py

run:
	uvicorn app.main:app --reload --port 8080

test:
	pytest
