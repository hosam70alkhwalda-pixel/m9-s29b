"""Candidate generation against the live Fuseki endpoint.

Reference implementation. The function talks to Fuseki over HTTP — the KG
was POSTed into the ``recipes`` dataset by ``load_dataset.py``. The SPARQL
query body itself does not contain the surface form as text; the surface
form is passed as a parameter binding via SPARQLWrapper.addParameter.
"""

from SPARQLWrapper import JSON, SPARQLWrapper

DEFAULT_ENDPOINT = "http://localhost:3030/recipes/sparql"

_PREFIX = (
    "PREFIX : <http://aispire.example.org/recipes/>\n"
    "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
)

_CANDIDATES_Q = _PREFIX + """
SELECT DISTINCT ?uri WHERE {
    { ?uri skos:prefLabel ?label }
    UNION
    { ?uri skos:altLabel ?label }
    FILTER (LCASE(STR(?label)) = LCASE(STR(?surface)))
}
"""


def candidates(surface_form: str, endpoint: str = DEFAULT_ENDPOINT) -> list[str]:
    """Return KG URIs whose skos:prefLabel or skos:altLabel matches surface_form.

    Case-insensitive. The surface form is passed as a SPARQL parameter
    binding — not interpolated into the query body.
    """
    sw = SPARQLWrapper(endpoint)
    sw.setReturnFormat(JSON)
    sw.setQuery(_CANDIDATES_Q)
    sw.addParameter("surface", surface_form)
    rows = sw.queryAndConvert()["results"]["bindings"]
    return [r["uri"]["value"] for r in rows]


def has_type(uri: str, expected_type: str, endpoint: str = DEFAULT_ENDPOINT) -> bool:
    """Return True iff the KG asserts ``<uri> a <expected_type>``."""
    sw = SPARQLWrapper(endpoint)
    sw.setReturnFormat(JSON)
    sw.setQuery(
        _PREFIX
        + f"ASK WHERE {{ <{uri}> a <{expected_type}> }}"
    )
    return bool(sw.queryAndConvert().get("boolean", False))
