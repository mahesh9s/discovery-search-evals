import numpy as np

from evals.retrievers import HybridRetriever, KeywordRetriever, PinnedRetriever, SemanticRetriever
from evals.text import tokenize

CATALOG = [
    {"id": "out", "title": "Get Out", "year": 2017, "genres": ["Horror"], "cast": ["Daniel Kaluuya"],
     "extract": "A young man uncovers a disturbing secret when he meets his girlfriend's family."},
    {"id": "o11", "title": "Ocean's Eleven", "year": 2001, "genres": ["Crime"], "cast": ["George Clooney", "Brad Pitt"],
     "extract": "A gang of thieves plans a casino heist in Las Vegas."},
    {"id": "o12", "title": "Ocean's Twelve", "year": 2004, "genres": ["Crime"], "cast": ["George Clooney", "Brad Pitt"],
     "extract": "The sequel to Ocean's Eleven. The crew plans a heist in Europe."},
    {"id": "amelie", "title": "Amélie", "year": 2001, "genres": ["Romance"], "cast": ["Audrey Tautou"],
     "extract": "A shy waitress in Paris decides to change the lives of the people around her."},
]
FIELDS = {"title": 3.0, "cast": 2.0, "genres": 2.0, "extract": 1.0}


def fake_embedder(texts):
    """Bag-of-letters vectors: enough to rank, no model download."""
    out = np.zeros((len(texts), 26), dtype=np.float32)
    for i, text in enumerate(texts):
        for ch in text.lower():
            if "a" <= ch <= "z":
                out[i, ord(ch) - 97] += 1
    return out


def ids(results):
    return [doc_id for doc_id, _ in results]


def test_tokenize_handles_possessives_accents_and_short_titles():
    assert tokenize("Ocean's Eleven") == tokenize("oceans eleven") == ["ocean", "eleven"]
    assert tokenize("Amélie") == tokenize("amelie")
    assert tokenize("Get Out") == ["get", "out"]          # not swallowed as stopwords
    assert tokenize("movies with the") == []


def test_keyword_finds_title_and_cast():
    kw = KeywordRetriever(CATALOG, FIELDS)
    assert ids(kw.search("get out"))[0] == "out"
    assert set(ids(kw.search("brad pitt"))) == {"o11", "o12"}


def test_keyword_returns_empty_page_when_nothing_matches():
    assert KeywordRetriever(CATALOG, FIELDS).search("intersteller") == []


def test_semantic_always_returns_k_results():
    sem = SemanticRetriever(CATALOG, fake_embedder)
    assert len(sem.search("intersteller", k=3)) == 3


def test_hybrid_fuses_both_lists():
    kw = KeywordRetriever(CATALOG, FIELDS)
    sem = SemanticRetriever(CATALOG, fake_embedder)
    fused = ids(HybridRetriever([kw, sem]).search("casino heist", k=4))
    assert fused[0] in {"o11", "o12"} and len(fused) == 4


def test_pinning_puts_exact_title_first_even_when_ranker_prefers_the_sequel():
    class SequelFirst:
        def search(self, query, k=10):
            return [("o12", 2.0), ("o11", 1.0), ("out", 0.5)][:k]

    pinned = PinnedRetriever(CATALOG, SequelFirst())
    assert ids(pinned.search("oceans eleven", k=3)) == ["o11", "o12", "out"]


def test_pinning_lists_an_actors_films_newest_first():
    pinned = PinnedRetriever(CATALOG, KeywordRetriever(CATALOG, FIELDS))
    assert ids(pinned.search("movies with brad pitt"))[:2] == ["o12", "o11"]


def test_pinning_leaves_other_queries_alone():
    kw = KeywordRetriever(CATALOG, FIELDS)
    assert PinnedRetriever(CATALOG, kw).search("casino heist") == kw.search("casino heist")
