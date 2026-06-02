"""Direction (a) — Explainability. Build a per-result trace.

You implement:

    build_trace(result_row, sparql_string, linker_results, bindings) -> Trace
    pipeline_with_trace(query) -> list[tuple[dict, Trace]]

See the stretch assignment page for the task description. The ``Trace``
dataclass in ``extension_a/types.py`` is fully defined — construct and
return instances.
"""

from typing import List, Tuple

from extension_a.types import Trace


def build_trace(
    result_row: dict,
    sparql_string: str,
    linker_results: list,
    bindings: dict,
) -> Trace:
    """Build a Trace for ``result_row``.

    The trace must be reproducible: re-issuing ``sparql_fragment`` against
    Fuseki with ``bindings`` must return ``result_row``.
    """
    # TODO: extract a substring of sparql_string that is sufficient on its
    # own to produce result_row when bound with `bindings`. The simplest
    # correct choice is the full template; a stronger choice is the
    # WHERE-clause body. The autograder substring-checks against the full
    # template, so either passes.

    # TODO: derive the linker reason list — one entry per LinkResult whose
    # predicted_uri appears in `bindings.values()`.

    # TODO: construct and return a Trace.
    raise NotImplementedError(
        "Implement build_trace() — see the stretch assignment page."
    )


def pipeline_with_trace(query: str) -> List[Tuple[dict, Trace]]:
    """Run the baseline pipeline and attach a Trace to each result row.

    Returns a list of (result_row, trace) pairs.
    """
    # TODO: call pipeline_base(query) to get (results, debug).
    # TODO: for each row in results, call build_trace(row, debug["sparql"],
    # debug["linked"], debug["slots"]) and pair the row with its trace.
    raise NotImplementedError(
        "Implement pipeline_with_trace() — see the stretch assignment page."
    )
