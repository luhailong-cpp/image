"""Copy saved Unity inputs into a private validation project; never edits the source."""
from pathlib import Path
import argparse, hashlib, json, shutil, datetime
p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');p.add_argument('--record',default='input-snapshot.json');p.add_argument('--capture-only',action='store_true');a=p.parse_args()
src=Path('E:/work/mmorpg-client');dst=Path('E:/work/tmp/qdao-v13-verify-20260917');evidence=Path('E:/work/image/qdao_chibi_roster_v13/runtime-validation')
evidence.mkdir(parents=True,exist_ok=True)
assert dst.resolve().is_relative_to(Path('E:/work/tmp').resolve()) and dst!=src
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if not a.refresh and dst.exists(): raise SystemExit('Private validation directory already exists; use --refresh explicitly')
dst.mkdir(parents=True,exist_ok=True)
rows=[]
origin=dst if a.capture_only else src
for folder in ['Assets','Packages','ProjectSettings']:
    for f in (origin/folder).rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(origin);out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True)
        before=sha(f)
        if not a.capture_only and (not out.exists() or sha(out)!=before):shutil.copy2(f,out)
        after=before if a.capture_only else sha(f);copied=before if a.capture_only else sha(out)
        if before!=after or copied!=before:raise RuntimeError('Source changed while copying '+str(rel))
        rows.append({'path':rel.as_posix(),'sha256':copied,'bytes':out.stat().st_size})
if not a.refresh:
    cache=Path('E:/work/tmp/festival_game_verify_project_20260913/Library/PackageCache')
    if cache.exists():shutil.copytree(cache,dst/'Library/PackageCache',dirs_exist_ok=True)
    print('Copied package cache into independent storage')
record={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(src),'project':str(dst),'mode':('isolated saved-project snapshot after explicit reviewed source-file updates' if a.capture_only else 'private full Assets/Packages/ProjectSettings saved-file snapshot'),'shared_writable_links':False,'files':rows,'count':len(rows),'bytes':sum(r['bytes'] for r in rows)}
(evidence/a.record).write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in record.items() if k!='files'}))
