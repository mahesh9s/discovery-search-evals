"""Tokenisation shared by the keyword retrievers."""
import functools
import re
import unicodedata

import snowballstemmer

_STEMMER = snowballstemmer.stemmer("english")
_TOKEN = re.compile(r"[a-z0-9]+")
_POSSESSIVE = re.compile(r"['’]s\b")

# Function words, plus the domain words that show up in nearly every query
# ("movies", "films") and carry no retrieval signal. Kept deliberately short:
# aggressive stopword lists break title lookups such as "Get Out" or "Her".
STOPWORDS = frozenset(
    """
    a an and are as at be but by for from has have if in into is its of on or
    so that the their them they this to was were will with
    movie movies film films
    """.split()
)


@functools.lru_cache(maxsize=None)
def _stem(token: str) -> str:
    return _STEMMER.stemWord(token)


def tokenize(text: str) -> list[str]:
    """Lowercase, strip accents and possessives, drop stopwords, stem."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = _POSSESSIVE.sub("", text.lower())
    return [_stem(t) for t in _TOKEN.findall(text) if t not in STOPWORDS]
