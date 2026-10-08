from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
B=Path('D:/work/image/qdao_city_tiles_4k_20260916')
A=B/'builtin_q64_production/parallel_20261005/parent_audit_20261008'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
ip=A/'verified-current-index.json';I=read(ip)
assert I['summary']['completePixelCandidateCount']==48
assert len(I['preview']['sources'])==48
assert [len(a['entries']) for a in I['appearances']]==[11,7,7,7,5,5,6]
assert sum('parentRepairCandidate' in e for a in I['appearances'] for e in a['entries'])==5
assert I['preview']['sha256']==sha(A/'overview.jpg')
review={'checkedAt':now,'status':'layout_visually_reviewed','method':'Actually opened saved overview.jpg through view_image after publication.','imageSha256':sha(A/'overview.jpg'),'checks':['Seven named appearance cards plus summary card are visible; no overlapping labels or clipped text.','Counts 11,7,7,7,5,5,6 sum to48, missing1744; formal0 and city0/7 stated.','Tile thumbnails follow actual row/column positions with gray missing cells.','All thumbnails share 112/4096 scale; no production image edit or enlargement.'],'scope':'Contact-sheet layout and labeling only; not native tile artwork or whole-city acceptance.'}
I['preview']['visualReview']=review;I['updatedAt']=now
dump(ip,I)
S=read(B/'status.json');S['updatedAtUtc']=now;S['currentBatchSha256']=sha(ip);S['latestContinuation']['checkpoint']['sha256']=sha(ip);S['candidateVisualReview']=review;dump(B/'status.json',S)
rp=A/'README.md';t=rp.read_text(encoding='utf-8')
t=t.replace('## 审计证据\n','## 审计证据\n\n本轮 3 块新增来源审计：`'+sha(A/'live-refresh-20261008-source-audit.json')+'`。48 张候选在汇总前再次核验图像 SHA、4096×4096 尺寸与完整不透明像素；本次实际打开总览检查了排版和标注，范围仅为缩略预览。\n')
t=t.replace('增量审计：`dba19','历史增量审计：`dba19')
rp.write_text(t,encoding='utf-8')
validation={'checkedAt':now,'index':{'path':ip.as_posix(),'sha256':sha(ip)},'statusPath':(B/'status.json').as_posix(),'count':48,'distribution':[11,7,7,7,5,5,6],'missing':1744,'formalAccepted':0,'wholeCities':0,'parentRepairAttachmentsPreserved':5,'previewReview':review,'modifiedOnlyParentDeliveryEntrypoints':True,'childPixelsOrSelectionsModified':False}
dump(A/'publish-48-validation.json',validation)
print(json.dumps(validation,ensure_ascii=False))
