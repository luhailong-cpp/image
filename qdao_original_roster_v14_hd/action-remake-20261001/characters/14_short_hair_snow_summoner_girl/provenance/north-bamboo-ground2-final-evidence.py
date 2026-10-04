import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
rec=[]
for b in [5,7]:
 for rc in read(R/'provenance'/f'north-bamboo-ground2-batch{b}-receipts.json'):
  q=rc['q'];f=q['frame'];native=R/'run/staging'/(q['id']+'.png');np=Path(str(native)+'.generation.json');nm=read(np)
  evidence=rc.get('recoveryEvidence',{})
  nm['evidence']['recoveryAssociation']=evidence
  nm['evidence']['associationCaveat']='Saved request existed before generation. Tool cell lifetime was interrupted. Exact request-to-cache mapping is confirmed only where conversation returned path survived; other matches use chronology and visual identity and remain inferred.'
  save(np,nm)
  final=R/'run/NE'/f'{f}.png';fm=read(Path(str(final)+'.generation.json'));used=fm['derivedFrom']['sha256']==sha(native)
  rec.append({'direction':'NE','frame':int(f),'request':f'provenance/{q["id"]}.request.json','receipt':f'provenance/north-bamboo-ground2-batch{b}-receipts.json','nativeFile':native.relative_to(R).as_posix(),'nativeSha256':sha(native),'hostCachePath':rc['path'],'association':evidence['association'],'selectedForCurrentFormal':used,'formalFile':final.relative_to(R).as_posix(),'formalSha256':sha(final),'currentSelectedNative':fm['derivedFrom']['file'],'currentSelectedNativeSha256':fm['derivedFrom']['sha256']})
save(R/'audit/north-ground2-recovery-evidence.json',{'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None,'inferredRecoveredFrames':[8,9,10,14,15,16],'inferredStillUsedInCurrentFormal':[x['frame'] for x in rec if x['selectedForCurrentFormal'] and x['association'].startswith('inferred')],'evidenceBoundary':'Interrupted host calls completed in generated_images. Six request-to-output associations recovered by file chronology and visual match are inferred, not exact tool receipts. New replacements have exact receipts; current final NE08/09/10 still use inferred request associations. No model or quality was exposed. PNG identities and SHA checks are exact.','frames':rec})
checks=[]
for d in ['N','NE']:
 sheet=Image.new('RGB',(2048,2200),'#667579');dr=ImageDraw.Draw(sheet);sources=[];hashes=[]
 for f in range(1,17):
  p=R/'run'/d/f'{f:02}.png';m=read(Path(str(p)+'.generation.json'));im=Image.open(p);h=sha(p);n=R/m['derivedFrom']['file'];nr=Path(m['derivedFrom']['generationRecord']);nm=read(nr)
  errs=[]
  if im.size!=(1024,1024) or im.mode!='RGBA':errs.append('format')
  if m['sha256']!=h or m['registrationTransform']['outputSha256']!=h:errs.append('hash')
  if not n.exists():n=Path(nm['evidence']['toolReturnedPath'])
  if sha(n)!=m['derivedFrom']['sha256']:errs.append('native hash')
  if min(Image.open(n).size)<1024:errs.append('native too small')
  if m.get('actualModel') is not None or m.get('actualQuality') is not None:errs.append('unexposed actual')
  if m['registrationTransform']['globalScale']!=.8:errs.append('scale')
  checks.append({'file':p.relative_to(R).as_posix(),'sha256':h,'errors':errs});hashes.append(h)
  im=im.resize((512,512));x=(f-1)%4*512;y=(f-1)//4*550;sheet.paste(im,(x,y+30),im);dr.text((x+8,y+8),f'{d}{f:02} P{((f-1)%8)//2+1}  '+('LEFT' if f<=8 else 'RIGHT')+f' 75ms '+h[:10],fill='white');sources.append({'frame':f,'file':p.relative_to(R).as_posix(),'sha256':h})
 assert len(set(hashes))==16
 sheet.save(R/'run/staging'/f'north-ground2-final-{d}.jpg');save(R/'run/staging'/f'north-ground2-final-{d}.jpg.sources.json',sources)
save(R/'audit/north-ground2-technical-check.json',{'recordedAt':datetime.now(timezone.utc).isoformat(),'formalCount':len(checks),'allPassed':all(not c['errors'] for c in checks),'checks':checks})
print(json.dumps({'checks':len(checks),'errors':[c for c in checks if c['errors']],'inferredCurrent':[8,9,10]},ensure_ascii=False))
