import json
from pathlib import Path
from fastapi.testclient import TestClient
from cortex_ai.core import ModelManifest, LocalStorage
from cortex_ai.dataset import validate_jsonl
from cortex_ai.api import app

def test_manifest_validates():
    m=ModelManifest.load(Path('model-manifest.json')); m.validate(); assert m.model_id == 'deepseek-ai/DeepSeek-V4-Pro'

def test_checksum_verification(tmp_path):
    import hashlib
    digest=hashlib.sha256(b'').hexdigest()
    manifest=ModelManifest('test','rev','MIT','local',0,())
    shard=type('S',(),{'name':'fixture','size_bytes':0,'sha256':digest})()
    manifest=type('M',(),{'shards':(shard,)})()
    p=tmp_path/'fixture'; p.write_bytes(b'')
    assert LocalStorage(tmp_path).verify(manifest) == []
    p.write_bytes(b'bad'); assert LocalStorage(tmp_path).verify(manifest) == ['fixture']

def test_dataset_validation(tmp_path):
    p=tmp_path/'data.jsonl'; p.write_text(json.dumps({'instruction':'i','context':'c','input':'in','output':'o','tests':[],'result':'passed','status':'approved'})+'\n')
    assert validate_jsonl(p) == []

def test_api_contract():
    c=TestClient(app); assert c.get('/health').status_code == 200; assert c.get('/v1/models').json()['data'][0]['id'] == 'deepseek-ai/DeepSeek-V4-Pro'; assert c.get('/ready').status_code == 503
