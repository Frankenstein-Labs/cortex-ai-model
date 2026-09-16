from __future__ import annotations
import importlib.util, shutil, subprocess

def detect_hardware() -> dict:
    result={'cuda_available':False,'gpu_available':False,'gpu_count':0,'gpus':[],'cuda_version':None,'driver':None}
    if importlib.util.find_spec('torch'):
        import torch
        result['cuda_available']=bool(torch.cuda.is_available()); result['gpu_available']=result['cuda_available']; result['gpu_count']=torch.cuda.device_count()
        result['cuda_version']=getattr(torch.version,'cuda',None)
        for i in range(result['gpu_count']):
            props=torch.cuda.get_device_properties(i)
            result['gpus'].append({'index':i,'name':props.name,'vram_total_bytes':props.total_memory,'compute_capability':f'{props.major}.{props.minor}'})
    elif shutil.which('nvidia-smi'):
        try:
            out=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader,nounits'], text=True, timeout=5)
            for i,line in enumerate(out.strip().splitlines()):
                name,mem,driver=[x.strip() for x in line.split(',')]; result['gpus'].append({'index':i,'name':name,'vram_total_mib':int(mem),'driver':driver})
            result.update(gpu_available=bool(result['gpus']), gpu_count=len(result['gpus']), driver=result['gpus'][0].get('driver') if result['gpus'] else None)
        except Exception: pass
    return result
