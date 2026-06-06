"""Load the recipe-KG fixture into Neo4j and embed recipe descriptions.

Course-provided. Do not modify.

Steps (in order):
  1. Connect to Neo4j using NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD.
  2. Wipe any existing data (so re-runs are deterministic).
  3. Execute data/recipes_kg.cypher (statement-by-statement; the file uses
     ';' terminators so we split on those).
  4. Assert the Identity Discipline constraint exists.
  5. Create the Neo4j 5.x native vector index on (:Recipe).embedding
     (384-dim, cosine).
  6. Embed every recipe's `description` with sentence-transformers
     all-MiniLM-L6-v2 and SET r.embedding = $vec.
  7. Wait for the vector index to come ONLINE.
  8. Run acceptance assertions on node/relationship counts and entity
     uniqueness; exit non-zero on mismatch.

Expected counts (after load):
  Nodes: :Recipe=50, :Cuisine=8, :Ingredient=15, :Author=5, :Technique=5
         (total 83)
  All 50 Recipe nodes have r.embedding of length 384.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Course-provided embedding helpers — DO NOT modify these.
from retrieval.embed import get_embedder, embed_text


EXPECTED_NODE_COUNTS = {
    "Recipe": 50,
    "Cuisine": 8,
    "Ingredient": 15,
    "Author": 5,
    "Technique": 5,
}
EXPECTED_TOTAL_NODES = sum(EXPECTED_NODE_COUNTS.values())  # 83
EMBEDDING_DIM = 384
VECTOR_INDEX_NAME = "recipe_descriptions"


def _split_cypher_statements(text: str) -> list[str]:
    """Split a .cypher file on ';' terminators, stripping comments + blank lines."""
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.split("//", 1)[0].rstrip()
        if stripped:
            cleaned_lines.append(stripped)
    blob = "\n".join(cleaned_lines)
    return [s.strip() for s in blob.split(";") if s.strip()]


def main() -> int:
    load_dotenv()
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "testtest")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Step 2 — wipe existing data so reruns are deterministic.
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()

    # Step 3 — execute the fixture .cypher statement by statement.
    cypher_path = Path(__file__).resolve().parent / "data" / "recipes_kg.cypher"
    statements = _split_cypher_statements(cypher_path.read_text())
    print(f"[load_fixture] Executing {len(statements)} Cypher statements...")
    with driver.session() as session:
        for stmt in statements:
            session.run(stmt).consume()

    # Step 4 — assert Identity Discipline constraint exists.
    with driver.session() as session:
        constraints = session.run("SHOW CONSTRAINTS").data()
        names = {c.get("name") for c in constraints}
        assert "entity_id_unique" in names, (
            f"entity_id_unique constraint missing; have: {names}"
        )

    # Step 5 — create the vector index (idempotent).
    with driver.session() as session:
        session.run(
            "CREATE VECTOR INDEX recipe_descriptions IF NOT EXISTS "
            "FOR (r:Recipe) ON r.embedding "
            "OPTIONS { indexConfig: { "
            "  `vector.dimensions`: 384, "
            "  `vector.similarity_function`: 'cosine' "
            "}}"
        ).consume()

    # Step 6 — embed every recipe description and SET r.embedding.
    print("[load_fixture] Loading sentence-transformers model "
          "(first run downloads ~90 MB)...")
    embedder = get_embedder()
    with driver.session() as session:
        recipes = session.run(
            "MATCH (r:Recipe) RETURN r.id AS id, r.description AS description"
        ).data()
    print(f"[load_fixture] Embedding {len(recipes)} recipe descriptions...")
    with driver.session() as session:
        for row in recipes:
            vec = embed_text(embedder, row["description"])
            assert len(vec) == EMBEDDING_DIM, (
                f"Embedding dim mismatch: got {len(vec)}, expected {EMBEDDING_DIM}"
            )
            session.run(
                "MATCH (r:Recipe {id: $id}) SET r.embedding = $vec",
                id=row["id"], vec=vec,
            ).consume()

    # Step 7 — wait for the vector index to come ONLINE.
    print("[load_fixture] Waiting for vector index to come ONLINE...")
    deadline = time.time() + 30
    while time.time() < deadline:
        with driver.session() as session:
            rows = session.run(
                "SHOW INDEXES YIELD name, state WHERE name = $name "
                "RETURN state",
                name=VECTOR_INDEX_NAME,
            ).data()
        if rows and rows[0]["state"] == "ONLINE":
            break
        time.sleep(1)
    else:
        print(f"[load_fixture] Vector index '{VECTOR_INDEX_NAME}' did not "
              f"come ONLINE within 30s.", file=sys.stderr)
        return 2

    # Step 8 — acceptance assertions.
    with driver.session() as session:
        total = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        assert total == EXPECTED_TOTAL_NODES, (
            f"Node total mismatch: got {total}, expected {EXPECTED_TOTAL_NODES}"
        )
        for label, expected in EXPECTED_NODE_COUNTS.items():
            actual = session.run(
                f"MATCH (n:{label}) RETURN count(n) AS c"
            ).single()["c"]
            assert actual == expected, (
                f"{label} count mismatch: got {actual}, expected {expected}"
            )
        duplicates = session.run(
            "MATCH (n:Entity) WITH n.id AS id, count(*) AS c "
            "WHERE c > 1 RETURN id, c"
        ).data()
        assert not duplicates, f"Duplicate :Entity.id rows: {duplicates}"

    driver.close()
    print("[load_fixture] OK — fixture loaded, indexed, and embedded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
