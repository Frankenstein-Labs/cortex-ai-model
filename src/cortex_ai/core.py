from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class Shard:
    name: str
    size_bytes: int
    sha256: str
    uri: str | None = None

@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    revision: str
    license: str
    source: str
    total_size_bytes: int
    shards: tuple[Shard, ...]

    @classmethod
    def load(cls, path: Path) -> "ModelManifest":
        data = json.loads(path.read_text())
        shards = tuple(Shard(**item) for item in data["shards"])
        return cls(data["model_id"], data["revision"], data["license"], data["source"], data["total_size_bytes"], shards)

    def validate(self) -> None:
        if not self.model_id or not self.shards:
            raise ValueError("manifest must include model_id and at least one shard")
        if self.total_size_bytes != sum(s.size_bytes for s in self.shards):
            raise ValueError("total_size_bytes does not match shard sizes")
        for shard in self.shards:
            if len(shard.sha256) != 64 or any(c not in "0123456789abcdef" for c in shard.sha256.lower()):
                raise ValueError(f"invalid sha256 for {shard.name}")

class LocalStorage:
    def __init__(self, root: Path): self.root = root
    def path(self, name: str) -> Path: return self.root / name
    def available_bytes(self) -> int: return shutil.disk_usage(self.root).free
    def clear(self) -> None:
        if self.root.exists(): shutil.rmtree(self.root)
    def verify(self, manifest: ModelManifest) -> list[str]:
        missing = []
        for shard in manifest.shards:
            p = self.path(shard.name)
            if not p.exists() or p.stat().st_size != shard.size_bytes or sha256_file(p) != shard.sha256:
                missing.append(shard.name)
        return missing

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""): digest.update(chunk)
    return digest.hexdigest()

def system_info() -> dict[str, object]:
    return {"python": platform.python_version(), "platform": platform.platform(), "cuda": False, "gpu": None, "ram_bytes": _ram_bytes(), "disk_free_bytes": shutil.disk_usage(".").free}

def _ram_bytes() -> int | None:
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError): return None

class ModelRuntime:
    def __init__(self, model_path: Path, model_id: str): self.model_path, self.model_id = model_path, model_id
    def health(self) -> dict[str, object]: return {"loaded": False, "model": self.model_id, "model_path": str(self.model_path), "reason": "weights not loaded in test environment"}
    def complete(self, prompt: str, **_: object) -> str:
        raise RuntimeError("No local model backend is configured; install and configure vLLM/SGLang on a compatible GPU")
