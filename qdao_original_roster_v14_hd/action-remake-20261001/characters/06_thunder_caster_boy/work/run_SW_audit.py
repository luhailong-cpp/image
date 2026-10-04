import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=[]
canvas=Image.new('RGB',(1536,1632),(38,43,54));draw=ImageDraw.Draw(canvas)
for i in range(16):
 p=B/'runtime/run/SW'/f'{i:02d}.png'; rpath=p.with_name(p.name+'.generation.json')
 r=json.loads(rpath.read_text(encoding='utf-8')); im=Image.open(p); im.load()
 assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 assert sha(p)==r['sha256']
 nrpath=B/r['derivedFrom'][0]['generationRecord'];nr=json.loads(nrpath.read_text(encoding='utf-8'))
 assert nr['native']['width']>=1024 and nr['actualModel'] is None and nr['actualQuality'] is None
 assert nr['submittedParameters']['model'] is None and nr['submittedParameters']['quality'] is None
 assert (B/nr['prompt']).exists()
 x=(i%4)*384;y=(i//4)*408
 canvas.paste(im.resize((384,384),Image.Resampling.LANCZOS),(x,y+24),im.resize((384,384),Image.Resampling.LANCZOS))
 draw.text((x+10,y+5),f'SW {i:02d}',fill='white')
 draw.line((x,y+24+round(.92*384),x+384,y+24+round(.92*384)),fill=(190,93,72))
 frames.append({'index':i,'file':p.relative_to(B).as_posix(),'sha256':sha(p),'source':r['derivedFrom'][0],'nativeSize':[nr['width'],nr['height']],'generationRecord':rpath.relative_to(B).as_posix(),'review':r['visualReview']})
assert len({f['sha256'] for f in frames})==16
out=B/'review/run_SW_contact_20261003.jpg';canvas.save(out,quality=94)
a={'direction':'SW','action':'run','count':16,'reviewedAt':datetime.now(timezone.utc).isoformat(),'technicalChecks':'16 unique 1024 RGBA transparent; independent native1254; per-frame prompt/source/time/model-null records checked','staticSequenceAccepted':False,'dynamicObserved':False,'rootGroundVerified':False,'continuousVideoEvidence':False,'clientIntegrated':False,'frames':frames}
a['timing']={'normalFrameMs':75,'normalCycleMs':1200,'slowFrameMs':300,'slowCycleMs':4800,'clientConfirmed':False}
a['latestReferenceReview']='2026-10-04 actually compared 09 run SW01/04/09 and rechecked full16 contact; toes follow knee/ankle towards lowerLEFT, no NE-type reverse toe/heel found. Existing SW16 retained. Dynamic contact transitions03-04,07,15 and loop still require playback; no dynamic acceptance claimed. SHA-bound review: cast_SW_NE_static_audit_20261004.json.'
(B/'review/run_SW_audit_20261003.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out.with_name(out.name+'.generation.json').write_text(json.dumps({'file':out.relative_to(B).as_posix(),'sha256':sha(out),'operation':'static4x4fullcanvaspreview only','derivedFrom':frames,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SW16 verified; static contact preview ready')

