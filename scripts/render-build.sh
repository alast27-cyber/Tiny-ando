#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Safety check: ensure we installed CPU-only torch on Render.
python - <<'PY'
import torch
if torch.version.cuda is not None:
    raise SystemExit(f"Expected CPU-only torch, found CUDA build: {torch.version.cuda}")
print(f"Verified CPU-only torch: {torch.__version__}")
PY
