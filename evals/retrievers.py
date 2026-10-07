"""The systems under test.

Every retriever exposes search(query, k) -> [(doc_id, score), ...] so the
harness can treat a keyword index, an embedding model and a fusion of the two
identically. Swapping in a different model means writing one function.
"""
from collections import defaultdict
from typing import Callable, Sequence

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from .text import tokenize

Embedder = Callable[[Sequence[str]], np.ndarray]


def _field_text(doc: dict, field: str) -> str:
    value = doc[field]
    return " ".join(value) if isinstance(value, list) else str(value)


class KeywordRetriever:
    """BM25 over weighted fields (a simplified BM25F).

    Term frequencies from each field are scaled by the field weight and summed
    before saturation, so a title match counts for more than a synopsis match
    without letting long synopses dominate.
    """

    def __init__(self, catalog: list[dict], field_weights: dict[str, float],
                 k1: float = 1.2, b: float = 0.75):
        self.ids = [d["id"] for d in catalog]
        self.k1 = k1
        vectorizer = CountVectorizer(analyzer=tokenize)
        vectorizer.fit(_field_text(d, f) for d in catalog for f in field_weights)
        tf = None
        for field, weight in field_weights.items():
            counts = vectorizer.transform(_field_text(d, field) for d in catalog)
            weighted = counts.astype(np.float32) * weight
            tf = weighted if tf is None else tf + weighted
        self.tf = tf.tocsc()
        self.vocab = vectorizer.vocabulary_
        doc_len = np.asarray(tf.sum(axis=1)).ravel()
        self.length_norm = k1 * (1 - b + b * doc_len / doc_len.mean())
        df = np.diff(self.tf.indptr)
        self.idf = np.log(1 + (len(catalog) - df + 0.5) / (df + 0.5))

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        scores = np.zeros(len(self.ids), dtype=np.float64)
        for token in set(tokenize(query)):
            j = self.vocab.get(token)
            if j is None:
                continue
            start, end = self.tf.indptr[j], self.tf.indptr[j + 1]
            rows, tf = self.tf.indices[start:end], self.tf.data[start:end]
            scores[rows] += self.idf[j] * tf * (self.k1 + 1) / (tf + self.length_norm[rows])
        order = np.argsort(-scores, kind="stable")[:k]
        # A keyword index returns nothing when no term matches. That empty
        # result page is a real product behaviour, so it is preserved here.
        return [(self.ids[i], float(scores[i])) for i in order if scores[i] > 0]


def load_embedder() -> Embedder:
    """WordLlama: a 16 MB static embedding model that runs on a laptop CPU.

    Chosen so the repo reproduces in seconds with no GPU and no API key. It is
    a POC-grade model, not a production one. Pointing the cache at the wheel's
    own directory makes it use the bundled weights and tokenizer, so nothing is
    downloaded at eval time.
    """
    import pathlib

    import wordllama
    from wordllama import WordLlama

    model = WordLlama.load(cache_dir=pathlib.Path(wordllama.__file__).parent)
    return lambda texts: np.asarray(model.embed(list(texts)), dtype=np.float32)


def _unit(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(norms, 1e-12, None)


class SemanticRetriever:
    """Cosine similarity between the query and each title's embedded text."""

    def __init__(self, catalog: list[dict], embedder: Embedder | None = None):
        self.ids = [d["id"] for d in catalog]
        self.embed = embedder or load_embedder()
        texts = [f"{d['title']}. {', '.join(d['genres'])}. {d['extract']}" for d in catalog]
        self.matrix = _unit(self.embed(texts))

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        scores = self.matrix @ _unit(self.embed([query]))[0]
        order = np.argsort(-scores, kind="stable")[:k]
        return [(self.ids[i], float(scores[i])) for i in order]


class HybridRetriever:
    """Reciprocal rank fusion of several retrievers (Cormack et al., 2009)."""

    def __init__(self, retrievers: list, rrf_k: int = 60, depth: int = 100):
        self.retrievers = retrievers
        self.rrf_k = rrf_k
        self.depth = depth

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        fused: dict[str, float] = defaultdict(float)
        for retriever in self.retrievers:
            for rank, (doc_id, _) in enumerate(retriever.search(query, self.depth), start=1):
                fused[doc_id] += 1.0 / (self.rrf_k + rank)
        return sorted(fused.items(), key=lambda item: (-item[1], item[0]))[:k]


class PinnedRetriever:
    """Known-item guard in front of any ranker.

    If the query, once tokenised, is exactly a title or exactly a cast member's
    name, those titles are pinned to the top (newest first) and the wrapped
    ranker fills the rest of the page. Anything else passes straight through.
    There is nothing to tune: a query either is a title or a name, or it is not.
    """

    def __init__(self, catalog: list[dict], fallback):
        self.fallback = fallback
        self.by_title: dict[tuple, list[str]] = defaultdict(list)
        self.by_person: dict[tuple, list[str]] = defaultdict(list)
        for d in sorted(catalog, key=lambda d: (-d["year"], d["title"])):
            self.by_title[tuple(tokenize(d["title"]))].append(d["id"])
            for name in d["cast"]:
                self.by_person[tuple(tokenize(name))].append(d["id"])

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        key = tuple(tokenize(query))
        pinned = list(dict.fromkeys(self.by_title.get(key, []) + self.by_person.get(key, []))) if key else []
        results = [(doc_id, float("inf")) for doc_id in pinned[:k]]
        if len(results) < k:
            seen = set(pinned)
            rest = [r for r in self.fallback.search(query, k + len(pinned)) if r[0] not in seen]
            results += rest[: k - len(results)]
        return results


# Field weights were set once, before any results were looked at, and have not
# been tuned against the golden set.
META_FIELDS = {"title": 3.0, "cast": 2.0, "genres": 2.0}
FULL_FIELDS = {**META_FIELDS, "extract": 1.0}

BASELINE = "keyword_meta"


def build_systems(catalog: list[dict], embedder: Embedder | None = None) -> dict:
    keyword_meta = KeywordRetriever(catalog, META_FIELDS)
    keyword_full = KeywordRetriever(catalog, FULL_FIELDS)
    semantic = SemanticRetriever(catalog, embedder)
    hybrid = HybridRetriever([keyword_full, semantic])
    return {
        # Round 1
        "keyword_meta": keyword_meta,   # today: title, cast and genre matching
        "keyword_full": keyword_full,   # cheap fix: also index the synopsis
        "semantic": semantic,           # the POC: embedding retrieval
        "hybrid": hybrid,               # the POC fused with the cheap fix
        # Round 2, after error analysis: the same rankers behind a known-item guard
        "keyword_pinned": PinnedRetriever(catalog, keyword_full),
        "hybrid_pinned": PinnedRetriever(catalog, hybrid),
    }
