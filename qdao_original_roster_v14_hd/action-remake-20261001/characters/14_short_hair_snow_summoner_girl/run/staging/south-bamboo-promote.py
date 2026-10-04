from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
d=sys.argv[1]
if d not in ('SW','SE'):raise ValueError('ownership')
selection=json.loads((R/f'audit/south-contact-{d}-selection.json').read_text(encoding='utf-8'))
rp=R/f'run/{d}/registration.json';reg=json.loads(rp.read_text(encoding='utf-8-sig'))
for nstr,version in selection['versions'].items():
 n=int(nstr);src=R/f'run/staging/south-bamboo-contact-{d}-{n:02}-v{version}.png';dest=R/f'run/{d}/{n:02}.png'
 if not src.exists() or not Path(str(src)+'.generation.json').exists():raise ValueError(str(src))
 export(src,dest)
 row=next(x for x in reg['frames'] if x['file']==f'run/{d}/{n:02}.png')
 row['sha256']=sha(dest);row['srcRoot']=[selection['sourceRootX'][0 if n<=8 else 1],960]
 row['basis']='Manually reviewed fixed same-direction hip reference; common virtual source ground960. No per-frame sole fitting; native fullcanvas then single0.8 registration.'
 row['selectedNative']=src.relative_to(R).as_posix();row['confidence']='static reviewed, root dynamic review pending'
reg['status']='static_pending_root_preview';write(rp,reg);apply(rp)
observations=selection['observations']
frames=[]
for n in range(1,17):
 p=R/f'run/{d}/{n:02}.png';m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 frames.append({'frame':n,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'supportLeg':'left' if n<=8 else 'right','position':'P'+str(((n-1)%8)//2+1),'durationMs':75,'observations':observations[n-1],'nativeSource':m['derivedFrom'],'registration':m.get('registrationTransform')})
pairs=[]
for k in range(8):
 i=k*2;pairs.append({'frames':[i+1,i+2],'position':'P'+str(k%4+1),'supportLeg':'left' if k<4 else 'right','observations':observations[i]+' '+observations[i+1]})
audit={'schemaVersion':2,'direction':d,'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'static_pending_root_preview','reviewScope':'Full PNG and two independent static fullbody/lowerbody sheets. No live playback claimed.','cycleMs':1200,'frameDurationMs':75,'contacts':[{'frames':list(range(1,9)),'supportLeg':'left','observations':'Left support chain: front landing -> under pelvis -> slightly behind -> rear forefoot, two independent poses at every position. Hip/thigh continuity read with phase sequence; skirt partially occludes proximal joints.'},{'frames':list(range(9,17)),'supportLeg':'right','observations':'Opposite right support chain at four spatial positions. Swing limb stays separate from support; rear forefoot contact is judged from ankle/heel/toe geometry, not minimum image pixel.'}],'positionPairs':pairs,'frames':frames,'staticChecks':{'headBodyScale':'Reviewed cranium/face/torso against neighbors; no per-frame scale adjustment','hands':'Two shoulder/sleeve/wrist chains; right crystal, left fox, no third sleeve','shoeAxes':'Boot long axes follow diagonal travel; no obvious outward toe twisting','root':'One fixed0.8 scale, manual pelvic x and common sourceGround960 target942; no per-frame vertical contact correction','loop':'Static08->09 and16->01 comparison; dynamic approval reserved for root'}}
write(R/f'audit/contact-{d}-review.json',audit)
ground={'schemaVersion':2,'direction':d,'status':'static_pending_root_preview','cycleMs':1200,'frameDurationMs':75,'criterion':'four spatial positions per leg, two independent frames per position; continuous8frame support then other leg','frames':[dict(file=f['file'],sha256=f['sha256'],observedPhase=f['position'],supportLeg=f['supportLeg'],observation=f['observations'],durationMs=75,nativeSource=f['nativeSource']) for f in frames],'contactAudit':f'audit/contact-{d}-review.json'}
write(R/f'run/{d}/grounding-review.json',ground)
print(json.dumps({'direction':d,'promoted':len(selection['versions']),'audit':f'audit/contact-{d}-review.json','status':'static_pending_root_preview'}))
