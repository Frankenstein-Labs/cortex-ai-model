# Deployment

CPU development runs manifest, storage, dataset, API-contract, and security tests without model weights. GPU deployment requires a supported NVIDIA driver/CUDA stack, sufficient VRAM/RAM/disk, a pinned vLLM or SGLang version, verified external weights, and mounted model cache. Docker images contain code only; weights are mounted or downloaded explicitly at runtime.
