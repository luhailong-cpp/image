import json,hashlib,sys
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[2]
group=root/'provenance/run-south'
key=sys.argv[1]
d,f=key.split('-')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=json.loads((group/(key+'.receipt.json')).read_text(encoding='utf-8'))
request=json.loads((group/(key+'.request.json')).read_text(encoding='utf-8'))
src=Path(receipt['nativeSourcePath'])
im=Image.open(src)
assert min(im.size)>=1024 and im.mode=='RGBA', (im.size,im.mode)
nativeSize=list(im.size); nativeSha=sha(src)
out=root/f'runtime/run/{d}/{f}.png';out.parent.mkdir(parents=True,exist_ok=True)
pixels=np.array(im.resize((1024,1024),Image.Resampling.LANCZOS))
noise=pixels[:,:,3]<=2
cleaned=int(noise.sum())
pixels[noise]=0
Image.fromarray(pixels,'RGBA').save(out)
assert Image.open(out).getchannel('A').getextrema()[0]==0
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
record={'file':out.relative_to(root).as_posix(),'sha256':sha(out),'generatedAt':receipt['completedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':request['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':receipt['unverifiedReason'],'evidence':{'receipt':f'provenance/run-south/{key}.receipt.json','request':f'provenance/run-south/{key}.request.json'},'prompt':request['prompt'],'references':[{'path':p,'purpose':'direction identity and camera' if i==0 else 'approved main drawing style'} for i,p in enumerate(request['referenced_image_paths'])],'width':1024,'height':1024,'nativeSize':nativeSize,'format':'PNG','derivedFrom':{'path':str(src),'sha256':nativeSha,'nativeSize':nativeSize},'operation':'Uniform resize entire canvas to 1024x1024 using Lanczos; no bbox crop, anchoring shift, mirroring, deformation or interpolation.'}
record['alphaNoiseCleanup']={'thresholdInclusive':2,'operation':'Set all RGBA channels to zero only for alpha<=2; preserve all pixels with alpha>2','pixelsCleared':cleaned}
recordpath=group/(key+'.generation.json');write(recordpath,record)
selection=root/'selection/run-south.json';data=json.loads(selection.read_text(encoding='utf-8')) if selection.exists() else {'frames':[]}
data['frames']=[x for x in data['frames'] if not(x['direction']==d and x['frame']==int(f))]
data['frames'].append({'action':'run','direction':d,'frame':int(f),'file':record['file'],'sha256':sha(out),'generationRecord':recordpath.relative_to(root).as_posix(),'generationRecordSha256':sha(recordpath),'sourceNativeSize':nativeSize})
write(selection,data)
print(json.dumps({'file':str(out),'nativeSize':nativeSize,'nativeSha256':nativeSha,'sha256':sha(out)},ensure_ascii=False))
