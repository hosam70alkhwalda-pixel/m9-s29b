"""Pick the single best URI from a candidate set, or return NIL.

Reference implementation. Two signals applied in order:

1. **Type compatibility** — keep only candidates whose ``rdf:type`` is
   compatible with ``ner_label`` according to ``NER_LABEL_TO_KG_TYPE``.
2. **Popularity prior** — when type filtering leaves more than one
   candidate, prefer the candidate that participates in the most triples
   (a cheap popularity signal computed via ``?uri ?p ?o`` count).

Returns ``None`` (NIL) when no candidate survives or the popularity signal
is tied at the top.
"""

from typing import Optional

from SPARQLWrapper import JSON, SPARQLWrapper

from linker.lookup import DEFAULT_ENDPOINT, has_type
from linker.ner_to_kg_type import NER_LABEL_TO_KG_TYPE


def _popularity(uri: str, endpoint: str) -> int:
    sw = SPARQLWrapper(endpoint)
    sw.setReturnFormat(JSON)
    sw.setQuery(
        f"SELECT (COUNT(*) AS ?n) WHERE {{ <{uri}> ?p ?o }}"
    )
    rows = sw.queryAndConvert()["results"]["bindings"]
    if not rows:
        return 0
    return int(rows[0]["n"]["value"])


def disambiguate(
    candidate_uris: list[str],
    ner_label: str,
    doc_context: dict,
    endpoint: str = DEFAULT_ENDPOINT,
) -> tuple[Optional[str], str]:
    """Return ``(uri, reason)`` — the best URI plus a reason string.

    ``reason`` is one of ``"resolved-by-type"``, ``"resolved-by-context"``,
    ``"nil-ambiguous"``.
    """
    kg_type = NER_LABEL_TO_KG_TYPE.get(ner_label)
    if kg_type is None:
        return None, "nil-no-type-mapping"
    typed = [u for u in candidate_uris if has_type(u, kg_type, endpoint)]
    if len(typed) == 0:
        return None, "nil-ambiguous"
    if len(typed) == 1:
        return typed[0], "resolved-by-type"
    # Secondary signal: popularity (triples-out count).
    scored = sorted(
        ((u, _popularity(u, endpoint)) for u in typed),
        key=lambda t: -t[1],
    )
    if scored[0][1] > scored[1][1]:
        return scored[0][0], "resolved-by-context"
    return None, "nil-ambiguous"
