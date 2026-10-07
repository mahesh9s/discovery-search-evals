"""Build a judging pool: every (query, result) pair that some system returns
in its top 10 and nobody has graded yet.

    python -m evals.pool                      # write judging/pool.tsv
    python -m evals.pool --merge judging/pool.tsv   # fold graded rows into qrels

The pool is shuffled and carries no system names, so whoever grades it cannot
tell which system surfaced which title. Fill in the grade column (0, 1 or 2)
against the rubric notes in the query files, then merge.
"""
import argparse
import csv
import pathlib
import random

from .data import DATA, QUERY_SETS, ROOT, load_catalog, load_qrels, load_queries
from .metrics import K
from .retrievers import build_systems

POOL = ROOT / "judging" / "pool.tsv"
FIELDS = ["query_id", "query", "doc_id", "title", "year", "genres", "extract", "grade"]


def build_pool(out: pathlib.Path = POOL) -> int:
    catalog = load_catalog()
    by_id = {d["id"]: d for d in catalog}
    qrels_path = DATA / "qrels.tsv"
    qrels = load_qrels(qrels_path) if qrels_path.exists() else {}
    systems = build_systems(catalog)

    rows = []
    for q in [q for name in QUERY_SETS for q in load_queries(name)]:
        judged = qrels.get(q["id"], {})
        unjudged = {doc_id for s in systems.values() for doc_id, _ in s.search(q["query"], K)}
        for doc_id in sorted(unjudged - judged.keys()):
            d = by_id[doc_id]
            rows.append({"query_id": q["id"], "query": q["query"], "doc_id": doc_id,
                         "title": d["title"], "year": d["year"],
                         "genres": ", ".join(d["genres"]), "extract": d["extract"], "grade": ""})

    random.Random(13).shuffle(rows)
    rows.sort(key=lambda r: r["query_id"])  # stable: grouped by query, shuffled within
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def merge(pool_path: pathlib.Path) -> int:
    with pool_path.open(encoding="utf-8", newline="") as f:
        graded = [r for r in csv.DictReader(f, delimiter="\t") if r["grade"].strip() != ""]
    for r in graded:
        if r["grade"].strip() not in {"0", "1", "2"}:
            raise ValueError(f"grade must be 0, 1 or 2: {r['query_id']} {r['doc_id']}")
    with (DATA / "qrels.tsv").open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        for r in graded:
            writer.writerow([r["query_id"], r["doc_id"], r["grade"].strip(), "pooled"])
    return len(graded)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--merge", type=pathlib.Path, help="graded pool file to fold into qrels.tsv")
    args = parser.parse_args()
    if args.merge:
        print(f"merged {merge(args.merge)} judgments into data/qrels.tsv")
    else:
        print(f"{build_pool()} unjudged results written to {POOL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
