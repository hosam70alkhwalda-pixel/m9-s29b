# Module 9 Week B — Stretch Thu — GraphRAG Hybrid Retrieval on Neo4j

> **Honors Track.** Stretch is for learners who have completed all
> core assignments, are On Track or Advanced, and are attending
> consistently. See the cohort Honors Track policy for details.

This stretch implements **GraphRAG hybrid retrieval** over the Module 9
Week B recipe knowledge graph. You will combine Neo4j 5.x's **native
vector index** (over recipe descriptions, embedded with
`sentence-transformers/all-MiniLM-L6-v2`) with **1-hop Cypher
traversal** (cuisine, author, ingredients) and **fuse** the two
signals into a single ranked retrieval score.

## Production-discipline framing

Hybrid retrieval — vector index + graph traversal fused at answer time
— is a **first-class production pattern**, not a hack or a fallback.
It is the *schema-bounded NL→evidence* primitive you already saw on
Weaviate in Module 8 (vector-only) and that you will meet again on the
deployment surface in Module 10 (as the retrieval layer behind a
FastAPI service). The engine differs across the M8 → M9 → M10 bridge
(Weaviate's HNSW versus Neo4j's native vector index versus whatever
production engine sits behind a deployed service); the primitive does
not. The carry-forward is deliberate.

## Prerequisites

- **Integration 9B complete** (you have a working deterministic
  NL→Cypher mapper).
- **Lab 9B complete** (you understand the recipe-domain schema this
  stretch loads a subset of).

## What you will build

You will complete four small modules under `retrieval/`:

| File | What you implement |
|---|---|
| `vector_search.py` | `vector_candidates(driver, embedder, query, k)` — query the Neo4j vector index for the top-k vector-similar recipes |
| `traversal.py` | `expand_context(driver, recipe_id)` — 1-hop Cypher traversal for cuisine, author, ingredients |
| `fuse.py` | `fuse(vector_results, contexts)` — combine vector score + structural completeness into one ranked score |
| `hybrid.py` | `hybrid_retrieve(driver, embedder, query, k=10)` — orchestrate all three steps |

Course-provided (do not modify):

- `retrieval/embed.py` — wraps `all-MiniLM-L6-v2` (384-dim).
- `load_fixture.py` — loads the recipe KG, creates the vector index,
  embeds every recipe description, and runs acceptance assertions.
- `data/recipes_kg.cypher` — the fixture (~83 nodes).
- `data/eval_queries.json` — 8 paraphrastic NL queries with gold
  recipe-id sets, used by the autograder for recall@10.

## Setup

Local Neo4j (one-time per machine):

```bash
docker compose up -d
docker compose logs -f neo4j | head  # wait for "Started."
```

Python environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python load_fixture.py     # ~1-2 min on first run (downloads MiniLM)
pytest tests/ -v           # all green when you're done
```

## Tests

The autograder runs the following checks:

- Vector index `recipe_descriptions` exists and is ONLINE; every
  Recipe has a 384-dim embedding.
- `vector_candidates(...)` returns candidates with `recipe_id` and
  `score` in [0, 1].
- `expand_context(...)` returns non-empty cuisine and ingredients for
  a known recipe.
- `fuse(...)` ranks according to the documented combination rule.
- `hybrid_retrieve` achieves a recall@10 threshold across the 8 eval
  queries.
- Identity Discipline: no duplicate `:Entity.id`.

## How to submit

See `FORK-SUBMIT.md`.

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.
