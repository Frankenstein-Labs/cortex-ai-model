from pathlib import Path
import json, typer
from .core import ModelManifest, system_info
from .storage import HuggingFaceStorage, StorageError
app=typer.Typer(help='CORTEX AI model runtime foundation'); model=typer.Typer(); dataset=typer.Typer(); train=typer.Typer(); app.add_typer(model,name='model'); app.add_typer(dataset,name='dataset'); app.add_typer(train,name='train')

def manifest(path): m=ModelManifest.load(path); m.validate(); return m
@model.command('info')
def model_info(manifest_path:Path=typer.Option(Path('model-manifest.json'),'--manifest')):
    m=manifest(manifest_path); typer.echo(json.dumps({'model_id':m.model_id,'revision':m.revision,'license':m.license,'total_size_bytes':m.total_size_bytes,'shards':len(m.shards)},indent=2))
@model.command('list')
def model_list(cache:Path=Path('models')): typer.echo(json.dumps(HuggingFaceStorage(cache).metadata(),indent=2))
@model.command('verify')
def model_verify(manifest_path:Path=typer.Option(Path('model-manifest.json'),'--manifest'),cache:Path=Path('models')):
    missing=HuggingFaceStorage(cache).verify(manifest(manifest_path)); typer.echo(json.dumps({'valid':not missing,'missing':missing},indent=2)); raise typer.Exit(1 if missing else 0)
@model.command('delete')
def model_delete(name:str,cache:Path=Path('models')): HuggingFaceStorage(cache).delete(name); typer.echo(f'deleted {name}')
@model.command('download')
def model_download(manifest_path:Path=typer.Option(Path('model-manifest.json'),'--manifest'),cache:Path=Path('models')):
    m=manifest(manifest_path); typer.echo(f'required bytes: {m.total_size_bytes}; cache free: {HuggingFaceStorage(cache).available_space()}')
    if not typer.confirm('Proceed with explicit download?'): raise typer.Abort()
    for shard in m.shards: typer.echo(f'downloading {shard.name}'); HuggingFaceStorage(cache).download(shard)
@app.command('system-info')
def system_info_cmd(): typer.echo(json.dumps(system_info(),indent=2))
@app.command('run')
def run(model_path:Path=typer.Option(...),device:str='auto',backend:str='vllm'): typer.echo(f'backend={backend} model={model_path} device={device}; load requires installed GPU backend and verified weights')
@app.command('serve')
def serve(host:str='127.0.0.1',port:int=8000):
    import uvicorn; uvicorn.run('cortex_ai.api:app',host=host,port=port)
@dataset.command('validate')
def dataset_validate(path:Path):
    from .dataset import validate_jsonl; errors=validate_jsonl(path); typer.echo(json.dumps({'valid':not errors,'errors':errors},indent=2)); raise typer.Exit(1 if errors else 0)
@dataset.command('build')
def dataset_build(input_path:Path,output_path:Path):
    from .dataset import build_dataset; typer.echo(f'wrote {build_dataset(input_path,output_path)} examples')
@train.command('sft')
def train_sft(): raise typer.ClickException('training backend unavailable: install the selected GPU training dependencies and provide a verified base model')
@train.command('lora')
def train_lora(): raise typer.ClickException('training backend unavailable: install PEFT/Transformers and provide a compatible GPU')
@train.command('qlora')
def train_qlora(): raise typer.ClickException('training backend unavailable: install bitsandbytes/PEFT/Transformers and provide a compatible GPU')
@app.command('evaluate')
def evaluate(): raise typer.ClickException('evaluation datasets and a loaded model backend are required; no score is fabricated')
if __name__=='__main__': app()
