from pathlib import Path
import json,hashlib
from PIL import Image
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
for n in [6,7]:
 slot=f'cast-W-{n:02}'
 old=root/(slot+'.png'); oldr=Path(str(old)+'.generation.json')
 new=root/(slot+'-margin-v2.png'); newr=Path(str(new)+'.generation.json')
 if not new.exists(): continue
 hist=json.loads(oldr.read_text(encoding='utf-8'))
 hist['review']={'status':'superseded','reason':'spear tip clipped at top; corrected by margin-v2'}
 hist['imageRetention']='old local PNG removed after replacement and metadata verified'
 (root/'rejected'/f'{slot}-margin-v1.png.generation.json').write_text(json.dumps(hist,ensure_ascii=False,indent=2),encoding='utf-8')
 rec=json.loads(newr.read_text(encoding='utf-8'));rec['file']=slot+'.png'
 rec['derivedFromEdit']={'file':slot+'.png','sha256':hist['sha256'],'record':'rejected/'+slot+'-margin-v1.png.generation.json'}
 rec['review']={'status':'candidate','marginRepair':'passed static: complete spear tip and transparent top margin','dynamic':'unverified'}
 old.write_bytes(new.read_bytes());oldr.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 new.unlink();newr.unlink()
entries=[]
for p in sorted(root.glob('cast-?-??.png')):
 im=Image.open(p);r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
 entries.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'record':p.name+'.generation.json','nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':list(im.getchannel('A').getextrema()),'bboxAlpha':list(im.getchannel('A').getbbox()),'review':r.get('review')})
status={'updatedAt':datetime.now(timezone.utc).isoformat(),'action':'cast','expected':32,'presentCandidateCount':len(entries),'missing':[],'formalExportCount':0,'visualPassedCount':0,'dynamicPassedCount':0,'frameDurationMs':45,'durationMs':720,'releaseFrame':9,'targetRootAnchor':[512,942],'targetCanvas':[1024,1024],'generationRoute':'builtin','actualModel':None,'actualQuality':None,'status':'all native slots available; sequence registration and continuity still need work','reviewSummary':['All32 inspected in full-canvas contacts, original frames viewed during generation; identity, two hands, spear and two boots generally readable.','W06/W07 clipped spear tips replaced by targeted AI edits; source pixels verified present before cleanup.','E04 narrow/standing pose between crouched E03 and wider E05 causes stance discontinuity. E07-to-E08 transition abruptly extends; W07-to-W08 lowers spear quickly.','Multiple frames have head/body scale and position variations. No per-frame bbox scaling or lowest-foot snapping applied. Need fixed-direction registration and native pose edits where necessary.','No full-speed browser or client playback approval; contacts alone cannot establish dynamic pass.'],'entries':entries,'client':'not integrated'}
(root/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'present':len(entries),'W06top':next(e for e in entries if e['file']=='cast-W-06.png')['bboxAlpha'][1],'W07top':next(e for e in entries if e['file']=='cast-W-07.png')['bboxAlpha'][1]}))

