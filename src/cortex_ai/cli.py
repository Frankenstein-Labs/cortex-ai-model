from pathlib import Path
import json
import typer
from .core import ModelManifest, LocalStorage, system_info

app = typer.Typer(help="CORTEX AI model runtime foundation")
model = typer.Typer(); dataset = typer.Typer(); train = typer.Typer()
app.add_typer(model, name="model"); app.add_typer(dataset, name="dataset"); app.add_typer(train, name="train")

@model.command("verify")
def model_verify(manifest: Path = Path("model-manifest.json"), cache: Path = Path("models")):
    m = ModelManifest.load(manifest); m.validate(); missing = LocalStorage(cache).verify(m)
    typer.echo(json.dumps({"valid": not missing, "missing": missing}, indent=2)); raise typer.Exit(1 if missing else 0)

@model.command("info")
def model_info(manifest: Path = Path("model-manifest.json")):
    m = ModelManifest.load(manifest); typer.echo(json.dumps({"model_id":m.model_id,"revision":m.revision,"license":m.license,"total_size_bytes":m.total_size_bytes,"shards":len(m.shards)}, indent=2))

@app.command("system-info")
def system_info_cmd(): typer.echo(json.dumps(system_info(), indent=2))

@app.command("run")
def run(model_path: Path = typer.Option(...), device: str = "auto"):
    typer.echo(f"CORTEX runtime preparation: model={model_path} device={device}; no weights loaded")

@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn
    uvicorn.run("cortex_ai.api:app", host=host, port=port)

@dataset.command("validate")
def dataset_validate(path: Path):
    from .dataset import validate_jsonl
    errors = validate_jsonl(path); typer.echo(json.dumps({"valid": not errors, "errors": errors}, indent=2)); raise typer.Exit(1 if errors else 0)

@dataset.command("build")
def dataset_build(input_path: Path, output_path: Path):
    from .dataset import build_dataset
    typer.echo(f"wrote {build_dataset(input_path, output_path)} examples")

@train.command("sft")
def train_sft(): typer.echo("SFT pipeline is prepared but requires an explicit training backend and GPU; no training launched.")

@train.command("lora")
def train_lora(): typer.echo("LoRA pipeline is prepared but requires an explicit training backend and GPU; no training launched.")

if __name__ == "__main__": app()
