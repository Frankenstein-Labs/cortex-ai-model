# CORTEX AI

CORTEX AI is a model-agnostic foundation for a programming and reasoning system. This repository combines **CORTEX-owned runtime, storage, serving, dataset, evaluation, and permission boundaries** with the independently published **DeepSeek-V4-Pro** model reference. It is not a wrapper that embeds or republishes model weights.

## Current status

The official model card identifies DeepSeek-V4-Pro as a 1.6T-parameter MoE model with 49B activated parameters and a 1M-token context. The model card is marked MIT and points to Hugging Face and ModelScope artifacts. The weights are intentionally not committed, downloaded, or placed in Docker images. The repository manifest is metadata-only until an approved immutable upstream revision and complete shard inventory are recorded; CI does **not** claim to load or serve the full model.

## Quick start

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
cortex-ai model info
cortex-ai model verify
cortex-ai system-info
pytest
```

For a GPU deployment, set `HF_TOKEN` in the environment, obtain the exact approved model revision from the official source, populate a real manifest with verified shard sizes and SHA-256 values, download into a mounted cache with `cortex-ai model download`, verify it, then configure vLLM or SGLang as the backend. Never place credentials in Git.

## API

`cortex-ai serve` starts FastAPI endpoints at `/health`, `/ready`, `/v1/models`, `/v1/completions`, and `/v1/chat/completions`. `/ready` remains unavailable until a real inference backend is configured. The API shape is OpenAI-compatible where appropriate.

## Dataset and training boundary

Dataset examples are JSONL records with `instruction`, `context`, `input`, `output`, `tests`, `result`, and a review status. Only passed, reviewed/approved records are emitted by `dataset build`. SFT and LoRA commands are explicit preparation notices and never launch expensive training implicitly.

## Attribution and licensing

DeepSeek-V4-Pro is an upstream artifact. CORTEX code is separate and is licensed under Apache-2.0 in this repository. Confirm the upstream model, code, kernel, and runtime licenses before redistribution; do not copy third-party code without a compatible license.

See `docs/` for architecture, weights, GPU deployment, security, training, evaluation, and development notes.
