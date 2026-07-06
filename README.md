# arch-compliance

A CLI agent that scores a solution architecture document against your
organization's architecture standards, using Claude to grade each requirement
and deterministic code to aggregate the final compliance percentage.

## How it works

1. **`normalize-standards`** — reads one or more standards documents (PDF,
   Word, or Excel) and asks Claude to normalize them into a canonical rubric:
   a JSON list of atomic, checkable requirements, each with a category,
   mandatory flag, and weight (1-5).
2. **`evaluate`** — reads a solution architecture document (PDF or Word,
   including diagrams on PDF pages, which are sent to Claude as images) and
   grades it against every rubric item, producing a verdict
   (`pass`/`partial`/`fail`/`not_applicable`) with evidence and rationale for
   each.
3. Scoring is aggregated in code (not by the LLM): `pass` = full weight,
   `partial` = half weight, `fail` = zero, `not_applicable` items are excluded
   from the denominator. This keeps the final percentage deterministic and
   auditable — the LLM only grades individual, evidence-backed items.

## Install

```bash
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# One-time: turn your standards docs into a rubric
arch-compliance normalize-standards \
  --input standards/security.pdf standards/patterns.docx standards/checklist.xlsx \
  --output rubric.json

# Evaluate an architecture doc against the rubric
arch-compliance evaluate \
  --architecture solutions/payments-platform-sad.pdf \
  --rubric rubric.json \
  --format md \
  --output report.md
```

Re-run `evaluate` against the same `rubric.json` for as many architecture
documents as you like — the rubric only needs to be regenerated when the
standards documents change.

## Notes / limitations

- `ARCH_COMPLIANCE_MODEL` env var overrides the default model.
- Architecture text is truncated to ~60k characters and diagrams to the first
  20 PDF pages per call; very large documents may need to be split.
- Review the generated `rubric.json` before relying on it — spot-check that
  requirements were split atomically and weighted sensibly, since it's the
  basis for every future score.
