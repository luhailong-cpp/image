from pathlib import Path
import json,hashlib,shutil,sys
from PIL import Image
dire=Path(sys.argv[1]); stem=sys.argv[2]
receipt=json.loads((dire/(stem+'.receipt.json')).read_text(encoding='utf8'))
request=json.loads((dire/(stem+'.request.json')).read_text(encoding='utf8'))
native=dire/(stem+'.native.png'); out=dire/(stem+'.png')
shutil.copy2(receipt['source'],native)
im=Image.open(native); size=im.size; mode=im.mode
assert min(size)>=1024 and mode=='RGBA'
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
common={'tool':'image_gen.imagegen','route':'builtin','generatedAt':receipt['generatedAt'],'configSnapshot':config,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin tool exposes neither model/quality selectors nor actual values','prompt':stem+'.prompt.txt','request':stem+'.request.json','receipt':stem+'.receipt.json','references':[{'file':p,'sha256':sha(Path(p))} for p in request['referenced_image_paths']],'outputScalePolicy':'full-canvas-to1024-no-translation'}
nr=dict(common,file=native.name,sha256=sha(native),width=size[0],height=size[1],mode=mode,format='PNG',status='candidate-pending-visual-review')
(dire/(native.name+'.generation.json')).write_text(json.dumps(nr,indent=2,ensure_ascii=False),encoding='utf8')
er=dict(common,file=out.name,sha256=sha(out),width=1024,height=1024,mode='RGBA',format='PNG',nativeSize=list(size),derivedFrom={'file':native.name,'sha256':sha(native),'generationRecord':native.name+'.generation.json'},operation='uniform full canvas resize to1024; no crop, shift, bbox normalization, grounding or mirroring',status='candidate-pending-visual-review')
(dire/(out.name+'.generation.json')).write_text(json.dumps(er,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({'out':str(out),'nativeSize':size,'sha256':sha(out)}))
