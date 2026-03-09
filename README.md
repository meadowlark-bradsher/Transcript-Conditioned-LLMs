# LLMs Don't Keep Secrets

This project demonstrates, with controlled experiments, how LLM outputs depend on transcript text and transcript order.

If you are new to the project, start with:

1. [`transcript_conditioning_demo.ipynb`](transcript_conditioning_demo.ipynb)
2. [`transcript_bubbles.html`](transcript_bubbles.html)
3. this README section by section

## Why This Repo Exists

Many people talk about models "keeping a secret" in multi-turn games. This repo tests that idea directly in a toy 20-questions domain.

Two core questions are tested:

1. If the model only sees a transcript, does it reconstruct the implied secret?
2. If logical content is unchanged, can transcript order still change model outputs?

## What You Will Find Here

- [`transcript_conditioning_demo.ipynb`](transcript_conditioning_demo.ipynb): main notebook with both experiments.
- [`transcript_conditioning_demo-executed.ipynb`](transcript_conditioning_demo-executed.ipynb): executed run for reference.
- [`transcript_bubbles.html`](transcript_bubbles.html): interactive visual explanation.
- [`scripts/setup_tc70_env.sh`](scripts/setup_tc70_env.sh): reproducible environment bootstrap.
- [`spec.md`](spec.md), [`20q-spec.md`](20q-spec.md): task and toy-domain specs.

## Experiment 1: Transcript Reconstruction

### The question

When asked "What was your secret?" does the model reveal a hidden committed state, or infer from transcript evidence?

### The setup

- 6 animal secrets.
- Each secret has 8 binary features.
- One synthetic Q/A transcript per secret.
- The model is only given transcript text and the candidate secret list.

### What to look for

For each transcript:

1. deterministic feasible-set checker says exactly one secret is valid.
2. model output matches that implied secret.

### Reference result (Llama-3.1-70B-Instruct)

| Transcript implies | Model declared | Match |
|---|---|---|
| cat | cat | ✓ |
| dog | dog | ✓ |
| eagle | eagle | ✓ |
| salmon | salmon | ✓ |
| shark | shark | ✓ |
| crocodile | crocodile | ✓ |

The contradictory transcript (no feasible secret) yields a conflict/error-style response rather than a stable hidden-secret reveal.

## Experiment 2: Transcript Ordering Effect

### The question

If the logical feasible set is the same, does ordering of evidence still matter?

### The setup

- Candidate list reduced to 5 animals.
- Choose 3 Q/A constraints where feasible set is exactly `{salmon, shark}`.
- Evaluate all 6 permutations of those same 3 constraints.
- Feasible-set checker confirms each permutation has the same logical set.

### What to look for

1. greedy outputs can flip across permutations.
2. in sampling mode, `P(salmon)` varies by permutation.
3. effect size is measured as `max(P(salmon)) - min(P(salmon))`.

This isolates order effects from pure logical content.

## Reproducible Setup (GH200 / CUDA Recommended)

### Recommended path

```bash
bash scripts/setup_tc70_env.sh
```

What this script does:

1. creates `~/venvs/tc70`
2. installs pinned CUDA/Python dependencies
3. registers kernel `Python (tc70-70b)`
4. prints a version sanity check

### Manual fallback

```bash
python3 -m venv ~/venvs/tc70
source ~/venvs/tc70/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install --index-url https://download.pytorch.org/whl/cu126 torch==2.10.0+cu126
python -m pip install "numpy>=1.24,<2" "transformers==4.46.3" "accelerate==1.1.1" "bitsandbytes==0.49.2" huggingface_hub safetensors pandas matplotlib jupyter ipykernel
python -m ipykernel install --user --name tc70 --display-name "Python (tc70-70b)"
```

### Launch

```bash
source ~/venvs/tc70/bin/activate
jupyter lab --no-browser --port 8888
```

In Jupyter, select kernel **`Python (tc70-70b)`**.

## Notebook Run Order

For a full run:

1. setup/import cells
2. secret and question definitions
3. transcript + prompt + feasibility functions
4. `## 7a. CUDA Sanity Check`
5. `## 7. Model Loading`
6. `## 8. Inference Function`
7. run either:
   - legacy baseline sections (`## 9` to `## 12`)
   - ordering study section (`## 13` onward)

Outputs are written under `transcript_ordering_results/` (for example `runs.csv` and `config.json`).

## GitHub Pages

Pages is already wired with:

- [`.github/workflows/pages.yml`](.github/workflows/pages.yml)
- [`index.html`](index.html)
- [`.nojekyll`](.nojekyll)

One-time repo setting:

1. open **Settings -> Pages**
2. set **Source** to **GitHub Actions**

After push to `main`, deployment runs automatically.

## Troubleshooting

If GPU memory gets stuck after failed model load:

```bash
sudo nvidia-smi -pm 0
sudo systemctl stop nvidia-persistenced
sudo nvidia-smi --gpu-reset -i 0
sudo systemctl start nvidia-persistenced
sudo nvidia-smi -pm 1
nvidia-smi
```

## Practical Takeaways

- Secret declarations are reconstructed from visible transcript state.
- Constraint aggregation is path-dependent: order can change outputs even when logical feasible set is unchanged.
