# Security Policy

## Reporting a Vulnerability
Please open a private security advisory or email the maintainers (see repo metadata). Do not open public issues for undisclosed vulnerabilities.

## Data & Privacy
- Inputs restricted to `local://data/**`; outputs restricted to `local://runs/**`.
- **No row-level data** is exported—only aggregates and text artifacts.
- **Small-cell suppression** (default `k=10`) masks subgroup cells with insufficient counts.

## Dependencies
- Pin versions. Monitor and update when CVEs are disclosed.
- Reproduce runs after dependency bumps; compare manifests and golden outputs.

