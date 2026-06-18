# Learner Notes — Stretch Thu (GraphRAG Hybrid Retrieval)

## Design decisions

### Vector candidates

I used Neo4j’s vector index with the course-provided MiniLM-L6-v2 embeddings (384 dimensions). I did not tune low-level vector-index parameters because the focus of this exercise was retrieval quality and graph-based fusion rather than index optimization.

The retriever requests the top-k vector candidates and then applies graph-based context retrieval and fusion before returning the final ranked results. I kept the candidate count close to the returned count because the dataset is relatively small and retrieval latency was not a bottleneck.

### Traversal

I used a batched retrieval strategy rather than fetching graph context separately for each candidate.

The main reasons were:

* Fewer database round trips.
* Lower query latency.
* Consistent retrieval behavior across candidates.
* Better scalability if the number of vector candidates increases.

Fetching context lazily per candidate would be simpler to reason about but would introduce additional Neo4j queries and increase overall retrieval time.

### Fusion

I implemented the documented hybrid retrieval pipeline that combines vector retrieval with graph-derived evidence.

One limitation of this fusion rule is that semantic similarity can dominate when multiple recipes share similar language. In those cases, recipes from a related cuisine may rank highly even when they are not the intended target.

A possible alternative fusion rule would be:

```
final_score =

    0.6 * embedding_similarity +
    0.2 * ingredient_overlap +
    0.2 * cuisine_hierarchy_match
```

Where:

* `ingredient_overlap` rewards shared ingredients between the query and retrieved recipe.
* `cuisine_hierarchy_match` boosts recipes connected through cuisine hierarchy relationships such as `[:SUBCLASS_OF*0..]`.

I expect this alternative rule would help most for:

* "warm tortillas with marinated grilled meat and lime"
* "fresh tomato mozzarella and basil from southern italy"
* "fluffy stack of pancakes with maple syrup for breakfast"

These queries contain strong ingredient and cuisine signals that embeddings alone do not always capture.

---

## Eval observations

### Queries retrieved well

The following queries produced strong and intuitive top results:

1. stir-fried spicy chicken with peppercorn and peanuts
2. silky tofu in fiery sichuan numbing sauce
3. vinegared rice rolled with seaweed and fresh fish
4. noodle soup with rich pork broth and toppings

The top-ranked recipes appeared highly relevant and clustered around the intended cuisine and dish type.

### Queries with weaker retrieval

The following queries showed more ambiguity:

1. fresh tomato mozzarella and basil from southern italy
2. warm tortillas with marinated grilled meat and lime
3. creamy oven-baked layered pasta with meat sauce
4. fluffy stack of pancakes with maple syrup for breakfast

Observed failure modes:

* Semantically related but incorrect cuisine.
* Recipes sharing broad food concepts but not the target dish.
* Lexically similar recipes that are topically less precise.
* Generic breakfast or meat-based recipes appearing near the top because of overlapping terminology.

### Limits of MiniLM-L6-v2 on this corpus

MiniLM-L6-v2 performs well at capturing broad semantic meaning but has limitations when:

* Multiple cuisines share similar ingredients.
* Fine-grained culinary distinctions are important.
* Ingredient-specific signals should outweigh general semantic similarity.
* Queries refer to a specific canonical dish without naming it directly.

This suggests that embeddings alone are not always sufficient for recipe-domain retrieval and benefit from structured graph evidence.

---

## Production framing

GraphRAG hybrid retrieval combines vector search with graph traversal and fusion at answer time.

This pattern is valuable because the graph provides structured evidence that pure vector similarity cannot capture. A vector-only pipeline can identify semantically similar recipes, but it cannot naturally exploit explicit relationships such as cuisine hierarchy, ingredient links, or category structure.

One example is cuisine-aware retrieval. Through graph traversal, a recipe can receive additional support because it belongs to the same cuisine family or shares structured ingredient relationships with the query. A vector-only Weaviate pipeline would rely entirely on embedding similarity and could not use these explicit graph relationships during ranking.

As a result, the Neo4j hybrid approach can return results supported by both semantic similarity and structured graph evidence, producing more reliable retrieval for ambiguous food-related queries.
