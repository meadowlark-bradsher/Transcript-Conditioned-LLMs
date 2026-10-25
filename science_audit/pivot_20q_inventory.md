# Pivot 20Q Inventory

Active study line:

- `S01` [notebooks/01_core_experiment_infrastructure.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/01_core_experiment_infrastructure.ipynb)
- `S02` [notebooks/02_scoring_engine_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/02_scoring_engine_demo.ipynb)
- `S03` [notebooks/03_intervention_detection.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/03_intervention_detection.ipynb)
- `S04` [notebooks/04b_failure_regime_pilot.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/04b_failure_regime_pilot.ipynb)

Primary implementation modules:

- [experiment/scoring.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/scoring.py)
- [experiment/analysis.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/analysis.py)
- [experiment/pilot.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/pilot.py)
- [experiment/trajectory.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/trajectory.py)

This note is an inventory of the math and statistics in the current pivot line.
It does not change or validate the implementations yet.

## S01: Deterministic mechanics

Core mathematical objects:

- fixed ordered secret universe
- full yes/no mask over secrets
- restriction of masks to the feasible set
- feasible-set update by the true branch

Interpretation:

- exact mechanics, not statistical inference

## S02: Per-turn scoring

### Binary partition entropy

Implemented in:
[experiment/scoring.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/scoring.py)

Role:

- measures how evenly a question splits the current feasible set

Type:

- exact descriptive metric

### Belief entropy under uniform posterior

Implemented in:
[experiment/scoring.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/scoring.py)

Role:

- uses `log2(feasible_size)` as a coarse state-uncertainty measure

Type:

- exact under the uniform-belief assumption
- assumption should remain explicit

### Null-refinement and duplicate-partition logic

Implemented in:
[experiment/scoring.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/scoring.py)

Role:

- identifies wasted questions

Type:

- exact rule-based diagnostics

### Quality score

Implemented in:
[experiment/scoring.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/scoring.py)

Role:

- collapses partition quality and failure flags into a single turn-level score

Type:

- heuristic scoring rule

## S03: Intervention detection

### Rolling-window threshold detector

Implemented in:
[experiment/analysis.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/analysis.py)

Role:

- finds the first persistent degradation point in question quality

Type:

- heuristic detector, intentionally simple and interpretable

### Run-level intervention summaries

Implemented in:
[experiment/analysis.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/analysis.py)

Derived quantities include:

- intervention turn
- entropy at intervention
- tokens before intervention
- mean pre-intervention quality
- duplicate/null/invalid counts

Type:

- descriptive aggregation over deterministic mechanics plus heuristic trigger

## S04: Failure-regime pilot

### Pilot-grid construction

Implemented in:
[experiment/pilot.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/pilot.py)

Role:

- builds compact regime sweeps over model, universe size, and max turns

Type:

- experimental design helper

### Pilot cell summarization

Implemented in:
[experiment/pilot.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/pilot.py)

Derived quantities include:

- intervention detection rate
- median intervention turn
- median entropy at intervention
- duplicate/null/invalid averages
- mean tokens before intervention

Type:

- descriptive summary with heuristic regime labeling

### Regime selection

Implemented in:
[experiment/pilot.py](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/experiment/pilot.py)

Role:

- selects a usable operating regime from the pilot table

Type:

- heuristic model-selection step, not a statistical estimator

## Audit priority

If you later want to reduce cognitive debt in this pivot line, the likely order is:

1. partition entropy and belief entropy assumptions
2. quality score construction
3. intervention threshold/window logic
4. pilot regime-selection heuristics
