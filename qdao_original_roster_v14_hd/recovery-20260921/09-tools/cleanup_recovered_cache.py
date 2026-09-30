"""Handle the sole recovered 09 return whose wrapper lacked originalGeneratedFile."""
import json
from pathlib import Path
from datetime import datetime, timezone
from common import DELIVERY, sha

final=DELIVERY/'final'
recovered=json.loads((final/'evidence/generation/E13-v4/recovered-completion.json').read_text(encoding='utf-8'))
generation=json.loads((final/'evidence/generation/E13-v4/generation.json').read_text(encoding='utf-8'))
item=recovered['exactEvent']['payload']['item']
path=Path(item['savedPath'])
root=Path('C:/Users/Administrator/.codex/generated_images').resolve()
assert path.is_absolute() and not path.is_symlink() and path.resolve().is_relative_to(root)
assert item['id']==path.stem and path.name=='exec-b1d3345f-794c-4476-b83f-a0fcb3a4d8b8.png'
assert generation['visualReview']=='rejected_rgb_checkerboard'
assert recovered['sha256']==generation['sha256']==sha(path)
checks=json.loads((final/'package-checksums.json').read_text(encoding='utf-8'))
assert all(sha(final/p)==digest for p,digest in checks['files'].items())
bytes_=path.stat().st_size
path.unlink();assert not path.exists()
now=datetime.now(timezone.utc).isoformat()
result_path=final/'host-cache-cleanup.json'
result=json.loads(result_path.read_text(encoding='utf-8'))
result['items'].append({'historicalPath':str(path),'sha256':generation['sha256'],'bytes':bytes_,'deleted':True,'recoveredEventEvidence':'evidence/generation/E13-v4/recovered-completion.json'})
result['files']+=1;result['bytes']+=bytes_;result['recoveredItemDeletedAt']=now
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(result_path,result)
retention_path=final/'retention.json';retention=json.loads(retention_path.read_text(encoding='utf-8'))
retention['documentedHostCacheOriginalsDeleted']=result['files'];write(retention_path,retention)
all_files={p.relative_to(final).as_posix():sha(p) for p in final.rglob('*') if p.is_file() and p.name!='package-checksums.json'}
write(final/'package-checksums.json',{'algorithm':'sha256','files':all_files,'selfExcluded':'package-checksums.json','refreshedAfterRecoveredCacheCleanupAt':now})
assert all(sha(final/p)==digest for p,digest in all_files.items())
print(json.dumps({'hostCacheDeleted':result['files'],'bytes':result['bytes'],'recoveredRgbRejectRemoved':True}))
