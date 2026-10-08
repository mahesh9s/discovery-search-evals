# evals

The harness itself. Run each module with `python -m evals.<name>` from the repo root.

| Module | What it does |
|---|---|
| `retrievers.py` | The six systems under test, all behind `search(query, k)` |
| `run.py` | Runs every system over a query set and writes `results/` |
| `metrics.py` | NDCG@10, Recall@10, MRR@10, Hit@1, Judged@10 |
| `stats.py` | Paired bootstrap confidence intervals over queries |
| `gates.py` | Checks results against the ship gates in `gates.yaml` |
| `failures.py` | Per-query failure report for the dev set |
| `pool.py` | Builds a blind judging sheet of unjudged results, and merges grades back |
| `chart.py` | Draws `results/dev/ndcg_by_slice.png` |
| `data.py`, `text.py` | Loaders and the shared tokenizer |
