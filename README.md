# LLMs Don't Keep Secrets

Controlled experiments on transcript-conditioned reasoning and transcript-order effects in LLMs.

## Overview

This repo contains two experiments:

1. **Transcript reconstruction**: the model declares different secrets based only on transcript content.
2. **Transcript ordering effect**: with the same logical feasible set, changing Q/A order changes model outputs.

Primary notebook: [`transcript_conditioning_demo.ipynb`](transcript_conditioning_demo.ipynb)

## Repo Contents

- [`transcript_conditioning_demo.ipynb`](transcript_conditioning_demo.ipynb): main notebook (legacy + ordering study).
- [`transcript_conditioning_demo-executed.ipynb`](transcript_conditioning_demo-executed.ipynb): executed reference.
- [`transcript_bubbles.html`](transcript_bubbles.html): visual walkthrough.
- [`scripts/setup_tc70_env.sh`](scripts/setup_tc70_env.sh): reproducible environment bootstrap.
- [`spec.md`](spec.md), [`20q-spec.md`](20q-spec.md): task/domain specs.

## Experiment 1: Transcript Reconstruction

**Question**  
Does a model keep a hidden committed secret, or infer the secret from the visible transcript?

**Design**

- Secret space: 6 animals.
- Each secret is an 8-feature binary vector.
- One synthetic transcript per secret.
- Model is not part of the original conversation; it only sees transcript text.

**Reference result (Llama-3.1-70B-Instruct)**

| Transcript implies | Model declared | Match |
|---|---|---|
| cat | cat | ✓ |
| dog | dog | ✓ |
| eagle | eagle | ✓ |
| salmon | salmon | ✓ |
| shark | shark | ✓ |
| crocodile | crocodile | ✓ |

**Outcome**: 6/6 correct.  
Contradictory transcript (no feasible secret) leads to conflict/error-style response, not a stable hidden secret reveal.

## Experiment 2: Transcript Ordering Effect

**Question**  
If logical content is held constant, does the order of constraints still change predictions?

**Design**

- Candidate list reduced to 5 animals.
- Chosen transcript has feasible set exactly `{salmon, shark}`.
- Use 3 Q/A constraints and test all `3! = 6` orderings.
- Feasible set remains identical for all permutations.

**Observed pattern**

- Greedy decoding can flip by permutation.
- Sampling (`n=40` per permutation) shows large shifts in `P(salmon)` across permutations.
- In the reference run, range `max(P(salmon)) - min(P(salmon)) = 0.50 (max 1.00, min 0.50)`.

# Takeaways

- LLM secret declarations are reconstructed from transcript state.
- Transcript constraint aggregation is path-dependent (order-sensitive), not purely order-invariant logical conjunction.

## Reproducible Setup (>= 80GB Recommended)

### Fast path (recommended)

```bash
bash scripts/setup_tc70_env.sh
```

This creates `~/venvs/tc70`, installs pinned versions, and registers kernel `Python (tc70-70b)`.

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

In Jupyter, pick kernel **`Python (tc70-70b)`**.

## Run Order in Notebook

1. Run setup + imports + secret definitions.
2. Run **`## 7a. CUDA Sanity Check`** (must pass).
3. Run **`## 7. Model Loading`**.
4. Run **`## 8. Inference Function`**.
5. For ordering study, run **`## 13. Transcript Ordering Effect Study`** section cells.

Outputs are written under `transcript_ordering_results/` (including `runs.csv` and `config.json`).

## Troubleshooting

If GPU memory appears stuck after a failed load:

```bash
sudo nvidia-smi -pm 0
sudo systemctl stop nvidia-persistenced
sudo nvidia-smi --gpu-reset -i 0
sudo systemctl start nvidia-persistenced
sudo nvidia-smi -pm 1
nvidia-smi
```
