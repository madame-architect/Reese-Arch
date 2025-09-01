# Reese-Arch: Agent-Driven Experiment Planning & Deterministic Compute

_Reese-Arch_ is a tiny, disease-agnostic framework for **reproducible science** with two microservices:
- **Agent Researcher** — translates a plain-language scientific question into a validated analysis plan.
- **Compute-Engine** — executes core statistical methods deterministically and emits an **Evidence Card** + **Provenance Manifest**.

This repo embraces best practices from **The Turing Way** (reproducibility, provenance, openness) and community norms inspired by **SICSS** (clear project plans and post-mortems).

---

## Why it exists (30 seconds)
- **Transparent**: Plans, assumptions, and caveats are explicit.
- **Deterministic**: Fixed seeds, pinned environments, and manifests.
- **Portable**: Domain-agnostic contracts (plan, data dictionary).
- **Auditable**: Evidence Cards with data fingerprints and policy trails.

---

## Architecture (at a glance)

```mermaid
flowchart LR
  Q[Research Question] --> A[/Agent Researcher: /v1/plan.draft & /v1/run/]
  A --> V{Validate Plan & Data}
  V -->|ok| C[/Compute-Engine: /v1/execute/]
  C --> R{Power ≥ Target?}
  R -- no --> A2[Agent: Autotune n_per_arm (once)]
  A2 --> C
  R -- yes --> E[[Evidence Card + Manifest]]
  C --> E
```

### Sequence

```mermaid
sequenceDiagram
  participant U as Researcher
  participant A as Agent Researcher
  participant C as Compute-Engine
  U->>A: POST /v1/run { plan_json | plan_yaml }
  A->>C: POST /v1/execute { plan_json }
  C-->>A: results_json
  A->>A: goal check (power vs. target; apply policy if needed)
  alt power < target & autotune enabled
    A->>C: POST /v1/execute { adjusted plan }
    C-->>A: results_json (2nd pass)
  end
  A->>C: POST /v1/render { final plan + results_json }
  C-->>A: evidence_card.md/.pdf + manifest.json
  A-->>U: run_id + artifact paths
```

---

## Quickstart

1. **Bring up services**

   ```bash
   docker compose up --build
   ```

2. **Draft a plan (optional)**

   ```bash
   curl -s http://localhost:8080/v1/plan.draft \
     -H 'Content-Type: application/json' \
     -d '{"question":"If I lower score threshold from 26 to 24, what happens to power?"}'
   ```

3. **Run (validate → execute → autotune once → render)**

   ```bash
   curl -s http://localhost:8080/v1/run \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: demo-001' \
     -d @plan.json | jq
   ```

Artifacts appear under `runs/<run_id>/`.

---

## Reproducibility Checklist (informed by *The Turing Way*)

* [ ] **Version lock**: language/runtime and library versions pinned.
* [ ] **Deterministic seeds**: all randomized ops seeded and recorded.
* [ ] **Plan hash**: SHA-256 of normalized plan embedded in the card & manifest.
* [ ] **Data dictionary**: column roles/types declared; dataset fingerprint recorded.
* [ ] **Environment capture**: OS/Python, container digest, `pip freeze` recorded.
* [ ] **Idempotency**: identical inputs + `Idempotency-Key` return the same artifacts.
* [ ] **Privacy**: small-cell suppression (n < k) enforced in all outputs.
* [ ] **Policy trail**: any agentic autotune recorded (what changed and why).
* [ ] **Open artifacts**: Evidence Card & manifest are text-based and reviewable.

> *Acknowledgement*: Checklist items are **adapted from principles in The Turing Way** guide on reproducible research. See the project’s documentation for deeper guidance.

---

## Where to go next

* **API details** → [`docs/API.md`](API.md)
* **Project governance** → [`docs/GOVERNANCE.md`](GOVERNANCE.md)
* **How to contribute** → [`docs/CONTRIBUTING.md`](CONTRIBUTING.md)
* **Security policy** → [`docs/SECURITY.md`](SECURITY.md)
* **Cite this project** → [`docs/CITATION.cff`](CITATION.cff)

---

## Citation

If you use this framework, please cite it as described in [`CITATION.cff`](CITATION.cff).

