# Storage

`ModelStorage` constrains shard names to a single cache directory, rejects traversal and symlink escape, verifies complete files, supports `.part` resume files, retries with exponential backoff, and exposes cache metadata. Hugging Face is the first provider; S3-compatible, R2, MinIO, and local providers can implement the same interface.
