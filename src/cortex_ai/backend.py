from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

class BackendUnavailable(RuntimeError): pass
class ModelNotLoaded(RuntimeError): pass
@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    max_tokens: int = 128
    temperature: float = 0.2

class ModelBackend(ABC):
    @abstractmethod
    def load(self) -> None: ...
    @abstractmethod
    def unload(self) -> None: ...
    @abstractmethod
    def health(self) -> dict: ...
    @abstractmethod
    def generate(self, request: GenerationRequest) -> str: ...
    def stream(self, request: GenerationRequest) -> Iterator[str]:
        yield self.generate(request)
    def chat(self, messages: list[dict], **kwargs) -> str:
        return self.generate(GenerationRequest('\n'.join(f"{m['role']}: {m['content']}" for m in messages), **kwargs))

class UnavailableBackend(ModelBackend):
    def __init__(self, name: str, model_path: str): self.name, self.model_path, self.loaded = name, model_path, False
    def load(self) -> None: raise BackendUnavailable(f'{self.name} is unavailable; install its GPU runtime and provide verified weights')
    def unload(self) -> None: self.loaded=False
    def health(self) -> dict: return {'backend': self.name, 'loaded': self.loaded, 'available': False, 'model_path': self.model_path}
    def generate(self, request: GenerationRequest) -> str: raise BackendUnavailable(f'{self.name} is not configured')
class VLLMBackend(UnavailableBackend):
    def __init__(self, model_path: str): super().__init__('vllm', model_path)
class SGLangBackend(UnavailableBackend):
    def __init__(self, model_path: str): super().__init__('sglang', model_path)
