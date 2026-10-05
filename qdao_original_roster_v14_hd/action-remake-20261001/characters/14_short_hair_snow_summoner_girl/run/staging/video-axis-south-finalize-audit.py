from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
auditpath=R/'audit/video-axis-S-SE-SW-review.json';a=read(auditpath)
changed={('SE',7),('SE',14),('SW',5)}
repairObs={
 ('SE',7):'已修复：右摆动小腿继续向右下前送，位于06与08之间；保留自然轻微膝屈与踝背屈，左后前掌支撑位置保留，消除缩回膝后的回跳。',
 ('SE',14):'已修复：左摆动小腿处于13到15的前送展开中间姿态，右支撑足仍在髋后P3承重，未再折回膝下。',
 ('SW',5):'主线程已修复并由本线程复看：右摆腿维持屈膝，脚在髋下后方经过，衔接04与06而不提前伸直；左支撑腿保留。'}
changes=[]
for f in a['frames']:
 key=(f['direction'],f['frame']);p=Path(f['file']);h=sha(p)
 if h!=f['sha256']:
  assert key in changed,(key,h)
  f['diagnosisInputSha256']=f['sha256'];f['sha256']=h
  m=read(Path(str(p)+'.generation.json'));im=Image.open(p);assert im.size==(1024,1024) and im.mode=='RGBA'
  assert m['sha256']==h
  f['observationBeforeRepair']=f['observation'];f['observation']=repairObs[key]
  f['continuityStatus']='static_repaired_pending_root_preview';f['nativeSource']=m['derivedFrom'];f['registration']=m['registrationTransform']
  changes.append({'direction':key[0],'frame':key[1],'file':f['file'],'sha256':h,'observation':f['observation']})
assert len(changes)==3
for q in a['confirmedContinuityFindings']:
 q['status']='static_repaired_pending_root_preview';q['selectedFile']=f'run/{q["direction"]}/{q["frame"]:02}.png'
 q['selectedSha256']=sha(R/q['selectedFile'])
a['notes'][0]['decision']='Root independently confirmed and repaired; reviewed new SW05; no change to other SW frames.'
a['notes'][0]['status']='static_repaired_by_root_pending_preview'
a['status']='static_repairs_complete_pending_root_preview';a['completedAt']=datetime.now(timezone.utc).isoformat()
a['repairs']=changes;a['formalPngWritesByThisAgent']=['run/SE/07.png','run/SE/14.png']
a['finalQaEvidence']=['run/staging/video-axis-SE-repair-neighbors.jpg']
a['verification']={'all48CurrentHashesChecked':True,'changedFrames':3,'changedByThisAgent':2,'SUnchanged':True,'actualModelQuality':'null in both native generation records; builtin does not expose confirmation','noExtraScale':True,'dimensions':'1024RGBA formal;1254RGBA native'}
write(auditpath,a)
cp=R/'audit/contact-SE-review.json';c=read(cp)
gp=R/'run/SE/grounding-review.json';g=read(gp)
for n in (7,14):
 p=R/f'run/SE/{n:02}.png';m=read(Path(str(p)+'.generation.json'));obs=repairObs[('SE',n)]
 for f in c['frames']:
  if f['file']==f'run/SE/{n:02}.png':f.update(sha256=sha(p),observations=obs,nativeSource=m['derivedFrom'],registration=m['registrationTransform'])
 for f in g['frames']:
  if f['file']==f'run/SE/{n:02}.png':f.update(sha256=sha(p),observation=obs,nativeSource=m['derivedFrom'])
 for pair in c['positionPairs']:
  if n in pair['frames']:pair['videoAxisRepairObservation']=obs
c['status']='static_pending_root_preview';g['status']='static_pending_root_preview';g['videoAxisRepairAudit']='audit/video-axis-S-SE-SW-review.json'
write(cp,c);write(gp,g)
print(json.dumps({'updated':str(auditpath),'checked':48,'repairs':changes},ensure_ascii=True))
