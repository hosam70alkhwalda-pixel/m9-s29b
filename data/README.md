# Stretch Thu — Data fixtures

## `recipes_kg.cypher`

An ~83-node subset of the Module 9 Week B recipe knowledge graph, scoped down
for fast embedding in CI.

| Label        | Count |
|--------------|-------|
| `:Recipe`    | 50    |
| `:Cuisine`   | 8     |
| `:Ingredient`| 15    |
| `:Author`    | 5     |
| `:Technique` | 5     |
| **Total**    | **83**|

Every node carries the `:Entity` label and a unique `id` (`<label>:<slug>`),
identical to the canonical Lab W9B schema. Identity Discipline is enforced
by the `entity_id_unique` constraint at fixture-load time.

Relationships (subset of the Lab W9B schema):

- `(:Recipe)-[:USES_INGREDIENT]->(:Ingredient)`
- `(:Recipe)-[:OF_CUISINE]->(:Cuisine)`
- `(:Recipe)-[:BY_AUTHOR]->(:Author)`
- `(:Recipe)-[:REQUIRES_TECHNIQUE]->(:Technique)`
- `(:Cuisine)-[:SUBCLASS_OF]->(:Cuisine)` — 3-level hierarchy
  (`Sichuan -> Chinese -> Asian -> World`, etc.)

Recipe descriptions are short, distinctive natural-language sentences chosen
so embedding-based retrieval is a meaningful signal (not exact-keyword
matchable).

## `eval_queries.json`

8 paraphrastic natural-language queries, each with a small set of
`gold_recipe_ids` (the recipes a high-quality retriever should surface in
its top-k). Queries span multiple cuisines (Sichuan, Italian, Japanese,
Mexican, North American) and use varied phrasing — synonyms, sensory
descriptors, and category words — so simple keyword matching is
insufficient. Used by `tests/test_hybrid.py::test_hybrid_recall_at_10`.
