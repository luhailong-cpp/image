import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
Q=Path(__file__).resolve().parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
tr=Q/'west-corner-r08r09c04c05-v3-export-trace.json';t=rd(tr)
for r in t['tiles']:
 for k in ['base','context','candidate']:
  assert ref(Path(r[k]['path']))['sha256']==r[k]['sha256']
a={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','scope':'r08_c05 internal and currently available north/south/east joins from v7, repaired r09_c04/r09_c05 top west corner, and affected r08_c05/r09_c05 horizontal joint. r08_c04 full tile and remaining west edge are not accepted.','trace':ref(tr),'tiles':t['tiles'],'qa':[dict(q,result='pass',viewedAtNativeResolution=True) for q in t['qa'][:2]],'partialPreview':dict(t['qa'][2],viewedAtNativeResolution=True,result='not a full corner acceptance; upper-left r08_c04 joints pending full tile composition'),'inheritedAudit':ref(Q/'block2x2-r08r09c05c06-v7-art-audit.json'),'closedExternalIssue':ref(Q/'block2x2-r08r09c05c06-v7-west-external-top-audit.json'),'decision':'Second native repair v2 with v3 closed hard mask removes the former vertical material cutoff across the south-row export boundary while keeping paving geometry. v1 repair and v1/v2 mask compositions not selected.','attempts':2,'sourcePixelIdentity':True,'nativePixelsResampled':False,'formalAcceptedCount':0,'runtimeClaims':False,'remaining':['r08_c04 still 3/16; its full internal seams and r08_c04/r08_c05 west-edge join pending','r08_c05 north edge to row7 pending','full-map and runtime acceptance pending'],'exportOwnership':'Root only; no index/ledger/progress writes'}
p=Q/'west-corner-r08r09c04c05-v3-art-audit.json';assert not p.exists();p.write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8');print(json.dumps({'audit':ref(p),'trace':ref(tr)}))

