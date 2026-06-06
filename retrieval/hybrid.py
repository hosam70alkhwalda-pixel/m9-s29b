"""Hybrid GraphRAG retrieval:

  1. Embed the natural-language query (sentence-transformers).
  2. Use Neo4j's native vector index to retrieve top-k vector-similar recipes.
  3. For each candidate recipe, traverse one Cypher hop to gather context
     (cuisine name, author, ingredient list).
  4. Fuse vector similarity + structural signal into a single ranked score.

Returns: list of {recipe_id, name, score, context} ordered by score DESC.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

from .vector_search import vector_candidates
from .traversal import expand_context
from .fuse import fuse


def hybrid_retrieve(
    driver,
    embedder: SentenceTransformer,
    query: str,
    k: int = 10,
) -> list[dict]:
    """Run the full hybrid pipeline for a single natural-language query.

    Arguments:
      driver: a Neo4j driver instance
      embedder: a SentenceTransformer (from retrieval.embed.get_embedder())
      query: the natural-language query string
      k: the number of vector candidates to fetch and the size of the
         returned ranked list (the fused output is sliced to top-k).

    Returns: a list of at most k dicts, each {recipe_id, name, score, context},
    ordered by fused score DESC.
    """
    # TODO: Call vector_candidates(...) to get the top-k vector candidates.

    # TODO: For each candidate, call expand_context(...) to gather its
    #       1-hop structural context. Build a {recipe_id: context_dict} map.

    # TODO: Call fuse(...) to combine vector + structural signals into a
    #       single ranking, then return the top-k entries.

    raise NotImplementedError("hybrid_retrieve not implemented")
