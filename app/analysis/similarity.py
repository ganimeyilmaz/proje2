from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.normalize.rules import fold_tr


def token_jaccard(a: str, b: str) -> float:
    sa = set(fold_tr(a).split())
    sb = set(fold_tr(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def tfidf_cosine(texts_a: list[str], texts_b: list[str]) -> float:
    docs = [" ".join(texts_a).strip(), " ".join(texts_b).strip()]
    if not docs[0] or not docs[1]:
        return 0.0
    vectorizer = TfidfVectorizer(min_df=1)
    try:
        matrix = vectorizer.fit_transform(docs)
    except ValueError:
        return 0.0
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])


def program_jaccard(titles_a: set[str], titles_b: set[str]) -> float:
    if not titles_a or not titles_b:
        return 0.0
    return len(titles_a & titles_b) / len(titles_a | titles_b)


def compare_title_sets(a: set[str], b: set[str]) -> dict:
    return {
        "shared": sorted(a & b),
        "only_a": sorted(a - b),
        "only_b": sorted(b - a),
        "jaccard": program_jaccard(a, b),
    }
