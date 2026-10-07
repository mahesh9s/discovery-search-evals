"""The ship decision, as a test.

gates.yaml names the candidate that has been cleared for an online A/B test.
If a change to the catalog, the tokenizer or a ranker makes it stop clearing
any gate, on either query set, this fails before the change merges.
"""
import pytest

from evals.data import QUERY_SETS, load_queries
from evals.gates import check_gates, load_gates
from evals.retrievers import build_systems
from evals.run import aggregate, evaluate


@pytest.fixture(scope="module")
def results(catalog, qrels):
    systems = build_systems(catalog)
    out = {}
    for name in QUERY_SETS:
        queries = load_queries(name)
        slices = list(dict.fromkeys(q["slice"] for q in queries))
        _, rows = evaluate(systems, queries, qrels)
        out[name] = aggregate(rows, slices)
    return out


@pytest.mark.parametrize("name", list(QUERY_SETS))
def test_promoted_candidate_clears_every_gate(results, name):
    config = load_gates()
    means, comparisons, _ = results[name]
    failed = [o for o in check_gates(config["promoted"], means, comparisons, config) if not o["passed"]]
    assert not failed, f"{config['promoted']} no longer clears {[o['gate'] for o in failed]} on {name}"


@pytest.mark.parametrize("name", list(QUERY_SETS))
def test_comparisons_rest_on_judged_results(results, name):
    """An unjudged result scores as a miss. If a system starts returning titles
    nobody has graded, its numbers are not comparable until they are."""
    means, _, _ = results[name]
    for system, by_slice in means.items():
        assert by_slice["all"]["judged@10"] >= 0.98, (
            f"{system} returns ungraded titles on {name}: run python -m evals.pool and grade them")
