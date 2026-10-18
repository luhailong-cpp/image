from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];tile,apath,qpath=sys.argv[1:];assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in range(1,9)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap,qp=Path(apath),Path(qpath);assert ap.is_relative_to(B/tile) and qp.is_relative_to(B/tile)
a,v=read(ap),read(qp);assert a['tile']==tile and a['verifiedNativeCount']==16 and not a['formalAccepted'] and not v.get('formalAccepted',False)
for k,size in [('output',(4096,4096)),('contextOutput',(4326,4326))]:
 e=a[k];assert sha(e['file'])==e['sha256']
 with Image.open(e['file']) as im:assert im.size==size
cat=read(B/'current-candidates.json');old=cat['tiles'].get(tile);now=datetime.now(timezone.utc).isoformat()
new={'tile':tile,'source':'native-full16-worker-reviewed-candidate','assembly':str(ap),'assemblySha256':sha(ap),'candidate':a['output'],'context':a['contextOutput'],'coreWorldBox':a['selectedCoreWorldBox'],'verifiedNativeSlots':16,'sourceResampling':False,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'workerReview':str(qp),'workerReviewSha256':sha(qp),'adoptionScope':'Actual output/context hashes and dimensions checked; actual worker visual QA remains failed. No acceptance inferred.'}
rp=B/'pipeline-tools/candidate-adoptions'/f'{tile}.{a["output"]["sha256"][:16]}.json';assert not rp.exists();rp.parent.mkdir(parents=True,exist_ok=True)
rp.write_text(json.dumps({'recordedAtUtc':now,'oldEntry':old,'newEntry':new,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cat['tiles'][tile]=new;cat['updatedAtUtc']=now;(B/'current-candidates.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(B/'progress.json');p['latestCandidateUpdate']={'tile':tile,'candidate':a['output']['file'],'candidateSha256':a['output']['sha256'],'review':str(qp),'adoptionReceipt':str(rp),'recordedAtUtc':now,'formalAccepted':False};p['countsSnapshotMayHaveAdvanced']=True
(B/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tile':tile,'candidate':a['output']['file'],'sha256':a['output']['sha256'],'catalogCount':len(cat['tiles']),'adoptionReceipt':str(rp),'formalAccepted':False}))

