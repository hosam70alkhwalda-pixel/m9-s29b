"""Working reference NL→KG pipeline (stretch baseline — do not modify).

This is the vendored Week B integration pipeline, complete and runnable.
Your extension hooks into the result stream produced here. The baseline
regression test in ``tests/`` re-imports and exercises ``pipeline_base``
to confirm you have not modified it.

Public entry point:

    pipeline_base(query: str) -> tuple[list[dict], dict]

returns ``(results, debug)`` where ``debug`` carries the linker results,
chosen intent, slot bindings, and the SPARQL template string that produced
``results``. Extensions consume ``debug`` to build traces (direction a)
or detect NIL paths (direction b).
"""

import sys
from typing import Any, List, Tuple

from SPARQLWrapper import JSON, SPARQLWrapper

from intent.classify import Intent, classify
from linker.link import link
from sparql.template import query_for

FUSEKI_ENDPOINT = "http://localhost:3030/recipes/sparql"

# Lazy spaCy load — only when an actual query runs.
_NLP = None


def _nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _ner_spans(query: str) -> List[dict]:
    doc = _nlp()(query)
    return [
        {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
        for ent in doc.ents
    ]


def _slot_for_intent(intent: Intent, linked) -> dict:
    """Pick the first non-NIL URI of the relevant kind for the intent."""
    slots: dict = {}
    for lr in linked:
        if lr.predicted_uri is None:
            continue
        uri = lr.predicted_uri
        if intent == Intent.RECIPES_BY_CUISINE and "queried_cuisine" not in slots:
            if any(k in uri for k in ("Italian", "French", "Greek", "Thai", "Japanese",
                                       "Mexican", "European", "Asian", "turkeyCuisine")):
                slots["queried_cuisine"] = uri
        elif intent == Intent.RECIPES_BY_INGREDIENT and "queried_ingredient" not in slots:
            if any(k in uri for k in ("eggplant", "basil", "salt", "parmesan", "tomato",
                                       "garlic", "orangeFruit", "turkeyMeat", "freshBasil")):
                slots["queried_ingredient"] = uri
        elif intent == Intent.RECIPES_BY_AUTHOR and "queried_author" not in slots:
            if "Author" in uri:
                slots["queried_author"] = uri
    return slots


def _execute(template_str: str, init_bindings: dict) -> List[dict]:
    """Execute via rdflib so initBindings substitutes URIs correctly."""
    from rdflib import Graph, URIRef
    from rdflib.plugins.stores import sparqlstore

    store = sparqlstore.SPARQLStore(FUSEKI_ENDPOINT)
    g = Graph(store=store)
    py_bindings = {k: URIRef(v) for k, v in init_bindings.items()}
    rows = []
    for row in g.query(template_str, initBindings=py_bindings):
        rows.append({"recipe": str(row[0]), "name": str(row[1]), "score": float(row[2])})
    return rows


def pipeline_base(query: str) -> Tuple[List[dict], dict]:
    """Run the baseline NL→KG pipeline. Returns (results, debug)."""
    spans = _ner_spans(query)
    linked = link(query, spans)
    intent = classify(query)
    debug = {
        "query": query,
        "ner_spans": spans,
        "linked": linked,
        "intent": intent,
        "slots": {},
        "sparql": "",
    }
    if intent == Intent.UNKNOWN:
        sys.stderr.write(f"pipeline: UNKNOWN intent for {query!r}\n")
        return [], debug

    if intent == Intent.FIND_RECIPE:
        slots: dict = {}
    else:
        slots = _slot_for_intent(intent, linked)
        if not slots:
            sys.stderr.write(f"pipeline: NIL slots for intent {intent} on {query!r}\n")
            debug["slots"] = slots
            return [], debug

    template = query_for(intent, slots)
    debug["slots"] = slots
    debug["sparql"] = template
    rows = _execute(template, slots)
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:5], debug


def pipeline(query: str) -> List[dict]:
    """Backwards-compatible entry point that returns only the results."""
    rows, _ = pipeline_base(query)
    return rows
