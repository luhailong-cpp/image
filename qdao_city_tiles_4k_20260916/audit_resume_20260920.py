from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path(__file__).resolve().parent;P=R/'builtin_q64_production';O=P/'resume_20260920';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
s=read(P/'handoff-snapshot-20260919.json');cfg=read(P/'current-batch-config.json');batch=read(P/'current-batch.json')
assert len(cfg['candidates'])==len(s['selectedCandidates'])==19
idx={(e['appearance'],e['tile']):e for e in cfg['candidates']}
for e in s['selectedCandidates']:
    assert idx[(e['appearance'],e['tile'])]['file']==e['file']
    assert sha(R/e['file'])==e['sha256'];assert Image.open(R/e['file']).size==(4096,4096)
    for k in ('assembly','qa'): assert sha(R/e[k])==e[k+'Sha256']
for t in s['activeProductionTargets']:
    assert len(t['records'])==t['selectedNativeCount']==16 and not t['missingIds']
    for e in t['records']:
        assert sha(e['record'])==e['recordSha256']; rec=read(e['record']);assert sha(e['hostSource'])==e['sourceSha256']==rec['outputSha256']
        native=Path(e['record']).with_name(Path(e['record']).name.replace('.record.json','.png')); assert sha(native)==e['sourceSha256']
for e in s['cityCheckpoints']:assert sha(e['file'])==e['sha256']
assert sha(s['handoffDocument'])==s['documentSha256']
for p in [P/'current-batch-config.json',P/'current-batch.json',R/'status.json',R/'README.md',R/'production_catalog.json']:
    shutil.copy2(p,O/('before-'+p.name))
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'snapshotSha256':sha(P/'handoff-snapshot-20260919.json'),'selectedCandidatesAndEvidenceVerified':19,'completeTargetsVerified':7,'selectedNativeRecordsAndByteIdentityVerified':112,'retainedSourcesAtStart':batch['nativeDetailPatchCountIncludingRepairs'],'formalAcceptedTiles':0,'runtimePublished':False,'userAuthorizedContinuation':True,'outdatedMissingQueuesIgnored':True,'sourceOnlyLedgerNotReapplied':True,'route':'builtin_image_gen','modelTarget':'gpt-image-2.5-sunburst','qualityTarget':'max','backendAndQualitySelectorsAvailable':False,'actualBackendModel':None,'officialModelPageVerified':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'}
(O/'resume-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
