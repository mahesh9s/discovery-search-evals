# tests

Run with `python -m pytest -q`.

| File | What it checks |
|---|---|
| `test_metrics.py` | Metric and bootstrap maths against hand calculations |
| `test_retrievers.py` | Tokenizer, keyword, semantic, hybrid and pinning behaviour on a tiny catalog |
| `test_golden_set.py` | The golden set stays balanced, unique and fully judged |
| `test_decision.py` | The promoted candidate still clears every ship gate on both query sets |
