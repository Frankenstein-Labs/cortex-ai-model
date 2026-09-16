from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pathlib import Path
from .core import ModelRuntime
from .backend import BackendUnavailable

app=FastAPI(title='CORTEX AI',version='0.2.0')
runtime=ModelRuntime(Path('models/deepseek-v4-pro'),'deepseek-ai/DeepSeek-V4-Pro')
class Completion(BaseModel):
    model:str; prompt:str=Field(min_length=1); max_tokens:int=Field(default=128,gt=0,le=8192); temperature:float=Field(default=.2,ge=0,le=2); stream:bool=False
class ChatMessage(BaseModel): role:str; content:str=Field(min_length=1)
class ChatCompletion(BaseModel):
    model:str; messages:list[ChatMessage]=Field(min_length=1); max_tokens:int=Field(default=128,gt=0,le=8192); temperature:float=Field(default=.2,ge=0,le=2); stream:bool=False

def check_model(model):
    if model != runtime.model_id: raise HTTPException(404,detail={'error':{'type':'model_not_found','message':f'unknown model: {model}'}})
def backend_error(exc): raise HTTPException(503,detail={'error':{'type':'backend_unavailable','message':str(exc)}})
@app.get('/health')
def health(): return {'status':'ok','runtime':runtime.health()}
@app.get('/ready')
def ready():
    if not runtime.health()['loaded']: raise HTTPException(503,detail={'error':{'type':'model_not_loaded','message':'verified weights and a loaded backend are required'}})
    return {'status':'ready'}
@app.get('/v1/models')
def models(): return {'object':'list','data':[{'id':runtime.model_id,'object':'model','owned_by':'deepseek-ai'}]}
def sse(events):
    for event in events: yield f'data: {event}\n\n'
@app.post('/v1/completions')
def completions(req:Completion):
    check_model(req.model)
    try:
        if req.stream: return StreamingResponse(sse(runtime.stream(req.prompt,max_tokens=req.max_tokens,temperature=req.temperature)),media_type='text/event-stream')
        text=runtime.complete(req.prompt,max_tokens=req.max_tokens,temperature=req.temperature)
        return {'id':'cortex-completion','object':'text_completion','model':req.model,'choices':[{'index':0,'text':text,'finish_reason':'stop'}]}
    except (BackendUnavailable, RuntimeError) as exc: backend_error(exc)
@app.post('/v1/chat/completions')
def chat(req:ChatCompletion):
    check_model(req.model); prompt='\n'.join(f'{m.role}: {m.content}' for m in req.messages)
    try:
        if req.stream: return StreamingResponse(sse(runtime.stream(prompt,max_tokens=req.max_tokens,temperature=req.temperature)),media_type='text/event-stream')
        text=runtime.complete(prompt,max_tokens=req.max_tokens,temperature=req.temperature)
        return {'id':'cortex-chat','object':'chat.completion','model':req.model,'choices':[{'index':0,'message':{'role':'assistant','content':text},'finish_reason':'stop'}]}
    except (BackendUnavailable, RuntimeError) as exc: backend_error(exc)
