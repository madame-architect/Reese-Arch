# Contributing to Reese-Arch

Thanks for helping build reproducible science tools!

## How to Contribute
1. Open an issue to discuss your idea or bug.
2. Fork & branch: `feat/<short-name>` or `fix/<short-name>`.
3. Add/adjust tests; keep coverage for changed lines.
4. Run lint & tests locally; ensure determinism (fixed seeds).
5. Submit a PR with a clear description, assumptions, and reproducibility notes.

## Coding & Docs Standards
- Type hints, small pure functions, explicit assumptions.
- Markdown docs with examples. Prefer **Mermaid** for simple diagrams.
- Keep APIs stable; if you must break them, propose a migration path.

## Reproducibility Checklist (adapted from _The Turing Way_)
- Pin dependencies; capture `pip freeze` in manifests.
- Record random seeds and plan hashes.
- Provide a **data dictionary** (roles/types) and dataset fingerprints.
- Enforce **small-cell suppression** in examples and tests.
- Use idempotency keys in integration tests.

## Commit Messages
- Use conventional style (e.g., `feat(engine): add chi2 power`).

## PR Review Expectations
- At least one maintainer + one reviewer for statistical correctness on methods changes.
- Include before/after numbers for any math changes.

