# Reese-Arch API Overview

This project exposes two microservices:

- **Agent Researcher** (port 8080)
  - `POST /v1/plan.draft` — optional: natural-language question → plan draft (JSON & YAML).
  - `POST /v1/run` — agentic loop: validate → execute → (autotune once) → render.

- **Compute-Engine** (port 8081)
  - `POST /v1/execute` — deterministic stats & power on a validated plan.
  - `POST /v1/render` — produce Evidence Card (Markdown, optional PDF) + Provenance Manifest.

### OpenAPI (machine-readable)
- Agent Researcher: [`agent-researcher/openapi.yaml`](../agent-researcher/openapi.yaml)
- Compute-Engine: [`compute-engine/openapi.yaml`](../compute-engine/openapi.yaml)

---

## Minimal plan (JSON)
```json
{
  "question": "Impact of relaxing a threshold on power and representation?",
  "dataset": { "uri": "local://data/data.parquet", "dict": "local://data/data_dict.yaml" },
  "cohorts": {
    "baseline": { "and": [ { "col": "age", "op": ">=", "val": 50 }, { "col": "score", "op": ">=", "val": 26 } ] },
    "proposed": { "and": [ { "col": "age", "op": ">=", "val": 50 }, { "col": "score", "op": ">=", "val": 24 } ] }
  },
  "endpoint": { "type": "continuous", "value": "endpoint_value" },
  "analysis": {
    "stat": "mean_diff",
    "power": { "method": "normal_approx", "alpha": 0.05, "n_per_arm": 150, "target": 0.8, "effect_assumed": 0.2 }
  },
  "fairness": { "subgroups": ["sex", "age_band"] },
  "policy": { "autotune": { "enable": true, "param": "analysis.power.n_per_arm", "factor": 1.15, "max_times": 1 } },
  "privacy": { "small_cell_k": 10 },
  "seed": 20250901
}
```

### Example: run end-to-end

```bash
curl -s http://localhost:8080/v1/run \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: example-001' \
  -d @plan.json | jq
```

**Outputs** (under `runs/<run_id>/`): `evidence_card.md`, `manifest.json`, `results.json`, optional `evidence_card.pdf`.

