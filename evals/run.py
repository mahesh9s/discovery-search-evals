"""Run every system over a query set and write the results.

    python -m evals.run              # both sets
    python -m evals.run --set dev    # just the development set

Outputs, under results/<set>/:
    summary.md      the tables a decision gets made from
    metrics.json    the same numbers, machine-readable, plus gate outcomes
    per_query.csv   one row per system and query
    runs.json       the top 10 each system returned for each query
"""
import argparse
import csv
import json
from collections import defaultdict

import numpy as np

from .data import QUERY_SETS, RESULTS, load_catalog, load_qrels, load_queries
from .gates import check_gates, load_gates
from .metrics import K, METRICS
from .retrievers import BASELINE, build_systems
from .stats import paired_bootstrap

COMPARED = ["ndcg@10", "recall@10", "mrr@10", "hit@1"]

# Comparisons that are not against the baseline, as (candidate, reference).
# This one asks the question that matters once the cheap fixes are in:
# does the embedding model still add anything?
HEAD_TO_HEAD = [("hybrid_pinned", "keyword_pinned")]


def evaluate(systems: dict, queries: list[dict], qrels: dict) -> tuple[dict, list[dict]]:
    runs, rows = {}, []
    for name, system in systems.items():
        runs[name] = {}
        for q in queries:
            ranked = [doc_id for doc_id, _ in system.search(q["query"], K)]
            runs[name][q["id"]] = ranked
            judged = qrels.get(q["id"], {})
            row = {"system": name, "query_id": q["id"], "slice": q["slice"], "query": q["query"],
                   "n_results": len(ranked)}
            row.update({m: round(fn(ranked, judged), 4) for m, fn in METRICS.items()})
            rows.append(row)
    return runs, rows


def aggregate(rows: list[dict], slices: list[str]) -> tuple[dict, dict, dict]:
    """Mean of each metric per system and slice, each system's paired
    comparison against the baseline on the same queries, and the extra
    head-to-head comparisons."""
    values = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in rows:  # rows are in query order for every system, so lists align
        for s in ("all", r["slice"]):
            for m in METRICS:
                values[r["system"]][s][m].append(r[m])
            values[r["system"]][s]["empty"].append(float(r["n_results"] == 0))

    means = {sys: {s: {m: round(float(np.mean(v)), 4) for m, v in values[sys][s].items()}
                   for s in ["all", *slices]} for sys in values}
    comparisons = {sys: {s: {m: paired_bootstrap(values[sys][s][m], values[BASELINE][s][m])
                             for m in COMPARED} for s in ["all", *slices]}
                   for sys in values if sys != BASELINE}
    head_to_head = {f"{a} vs {b}": {s: {m: paired_bootstrap(values[a][s][m], values[b][s][m])
                                        for m in COMPARED} for s in ["all", *slices]}
                    for a, b in HEAD_TO_HEAD if a in values and b in values}
    return means, comparisons, head_to_head


def _fmt_delta(c: dict) -> str:
    return f"{c['delta']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]"


def write_summary(name, means, comparisons, head_to_head, gate_results, queries, n_titles, slices) -> str:
    n = len(queries)
    per_slice = n // len(slices)
    systems = list(means)
    out = [f"# Eval results: {name} set", "",
           f"{n} queries ({per_slice} per slice), {n_titles:,} titles, top {K} results per query. "
           f"Baseline: `{BASELINE}`. Regenerate with `python -m evals.run`.", "",
           "## Overall", "",
           "| System | NDCG@10 | Recall@10 | MRR@10 | Hit@1 | Empty result pages | Judged@10 |",
           "|---|---|---|---|---|---|---|"]
    for s in systems:
        a = means[s]["all"]
        out.append(f"| `{s}` | {a['ndcg@10']:.3f} | {a['recall@10']:.3f} | {a['mrr@10']:.3f} | "
                   f"{a['hit@1']:.3f} | {round(a['empty'] * n)} of {n} | {a['judged@10']:.0%} |")

    out += ["", "## NDCG@10 by intent slice", "",
            "| System | " + " | ".join(slices) + " |", "|---|" + "---|" * len(slices)]
    for s in systems:
        out.append(f"| `{s}` | " + " | ".join(f"{means[s][sl]['ndcg@10']:.3f}" for sl in slices) + " |")

    out += ["", "## Hit@1 by intent slice", "",
            "| System | " + " | ".join(slices) + " |", "|---|" + "---|" * len(slices)]
    for s in systems:
        out.append(f"| `{s}` | " + " | ".join(f"{means[s][sl]['hit@1']:.3f}" for sl in slices) + " |")

    out += ["", f"## Change in NDCG@10 against `{BASELINE}`", "",
            "Mean difference with a 95% paired bootstrap interval (10,000 resamples of the queries). "
            "An interval that includes zero is not a result.", "",
            "| System | all | " + " | ".join(slices) + " | Wins / losses / ties |",
            "|---|---|" + "---|" * len(slices) + "---|"]
    for s, cmp in comparisons.items():
        a = cmp["all"]["ndcg@10"]
        out.append(f"| `{s}` | {_fmt_delta(a)} | "
                   + " | ".join(_fmt_delta(cmp[sl]["ndcg@10"]) for sl in slices)
                   + f" | {a['wins']} / {a['losses']} / {a['ties']} |")

    for label, cmp in head_to_head.items():
        a = cmp["all"]["ndcg@10"]
        out += ["", f"## Head to head: `{label.replace(' vs ', '` vs `')}`", "",
                "Change in NDCG@10, same interval method.", "",
                "| all | " + " | ".join(slices) + " | Wins / losses / ties |",
                "|---|" + "---|" * len(slices) + "---|",
                f"| {_fmt_delta(a)} | " + " | ".join(_fmt_delta(cmp[sl]["ndcg@10"]) for sl in slices)
                + f" | {a['wins']} / {a['losses']} / {a['ties']} |"]

    out += ["", "## Gates (see gates.yaml)", "",
            "| System | " + " | ".join(g["gate"] for g in next(iter(gate_results.values()))) + " | Eligible for A/B |",
            "|---|" + "---|" * len(next(iter(gate_results.values()))) + "---|"]
    for s, outcomes in gate_results.items():
        cells = [f"{'pass' if o['passed'] else 'FAIL'} ({o['observed']:+.3f})" for o in outcomes]
        out.append(f"| `{s}` | " + " | ".join(cells) + f" | {'yes' if all(o['passed'] for o in outcomes) else 'no'} |")
    return "\n".join(out) + "\n"


def run_set(name: str, systems: dict, n_titles: int, qrels: dict, gate_config: dict) -> str:
    queries = load_queries(name)
    slices = list(dict.fromkeys(q["slice"] for q in queries))
    runs, rows = evaluate(systems, queries, qrels)
    means, comparisons, head_to_head = aggregate(rows, slices)
    gate_results = {s: check_gates(s, means, comparisons, gate_config) for s in comparisons}

    out_dir = RESULTS / name
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "per_query.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "runs.json").write_text(json.dumps(runs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "metrics.json").write_text(json.dumps(
        {"query_set": name, "n_queries": len(queries), "n_titles": n_titles, "k": K, "baseline": BASELINE,
         "means": means, "vs_baseline": comparisons, "head_to_head": head_to_head, "gates": gate_results},
        indent=1) + "\n", encoding="utf-8")
    summary = write_summary(name, means, comparisons, head_to_head, gate_results, queries, n_titles, slices)
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", choices=[*QUERY_SETS, "all"], default="all", dest="query_set")
    args = parser.parse_args()

    catalog, qrels, gate_config = load_catalog(), load_qrels(), load_gates()
    systems = build_systems(catalog)
    for name in (QUERY_SETS if args.query_set == "all" else [args.query_set]):
        print(run_set(name, systems, len(catalog), qrels, gate_config))


if __name__ == "__main__":
    main()
