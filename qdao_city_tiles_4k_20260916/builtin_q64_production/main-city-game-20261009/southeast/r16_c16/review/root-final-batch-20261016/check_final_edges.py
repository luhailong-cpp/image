from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parent.parent;Z=T.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inf(p):return {'path':str(p),'sha256':sha(p)}
def current(t):
 d=read(Z/t/'candidate/latest-assembly.json')['candidate'];p=Path(d['path']);assert sha(p)==d['sha256'];return p,Image.open(p).convert('RGB')
cp,c=current('r16_c16');npth,n=current('r15_c16');wp,w=current('r16_c15')
audit=read(T/'review/independent-20261016/audit-inputs.json');oldN=Image.open(audit['neighbors']['north']['candidate']['path']).convert('RGB');oldW=Image.open(audit['neighbors']['west']['candidate']['path']).convert('RGB')
assert n.crop((0,3776,4096,4096)).tobytes()==oldN.crop((0,3776,4096,4096)).tobytes()
assert w.crop((3776,0,4096,4096)).tobytes()==oldW.crop((3776,0,4096,4096)).tobytes()
changed=[];reused=[]
for e in audit['crops']:
 x,y,x1,y1=e['coreBox']
 if y<0:
  im=Image.new('RGB',(x1-x,y1-y));im.paste(n.crop((x,4096+y,x1,4096)),(0,0));im.paste(c.crop((x,0,x1,y1)),(0,-y))
 elif x<0:
  im=Image.new('RGB',(x1-x,y1-y));im.paste(w.crop((4096+x,y,4096,y1)),(0,0));im.paste(c.crop((0,y,x1,y1)),(-x,0))
 else:im=c.crop((x,y,x1,y1))
 old=Image.open(e['path']).convert('RGB');assert sha(e['path'])==e['sha256']
 if im.tobytes()==old.tobytes():reused.append({'name':e['name'],'originalEvidence':{'path':e['path'],'sha256':e['sha256']},'pixelsExactlyUnchanged':True})
 else:
  p=D/(e['name']+'-final.png');assert not p.exists();im.save(p);changed.append({'name':e['name'],'path':str(p),'sha256':sha(p),'coreBox':e['coreBox'],'reviewStatus':'pending_root_native_view'})
data={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':inf(cp),'north':inf(npth),'west':inf(wp),'northBottom320ExactlyUnchanged':True,'westEast320ExactlyUnchanged':True,'reused':reused,'changed':changed,'formalAccepted':False}
with (D/'final-evidence-reuse.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps({'report':inf(D/'final-evidence-reuse.json'),'reusedCount':len(reused),'changed':changed}))
sd=Z/'r16_c15/review/resume-20261016';qd=Z/'r16_c15/repairs/local-seams-20261016-v1/trial-v2';names=['I01-unchanged','N01-local','north-final-local','north-final-q0','north-final-q2','W02-local','west-final-q0']
qa={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidate':inf(wp),'nativeEvidenceActuallyViewed':[inf(qd/(name+'.png')) for name in names],'localRepairQA':'passed_I01_N01_W01_W02_no_new_mask_boundary_break','actualNorthSource':inf(Z/'r15_c15/candidate/r15_c15-4k-south-v2-west-v1-20261016.png'),'northPairLocalQA':'passed_updated_north_post_removal_and_original_quadrant_reuse','eastPairQA':'failed_r16_c16_W02_and_pending_W03_W04_as_recorded_on_eastern_tile','materialFinish':'inherited_fine_grid_watch','formalAccepted':False}
with (sd/'root-local-qa-20261016.json').open('x',encoding='utf-8') as f:json.dump(qa,f,indent=2)
