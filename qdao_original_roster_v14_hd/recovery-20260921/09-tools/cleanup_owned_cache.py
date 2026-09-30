"""Delete only SHA-matched built-in cache originals documented for character 09."""
import json
from datetime import datetime, timezone
from pathlib import Path
from common import DELIVERY, sha

final=DELIVERY/'final'
cache_root=Path('C:/Users/Administrator/.codex/generated_images').resolve()
records=final/'evidence/generation'
target={}
for source in records.rglob('generation.json'):
    generation=json.loads(source.read_text(encoding='utf-8-sig'))
    assert generation.get('character')=='09_bamboo_archer_girl' or (
        source.parent.name=='E13-v4' and generation.get('file','').replace('\\','/').endswith('/09-generation/E13-v4/raw.png')
        and generation.get('visualReview')=='rejected_rgb_checkerboard')
    evidence=generation.get('evidence',{})
    original=evidence.get('originalGeneratedFile')
    if not original:continue
    path=Path(original)
    assert path.is_absolute() and not path.is_symlink()
    resolved=path.resolve()
    assert resolved.is_relative_to(cache_root) and resolved.name.startswith('exec-') and resolved.suffix.lower()=='.png'
    digest=evidence.get('originalSha256') or generation['sha256']
    assert digest==generation['sha256']
    assert resolved not in target or target[resolved]==digest
    target[resolved]=digest
assert target
checksums=json.loads((final/'package-checksums.json').read_text(encoding='utf-8'))
assert all(sha(final/p)==digest for p,digest in checksums['files'].items())
for path,digest in target.items():
    assert path.is_file() and sha(path)==digest,(str(path),'cache source changed')
log=[]
for path,digest in target.items():
    bytes_=path.stat().st_size
    path.unlink()
    assert not path.exists()
    log.append({'historicalPath':str(path),'sha256':digest,'bytes':bytes_,'deleted':True})
now=datetime.now(timezone.utc).isoformat()
result={'character':'09_bamboo_archer_girl','completedAt':now,'scope':'Exact SHA-verified generated_images cache files recorded for 09 only',
        'files':len(log),'bytes':sum(x['bytes'] for x in log),'otherCacheFilesUntouched':True,
        'items':log}
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(final/'host-cache-cleanup.json',result)
retention_path=final/'retention.json';retention=json.loads(retention_path.read_text(encoding='utf-8'))
retention['documentedHostCacheOriginalsDeleted']=len(log)
retention['hostCacheCleanupResult']='host-cache-cleanup.json'
write(retention_path,retention)
readme_path=final/'README.md'
readme=readme_path.read_text(encoding='utf-8')
readme+='\n本次生成对应的宿主缓存原图也已逐文件核对 SHA 后删除，记录见 [host-cache-cleanup.json](host-cache-cleanup.json)。\n'
readme_path.write_text(readme,encoding='utf-8')
all_files={p.relative_to(final).as_posix():sha(p) for p in final.rglob('*') if p.is_file() and p.name!='package-checksums.json'}
write(final/'package-checksums.json',{'algorithm':'sha256','files':all_files,'selfExcluded':'package-checksums.json','refreshedAfterCacheCleanupAt':now})
assert all(sha(final/p)==digest for p,digest in all_files.items())
print(json.dumps({k:result[k] for k in ('character','completedAt','files','bytes','otherCacheFilesUntouched')},ensure_ascii=False))
