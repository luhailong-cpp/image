"""Mark a verified 09 cleanup complete and refresh final package checksums."""
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from common import DELIVERY, GENERATION, DIRS, sha

final=DELIVERY/'final'
marker=final/'post-cleanup-validation.json'
assert final.is_dir() and not marker.exists()
plan_path=final/'cleanup-plan.json'; retention_path=final/'retention.json'; readme_path=final/'README.md'
plan=json.loads(plan_path.read_text(encoding='utf-8'))
retention=json.loads(retention_path.read_text(encoding='utf-8'))
result=json.loads((final/'cleanup-result.json').read_text(encoding='utf-8'))
logs=[json.loads(line) for line in (final/'cleanup-executed.jsonl').read_text(encoding='utf-8-sig').splitlines()]
assert result['status']=='completed' and result['files']==len(plan['files'])==len(logs)
by_path={row['path']:row for row in logs}
assert len(by_path)==len(logs)
for item in plan['files']:
    log=by_path[item['path']]
    assert log['deleted'] is True and log['sha256']==item['sha256'] and log['bytes']==item['bytes']
    assert not Path(item['path']).exists(),item['path']
expected={f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)}|{f'idle/{d}.png' for d in DIRS}
actual={p.relative_to(final/'runtime').as_posix() for p in (final/'runtime').rglob('*.png')}
assert actual==expected
manifest=json.loads((final/'manifest.json').read_text(encoding='utf-8'))
accept=json.loads((final/'acceptance.json').read_text(encoding='utf-8'))
assert manifest['walkCount']==128 and manifest['idleCount']==8
assert accept['status']=='passed' and accept['reviewedManifestSha256']==sha(final/'evidence/reviewed-snapshot-manifest.json')
for row in manifest['files']:
    assert sha(final/row['path'])==row['sha256']
for d in DIRS:
    for bg in ('dark','light'):
        gif=final/f'preview/{d}-{bg}-30ms.gif'
        with Image.open(gif) as im:
            durations=[]
            for i in range(im.n_frames):
                im.seek(i); durations.append(im.info['duration'])
            assert durations==[30]*16 and im.info['loop']==0
sources=json.loads((final/'sources/index.json').read_text(encoding='utf-8'))
assert len(sources['images'])==136
for item in sources['images']:
    assert (final/item['generationEvidence']).is_file()
    assert sha(final/item['runtimePath'])==item['sha256']
for item in retention['nativeImages']:
    assert not Path(item['historicalPath']).exists()
    item['deleted']=True
    item['plannedRemoval']=False
retention['imageDeletionExecutedAfterPackaging']=True
retention['currentOriginalImageStatus']='Project-local character 09 originals, rejects and processing images in cleanup-plan.json were SHA-verified then deleted.'
retention['cleanupResult']='cleanup-result.json'
retention['cleanupExecutedAt']=result['completedAt']
plan['execution']='completed'
plan['executedAt']=result['completedAt']
plan['executionLog']='cleanup-executed.jsonl'
for item in plan['files']:
    item['deleted']=True
    item['action']='sha_verified_deleted'
readme=readme_path.read_text(encoding='utf-8')
old='本包不含生成原图。源目录原图仍待收尾清理，当前状态见 [retention.json](retention.json)；[cleanup-plan.json](cleanup-plan.json) 仅为清单，本工具不执行删除。'
new='本包不含生成原图。09 原图、拒稿和中间图已按 SHA 校验清理，结果见 [cleanup-result.json](cleanup-result.json) 与 [retention.json](retention.json)；正式角色肖像、设计成图及其他角色保留。'
assert old in readme
readme=readme.replace(old,new)
readme=readme.replace('历史绝对路径不伪改为不存在的包内图片路径。清理后，可用哈希与文字证据追溯，但不能声称仍可读取原图重新验像素。','历史绝对路径保留为来源事实；清理后由哈希与包内文字证据追溯。原图已不在，不能再重新读取原图验像素。')
now=datetime.now(timezone.utc).isoformat()
validation={'character':'09_bamboo_archer_girl','sealedAt':now,'cleanupFiles':len(logs),'cleanupBytes':result['bytes'],
            'walk':128,'idle':8,'directions':list(DIRS),'gifCount':16,'gifFrameDurationMs':30,'gifCycleMs':480,
            'manifestSha256':sha(final/'manifest.json'),'reviewedManifestSha256':accept['reviewedManifestSha256'],
            'sourceIndexCount':136,'remainingPlannedPaths':0,'projectGenerationImagesRemaining':sum(p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff'} for p in GENERATION.rglob('*') if p.is_file()),
            'clientIntegration':'not_performed'}
assert validation['projectGenerationImagesRemaining']==0
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(retention_path,retention);write(plan_path,plan);readme_path.write_text(readme,encoding='utf-8');write(marker,validation)
files={p.relative_to(final).as_posix():sha(p) for p in final.rglob('*') if p.is_file() and p.name!='package-checksums.json'}
write(final/'package-checksums.json',{'algorithm':'sha256','files':files,'selfExcluded':'package-checksums.json',
                                      'refreshedAfterCleanupAt':now})
assert all(sha(final/relative)==digest for relative,digest in files.items())
print(json.dumps(validation,ensure_ascii=False))
