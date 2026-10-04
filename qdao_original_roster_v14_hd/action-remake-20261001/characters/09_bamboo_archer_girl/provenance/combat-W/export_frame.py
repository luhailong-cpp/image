import json,sys,hashlib,re
from pathlib import Path
from PIL import Image
import numpy as np
base=Path(__file__).resolve().parents[2]
p=Path(sys.argv[1])
request=json.loads(p.read_text(encoding='utf-8-sig'))
receipt=json.loads(p.with_suffix('.receipt.json').read_text(encoding='utf-8-sig'))
hint=receipt['result']['output_hint']
matches=re.findall(r' as ([A-Z]:\\[^\n]+?\.png)',hint)
src=Path(matches[-1]); data=src.read_bytes(); sha=lambda b:hashlib.sha256(b).hexdigest()
slot=request['slot'];action,di,num=slot.split('/')
dest=base/'runtime'/action/di/(num+'.png'); dest.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src)
assert im.width>=1024 and im.height>=1024 and im.mode=='RGBA',(im.size,im.mode)
native=im.size
arr=np.array(im); arr[arr[:,:,3]<=2]=0
im=Image.fromarray(arr,'RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
arr=np.array(im); arr[arr[:,:,3]<=2]=0; im=Image.fromarray(arr,'RGBA'); im.save(dest)
outsha=sha(dest.read_bytes())
record={'file':dest.relative_to(base).as_posix(),'sha256':outsha,'generatedAt':receipt['returnedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':request['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**request['submittedParameters']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具无model/quality选择器且未披露实际型号、质量。','width':1024,'height':1024,'format':'PNG RGBA','sourceNativeSize':list(native),'nativeSize':list(native),'nativeCellSize':list(native),'prompt':p.relative_to(base).as_posix(),'references':request['references'],'evidence':{'toolReceipt':p.with_suffix('.receipt.json').relative_to(base).as_posix(),'actualFieldsDisclosed':[]},'derivedFrom':{'file':str(src),'sha256':sha(data),'width':native[0],'height':native[1],'generationRecord':p.with_suffix('.receipt.json').relative_to(base).as_posix()},'operation':'entire canvas uniform resize to 1024x1024 with Lanczos; no crop, bbox normalization, translation, mirroring, interpolation of animation or minimum-pixel foot alignment','slot':slot,'phase':request['phase']}
recordpath=base/'provenance'/'combat-W'/(slot.replace('/','-')+'.generation.json')
record['operation']+='; set only alpha<=2/255 pixels to RGBA zero before and after resize, preserve all alpha>2'
record['referenceMetadata']=request.get('referenceMetadata',[])
if recordpath.exists():
 old=json.loads(recordpath.read_text(encoding='utf-8')); hist=recordpath.parent/'history'; hist.mkdir(exist_ok=True)
 (hist/(recordpath.stem+'-'+old['sha256'][:12]+'.json')).write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
recordpath.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
selection=base/'selection'/'combat-W.json';selection.parent.mkdir(parents=True,exist_ok=True)
sel=json.loads(selection.read_text(encoding='utf-8')) if selection.exists() else {'frames':[]}
sel['frames']=[x for x in sel['frames'] if (x['action'],x['direction'],x['frame'])!=(action,di,int(num))]
sel['frames'].append({'action':action,'direction':di,'frame':int(num),'file':record['file'],'sha256':outsha,'generationRecord':recordpath.relative_to(base).as_posix(),'generationRecordSha256':sha(recordpath.read_bytes()),'sourceNativeSize':list(native)})
selection.write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':outsha,'nativeSize':native,'alphaExtrema':im.getchannel('A').getextrema()},ensure_ascii=False))

