import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent.parent;q=z/'qa';n=z/'native'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,o):assert not p.exists();p.write_text(json.dumps(o,indent=2),encoding='utf-8')
def prepare(stem,trace_name,box,detail):
 tr=q/trace_name;trace=json.loads(tr.read_text());coords={'r08_c04':(0,0),'r08_c05':(4096,0),'r09_c04':(0,4096),'r09_c05':(4096,4096)}
 out=np.zeros((1254,1254,3),np.uint8)
 for entry in trace['tiles']:
  tile=entry['tile'];tx,ty=coords[tile];l=max(box[0],tx);t=max(box[1],ty);r=min(box[2],tx+4096);b=min(box[3],ty+4096)
  if l<r and t<b:
   p=Path(entry['candidate']['path']);assert sha(p)==entry['candidate']['sha256'];a=np.array(Image.open(p).convert('RGB'));out[t-box[1]:b-box[1],l-box[0]:r-box[0]]=a[t-ty:b-ty,l-tx:r-tx]
 src=q/(stem+'-source-1254.png');assert not src.exists();Image.fromarray(out).save(src)
 prompt='Use case: precise-object-edit. Edit this exact native 1254x1254 daylight hand-painted game art, with no crop, resize, camera shift or framing change. '+detail+' Preserve the existing rounded Q Daoist style, quiet pale stone detail and natural daylight. No new objects, text, grid, UI, blur, sharpening or smoothing. Output native 1254x1254.'
 pp=n/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r08_c04','patch':'external_repair','prompt':pp.as_posix(),'tool':'image_gen__imagegen','route':'builtin','coordinates':{'tileContextBox':box,'globalContextBox':[12288+box[0],28672+box[1],12288+box[2],28672+box[3]],'sourceCoreBox':[115,115,1139,1139]},'references':[{'path':src.as_posix(),'sha256':sha(src),'role':'exact native current composite','dimensions':[1254,1254]}],'submittedParameters':{'transparent_background':False,'model':None,'quality':None,'referenced_image_paths':[src.as_posix()]},'actualModel':None,'baseTrace':{'path':tr.as_posix(),'sha256':sha(tr)}}
 wr(n/(stem+'.request.json'),req);wr(Path(str(src)+'.derivation.json'),{'operation':'integer core mosaic crop only, no resize','inputTrace':req['baseTrace'],'output':req['references'][0],'tileContextBox':box})
 print(json.dumps(req))
if __name__=='__main__':prepare(*json.loads(sys.argv[1]))

