"""Direction (b) — Robustness. Fuzzy-match fallback when the linker NILs.

You implement:

    fuzzy_fallback(query: str, fuseki_endpoint: str) -> list[dict]
    pipeline_with_fallback(query: str) -> list[dict]

The fallback runs when ``pipeline_base`` returns an empty result list AND
the linker returned at least one NIL on a key entity. Implementation uses
SPARQL ``regex(STR(?label), ..., "i")`` or
``CONTAINS(LCASE(STR(?label)), LCASE(?surface))`` over the recipes KG.

See the stretch assignment page for the task description and the
20-query evaluation set in ``extension_b/eval_queries.jsonl``.
"""

from typing import List


def fuzzy_fallback(query: str, fuseki_endpoint: str) -> List[dict]:
    """Run a fuzzy-match fallback against the KG.

    Returns the same shape as ``pipeline_base`` results: list of dicts
    with at least ``recipe``, ``name``, ``score`` keys. Returns an empty
    list when no fuzzy match recovers a result.
    """
    # TODO: tokenize the query to recover candidate surface forms (the
    # ones the strict linker rejected). Lowercasing + splitting on
    # whitespace + stopword removal is enough.

    # TODO: issue a SPARQL query against the recipes KG that matches
    # ?label loosely via regex or CONTAINS(LCASE(...), ...). Bind the
    # candidate surface fragment via SPARQLWrapper.addParameter — do NOT
    # interpolate it into the query body.

    # TODO: return result dicts in the same shape as pipeline_base. If
    # nothing matches, return [].
    raise NotImplementedError(
        "Implement fuzzy_fallback() — see the stretch assignment page."
    )


def pipeline_with_fallback(query: str) -> List[dict]:
    """Run the baseline pipeline; on empty + NIL linker, invoke the fallback."""
    # TODO: call pipeline_base(query) to get (results, debug).
    # TODO: if results is non-empty, return it (baseline succeeded).
    # TODO: if the linker debug shows at least one NIL on a key entity,
    # call fuzzy_fallback and return its results.
    # TODO: otherwise, return [] (preserve genuine no-result cases).
    raise NotImplementedError(
        "Implement pipeline_with_fallback() — see the stretch assignment page."
    )
