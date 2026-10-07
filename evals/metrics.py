"""Ranking metrics. Each takes the ranked doc ids for one query and that
query's judgments {doc_id: grade}, and returns a float in [0, 1]."""
import math

K = 10


def _gain(grade: int) -> float:
    return 2.0 ** grade - 1.0


def ndcg(ranked: list[str], judged: dict[str, int], k: int = K) -> float:
    dcg = sum(_gain(judged.get(d, 0)) / math.log2(i + 2) for i, d in enumerate(ranked[:k]))
    ideal = sorted(judged.values(), reverse=True)[:k]
    idcg = sum(_gain(g) / math.log2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg if idcg > 0 else 0.0


def recall(ranked: list[str], judged: dict[str, int], k: int = K) -> float:
    relevant = {d for d, g in judged.items() if g > 0}
    if not relevant:
        return 0.0
    # Capped at k so a query with 40 relevant titles can still score 1.0.
    return len(relevant.intersection(ranked[:k])) / min(len(relevant), k)


def mrr(ranked: list[str], judged: dict[str, int], k: int = K) -> float:
    for i, d in enumerate(ranked[:k]):
        if judged.get(d, 0) > 0:
            return 1.0 / (i + 1)
    return 0.0


def hit_at_1(ranked: list[str], judged: dict[str, int]) -> float:
    """1.0 when the first result is one of the best possible answers."""
    best = max(judged.values(), default=0)
    return float(bool(ranked) and best > 0 and judged.get(ranked[0], 0) == best)


def judged_at_k(ranked: list[str], judged: dict[str, int], k: int = K) -> float:
    """Share of the returned results that a human has actually judged.

    Unjudged results score as not relevant, which quietly punishes any new
    system that surfaces titles the old ones never did. When this drops below
    1.0, label the gap (python -m evals.pool) before trusting the comparison.
    """
    top = ranked[:k]
    return sum(d in judged for d in top) / len(top) if top else 1.0


METRICS = {
    "ndcg@10": ndcg,
    "recall@10": recall,
    "mrr@10": mrr,
    "hit@1": hit_at_1,
    "judged@10": judged_at_k,
}
