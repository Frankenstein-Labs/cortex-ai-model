# GPU deployment

The development environment has no NVIDIA runtime or Docker daemon, so full-model loading is not tested here. On a compatible host: install the pinned runtime, download and verify the manifest, inspect GPU/VRAM/CUDA/compute capability and free disk, mount the cache, configure vLLM or SGLang, start the API, then run evaluation. Do not infer sufficiency from activated parameter count alone; total weights, precision, KV cache, context length, and runtime overhead matter.
