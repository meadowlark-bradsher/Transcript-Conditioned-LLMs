# Study Registry

This directory is the post-processing layer for keeping finished work separate
from exploratory work.

The intent is:

- preserve completed studies without letting later experimentation rewrite their story
- make active pivot work easy to identify
- keep lower-priority branches visible without letting them dominate the repo

Study IDs are conceptual. They do not need to match notebook filenames.

## Tracks

### Legacy transcript studies

These are the finished studies in
[notebooks/transcript_conditioning_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/transcript_conditioning_demo.ipynb).

| Study ID | Status | Notebook | Scope | Preservation intent |
|---|---|---|---|---|
| `LT01` | complete | [notebooks/transcript_conditioning_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/transcript_conditioning_demo.ipynb) | Transcript reconstruction: outputs track transcript-implied secret rather than a hidden committed state | Treat as finished scientific work; avoid casual edits |
| `LT02` | complete | [notebooks/transcript_conditioning_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/transcript_conditioning_demo.ipynb) | Transcript ordering effect: same logical content, different order, different model behavior | Treat as finished scientific work; avoid casual edits |

### Active pivot studies

These are the notebooks most relevant to the current multiple-choice pivot.

| Study ID | Status | Notebook | Scope | Notes |
|---|---|---|---|---|
| `S01` | active | [notebooks/01_core_experiment_infrastructure.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/01_core_experiment_infrastructure.ipynb) | Deterministic finite-secret mechanics | Good foundation layer |
| `S02` | active | [notebooks/02_scoring_engine_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/02_scoring_engine_demo.ipynb) | Per-turn scoring and diagnostics | Good scoring layer |
| `S03` | active | [notebooks/03_intervention_detection.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/03_intervention_detection.ipynb) | Threshold-based intervention detection | Candidate detector logic for pivot |
| `S04` | active | [notebooks/04b_failure_regime_pilot.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/04b_failure_regime_pilot.ipynb) | Compact pilot grid for usable failure regimes | Post-processing study ID chosen so notebook `04b` becomes Study 4 |

### Cross-model replications

Ports of the legacy studies to other models. They reuse the legacy toy domain
verbatim and write outputs to `artifacts/run_outputs/`, so `LT01`/`LT02` stay untouched.

| Study ID | Status | Script | Scope | Notes |
|---|---|---|---|---|
| `J01` | pilot run (jev-1.14.0, 2026-10-25) | [scripts/jev_experiment.py](../scripts/jev_experiment.py) | `LT01` on TypeSafe Jev: Choice-question distribution over secrets per transcript, plus the contradictory transcript | Reads P(secret) directly; no free-text parsing |
| `J02` | pilot run (jev-1.14.0, 2026-10-25) | [scripts/jev_experiment.py](../scripts/jev_experiment.py) | `LT02` on Jev: P(salmon \| {salmon, shark}) across 6 permutations × 2 candidate-list orders | Repeated identical calls measure the API's nondeterminism floor |

### Lower-priority archived branch

These notebooks are still useful reference material, but they are lower priority
for the current pivot away from live oracle experimentation.

| Archive ID | Status | Notebook | Scope |
|---|---|---|---|
| `X01` | archived-for-now | [notebooks/04_calibration_and_live_oracle.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/04_calibration_and_live_oracle.ipynb) | Live oracle calibration |
| `X02` | archived-for-now | [notebooks/05_live_experiment_results.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/05_live_experiment_results.ipynb) | Live experiment execution and analysis |
| `X03` | archived-for-now | [notebooks/06_fixed_regime_collection.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/06_fixed_regime_collection.ipynb) | Fixed-regime collection and export |

## Working Rules

- Treat `LT01` and `LT02` as protected legacy studies.
- New experiment churn should not directly rewrite the story of those legacy studies.
- If a new direction needs incompatible logic, prefer a new study note or branch over mutating finished work in place.
- Keep notebook math in place for now, but audit it in `science_audit/` before trusting or extending it.

## Recommended Practice

For future work:

1. Keep `main` as the clean accepted state.
2. Use a branch or `git worktree` per experiment thread.
3. Commit at study boundaries, not only at the end.
4. Write generated outputs to ignored artifact locations, not tracked source locations.
5. When a study is complete, update this registry before starting the next major thread.
