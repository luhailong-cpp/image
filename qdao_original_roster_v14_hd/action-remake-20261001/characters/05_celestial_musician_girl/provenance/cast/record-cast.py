from pathlib import Path
from PIL import Image
import hashlib, json, sys
base=Path(__file__).resolve().parents[2]
stem=sys.argv[1]
direction=sys.argv[2]
frame=int(sys.argv[3])
version=sys.argv[4]
source=Path(sys.argv[5])
dest=base/'staging'/'cast'/f'{direction}-{frame:02d}-{version}.png'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_bytes(source.read_bytes())
request=json.loads((base/'provenance'/'cast'/f'{stem}.request.json').read_text(encoding='utf-8-sig'))
receipt=json.loads((base/'provenance'/'cast'/f'{stem}.tool-result.json').read_text(encoding='utf-8-sig'))
im=Image.open(dest)
a=im.getchannel('A') if im.mode=='RGBA' else None
references=[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'actuallyViewed':True,'actuallySubmitted':True,'purpose':['directional idle strict camera and scale','identity costume instrument details, not camera','approved main hand-painted style'][i]} for i,p in enumerate(request['args']['referenced_image_paths'])]
record={'schemaVersion':1,'file':dest.relative_to(base).as_posix(),'sourcePath':str(source),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'generatedAtUTC':receipt['finishedAtUTC'],'nativeWidth':im.width,'nativeHeight':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':a.getextrema() if a else None,'alphaBBox':a.getbbox() if a else None,'status':'generated_pending_visual_review','slot':{'action':'cast','direction':direction,'frame':frame,'totalPerDirection':16,'durationMs':45},'tool':'image_gen__imagegen','route':'builtin','configSnapshot':request['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**request['args']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未提供model/quality选择器且未披露实际型号与质量。','prompt':f'provenance/cast/{stem}.prompt.txt','evidence':{'request':f'provenance/cast/{stem}.request.json','receipt':f'provenance/cast/{stem}.tool-result.json'},'references':references,'visualReview':{'reviewed':False,'passed':False},'export':{'completed':False,'targetSize':[1024,1024],'method':'pending global baseline, full-canvas uniform scaling only','virtualRoot':[512,942],'pivot':[0.5,0.08]}}
(base/'provenance'/'cast'/f'{stem}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'width':im.width,'height':im.height,'sha256':record['sha256']},ensure_ascii=False))

