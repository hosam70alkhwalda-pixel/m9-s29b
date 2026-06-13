"""Hybrid GraphRAG retrieval autograder."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parent.parent
_UNMODIFIED_LEARNER_NOTES_MD5 = "f64859f027aca20766eab64e307692c1"


def test_learner_notes_modified():
    """Sentinel: `learner_notes.md` is a TA-rubric-graded deliverable.
    A submission whose `learner_notes.md` is byte-identical to the
    starter template has not been filled in.
    """
    notes = _REPO_ROOT / "learner_notes.md"
    assert notes.exists(), "learner_notes.md is missing from the submission"
    h = hashlib.md5(notes.read_bytes()).hexdigest()
    assert h != _UNMODIFIED_LEARNER_NOTES_MD5, (
        "learner_notes.md is the unmodified starter template. Replace each "
        "bullet question with a narrative answer before resubmitting."
    )


# ---------------------------------------------------------------------------
# Fixture acceptance
# ---------------------------------------------------------------------------

EXPECTED_COUNTS = {
    "Recipe": 50,
    "Cuisine": 8,
    "Ingredient": 15,
    "Author": 5,
    "Technique": 5,
}


def test_load_fixture_acceptance(neo4j_driver):
    """The fixture is loaded with the expected node counts."""
    with neo4j_driver.session() as session:
        for label, expected in EXPECTED_COUNTS.items():
            actual = session.run(
                f"MATCH (n:{label}) RETURN count(n) AS c"
            ).single()["c"]
            assert actual == expected, (
                f"{label} count mismatch: got {actual}, expected {expected}"
            )


# ---------------------------------------------------------------------------
# Vector search
# ---------------------------------------------------------------------------

def test_vector_search_returns_candidates(neo4j_driver, embedder):
    from retrieval.vector_search import vector_candidates

    results = vector_candidates(
        neo4j_driver, embedder,
        "stir-fried spicy chicken with peppercorn",
        k=10,
    )
    assert isinstance(results, list)
    assert len(results) >= 1, "vector_candidates returned no candidates"
    assert len(results) <= 10
    for r in results:
        assert "recipe_id" in r and isinstance(r["recipe_id"], str)
        assert "score" in r and isinstance(r["score"], (int, float))
        assert 0.0 <= r["score"] <= 1.0, (
            f"vector_candidates score {r['score']} not in [0, 1]"
        )

    # Sorted by score DESC.
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), (
        "vector_candidates results must be sorted by score DESC"
    )


# ---------------------------------------------------------------------------
# Traversal
# ---------------------------------------------------------------------------

def test_expand_context_returns_neighbors(neo4j_driver):
    from retrieval.traversal import expand_context

    # recipe:011 = Margherita Pizza; has cuisine, author, and ingredients in
    # the fixture.
    context = expand_context(neo4j_driver, "recipe:011")
    assert isinstance(context, dict)
    assert set(context.keys()) >= {"cuisine", "author", "ingredients"}
    assert context["cuisine"] == "Italian", (
        f"Margherita Pizza cuisine should be Italian, got {context['cuisine']}"
    )
    assert context["author"] is not None and context["author"] != "", (
        f"Margherita Pizza should have an author, got {context['author']}"
    )
    assert isinstance(context["ingredients"], list)
    assert len(context["ingredients"]) >= 1, (
        f"Margherita Pizza should have ingredients, got {context['ingredients']}"
    )
    # Ingredients should be sorted (deterministic).
    assert context["ingredients"] == sorted(context["ingredients"]), (
        "expand_context ingredients list must be alphabetically sorted"
    )


# ---------------------------------------------------------------------------
# Fusion
# ---------------------------------------------------------------------------

def test_fuse_ranks_correctly():
    """With controlled scores, the documented fusion rule must hold."""
    from retrieval.fuse import fuse, STRUCTURAL_BOOST_PER_FIELD

    vector_results = [
        {"recipe_id": "r:A", "name": "A", "score": 0.90},  # rich context
        {"recipe_id": "r:B", "name": "B", "score": 0.95},  # bare context
        {"recipe_id": "r:C", "name": "C", "score": 0.80},  # partial context
    ]
    contexts = {
        "r:A": {"cuisine": "Italian", "author": "X", "ingredients": ["basil"]},
        "r:B": {"cuisine": None,      "author": None, "ingredients": []},
        "r:C": {"cuisine": "Asian",   "author": None, "ingredients": ["ginger"]},
    }
    ranked = fuse(vector_results, contexts)

    # Expected fused scores:
    # A = 0.90 + 3 * BOOST
    # B = 0.95 + 0
    # C = 0.80 + 2 * BOOST
    boost = STRUCTURAL_BOOST_PER_FIELD
    expected = {
        "r:A": 0.90 + 3 * boost,
        "r:B": 0.95,
        "r:C": 0.80 + 2 * boost,
    }
    for entry in ranked:
        assert entry["score"] == pytest.approx(
            expected[entry["recipe_id"]], abs=1e-6
        ), (
            f"Fused score for {entry['recipe_id']}: got {entry['score']}, "
            f"expected {expected[entry['recipe_id']]}"
        )

    # Sorted DESC.
    actual_scores = [e["score"] for e in ranked]
    assert actual_scores == sorted(actual_scores, reverse=True), (
        "Fused results must be sorted by score DESC"
    )

    # Context attached.
    for entry in ranked:
        assert entry["context"] == contexts[entry["recipe_id"]]


# ---------------------------------------------------------------------------
# End-to-end recall@10
# ---------------------------------------------------------------------------

# Pinned 2026-06-05 against the reference hybrid retriever
# (answer-key.md §§5.2-5.5): mean recall@10 ≈ 0.82 on the 8-query eval
# set. Pin 0.60 leaves ~22pt headroom so a learner who lands the vector
# layer but stops short of structural fusion still passes.
RECALL_AT_10_THRESHOLD = 0.60


def test_hybrid_recall_at_10(neo4j_driver, embedder):
    """hybrid_retrieve must achieve recall@10 >= threshold across eval queries."""
    from retrieval.hybrid import hybrid_retrieve

    eval_path = Path(__file__).resolve().parent.parent / "data" / "eval_queries.json"
    eval_set = json.loads(eval_path.read_text())

    recalls = []
    per_query = []
    for item in eval_set:
        query = item["query"]
        gold = set(item["gold_recipe_ids"])
        results = hybrid_retrieve(neo4j_driver, embedder, query, k=10)
        retrieved = {r["recipe_id"] for r in results}
        hits = len(gold & retrieved)
        recall = hits / len(gold) if gold else 0.0
        recalls.append(recall)
        per_query.append((query, recall, sorted(gold & retrieved)))

    mean_recall = sum(recalls) / len(recalls)
    print("\n[hybrid_recall_at_10] per-query recall:")
    for q, r, hits in per_query:
        print(f"  {r:.2f}  {q!r}  hits={hits}")
    print(f"[hybrid_recall_at_10] mean recall@10 = {mean_recall:.3f}")

    assert mean_recall >= RECALL_AT_10_THRESHOLD, (
        f"Mean recall@10 = {mean_recall:.3f} < threshold "
        f"{RECALL_AT_10_THRESHOLD}"
    )


# ---------------------------------------------------------------------------
# Fusion must materially change ranking (anti-bypass gate)
# ---------------------------------------------------------------------------

# 10 fixture recipes ship deliberately bare of cuisine / author / ingredient
# context (see data/recipes_kg.cypher — search for "bare-context"). Those
# recipes get a fusion boost of 0; gold recipes with full context get +0.3.
# A learner who implements fuse() as `return vector_results` (bypassing the
# structural boost) will produce a ranking that differs from the fused
# ranking only by zero positions — this test rejects that bypass.
RANKING_DIFFERENCE_MIN_QUERIES = 3


def test_fusion_changes_ranking_from_vector_alone(neo4j_driver, embedder):
    """Verifies fusion is not a no-op against the fixture.

    For each eval query, compares the top-10 fused ranking against the
    top-10 raw-vector ranking. Asserts the two rankings differ on at least
    `RANKING_DIFFERENCE_MIN_QUERIES` of the 8 eval queries. A learner who
    bypasses the structural boost (e.g., `return vector_results`) will
    produce identical rankings on every query and fail this gate.
    """
    from retrieval.hybrid import hybrid_retrieve
    from retrieval.vector_search import vector_candidates

    eval_path = Path(__file__).resolve().parent.parent / "data" / "eval_queries.json"
    eval_set = json.loads(eval_path.read_text())

    differing = 0
    per_query = []
    for item in eval_set:
        query = item["query"]
        fused = hybrid_retrieve(neo4j_driver, embedder, query, k=10)
        vector = vector_candidates(neo4j_driver, embedder, query, k=10)
        fused_ids = [r["recipe_id"] for r in fused]
        vector_ids = [r["recipe_id"] for r in vector]
        if fused_ids != vector_ids:
            differing += 1
        per_query.append((query, fused_ids != vector_ids))

    print("\n[fusion_changes_ranking] per-query ranking changed (fused != vector):")
    for q, changed in per_query:
        print(f"  {'YES' if changed else 'NO ':>3}  {q!r}")
    print(f"[fusion_changes_ranking] {differing}/{len(eval_set)} queries "
          f"with differing ranking (need >= {RANKING_DIFFERENCE_MIN_QUERIES})")

    assert differing >= RANKING_DIFFERENCE_MIN_QUERIES, (
        f"Fusion produced the same ranking as vector-alone on "
        f"{len(eval_set) - differing}/{len(eval_set)} queries. The fixture "
        f"ships 10 deliberately context-bare recipes so that fusion must "
        f"materially demote them below context-rich gold. If your fused "
        f"ranking matches vector ranking, fuse() is bypassing the "
        f"structural boost — check that you are summing the per-field "
        f"boosts into the score and re-sorting DESC."
    )


# ---------------------------------------------------------------------------
# Parameterization: vector_search.py must use $params, not f-strings
# ---------------------------------------------------------------------------

def test_vector_search_uses_parameterized_cypher():
    """AST inspection: vector_search.py must not f-string interpolate `k`
    or `vector` (or the query embedding) into the Cypher passed to
    `session.run`. The vector-index call must use `$k` and `$vector`
    parameters bound by the driver — same safety contract as the Lab 9B
    `candidates.py` check and the Integration 9B `compile.py` check.
    """
    repo_root = Path(__file__).resolve().parent.parent
    vs_path = repo_root / "retrieval" / "vector_search.py"
    src = vs_path.read_text()
    tree = ast.parse(src)

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for piece in node.values:
                if isinstance(piece, ast.FormattedValue):
                    offenders.append(ast.unparse(piece.value))

    assert not offenders, (
        f"vector_search.py contains f-string interpolation "
        f"(silent Cypher-injection / serialization-error class): "
        f"{offenders}. The query embedding and `k` must flow through "
        f"`$vector` and `$k` parameters bound by the Neo4j driver — "
        f"never f-string-formatted into the Cypher text."
    )


# ---------------------------------------------------------------------------
# Starter sentinel
# ---------------------------------------------------------------------------

def test_starter_unmodified_fails():
    """Sentinel: unmodified starter modules raise NotImplementedError.

    This test FAILS on the unmodified starter (all four learner modules
    are stubs that raise NotImplementedError, and the assertion below
    requires at least one to be implemented). It PASSES once the learner
    has implemented at least one — at which point the rest of the
    autograder takes over as the real check.
    """
    from retrieval import vector_search, traversal, fuse, hybrid

    stubs_raising = 0
    try:
        vector_search.vector_candidates(None, None, "x", k=1)
    except NotImplementedError:
        stubs_raising += 1
    except Exception:
        pass

    try:
        traversal.expand_context(None, "recipe:001")
    except NotImplementedError:
        stubs_raising += 1
    except Exception:
        pass

    try:
        fuse.fuse([], {})
    except NotImplementedError:
        stubs_raising += 1
    except Exception:
        pass

    try:
        hybrid.hybrid_retrieve(None, None, "x", k=1)
    except NotImplementedError:
        stubs_raising += 1
    except Exception:
        pass

    assert stubs_raising < 4, (
        "All four retrieval modules still raise NotImplementedError — "
        "implement them and rerun pytest."
    )
