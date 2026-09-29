"""Enumerate only disposable character20 image files; deletion is done by PowerShell."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
R=Path(__file__).resolve().parent.parent
P=R/'20-final'
H=Path('C:/Users/Administrator/.codex/generated_images').resolve()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=read(P/'acceptance.json');audit=read(R/'20-tools/final-before-retention-checks.json')
assert audit['allPass'] and audit['rawFilesChecked'] and audit['count']==136
for row in A['files']:assert sha(P/row['slot'])==row['sha256']
M=read(P/'preview/manifest.json')
assert M['visualApproval'] and M['walkCount']==128 and M['idleCount']==8
for d,v in M['directions'].items():
 for url in v['walk']+[v['idle']]:
  target=(P/'preview'/url.split('?')[0]).resolve()
  assert target.is_relative_to(P) and target.exists(),url
for g in A['gifChecks']:assert sha(P/'preview'/g['file'])==g['sha256']

images={};already_missing=[];host_issues=[]
scopes=[R/x for x in ['20-generation','20-reference','20-qa','20-work']]
extensions={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tiff','.tif'}
def add(p,reason,expected=None):
 p=p.resolve()
 assert p.is_file() and not p.is_relative_to(P)
 digest=sha(p)
 if expected:assert digest==expected,(str(p),digest,expected)
 images[str(p)]={'path':str(p),'sha256':digest,'bytes':p.stat().st_size,'reason':reason}
for scope in scopes:
 for p in scope.rglob('*'):
  if p.is_file() and p.suffix.lower() in extensions:
   add(p,'Superseded raw/reference copy/reject/intermediate for completed character20')
inspection=R/'20-tools/E-SE-leg-inspection.png'
if inspection.exists():add(inspection,'Temporary leg inspection; final contact sheets retained')
for result in (R/'20-generation').glob('*/tool-result.json'):
 data=read(result);hint=data.get('output_hint','')
 matches=re.findall(r' as (.+?\.png) by default\.',hint)
 if not matches:
  host_issues.append({'attempt':result.parent.name,'reason':'No host path parsed','keys':list(data)})
  continue
 source=read(result.parent/'raw.png.generation.json')
 for value in matches:
  p=Path(value).resolve()
  assert p.is_relative_to(H),str(p)
  if p.exists():add(p,'Exact host original for character20 receipt; SHA matched',source['sha256'])
  else:already_missing.append({'path':str(p),'attempt':result.parent.name})
plan={'at':datetime.now(timezone.utc).isoformat(),'character':'20_star_formation_master_girl',
 'authorization':'User 2026-09-23 final-only image retention, confirmed in current AGENTS.md',
 'protectedFinalRoot':str(P),'allowedWorkspaceRoots':[str(p.resolve()) for p in scopes],
 'allowedSingleFile':str(inspection.resolve()),'allowedHostRoot':str(H),
 'verifiedFinalCount':136,'verifiedPreviewGifCount':16,'files':list(images.values()),
 'alreadyMissingHostOriginals':already_missing,'hostIssues':host_issues,
 'count':len(images),'bytes':sum(r['bytes'] for r in images.values())}
(R/'20-tools/retention-plan-20260928.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:plan[k] for k in ['count','bytes','verifiedFinalCount','verifiedPreviewGifCount','hostIssues']}))
print(json.dumps({'host':sum(str(H) in p for p in images),'workspace':sum(str(H) not in p for p in images),'alreadyMissing':len(already_missing)}))
