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

    Fusion rule (use this exact rule):
      final_score = vector_score
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if cuisine is non-empty else 0)
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if author  is non-empty else 0)
                  + STRUCTURAL_BOOST_PER_FIELD * (1 if ingredients is non-empty else 0)

    A "non-empty" context field is one that is not None and (for the list
    field) not an empty list.
    """
    # TODO: For each entry in vector_results, look up its context dict,
    #       compute the fused score per the rule above, and assemble the
    #       output dict.

    # TODO: Sort the resulting list by fused score DESC and return it.

    raise NotImplementedError("fuse not implemented")
