from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'run/staging/south-bamboo-S-13-v2.png';dest=R/'run/S/13.png'
req=json.loads((R/'provenance/south-bamboo-S-13-v2.request.json').read_text(encoding='utf-8'))
assert sha(dest)==req['previousOfficialSha']
export(src,dest)
rp=R/'run/S/registration.json';reg=json.loads(rp.read_text(encoding='utf-8-sig'))
row=next(x for x in reg['frames'] if x['file']=='run/S/13.png');row['sha256']=sha(dest);row['srcRoot'][1]=960;row['bambooRepairNative']='run/staging/south-bamboo-S-13-v2.png';row['basis']='Original manually reviewed pelvic x retained; shared source ground y960. Early flight rising toward14 apex; no per-frame sole alignment.'
rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8');apply(rp)
ap=R/'audit/bamboo-south-review.json';a=json.loads(ap.read_text(encoding='utf-8'))
a['reviewedAt']=datetime.now(timezone.utc).isoformat();a['formalChangedCount']=7;a['formalRetainedCount']=41;a['pendingFrame']=None
a['phaseNotes']['S']='05 early-flight with lead thigh forward and rear leg higher. 13 rising early flight, boot bottom about919 remains above target ground942;14 higher apex near899, then15/16 forward descent. Support02/03 and10/11 retained.'
a['completionClaim']='Seven local pose repairs exported and registered;41 other frames retained after fresh09 comparison. Whole-cycle playback at1200ms and all-action acceptance remain root responsibility.'
a['independentRootReview']={'S13v2':'Parent compared native v2,current14,09S13/14 and accepted early-flight rising toward14 apex; no false contact at13.','retainedRejectedVersions':'All requests/receipts/generation records preserved; failed scale, boot-axis, or leg-phase candidates not selected.'}
fr=next(x for x in a['frames'] if x['file']=='run/S/13.png');fr.update(status='repaired_and_registered',sha256=sha(dest),selectedNative='run/staging/south-bamboo-S-13-v2.png',observation='One leading screen-right thigh forward and trailing left leg behind; two forward shoe axes. Early flight rising toward14 apex, not ground contact. Parent independent static review accepted.')
fr.pop('candidate',None)
ap.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
s=R/'run/S/south-selected.json';j=json.loads(s.read_text(encoding='utf-8-sig'))
j['visualStatus']='Latest fresh bamboo comparison:7 local repairs +41 retained; audit/bamboo-south-review.json is latest pose audit. Final1200ms combined playback acceptance remains parent responsibility.'
for row in j['frames']:
 row['sha256']=sha(R/row['file'])
 auditrow=next(v for v in a['frames'] if v['file']==row['file'])
 if auditrow['status']=='repaired_and_registered':
  native=R/auditrow['selectedNative'];rec=json.loads(Path(str(native)+'.generation.json').read_text(encoding='utf-8'))
  row.update(selectedNative=auditrow['selectedNative'],nativeSha256=rec['sha256'],nativeSize=rec['nativeSize'],generationRecord=auditrow['selectedNative']+'.generation.json',actualModel=None,actualQuality=None)
s.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
out=Image.new('RGB',(1200,1320),(232,236,234));dr=ImageDraw.Draw(out)
for n in range(1,17):
 im=Image.open(R/f'run/S/{n:02}.png');im.thumbnail((300,300));x=((n-1)%4)*300;y=((n-1)//4)*330
 out.paste(im,(x,y),im);dr.text((x+10,y+302),f'S/{n:02} '+('repaired' if n in(5,13) else 'retained'),fill=(20,40,50))
out.save(R/'run/staging/south-bamboo-S-formal-contact.jpg',quality=94)
print(json.dumps({'repaired':7,'retained':41,'pendingPoseFrames':0,'dynamicPlayback':'root pending','S13sha':sha(dest)}))

