"""Working reference SPARQL templates keyed by Intent (stretch baseline).

This file is the WORKING reference. The base pipeline you are extending
uses these templates as-is. Modifying them will likely break the baseline
regression test.

The ``RECIPES_BY_CUISINE`` template uses ``rdfs:subClassOf*`` over the
cuisine hierarchy so a query bound with ``?queried_cuisine = :European``
returns recipes whose ``:cuisine`` is ``:Italian`` / ``:French`` / ``:Greek``.
"""

from intent.classify import Intent

PREFIX = (
    "PREFIX : <http://aispire.example.org/recipes/>\n"
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
)

_TEMPLATES = {
    Intent.FIND_RECIPE: PREFIX + """
        SELECT ?recipe ?name ?score WHERE {
            ?recipe a :Recipe ; :name ?name ; :popularityScore ?score .
        }
    """,
    Intent.RECIPES_BY_CUISINE: PREFIX + """
        SELECT ?recipe ?name ?score WHERE {
            ?recipe a :Recipe ; :name ?name ; :popularityScore ?score ; :cuisine ?c .
            ?c rdfs:subClassOf* ?queried_cuisine .
        }
    """,
    Intent.RECIPES_BY_INGREDIENT: PREFIX + """
        SELECT ?recipe ?name ?score WHERE {
            ?recipe a :Recipe ; :name ?name ; :popularityScore ?score ;
                    :primaryIngredient ?queried_ingredient .
        }
    """,
    Intent.RECIPES_BY_AUTHOR: PREFIX + """
        SELECT ?recipe ?name ?score WHERE {
            ?recipe a :Recipe ; :name ?name ; :popularityScore ?score ;
                    :authoredBy ?queried_author .
        }
    """,
}


def query_for(intent: Intent, slots: dict) -> str:
    """Return the SPARQL query body for ``intent``."""
    if intent not in _TEMPLATES:
        raise ValueError(f"No template for intent {intent}")
    return _TEMPLATES[intent]
