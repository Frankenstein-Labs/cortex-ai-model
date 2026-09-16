# Runtime

The API depends on `ModelRuntime`, which depends on a `ModelBackend`. vLLM and SGLang adapters currently fail explicitly when their optional GPU runtimes and verified weights are absent. A production adapter must implement load, unload, health, generate, chat, and token/event streaming. The API will not report ready or fabricate completions without a loaded backend.
