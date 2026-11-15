# Skills and verification

## What this repository demonstrates

Time-windowed SLO evidence, deployment correlation, and dependency triage. Model-driven probe selection, evidence hashing, and repeatable replay.

## Reproduce the result

Local Qwen2.5 0.5B returned `primary` → `page_candidate` and `missing-minute` → `review`. Run `make live` with Ollama or `make verify` for offline evaluation. Use `--require-decision` to make the complete evidence decision an explicit CI gate.

Run `make verify` locally. Ruff and Bandit medium/high checks passed for the checked Python code.

## Scope

Synthetic inputs drive the local model. Read-only probes provide evidence for deterministic policy decisions.

[agent.py](../agent.py) · [loop.py](../loop.py) · [domain.py](../domain.py) · [examples/eval.json](../examples/eval.json) · [examples/live-report.json](../examples/live-report.json) · [Architecture](../docs/ARCHITECTURE.md) · [Case study](../docs/CASE_STUDY.md) · [Runbook](../docs/RUNBOOK.md) · [CI template](../docs/github-actions/ci.yml)
