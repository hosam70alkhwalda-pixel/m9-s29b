"""Autograder for Stretch 9B Thu — Pipeline Extension.

Reads DIRECTION.md to dispatch to direction (a) Explainability or (b)
Robustness. Runs the chosen direction's tests against the learner's
extension. Baseline pipeline_base must remain unchanged.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ROOT = os.path.join(os.path.dirname(__file__), "..")
DIRECTION_PATH = os.path.join(ROOT, "DIRECTION.md")


def _read_direction() -> str:
    """Return 'a', 'b', or '' for undeclared."""
    if not os.path.exists(DIRECTION_PATH):
        return ""
    with open(DIRECTION_PATH) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith(">"):
                continue
            if line.lower() in {"a", "b"}:
                return line.lower()
    return ""


DIRECTION = _read_direction()


def test_direction_declared():
    """DIRECTION.md must declare either 'a' or 'b'."""
    assert DIRECTION in {"a", "b"}, (
        "DIRECTION.md must contain a single 'a' or 'b' on its own line."
    )


def test_baseline_pipeline_unchanged():
    """The vendored baseline pipeline_base must still import and run."""
    from pipeline_base import pipeline_base  # noqa: WPS433

    rows, debug = pipeline_base("italian recipes")
    assert isinstance(rows, list)
    assert isinstance(debug, dict)
    assert "intent" in debug and "sparql" in debug
    # The Italian-cuisine query should return at least one Italian recipe.
    assert len(rows) > 0, "baseline pipeline regressed on 'italian recipes'"


# ---------------- Direction (a) — Explainability ----------------


@pytest.mark.skipif(DIRECTION != "a", reason="Direction (a) not declared")
def test_trace_present_per_result():
    from extension_a.trace import pipeline_with_trace
    from extension_a.types import Trace

    queries = ["italian recipes", "recipes with basil", "recipes by marco"]
    for q in queries:
        paired = pipeline_with_trace(q)
        assert isinstance(paired, list)
        assert len(paired) > 0, f"no results for {q!r}"
        for row, trace in paired:
            assert isinstance(trace, Trace), "trace is not a Trace instance"
            assert trace.sparql_fragment, "trace.sparql_fragment is empty"
            assert isinstance(trace.linker_reasons, list)


@pytest.mark.skipif(DIRECTION != "a", reason="Direction (a) not declared")
def test_trace_fragment_appears_in_baseline_sparql():
    """Trace's sparql_fragment must appear verbatim in the baseline SPARQL template."""
    from extension_a.trace import pipeline_with_trace
    from pipeline_base import pipeline_base

    q = "italian recipes"
    _, base_debug = pipeline_base(q)
    paired = pipeline_with_trace(q)
    for row, trace in paired:
        assert trace.sparql_fragment in base_debug["sparql"], (
            "trace.sparql_fragment is not a substring of the executed template"
        )


@pytest.mark.skipif(DIRECTION != "a", reason="Direction (a) not declared")
def test_trace_linker_reasons_have_at_least_one_entry_per_linked_span():
    """For queries with at least one linked entity, linker_reasons is non-empty."""
    from extension_a.trace import pipeline_with_trace

    paired = pipeline_with_trace("recipes with basil")
    assert paired, "no results to inspect"
    found_non_empty = any(t.linker_reasons for _, t in paired)
    assert found_non_empty, "no trace had any linker_reasons entries"


# ---------------- Direction (b) — Robustness ----------------


@pytest.mark.skipif(DIRECTION != "b", reason="Direction (b) not declared")
def test_fallback_recovers_threshold_queries():
    """At least 8 of the 10 'recoverable' eval queries return non-empty results."""
    from extension_b.fallback import pipeline_with_fallback

    eval_path = os.path.join(ROOT, "extension_b", "eval_queries.jsonl")
    queries = []
    with open(eval_path) as f:
        for line in f:
            queries.append(json.loads(line))

    recoverable = [r for r in queries if r["expected"] == "recoverable"]
    recovered = 0
    for r in recoverable:
        rows = pipeline_with_fallback(r["query"])
        if rows:
            recovered += 1
    assert recovered >= 8, (
        f"fallback recovered {recovered}/10 recoverable queries; threshold is 8"
    )


@pytest.mark.skipif(DIRECTION != "b", reason="Direction (b) not declared")
def test_fallback_does_not_paper_over_unrecoverable_queries():
    """The 10 'empty' eval queries must still return empty after fallback."""
    from extension_b.fallback import pipeline_with_fallback

    eval_path = os.path.join(ROOT, "extension_b", "eval_queries.jsonl")
    bad_recoveries = []
    with open(eval_path) as f:
        for line in f:
            row = json.loads(line)
            if row["expected"] != "empty":
                continue
            results = pipeline_with_fallback(row["query"])
            if results:
                bad_recoveries.append(row["query"])
    # Allow at most 2 false-positives across the 10 unrecoverable queries.
    assert len(bad_recoveries) <= 2, (
        f"fallback wrongly recovered {len(bad_recoveries)} of 10 unrecoverable queries: "
        f"{bad_recoveries}"
    )


@pytest.mark.skipif(DIRECTION != "b", reason="Direction (b) not declared")
def test_fallback_triggers_on_nil():
    """fuzzy_fallback returns at least one result on a known-recoverable misspelling."""
    from extension_b.fallback import fuzzy_fallback

    rows = fuzzy_fallback(
        "recipes with eggplnt",
        os.environ.get("FUSEKI_ENDPOINT", "http://localhost:3030/recipes/sparql"),
    )
    assert isinstance(rows, list)
    assert len(rows) >= 1, "fuzzy_fallback returned no results for 'eggplnt' misspelling"
