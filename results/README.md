# results

Outputs of `python -m evals.run`, one folder per query set (`dev`, `heldout`). Everything here is regenerated, so do not edit it by hand.

| File | Contents |
|---|---|
| `summary.md` | The tables a decision gets made from |
| `metrics.json` | The same numbers, machine-readable, plus gate outcomes |
| `per_query.csv` | One row per system and query |
| `runs.json` | The top 10 each system returned for each query |
| `failures_*.md` | Failure reports from `python -m evals.failures` (dev only) |
| `ndcg_by_slice.png` | The chart in the README (dev only) |
