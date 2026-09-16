import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cortex_ai.api import app
from cortex_ai.core import ModelManifest
from cortex_ai.storage import ModelStorage, StorageError

def test_metadata_manifest_is_explicitly_valid():
    m=ModelManifest.load(Path('model-manifest.json')); m.validate(); assert not m.shards

def test_path_traversal_is_rejected(tmp_path):
    storage=ModelStorage(tmp_path)
    for name in ('../escape', '/etc/passwd', 'nested/file'):
        with pytest.raises(StorageError): storage.path(name)

def test_unknown_model_is_rejected():
    response=TestClient(app).post('/v1/completions',json={'model':'other','prompt':'hello'})
    assert response.status_code == 404

def test_backend_unavailable_is_clean_error():
    response=TestClient(app).post('/v1/completions',json={'model':'deepseek-ai/DeepSeek-V4-Pro','prompt':'hello'})
    assert response.status_code == 503
    assert response.json()['detail']['error']['type'] == 'backend_unavailable'

def test_streaming_without_backend_is_not_faked():
    response=TestClient(app).post('/v1/completions',json={'model':'deepseek-ai/DeepSeek-V4-Pro','prompt':'hello','stream':True})
    assert response.status_code == 503
