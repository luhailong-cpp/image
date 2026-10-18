from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'trial-v1'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def rgb(p):return np.array(Image.open(p).convert('RGB'))
co=rd(O/'composition.json');base=rgb(co['base']['path']);core=rgb(co['core']['path'])
for k in ['base','baseContext','north','native','receipt','preparation','alpha','minimumErrorPaths','core','context']:
 assert sha(co[k]['path'])==co[k]['sha256']
native=rgb(co['native']['path']);u0,v0,u1,v1=co['sourceCrop'];x0,y0,x1,y1=co['destinationCoreBox'];a=np.array(Image.open(co['alpha']['path']))
patch=native[v0:v1,u0:u1]
replay=base.copy()
for y in range(y1-y0):
 for x in range(x1-x0):
  w=int(a[y,x])
  for c in range(3):replay[y0+y,x0+x,c]=(int(base[y0+y,x0+x,c])*(255-w)+int(patch[y,x,c])*w+127)//255
assert np.array_equal(core,replay)
mask=np.zeros((4096,4096),bool);mask[y0:y1,x0:x1]=a>0
assert np.array_equal(core[~mask],base[~mask])
notes={'north-core-join-q1-100pct':'At actual core y0, upper joint near x1234 now continues into child. Previous flat-ended parallel child vertical near x1325 is removed. Diagonal slab course and existing first projecting belt connect without a gap.','top-boundary-100pct':'True immutable north endpoint joins the replacement without a new dark bar or doubled edge.','bottom-boundary-100pct':'Existing lower vertical grout and wall texture retained continuously through the stored mask boundary.','left-boundary-100pct':'Diagonal courses and shadowed return remain continuous; no clipping at the left mask edge.','right-boundary-100pct':'Horizontal projecting belt and natural stone texture continue through the right mask edge.','composed-local-1254':'Overall local context preserves the lower belt geometry and fixed north. Structural join is connected; this is a local pass only, not whole-tile art acceptance.'}
evidence=[]
for e in co['evidence']:
 assert sha(e['path'])==e['sha256'];name=Path(e['path']).stem
 evidence.append(dict(**e,visuallyViewedAtNativeResolution=True,status='passed_local_no_blocking_discontinuity',finding=notes[name]))
qa=dict(schemaVersion=1,tile='r16_c16',id='N02-north-corner',reviewer='/root/assembly_resume',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),composition=ev(O/'composition.json'),core=co['core'],actualNative=co['native'],north=co['north'],base=co['base'],attempt=1,status='passed_local_pending_root_independent_review',evidence=evidence,independentScalarPixelReplayExact=True,outsideMaskExact=True,allowedChildBox=[1050,0,1650,600],northPixelsImmutable=True,unrelatedWestAndRightIssues='not changed and not claimed passed',contextPolicy=co['contextPolicy'],published=False,formalAccepted=False)
p=O/'visual-qa.json';assert not p.exists();p.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(qa=ev(p),core=co['core'],composition=ev(O/'composition.json'))))

