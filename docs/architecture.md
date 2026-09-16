# Architecture

CORTEX separates model-specific integration from model-independent orchestration. Storage and manifest verification precede runtime loading; serving exposes a stable API; dataset and evaluation pipelines remain separate from inference. Future Engine, IDE, and Cloud clients should depend on the API and permission contracts rather than DeepSeek internals.

The initial runtime has a local-storage abstraction and an explicit backend boundary for vLLM/SGLang. Agent roles, memory, tools, sessions, and permissions are reserved as separate modules rather than presented as implemented capabilities.
