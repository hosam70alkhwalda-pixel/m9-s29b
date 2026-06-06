"""Structural context expansion via 1-hop Cypher traversal.

Given a vector-candidate recipe_id, walk one hop in the knowledge graph to
gather the structural context that the vector embedding alone does not
encode (cuisine taxonomy position, author provenance, ingredient list).
This is the "G" in GraphRAG.
"""

from __future__ import annotations


def expand_context(driver, recipe_id: str) -> dict:
    """Return the 1-hop structural context for a :Recipe node.

    Returns a dict with these keys (always present; lists/strings may be empty
    or None when the underlying relationship is absent):
      - "cuisine" (str | None): the name of the directly-linked :Cuisine
      - "author"  (str | None): the name of the directly-linked :Author
      - "ingredients" (list[str]): the names of all linked :Ingredient nodes
        (sorted alphabetically for deterministic ordering)
    """
    # TODO: Write a single Cypher query that starts from the :Recipe with
    #       the given id and gathers, via OPTIONAL MATCH, the linked
    #       :Cuisine name, :Author name, and the collected :Ingredient names.

    # TODO: Return the result as the documented dict shape (alphabetize
    #       the ingredient list so output is deterministic).

    raise NotImplementedError("expand_context not implemented")
