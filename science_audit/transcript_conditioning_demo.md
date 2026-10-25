# Transcript Conditioning Demo Audit

Notebook:
[notebooks/transcript_conditioning_demo.ipynb](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/notebooks/transcript_conditioning_demo.ipynb)

Study IDs:

- `LT01` transcript reconstruction
- `LT02` transcript ordering effect

This note inventories the scientific computing in the original notebook without
changing its implementation.

## LT01: Transcript Reconstruction

### Exact finite-domain semantics

Implemented through:

- transcript construction from binary feature assignments
- transcript parsing back into observed feature values
- feasible-set computation over the toy secret space

Core role:

- this is the exact semantics layer for the toy domain
- it is not statistical inference
- it is deterministic logic over a fully specified world

Trust status:

- conceptually strong
- worth preserving as the authoritative semantics of the original demo

### Uniqueness check

The notebook verifies that each constructed transcript maps to exactly one
feasible secret.

Core role:

- internal validity check for the reconstruction experiment

Trust status:

- exact logic check
- should remain attached to the study

## LT02: Transcript Ordering Effect

### Combinatorial search over 3-feature transcripts

Implemented through:

- enumeration of 3-feature subsets
- enumeration of all binary answer assignments for those subsets
- filtering to transcripts whose feasible set is exactly the target pair

Core role:

- deterministic experimental design search
- finds a minimally discriminating transcript family for the ordering study

Trust status:

- exact search over the toy domain

### Permutation generation

Implemented through:

- all permutations of the selected 3-question transcript

Core role:

- creates the treatment family for the ordering experiment
- keeps logical content fixed while changing presentation order

Trust status:

- exact combinatorial transformation

### Output parsing and ambiguity detection

Implemented through:

- secret-name extraction from free-form model outputs
- `OTHER` bucket when no target secret is recovered
- ambiguity flag when multiple target secrets are mentioned

Core role:

- converts model text into categorical outcomes

Trust status:

- useful but should be treated as a measurement layer, not ground truth
- parser edge cases are part of the study's uncertainty budget

### Repeated stochastic sampling protocol

Implemented through:

- repeated runs per permutation
- seeded sampled decoding
- one greedy run per permutation as a deterministic reference

Core role:

- estimates how output distributions vary by transcript order

Trust status:

- experiment protocol, not a statistical model
- reproducibility depends on model, decode config, and seed handling

### Conditional proportion endpoint

Primary endpoint:

- `P(A | output in {A, B})` by permutation

Core role:

- compares how often the model prefers one member of the target pair when the
  output lands inside the two-secret support

Trust status:

- reasonable summary statistic for the study
- excludes `OTHER`, so interpretation depends on how often `OTHER` occurs

### Wilson confidence intervals

Implemented through a Wilson interval helper over binomial counts.

Core role:

- uncertainty interval for the conditional proportion endpoint

Trust status:

- classical interval estimate
- low cognitive debt compared with more advanced modeling
- still worth unit-testing later

### Global chi-square test

Implemented through:

- `6 x 2` contingency table over permutation and `{A, B}` outcomes
- chi-square statistic
- optional p-value if `scipy` is available

Core role:

- asks whether the A/B distribution changes across transcript permutations

Trust status:

- standard omnibus test
- assumes count-table framing is the right summary for the question

### Effect-size range

Implemented as:

- `max(P(A)) - min(P(A))` across permutations

Core role:

- simple effect-size summary for order sensitivity

Trust status:

- descriptive rather than inferential
- useful because it is easy to interpret

### Optional control gate

Implemented through:

- a threshold on observed ordering effect size
- optional follow-up controls only run if the primary effect is strong enough

Core role:

- pragmatic experiment management
- not itself a statistical estimator

Trust status:

- heuristic workflow control

### Follow-up A: list-ordering control

Implemented through:

- rotating the candidate-list order while holding transcript neutral
- tracking `P(A | output in {A, B})` as position changes

Core role:

- control for confounding by candidate-list position rather than transcript order

Important interpretation note:

- this is not causal inference in the potential-outcomes or structural-causal
  sense
- it is a targeted control experiment for one suspected source of bias

Trust status:

- scientifically useful
- better described as a control or confound check than as a causal estimator

### Follow-up B: salience baseline

Implemented through:

- neutral transcript
- fixed candidate list
- repeated sampling to estimate baseline preference between the target pair

Core role:

- estimates baseline pairwise salience absent discriminating transcript evidence

Trust status:

- descriptive baseline, not a causal model

## Inventory Summary

The original notebook's scientific computing consists mainly of:

1. exact toy-domain semantics
2. combinatorial experimental design
3. repeated-sampling measurement
4. categorical parsing
5. binomial uncertainty intervals
6. a chi-square omnibus test
7. targeted controls for list-order and baseline salience

It does not currently contain a heavy causal-inference stack. The function
`run_list_ordering_control(...)` is best interpreted as a confound-control
experiment, not a formal causal estimator.

## Recommended future audit order

If you later externalize this notebook's science into a testable library, the
order should be:

1. exact feasible-set semantics
2. parser behavior
3. Wilson interval helper
4. chi-square table construction
5. control-experiment summaries
