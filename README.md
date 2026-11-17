# Supply Chain Anomaly Alerting & SOP-Grounded Resolution Agent

A prototype that flags supply chain anomalies with deterministic rules, retrieves matching SOPs, and verifies that every SOP citation in the drafted response was actually retrieved.

## What it does
- **Rule-based alert gating**: flags shipments with `delay_days > 3` or `defect_rate > 2%`.
- **SOP retrieval**: maps each anomaly to entries in a small, self-written SOP knowledge base (3 documents).
- **Citation verifier**: rejects any cited SOP ID (`[SOP-SC-XXX]`) that was not retrieved.

## Limitations
- Runs on simulated data and self-written SOPs.
- Response text is template-based; an LLM generation step is not included yet.

## Run
```bash
pip install pandas pytest
PYTHONPATH=. pytest tests/ -v
PYTHONPATH=. python src/agent.py
```
