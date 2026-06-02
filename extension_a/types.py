"""Trace dataclass for direction (a) — Explainability.

Fully implemented. You build instances of ``Trace`` inside
``extension_a/trace.py::build_trace``.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Trace:
    """A reproducible per-result trace.

    Attributes
    ----------
    recipe : str
        The result row's recipe URI.
    name : str
        The result row's recipe name.
    sparql_fragment : str
        A substring of the SPARQL template that produced this result. Used
        by the autograder to verify the trace reproduces the decision —
        the recorded fragment, re-issued against Fuseki with the same
        bindings, must return the same row.
    linker_reasons : list[str]
        The ``reason`` strings from the linker results that contributed
        to the slot bindings. At least one per linked span.
    bindings : dict
        The initBindings used at execution time (slot name -> URI).
    """

    recipe: str
    name: str
    sparql_fragment: str
    linker_reasons: List[str]
    bindings: dict = field(default_factory=dict)
