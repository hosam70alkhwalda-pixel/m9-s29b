"""Vector candidate retrieval over the Neo4j 5.x native vector index.

The vector index `recipe_descriptions` was created and populated by
`load_fixture.py`. Your job here is to query it for the top-k recipes
whose description embedding is most similar to the embedded query.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

from .embed import embed_text


def vector_candidates(
    driver,
    embedder: SentenceTransformer,
    query: str,
    k: int = 10,
) -> list[dict]:
    """Return the top-k vector-similar recipes for a natural-language query.

    Returns a list of dicts, each with keys:
      - "recipe_id" (str): the :Recipe.id property
      - "name" (str): the :Recipe.name property
      - "score" (float): similarity score in [0.0, 1.0] (cosine, normalized
        by Neo4j); higher = more similar
    Length of the returned list is at most k. Results are ordered by score DESC.
    """
    # TODO: Embed the query string into a 384-dim vector using embed_text(embedder, query).

    # TODO: Use Neo4j's native vector index to retrieve the top-k similar
    #       :Recipe nodes for that vector, returning recipe_id, name, and
    #       similarity score for each.

    raise NotImplementedError("vector_candidates not implemented")
