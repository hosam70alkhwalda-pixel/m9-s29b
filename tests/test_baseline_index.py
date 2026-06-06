"""Baseline checks on the vector index + embeddings created by load_fixture.py.

These tests run before the hybrid-retrieval tests so a learner whose
hybrid implementation is broken can still see whether the underlying
indexed graph is in good shape.
"""

from __future__ import annotations


def test_vector_index_exists(neo4j_driver):
    """The native vector index `recipe_descriptions` should exist and be ONLINE."""
    with neo4j_driver.session() as session:
        rows = session.run(
            "SHOW INDEXES YIELD name, state, type "
            "WHERE name = 'recipe_descriptions' "
            "RETURN name, state, type"
        ).data()
    assert rows, "Vector index 'recipe_descriptions' is missing — did load_fixture.py run?"
    assert rows[0]["state"] == "ONLINE", (
        f"Vector index 'recipe_descriptions' state is {rows[0]['state']}, "
        f"expected ONLINE"
    )


def test_vector_index_populated(neo4j_driver):
    """Every (:Recipe) node should have a 384-dim embedding."""
    with neo4j_driver.session() as session:
        rows = session.run(
            "MATCH (r:Recipe) RETURN r.id AS id, r.embedding AS emb LIMIT 5"
        ).data()
    assert len(rows) == 5, f"Expected 5 sampled recipes, got {len(rows)}"
    for row in rows:
        assert row["emb"] is not None, f"Recipe {row['id']} has no embedding"
        assert len(row["emb"]) == 384, (
            f"Recipe {row['id']} embedding has length {len(row['emb'])}, "
            f"expected 384"
        )


def test_entity_id_uniqueness(neo4j_driver):
    """Identity Discipline: no duplicate :Entity.id values."""
    with neo4j_driver.session() as session:
        duplicates = session.run(
            "MATCH (n:Entity) WITH n.id AS id, count(*) AS c "
            "WHERE c > 1 RETURN id, c"
        ).data()
    assert duplicates == [], f"Duplicate :Entity.id rows found: {duplicates}"
