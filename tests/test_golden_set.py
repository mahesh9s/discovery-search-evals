"""The golden set is a product artefact. These checks keep it honest."""
from collections import Counter

import pytest

from evals.data import QUERY_SETS, load_queries

SLICES = {"navigational", "person", "category", "descriptive", "vibe"}


@pytest.mark.parametrize("name,per_slice", [("dev", 8), ("heldout", 4)])
def test_every_slice_is_equally_represented(name, per_slice):
    counts = Counter(q["slice"] for q in load_queries(name))
    assert counts == {s: per_slice for s in SLICES}


def test_query_ids_and_text_are_unique_across_sets():
    queries = [q for name in QUERY_SETS for q in load_queries(name)]
    assert len({q["id"] for q in queries}) == len(queries)
    assert len({q["query"] for q in queries}) == len(queries)   # no leakage between dev and heldout


def test_every_query_has_a_rubric_and_a_best_answer(qrels):
    for name in QUERY_SETS:
        for q in load_queries(name):
            assert q["note"].strip(), f"{q['id']} has no rubric note"
            assert 2 in qrels[q["id"]].values(), f"{q['id']} has no grade 2 answer in the catalog"


def test_judgments_point_at_real_titles_and_valid_grades(catalog, qrels):
    known = {d["id"] for d in catalog}
    query_ids = {q["id"] for name in QUERY_SETS for q in load_queries(name)}
    assert set(qrels) == query_ids
    for query_id, judged in qrels.items():
        assert set(judged) <= known, f"{query_id} judges a title that is not in the catalog"
        assert set(judged.values()) <= {0, 1, 2}
