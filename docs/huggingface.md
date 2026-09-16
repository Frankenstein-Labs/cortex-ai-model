# Hugging Face setup

Set `HF_TOKEN` only in the environment or a local ignored secret manager. Review the upstream model card and license, select an approved immutable revision, populate shard metadata and hashes, then run `cortex-ai model download --manifest ...`. The command reports required disk space and requires explicit confirmation; it retries resumable downloads and verifies size and SHA-256. No token is logged or committed.

The current repository manifest is metadata-only because the exact shard inventory and immutable revision must be approved before a large download.
