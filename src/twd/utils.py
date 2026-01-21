from rapidfuzz import fuzz
from typing import List

def normalize(name) -> str:
    return name.lower().replace('-', ' ').replace('_', ' ')

def fuzzy_search(query, items, threshold = 50) -> List:
    """
    query: search input
    items: list of (alias, name)
    threshold: threshold score over which the entries are selected

    returns: list of (entry, score)
    """

    # return all items if query is empty
    if not query:
        return [(e, 100) for e in items]

    normalized_query = normalize(query)
    results = []

    # filtering
    for entry in items:
        alias, name = normalize(entry.alias), normalize(entry.name)

        alias_score = fuzz.ratio(normalized_query, alias)
        name_score = fuzz.ratio(normalized_query, name)

        # choose higher score
        best_score = max(alias_score, name_score)

        # filter out low scores
        if best_score > threshold:
            results.append((entry, best_score))

    results.sort(key=lambda x: x[1], reverse=True)

    return results

def linear_search(query, items) -> List:
    """
    simple substring search
    """
    result = [entry.alias for entry in items if query in entry.alias]

    return result
