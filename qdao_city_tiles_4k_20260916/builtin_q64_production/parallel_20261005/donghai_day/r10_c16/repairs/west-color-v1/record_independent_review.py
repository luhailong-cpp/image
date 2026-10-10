from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');D=R/'r10_c16/repairs/west-color-v1';P=R/'r10_c16/repairs/north-integrated-color-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='5089cf2e5fd0d00fdc5d73eac046bf41b9b816b3200523593f21f0f1fc9c9d87'
assert sha(D/'candidate.png')==expected
names=['qa/external/west-r10-c15-c16-common-edge-full.png']+['qa/external/west-wide-'+str(i)+'.png' for i in (2,3,4)]+['qa/assembly/internal-horizontal-y'+str(y)+'-full.png' for y in (1024,2048,3072)]+['qa/assembly/corner-sw.png','qa/assembly/overview-preview-1024.png']
views=[{'file':str(D/n),'sha256':sha(D/n),'actualVisualInspection':True,'passed':True,'scope':'y>=700 for west common edge; overview composition only' if '/external/' in n or 'overview' in n else 'entire sheet'} for n in names]
identity=[]
for f in sorted((D/'qa/assembly').glob('*.png')):
 old=P/'qa/assembly'/f.name
 if old.exists() and sha(f)==sha(old):identity.append({'file':str(f),'sha256':sha(f),'priorFile':str(old),'priorSha256':sha(old)})
assert len(identity)==17
d={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'fill16_left','candidateSha256':expected,'result':'pass','scope':'Changed west RGB field y>=700, three complete horizontal internal bands, SW core corner and overview. North/top700 and northwest four-tile join are explicitly pending final c15 north geometry; not approved by this report.','actualViewedSheets':views,'observations':['Common edge y>=700 has continuous stone faces and mortar curves; former straight tone cutoff is gone.','The small bright beveled face on lower stone remains a natural stone highlight and is continuous.','All three horizontal bands retain clean timber, rope, barrel and water shapes without new patch color bands; SW core corner is clean.'],'unchangedAssemblySheetsByExactSha256':identity,'priorReview':{'file':str(P/'independent-internal-review.json'),'sha256':sha(P/'independent-internal-review.json')},'wholeTileAccepted':False,'clientAcceptance':False}
out=D/'independent-west-internal-review.json';out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out),'actualViewed':len(views),'unchanged':len(identity)}))

