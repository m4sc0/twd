from rapidfuzz import fuzz
from typing import List

FUZZY_THRESHOLD = 50

def normalize(name) -> str:
    return name.lower().replace('-', ' ').replace('_', ' ')

def search(query, items, threshold = 50) -> List:
    """
    query: search input
    items: list of (alias, name)

    returns: list of (alias, name, score)
    """

    # return all items if query is empty
    if not query:
        return [(alias, name, 100) for alias, name in items]

    normalized_query = normalize(query)
    results = []

    # filtering
    for alias, name in items:
        alias_score = fuzz.WRatio(normalized_query, normalize(alias))
        name_score = fuzz.WRatio(normalized_query, normalize(name))

        # choose higher score
        best_score = max(alias_score, name_score)

        # filter out low scores
        if best_score >= threshold:
            results.append((alias, name, best_score))

    results.sort(key=lambda x: x[2], reverse=True)

    return results

