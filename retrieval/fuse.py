"""Score fusion: combine vector similarity with a structural signal.

The vector candidate gives you a similarity score. The traversal context
gives you graph evidence — does the recipe actually have a cuisine, an
author, and ingredients in the KG? Fuse the two into a single ranked
score so retrieval that's both semantically similar AND graph-rich rises
to the top.
"""

from __future__ import annotations


# Course-provided constant — the per-context-field boost. Combining a
# vector score in [0, 1] with three boosts of 0.1 keeps the final score
# in a comparable range.
STRUCTURAL_BOOST_PER_FIELD = 0.1


def _is_non_empty(value) -> bool:
    """A field is "non-empty" iff it's not None, and — for list fields —
    also not an empty list. Implemented generically (rather than relying
    on Python truthiness) so an empty string would NOT be silently
    treated the same as None: the documented rule only excludes None
    (and empty lists), nothing else.
    """
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    return True


def fuse(
    vector_results: list[dict],
    contexts: dict[str, dict],
) -> list[dict]:
    """Combine vector similarity with structural completeness into a single ranking.

    Arguments:
      vector_results: output of vector_candidates() — list of
        {"recipe_id", "name", "score"} dicts ordered by vector score DESC.
      contexts: a mapping recipe_id -> context dict (the output of
        expand_context() for that recipe).

    Returns: a list of dicts, each with keys:
      - "recipe_id" (str)
      - "name" (str)
      - "score" (float): the FUSED score (NOT the raw vector score)
      - "context" (dict): the context dict from `contexts`
    Ordered by fused score DESC.

    Fusion rule (used exactly as documented):
      final_score = vector_score
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if cuisine is non-empty else 0)
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if author  is non-empty else 0)
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if ingredients is non-empty else 0)
    """
    empty_context = {"cuisine": None, "author": None, "ingredients": []}

    fused: list[dict] = []
    for entry in vector_results:
        recipe_id = entry["recipe_id"]
        context = contexts.get(recipe_id, empty_context)

        boost = 0.0
        if _is_non_empty(context.get("cuisine")):
            boost += STRUCTURAL_BOOST_PER_FIELD
        if _is_non_empty(context.get("author")):
            boost += STRUCTURAL_BOOST_PER_FIELD
        if _is_non_empty(context.get("ingredients")):
            boost += STRUCTURAL_BOOST_PER_FIELD

        fused.append(
            {
                "recipe_id": recipe_id,
                "name": entry["name"],
                "score": entry["score"] + boost,
                "context": context,
            }
        )

    fused.sort(key=lambda d: d["score"], reverse=True)
    return fused