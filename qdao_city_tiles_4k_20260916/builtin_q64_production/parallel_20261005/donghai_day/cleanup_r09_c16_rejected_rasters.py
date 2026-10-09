"""Remove only superseded rejected-branch rasters after current final validation."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent.resolve();T=R/'r09_c16'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
final=T/'output/r09_c16.png';expected='75e40578e8c29233bd6b73fbf60a3ea0d7eec917769b93de51404ad34e99a5f9'
assert sha(final)==expected
with Image.open(final) as im:im.load();assert im.size==(4096,4096)
manifest=read(T/'output/assembly-manifest.json');assert manifest['output']['sha256']==expected and manifest['postprocessingProtected']
current=read(manifest['postprocessing']['manifest'])
paths=[x['file'] for x in current['nativeRepairs']]
assert paths and all('post-tonal-masked' in x for x in paths)
for entry in current['nativeRepairs']:
 assert sha(entry['file'])==entry['sha256']
 gen=read(entry['record']['file'])
 for ref in gen['references']:assert sha(ref['file'])==ref['sha256']
removed=[]
for relative in ('repairs/color-match','repairs/post-tonal-fix','repairs/post-integrated'):
 target=(T/relative).resolve()
 assert target.is_relative_to(T.resolve()) and target!=T.resolve()
 candidates=[p for p in target.rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.npz')]
 for path in candidates:
  resolved=path.resolve();assert resolved.is_relative_to(target) and resolved.is_relative_to(R)
  removed.append({'file':str(path),'sha256':sha(path),'reason':'Rejected/superseded branch; final uses color-match-v2 plus post-tonal-masked'})
 for path in candidates:path.unlink()
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'currentFinal':{'file':str(final),'sha256':expected},
 'currentDependenciesValidated':True,'preserved':'All JSON/prompt/source text records; color-match-v2 foundation and current masked repair dependencies remain.',
 'removed':removed}
(T/'qa/rejected-raster-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'removedFiles':len(removed),'finalSha256':expected}))
