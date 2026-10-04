from pathlib import Path
from PIL import Image
import hashlib,json,sys,datetime
ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/'provenance/run-north'
direction,frame,attempt,source=sys.argv[1:]
frame=int(frame);attempt=int(attempt)
stem=f'run-{direction}-{frame:02d}-attempt-{attempt}'
request=json.loads((PROV/(stem+'.request.json')).read_text(encoding='utf-8-sig'))
src=Path(source)
native_sha=hashlib.sha256(src.read_bytes()).hexdigest()
im=Image.open(src);native=im.size
if min(native)<1024: raise ValueError('Native frame is below 1024')
if im.mode!='RGBA':raise ValueError('Missing native RGBA')
if im.getchannel('A').getextrema()[0]!=0:raise ValueError('No transparent pixels')
im.paste((0,0,0,0),(0,0),im.getchannel('A').point(lambda a:255 if a<=2 else 0))
out=ROOT/f'runtime/run/{direction}/{frame:02d}.png';out.parent.mkdir(parents=True,exist_ok=True)
im=im.resize((1024,1024),Image.Resampling.LANCZOS)
im.paste((0,0,0,0),(0,0),im.getchannel('A').point(lambda a:255 if a<=2 else 0))
im.save(out)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
rec=PROV/(stem+'.generation.json')
record={
 'file':out.relative_to(ROOT).as_posix(),'sha256':sha,'generatedAt':request['requestedAt'],
 'tool':'image_gen','route':'builtin','configSnapshot':request['configSnapshot'],
 'submittedParameters':request['submittedParameters'],'actualModel':None,'actualQuality':None,
 'unverifiedReason':'宿主管理，工具无型号/质量选择器，返回未披露型号与质量。',
 'evidence':{'request':f'provenance/run-north/{stem}.request.json','receipt':f'provenance/run-north/{stem}.receipt.json'},
 'prompt':f'provenance/run-north/{stem}.request.json',
 'references':request.get('referenceMetadata',[{'file':x,'role':['角色身份与相机参考','已确认画法样板','跑姿连续性参考'][min(i,2)]} for i,x in enumerate(request['submittedParameters']['referenced_image_paths'])]),
 'width':1024,'height':1024,'nativeSize':list(native),'sourceNativeSize':list(native),'format':'PNG/RGBA',
 'derivedFrom':{'file':str(src),'sha256':native_sha,'width':native[0],'height':native[1],'generationReceipt':f'provenance/run-north/{stem}.receipt.json'},
 'operation':'Native alpha<=2 pixels set RGBA=0, then whole-canvas 1024x1024 Lanczos resize, then alpha<=2 reset RGBA=0; no crop, bbox normalization, ground alignment, mirroring or pose interpolation.',
 'alphaNoiseCleanup':{'thresholdInclusive':2,'stage':'native-and-after-whole-canvas-resize','rgbReset':True,'higherAlphaPixelsChanged':False},
 'sourceRetention':'Host native image remains pending final reference cleanup; project selected PNG is this whole-canvas derivative.'}
rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
selection=ROOT/'selection/run-north.json'
data=json.loads(selection.read_text(encoding='utf8')) if selection.exists() else {'frames':[]}
data['frames']=[x for x in data['frames'] if (x['direction'],x['frame'])!=(direction,frame)]
data['frames'].append({'action':'run','direction':direction,'frame':frame,'file':record['file'],'sha256':sha,'generationRecord':rec.relative_to(ROOT).as_posix(),'generationRecordSha256':hashlib.sha256(rec.read_bytes()).hexdigest(),'sourceNativeSize':list(native)})
data['frames'].sort(key=lambda x:(x['direction'],x['frame']))
selection.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'file':str(out),'sha256':sha,'nativeSize':native,'alpha_bbox':im.getchannel('A').getbbox()},ensure_ascii=False))
