from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
RUN=Path(__file__).resolve().parent
PROJECT=Path('E:/work/mmorpg-client')
FAMILY='Assets/Resources/World/Characters/QdaoOriginalRosterV13'
IDS=None  # Resolved from this run's actual completed publisher record below
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def require(v,m):
 if not v:raise ValueError(m)
publication=read(RUN/'publish-execute.json')
require(publication['status']=='completed' and publication['writesPerformed'] is True,'Formal publisher did not complete')
require(Path(publication['targetProject']).resolve()==PROJECT.resolve(),'Wrong publication target')
IDS=tuple(item['characterId'] for item in publication['candidates'])
require(IDS and len(set(IDS))==len(IDS) and set(IDS)=={'03_lotus_healer_girl'},'Unexpected run3 publication identities')
snapshot=read(RUN/'input-playmode.json')
rows={r['path']:r for r in snapshot['files']}
checked=[]
for character in IDS:
 base=FAMILY+'/'+character+'/'
 expected={k:v for k,v in rows.items() if k.startswith(base) and not k.endswith('.meta')}
 require(len(expected)==148,'Incomplete tested resource set '+character)
 actual={(p.relative_to(PROJECT).as_posix()) for p in (PROJECT/(base.rstrip('/'))).rglob('*') if p.is_file() and not p.name.endswith('.meta')}
 require(actual==set(expected),'Formal resource inventory differs '+character)
 for k,v in expected.items():
  path=PROJECT/k;digest=sha(path);require(digest==v['sha256'],'Formal bytes differ from actual tested input '+k)
  checked.append({'path':k,'sha256':digest,'bytes':path.stat().st_size})
 a=read(PROJECT/(base+'appearance.json'));m=read(PROJECT/(base+'manifest.json'))
 require(a['version']==13 and a['characterId']==character and a['frameCount']==16 and a['frameDurationMs']==30 and a['dedicatedIdle'] and a['alignmentVersion']==2 and a['contactFrame']==0 and a['status']==a['visualReview']=='passed','Formal activation contract differs')
 require(a['manifest_sha256']==sha(PROJECT/(base+'manifest.json')) and a['validation_sha256']==sha(PROJECT/(base+'validation.json')) and m['status']==m['visual_review']=='passed','Formal manifest binding differs')
protected=read(RUN/'formal-protected-characters-before.json');old={r['path']:r for r in protected['files']}
current={p.relative_to(PROJECT).as_posix():p for p in (PROJECT/'Assets/Resources/World/Characters').rglob('*') if p.is_file() and not any(p.relative_to(PROJECT).as_posix().startswith(FAMILY+'/'+character+'/') for character in IDS)}
added=sorted(set(current)-set(old));removed=sorted(set(old)-set(current));changed=[]
for k in sorted(set(old)&set(current)):
 digest=sha(current[k])
 if digest!=old[k]['sha256']:changed.append({'path':k,'before':old[k]['sha256'],'after':digest})
result={'status':'passed' if not (added or removed or changed) else 'failed','createdUtc':datetime.now(timezone.utc).isoformat(),'project':str(PROJECT),'publicationSha256':sha(RUN/'publish-execute.json'),'actualTestedInputSnapshotSha256':sha(RUN/'input-playmode.json'),'resources':checked,'resourceCount':len(checked),'protectedExistingFiles':len(old),'protectedAdded':added,'protectedRemoved':removed,'protectedChanged':changed}
out=RUN/'formal-publication-audit.json';require(not out.exists(),'Keep the existing audit; use a new run to repeat');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='resources'},ensure_ascii=False))
require(result['status']=='passed','Protected previous character resources changed')
