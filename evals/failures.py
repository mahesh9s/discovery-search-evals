"""Error analysis report: read what a system got wrong, query by query.

    python -m evals.failures                         # the round 1 candidate, hybrid
    python -m evals.failures --system hybrid_pinned

A query counts as a failure when the system scores below 0.5 NDCG@10 on it or
loses 0.1 or more to the baseline. Root-cause tags come from
analysis/failure_tags.yaml, which is filled in by a person after reading the
results. This only ever runs on the development set: reading the held-out
failures and then changing a system would stop that set being held out.
"""
import argparse
import csv
import json
from collections import Counter

import yaml

from .data import RESULTS, ROOT, load_catalog, load_qrels, load_queries
from .retrievers import BASELINE

LOW, REGRESSION = 0.5, -0.1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--system", default="hybrid")
    args = parser.parse_args()

    out_dir = RESULTS / "dev"
    by_id = {d["id"]: d for d in load_catalog()}
    qrels = load_qrels()
    runs = json.loads((out_dir / "runs.json").read_text(encoding="utf-8"))
    with (out_dir / "per_query.csv").open(encoding="utf-8", newline="") as f:
        ndcg = {(r["system"], r["query_id"]): float(r["ndcg@10"]) for r in csv.DictReader(f)}
    tagging = yaml.safe_load((ROOT / "analysis" / "failure_tags.yaml").read_text(encoding="utf-8"))

    failures = []
    for q in load_queries("dev"):
        score, base = ndcg[(args.system, q["id"])], ndcg[(BASELINE, q["id"])]
        if score < LOW or score - base <= REGRESSION:
            failures.append((q, score, base, tagging["queries"].get(q["id"], {"tag": "untagged", "note": ""})))

    tally = Counter(t["tag"] for *_, t in failures)
    lines = [f"# Failure analysis: `{args.system}` on the dev set", "",
             f"{len(failures)} of {len(load_queries('dev'))} queries fail "
             f"(NDCG@10 below {LOW}, or {abs(REGRESSION)} or more behind `{BASELINE}`).", "",
             "| Root cause | Queries | What it means |", "|---|---|---|"]
    for tag, count in tally.most_common():
        lines.append(f"| `{tag}` | {count} | {tagging['tags'].get(tag, 'Not tagged yet. Read the results below and add it to analysis/failure_tags.yaml.')} |")

    for q, score, base, t in failures:
        judged = qrels[q["id"]]
        top = runs[args.system][q["id"]]
        lines += ["", f"## {q['id']}: \"{q['query']}\"", "",
                  f"Slice: {q['slice']}. NDCG@10 {score:.2f} (baseline {base:.2f}). Root cause: `{t['tag']}`.",
                  *([f"", t["note"]] if t["note"] else []), "",
                  "Returned: " + ("; ".join(f"{by_id[d]['title']} ({by_id[d]['year']}) [{judged.get(d, '?')}]"
                                            for d in top[:5]) or "nothing") + "."]
        missed = [d for d, g in judged.items() if g == 2 and d not in top]
        if missed:
            lines.append("")
            lines.append(f"Missed {len(missed)} top-grade answers, including: "
                         + "; ".join(f"{by_id[d]['title']} ({by_id[d]['year']})" for d in missed[:3]) + ".")

    path = out_dir / f"failures_{args.system}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(failures)} failing queries written to {path.relative_to(ROOT)}")
    for tag, count in tally.most_common():
        print(f"  {count:2}  {tag}")


if __name__ == "__main__":
    main()
