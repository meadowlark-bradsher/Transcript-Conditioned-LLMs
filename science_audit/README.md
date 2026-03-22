# Science Audit

This directory is the explicit home for cognitive debt around math, statistics,
and experimental interpretation.

The goal is not to rewrite the notebook math yet. The goal is to make the
scientific computing visible, scoped, and auditable.

Each audit note should answer:

- what the quantity or procedure is
- where it is implemented
- whether it is exact, heuristic, or inferential
- what assumptions it depends on
- what still needs verification before full trust

## Current audit notes

- [science_audit/transcript_conditioning_demo.md](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/science_audit/transcript_conditioning_demo.md)
- [science_audit/pivot_20q_inventory.md](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/science_audit/pivot_20q_inventory.md)

## Scope rule

For now, this directory is inventory-first:

- no math rewrites
- no refactors for purity
- no behavior changes

It exists so you can inspect the scientific content before deciding what should
later become a testable library.
