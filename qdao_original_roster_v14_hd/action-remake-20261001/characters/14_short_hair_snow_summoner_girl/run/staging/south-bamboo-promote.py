from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
sel={'S/05':'south-bamboo-S-05-v2','SW/05':'south-bamboo-SW-05-v2','SW/12':'south-bamboo-SW-12-v2','SW/13':'south-bamboo-SW-13-v3','SE/12':'south-bamboo-SE-12-v3','SE/13':'south-bamboo-SE-13-v3'}
observations={'S/05':'Leading screen-left thigh projects forward; rear screen-right leg is behind and higher. Early flight foot height corrected to precede06/07 without full early extension.','SW/05':'Raised leading knee plus stretched trailing leg replace double-tucked hop; rear ankle now points down-left like front boot.','SW/12':'Previously straight leading kick corrected to knee lift with boot directly below knee; top of boot visible instead of broad sole.','SW/13':'Leading knee forward, trailing leg extended; both toe caps point down-left; v3 restores original upper-body scale.','SE/12':'Leading knee raised with boot underneath, rear leg stretches back; both toe tips rotated down-right; v3 restores original upper-body scale.','SE/13':'Distinct forward thigh and rear folded leg replace double tuck; front shin partially flexed to precede14 rather than reaching ground early.'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={f'run/{d}/{n:02}.png':sha(R/f'run/{d}/{n:02}.png') for d in ('S','SW','SE') for n in range(1,17)}
for key,label in sel.items():
 req=json.loads((R/'provenance'/f'{label}.request.json').read_text(encoding='utf-8'))
 assert before[f'run/{key}.png']==req['previousOfficialSha'],('formal concurrently changed',key)
for d in ('S','SW','SE'):
 rp=R/'run'/d/'registration.json'; reg=json.loads(rp.read_text(encoding='utf-8-sig'))
 for key,label in sel.items():
  if not key.startswith(d+'/'):continue
  src=R/'run/staging'/f'{label}.png'; dest=R/f'run/{key}.png'
  export(src,dest)
  row=next(x for x in reg['frames'] if x['file']==f'run/{key}.png')
  row['sha256']=sha(dest);row['srcRoot'][1]=960
  row['basis']='Original manually reviewed pelvic x preserved with upper-body lock; shared virtual ground y960. Bamboo comparison repair; no sole/minimum-pixel alignment.'
  row['bambooRepairNative']=src.relative_to(R).as_posix()
  meta=Path(str(src)+'.generation.json');j=json.loads(meta.read_text(encoding='utf-8'))
  j['review']={'status':'selected_local_pose_fix','observation':observations[key],'wholeCycleDynamicReview':'pending root review at1200ms'}
  meta.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
 rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
 apply(rp)
after={p:sha(R/p) for p in before}
assert [p for p in before if before[p]!=after[p]]==[p for p in before if p[4:-4] in sel]
B=R.parent/'09_bamboo_archer_girl'
rows=[]
for p in before:
 key=p[4:-4];d,n=key.split('/')
 im=Image.open(R/p);assert im.size==(1024,1024) and im.mode=='RGBA'
 ref=B/'runtime'/p
 row={'file':p,'beforeSha256':before[p],'sha256':after[p],'reference':str(ref),'referenceSha256':sha(ref),'reviewMode':'fresh visual16-frame contact comparison and full-size changed-frame/neighbor review'}
 if key in sel:row.update(status='repaired_and_registered',selectedNative='run/staging/'+sel[key]+'.png',observation=observations[key])
 elif key=='S/13':row.update(status='pending_candidate_review',candidate='run/staging/south-bamboo-S-13-v2.png',observation='Candidate removes double-knee tuck but leading foot y~919 precedes existing14 y~899; later v3/v5 enlarged upper body and v4 returned to tucked silhouette. Formal kept while choosing correct continuity fix.')
 else:row.update(status='retained_after_new_comparison',observation='No newly confirmed toe-out or knee/ankle-plane mismatch in fresh09 comparison; original retained. This is not whole-cycle dynamic sign-off.')
 rows.append(row)
audit={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'14 run S SW SE only;09 read-only','comparisonBasis':'09 actual corresponding runtime PNGs and full16 direction contacts; no inherited acceptance from old report','formalChangedCount':len(sel),'formalRetainedCount':48-len(sel),'pendingFrame':'run/S/13.png','normalCycleMs':1200,'timingOwner':'root; no timing files changed by this subagent','globalRegistration':{'scale':.8,'sourceGroundY':960,'targetRoot':[512,942],'sourceMode':'native originals/candidates before registration; wholecanvas1024 then one global registration; not double-scaled formal'},'actualModel':None,'actualQuality':None,'phaseNotes':{'S':'05 early-flight with lead thigh forward and rear leg higher; support02/03 and10/11 retained;13 candidate pending.','SW':'05/12/13 raised leading knee plus extended trailing ankle;06/07 and14/15 forward-swing retained.','SE':'12 leading knee lifted before13 early forward swing and14 greater extension;02/03 and10/11 support retained.'},'frames':rows,'completionClaim':'Six local pose repairs promoted. S13 unresolved candidate continuity; all-action and complete dynamic sign-off not claimed.'}
(R/'audit/bamboo-south-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
for d in ('S','SW','SE'):
 out=Image.new('RGB',(1200,1320),(232,236,234));draw=ImageDraw.Draw(out)
 for n in range(1,17):
  im=Image.open(R/f'run/{d}/{n:02}.png');im.thumbnail((300,300))
  x=((n-1)%4)*300;y=((n-1)//4)*330
  out.paste(im,(x,y),im);draw.text((x+10,y+302),f'{d}/{n:02} '+('repaired' if f'{d}/{n:02}' in sel else 'retained'),fill=(20,40,50))
 out.save(R/f'run/staging/south-bamboo-{d}-formal-contact.jpg',quality=94)
print(json.dumps({'changed':list(sel),'formalTotal':48,'pending':'S/13','audit':'audit/bamboo-south-review.json'}))

