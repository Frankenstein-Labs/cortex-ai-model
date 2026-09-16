from __future__ import annotations
import hashlib, json, os, platform, shutil
from dataclasses import dataclass
from pathlib import Path
from .hardware import detect_hardware
@dataclass(frozen=True)
class Shard: name:str; size_bytes:int; sha256:str; uri:str|None=None
@dataclass(frozen=True)
class ModelManifest:
    model_id:str; revision:str; license:str; source:str; total_size_bytes:int; shards:tuple[Shard,...]
    @classmethod
    def load(cls,path:Path):
        data=json.loads(path.read_text()); return cls(data['model_id'],data['revision'],data.get('license',''),data['source'],data['total_size_bytes'],tuple(Shard(**s) for s in data['shards']))
    def validate(self):
        if not self.model_id: raise ValueError('manifest must include model_id')
        if self.total_size_bytes != sum(s.size_bytes for s in self.shards): raise ValueError('total_size_bytes mismatch')
        for s in self.shards:
            if len(s.sha256)!=64 or any(c not in '0123456789abcdef' for c in s.sha256.lower()): raise ValueError(f'invalid sha256 for {s.name}')
def sha256_file(path:Path,chunk_size=1024*1024):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(chunk_size),b''): h.update(chunk)
    return h.hexdigest()
class LocalStorage:
    def __init__(self,root:Path): self.root=root
    def available_bytes(self): return shutil.disk_usage(self.root).free
    def verify(self,manifest):
        from .storage import ModelStorage
        return ModelStorage(self.root).verify(manifest)
    def clear(self):
        if self.root.exists(): shutil.rmtree(self.root)
class ModelRuntime:
    def __init__(self,model_path:Path,model_id:str,backend=None): self.model_path,self.model_id,self.backend=model_path,model_id,backend
    def health(self): return {'loaded':bool(self.backend and self.backend.health().get('loaded')),'model':self.model_id,'model_path':str(self.model_path),'backend':self.backend.health() if self.backend else None}
    def load(self):
        if not self.backend: raise RuntimeError('no model backend configured')
        self.backend.load()
    def complete(self,prompt,**kwargs):
        if not self.backend: raise RuntimeError('no model backend configured')
        from .backend import GenerationRequest
        return self.backend.generate(GenerationRequest(prompt,**kwargs))
    def stream(self,prompt,**kwargs):
        if not self.backend: raise RuntimeError('no model backend configured')
        from .backend import GenerationRequest
        return self.backend.stream(GenerationRequest(prompt,**kwargs))
def system_info(): return {'python':platform.python_version(),'platform':platform.platform(),'ram_bytes':_ram_bytes(),'disk_free_bytes':shutil.disk_usage('.').free,'hardware':detect_hardware()}
def _ram_bytes():
    try: return os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    except (ValueError,OSError): return None
