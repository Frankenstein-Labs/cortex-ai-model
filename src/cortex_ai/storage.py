from __future__ import annotations
import hashlib, json, os, time
from pathlib import Path
from urllib.request import Request, urlopen
from .core import ModelManifest, Shard, sha256_file

class StorageError(RuntimeError): pass
class InsufficientSpace(StorageError): pass

def safe_name(name: str) -> str:
    p = Path(name)
    if not name or p.is_absolute() or '..' in p.parts or p.name != name or name in {'.', '..'}:
        raise StorageError(f'unsafe shard name: {name!r}')
    return name

class ModelStorage:
    def __init__(self, root: Path): self.root = root.resolve(); self.root.mkdir(parents=True, exist_ok=True)
    def path(self, name: str) -> Path:
        safe_name(name); out=(self.root/name).resolve()
        if out.parent != self.root: raise StorageError('path escapes model cache')
        if out.exists() and out.is_symlink(): raise StorageError('symlink shard is not allowed')
        return out
    def exists(self, shard: Shard) -> bool:
        p=self.path(shard.name); return p.is_file() and p.stat().st_size == shard.size_bytes and sha256_file(p) == shard.sha256
    def verify(self, manifest: ModelManifest) -> list[str]: return [s.name for s in manifest.shards if not self.exists(s)]
    def list(self) -> list[str]: return sorted(p.name for p in self.root.iterdir() if p.is_file() and not p.name.endswith('.part'))
    def available_space(self) -> int: return os.statvfs(self.root).f_bavail * os.statvfs(self.root).f_frsize
    def delete(self, name: str) -> None: self.path(name).unlink(missing_ok=True)
    def metadata(self) -> dict: return {'root': str(self.root), 'files': self.list(), 'available_space_bytes': self.available_space()}
    def download(self, shard: Shard, *, retries: int = 3, timeout: int = 60) -> Path:
        if not shard.uri: raise StorageError(f'no URI for shard {shard.name}')
        target=self.path(shard.name)
        if self.exists(shard): return target
        if self.available_space() < shard.size_bytes: raise InsufficientSpace(f'need {shard.size_bytes} bytes, have {self.available_space()}')
        part=target.with_name(target.name+'.part'); start=part.stat().st_size if part.exists() else 0
        for attempt in range(retries):
            try:
                headers={'Range': f'bytes={start}-'} if start else {}
                with urlopen(Request(shard.uri, headers=headers), timeout=timeout) as response, part.open('ab') as out:
                    while chunk := response.read(1024*1024): out.write(chunk)
                if part.stat().st_size != shard.size_bytes: raise StorageError(f'size mismatch for {shard.name}')
                if sha256_file(part) != shard.sha256: raise StorageError(f'checksum mismatch for {shard.name}')
                part.replace(target); return target
            except Exception as exc:
                if attempt == retries-1: raise StorageError(f'download failed for {shard.name}: {exc}') from exc
                time.sleep(2 ** attempt)
        raise StorageError('unreachable')

class HuggingFaceStorage(ModelStorage):
    def __init__(self, root: Path, token: str | None = None):
        super().__init__(root); self.token=token or os.getenv('HF_TOKEN')
    def metadata(self) -> dict:
        data=super().metadata(); data['provider']='huggingface'; data['authenticated']=bool(self.token); return data
