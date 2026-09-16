# Weights

Weights are external artifacts. The manifest records model identity, revision, shard names, sizes, SHA-256 hashes, and source URIs. A production manifest must contain real values supplied by the upstream release or a controlled object store. Downloads must be resumable, cached outside Git, and verified before runtime startup. Keep `original`, `adapted`, `quantized`, and `fine-tuned` versions distinct.

The repository contains only a zero-byte fixture so CI can exercise verification without downloading hundreds of gigabytes.
