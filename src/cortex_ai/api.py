from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core import ModelRuntime
from pathlib import Path

app=FastAPI(title="CORTEX AI", version="0.1.0")
runtime=ModelRuntime(Path("models/deepseek-v4-pro"), "deepseek-ai/DeepSeek-V4-Pro")
class Completion(BaseModel): model: str; prompt: str; max_tokens: int = 128; temperature: float = 0.2; stream: bool = False
class ChatMessage(BaseModel): role: str; content: str
class ChatCompletion(BaseModel): model: str; messages: list[ChatMessage]; max_tokens: int = 128; temperature: float = 0.2; stream: bool = False

@app.get('/health')
def health(): return {"status":"ok", "runtime": runtime.health()}
@app.get('/ready')
def ready():
    data=runtime.health()
    if not data["loaded"]: raise HTTPException(503, detail=data)
    return {"status":"ready"}
@app.get('/v1/models')
def models(): return {"object":"list", "data":[{"id":runtime.model_id,"object":"model","owned_by":"deepseek-ai"}]}
@app.post('/v1/completions')
def completions(request: Completion):
    text=runtime.complete(request.prompt, max_tokens=request.max_tokens, temperature=request.temperature)
    return {"id":"cortex-completion","object":"text_completion","model":request.model,"choices":[{"index":0,"text":text,"finish_reason":"stop"}]}
@app.post('/v1/chat/completions')
def chat(request: ChatCompletion):
    prompt="\n".join(f"{m.role}: {m.content}" for m in request.messages)
    text=runtime.complete(prompt, max_tokens=request.max_tokens, temperature=request.temperature)
    return {"id":"cortex-chat","object":"chat.completion","model":request.model,"choices":[{"index":0,"message":{"role":"assistant","content":text},"finish_reason":"stop"}]}
