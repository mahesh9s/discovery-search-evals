import math

import pytest

from evals.metrics import hit_at_1, judged_at_k, mrr, ndcg, recall
from evals.stats import paired_bootstrap

JUDGED = {"a": 2, "b": 1, "c": 0, "d": 2}


def test_ndcg_perfect_ranking_is_one():
    assert ndcg(["a", "d", "b"], JUDGED) == pytest.approx(1.0)


def test_ndcg_matches_hand_calculation():
    # gains 2^g - 1: b=1 at rank 1, a=3 at rank 2; ideal is 3, 3, 1
    dcg = 1 / math.log2(2) + 3 / math.log2(3)
    idcg = 3 / math.log2(2) + 3 / math.log2(3) + 1 / math.log2(4)
    assert ndcg(["b", "a"], JUDGED) == pytest.approx(dcg / idcg)


def test_unjudged_and_empty_results_score_zero():
    assert ndcg(["x", "y"], JUDGED) == 0.0
    assert ndcg([], JUDGED) == 0.0
    assert mrr([], JUDGED) == 0.0
    assert hit_at_1([], JUDGED) == 0.0


def test_recall_is_capped_at_k():
    many = {f"d{i}": 2 for i in range(40)}
    assert recall([f"d{i}" for i in range(10)], many) == 1.0
    assert recall(["a", "x"], JUDGED) == pytest.approx(1 / 3)


def test_mrr_uses_first_relevant_result():
    assert mrr(["c", "x", "b"], JUDGED) == pytest.approx(1 / 3)


def test_hit_at_1_needs_a_best_grade_answer_first():
    assert hit_at_1(["a", "b"], JUDGED) == 1.0
    assert hit_at_1(["b", "a"], JUDGED) == 0.0   # acceptable is not the same as right


def test_judged_at_k_counts_grade_zero_as_judged():
    assert judged_at_k(["a", "c", "x", "y"], JUDGED) == 0.5


def test_bootstrap_identical_systems_show_no_difference():
    scores = [0.2, 0.9, 0.5, 0.0, 1.0]
    result = paired_bootstrap(scores, scores)
    assert result["delta"] == 0 and result["ci_low"] == 0 and result["ci_high"] == 0
    assert result["ties"] == 5


def test_bootstrap_consistent_gain_has_interval_above_zero():
    base = [0.1, 0.4, 0.3, 0.5, 0.2, 0.6, 0.0, 0.3]
    result = paired_bootstrap([b + 0.2 for b in base], base)
    assert result["ci_low"] > 0 and result["wins"] == 8


def test_bootstrap_mixed_result_interval_spans_zero():
    result = paired_bootstrap([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1])
    assert result["ci_low"] < 0 < result["ci_high"]
