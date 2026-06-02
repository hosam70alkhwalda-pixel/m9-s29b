# Module 9 Week B — Stretch (Honors Track): Pipeline Extension

> **Honors Track.** This stretch is for learners who have completed the required Week B work (Reading, Drill, Lab, Integration) and are On Track or Advanced. Stretch is not required for program completion but is required for Honors distinction.

For the full task description, see the assignment page: **Module 9 Week B — Stretch: Pipeline Extension**.

## What you are building

You extend the Week B integration's NL→KG pipeline with **one** of two pre-approved capabilities. The base pipeline (`pipeline_base.py`) is shipped working — you do not modify it. You build a thin extension layer on top.

### Direction (a) — Explainability

Add a per-result **trace** that records:
- the SPARQL fragment that produced each result row,
- the linker decisions (URIs + reasons) that fed the slot bindings,
- the bindings themselves.

Traces must be reproducible: re-issuing the recorded SPARQL fragment with the recorded bindings against the same KG must return the same row.

You implement `extension_a/trace.py`.

### Direction (b) — Robustness

Add a **fuzzy-match fallback** that runs when the linker returns NIL on a key entity. The fallback uses SPARQL `regex()` or `CONTAINS(LCASE(...), ...)` to recover results the strict linker dropped.

You implement `extension_b/fallback.py` and evaluate against `extension_b/eval_queries.jsonl` — 20 queries, half recoverable, half should still return empty.

## Choose your direction

Edit `DIRECTION.md` and replace `UNDECLARED` with `a` or `b` on its own line. The autograder reads it and dispatches.

## Setup

```bash
# Start Fuseki
docker compose up -d

# Install dependencies (cached from the integration — should be fast)
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Load the KG
python load_dataset.py

# Run the autograder
pytest tests/ -v
```

## What is shipped working — do not modify

- `pipeline_base.py` — vendored Week B integration pipeline (reference baseline)
- `linker/` — reference entity linker
- `intent/` — reference intent classifier
- `sparql/` — reference SPARQL templates
- `extension_a/types.py` — Trace dataclass
- `data/recipes_kg.ttl` — the KG

The baseline regression test re-imports `pipeline_base` and exercises one query against it; modifying the reference modules will likely break this test.

## What you author

- `extension_a/trace.py` (if you chose direction a) or `extension_b/fallback.py` (if you chose direction b)
- `DIRECTION.md` — declare which direction
- Update this README's "Direction notes" section with your design decisions, eval observations, and one tradeoff.

## Direction notes (replace this section)

> Replace this section with your direction choice, your design decisions, the one specific case where your extension changed the pipeline's behavior, and the tradeoff you had to make.

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.
