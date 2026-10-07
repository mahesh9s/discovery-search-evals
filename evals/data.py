"""Loaders for the catalog, the query set and the relevance judgments."""
import csv
import json
import pathlib
from collections import defaultdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def load_catalog(path: pathlib.Path = DATA / "catalog.jsonl") -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# dev: used to find failures and decide what to change.
# heldout: written later, never used for design; checks the dev results generalise.
QUERY_SETS = {"dev": DATA / "queries.yaml", "heldout": DATA / "queries_heldout.yaml"}


def load_queries(query_set: str = "dev") -> list[dict]:
    with QUERY_SETS[query_set].open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_qrels(path: pathlib.Path = DATA / "qrels.tsv") -> dict[str, dict[str, int]]:
    """Return {query_id: {doc_id: grade}}. Grade 0 rows are kept: they record
    that a result was looked at and judged not relevant, which is different
    from a result nobody has judged yet."""
    qrels: dict[str, dict[str, int]] = defaultdict(dict)
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            qrels[row["query_id"]][row["doc_id"]] = int(row["grade"])
    return dict(qrels)
