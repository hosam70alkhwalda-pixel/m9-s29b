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
    cypher = (
        "MATCH (r:Recipe {id: $id}) "
        "OPTIONAL MATCH (r)-[:OF_CUISINE]->(c:Cuisine) "
        "OPTIONAL MATCH (r)-[:BY_AUTHOR]->(a:Author) "
        "OPTIONAL MATCH (r)-[:USES_INGREDIENT]->(i:Ingredient) "
        "RETURN c.name AS cuisine, "
        "       a.name AS author, "
        "       collect(DISTINCT i.name) AS ingredients"
    )

    with driver.session() as session:
        result = session.run(cypher, id=recipe_id)
        row = result.single()

        if row is None:
            # No :Recipe with this id at all — return the documented
            # empty-context shape rather than raising, since the caller
            # (fuse) already knows how to treat an absent field as "no
            # structural boost."
            return {"cuisine": None, "author": None, "ingredients": []}

        ingredients = [name for name in row["ingredients"] if name is not None]
        return {
            "cuisine": row["cuisine"],
            "author": row["author"],
            "ingredients": sorted(ingredients),
        }