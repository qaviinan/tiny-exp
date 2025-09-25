# Experimentation OS — Lite

A lightweight, reproducible A/B experimentation toolkit built for portfolio demos.

## Quickstart
```bash
# 1) (Optional) create a venv and install deps
pip install -r requirements.txt

# 2) Run Streamlit app
streamlit run app.py
```

## What it does (today)
- Simulates user-level data with a known treatment effect (ground truth).
- Runs SRM check and a simple power/MDE calculator.
- Analyzes diff-in-means with optional CUPED variance reduction.
- Auto-drafts a decision memo (Markdown) with core diagnostics.
- Everything configured via `config.yaml` and metric registry in `metrics.yaml`.

## Structure
```
exp-os-lite/
├── app.py                 # Streamlit one-click run
├── config.yaml            # Run config (sample size, effect, alpha, power, etc.)
├── metrics.yaml           # Metric registry + guardrails
├── requirements.txt
├── src/
│   ├── simulator.py
│   ├── registry.py
│   ├── srm_power.py
│   ├── analyzer.py
│   ├── decision.py
│   └── memo.py
└── tests/
    └── test_smoke.py
```

## Notes
- This is intentionally minimal. Extend with stratification, sequential monitoring corrections, and adapters (DuckDB/BigQuery) when ready.
- Use `config.yaml` to switch between pure simulation and external data later without changing the interface.
