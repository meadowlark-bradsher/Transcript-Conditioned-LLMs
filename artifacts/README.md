# Artifacts Convention

This directory is the default home for generated experiment material that is
useful to keep around locally but should not crowd tracked source files.

Use these buckets:

- [artifacts/configs/](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/artifacts/configs/)
  saved run configs, manifests, and small metadata snapshots
- [artifacts/run_outputs/](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/artifacts/run_outputs/)
  raw run outputs, parquet/json/jsonl exports, and executed notebook captures
- [artifacts/derived/](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/artifacts/derived/)
  derived tables, plots, summaries, and post-processing outputs
- [artifacts/scratch/](/Users/meadowlarkbradsher/workspace/repos/genai/blog/transcript-conditioned-llm-demo/artifacts/scratch/)
  disposable one-off files produced while exploring

Guiding rule:

- inputs and source belong in the repo
- generated outputs belong in `artifacts/`

This convention is intentionally minimal. It is only a separation mechanism,
not a full experiment-tracking system.
