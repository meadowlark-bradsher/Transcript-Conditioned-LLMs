#!/usr/bin/env bash
set -euo pipefail

# Reproducible environment bootstrap for transcript_conditioning_demo.ipynb
# Tested target: GH200-class host with NVIDIA driver/CUDA runtime available.

VENV_DIR="${VENV_DIR:-$HOME/venvs/tc70}"
KERNEL_NAME="${KERNEL_NAME:-tc70}"
KERNEL_DISPLAY_NAME="${KERNEL_DISPLAY_NAME:-Python (tc70-70b)}"
CUDA_INDEX_URL="${CUDA_INDEX_URL:-https://download.pytorch.org/whl/cu126}"

echo "Creating virtual environment at: $VENV_DIR"
python3 -m venv "$VENV_DIR"

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing CUDA-enabled PyTorch..."
python -m pip install --index-url "$CUDA_INDEX_URL" torch==2.10.0+cu126

echo "Installing pinned notebook dependencies..."
python -m pip install \
  "numpy>=1.24,<2" \
  "transformers==4.46.3" \
  "accelerate==1.1.1" \
  "bitsandbytes==0.49.2" \
  huggingface_hub \
  safetensors \
  pandas \
  matplotlib \
  jupyter \
  ipykernel

echo "Registering Jupyter kernel: $KERNEL_NAME ($KERNEL_DISPLAY_NAME)"
python -m ipykernel install --user --name "$KERNEL_NAME" --display-name "$KERNEL_DISPLAY_NAME"

echo "Running environment verification..."
python - <<'PY'
import torch
import transformers
import accelerate
import bitsandbytes

print("torch:", torch.__version__)
print("torch cuda runtime:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
print("transformers:", transformers.__version__)
print("accelerate:", accelerate.__version__)
print("bitsandbytes:", bitsandbytes.__version__)
PY

cat <<'EOF'

Done.

Next steps:
1) Launch Jupyter from this env:
   source "$HOME/venvs/tc70/bin/activate"
   jupyter lab --no-browser --port 8888

2) In Jupyter, select kernel: "Python (tc70-70b)".
3) Run transcript_conditioning_demo.ipynb from top to bottom.
EOF

