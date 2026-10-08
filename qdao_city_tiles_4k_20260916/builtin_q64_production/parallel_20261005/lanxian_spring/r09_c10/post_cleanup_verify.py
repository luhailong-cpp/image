from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
mf=B/'selected/delivery.manifest.json';m=json.loads(mf.read_text());cl=json.loads((B/'selected/cleanup.manifest.json').read_text(encoding='utf-8-sig'))
for item in cl['preserved']:assert sha(item['file'])==item['sha256']
day=B.parent.parent/'lanxian_day/r09_c10/selected/extended4326.png'
assert sha(day)=='9f4279c1fec0ff91aa62fcb21e2fcb3e78ca021266732ed6096adb9338e341f5'
base=np.array(Image.open(day).convert('RGB'));ext=np.array(Image.open(B/'selected/extended4326.png').convert('RGB'));core=np.array(Image.open(B/'selected/core4096.png').convert('RGB'));mask=np.array(Image.open(B/'selected/surface-mask4326.png'))
assert np.array_equal(ext[115:4211,115:4211],core)
assert np.array_equal(ext[mask==0],base[mask==0])
source=base[2915:4169,815:2069].astype('int16');final=ext[2915:4169,815:2069]
green=(source[:,:,1]>source[:,:,0]+3)&(source[:,:,1]>source[:,:,2]+10)
assert np.array_equal(source[green],final[green])
check={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'pass','allSixPreservedPngHashesVerified':True,'outputs':m['outputs'],'exactCoreHalo':True,'outsideMaskChangedPixels':0,'sourceGreenChangedPixels':0,'changedCorePixels':int(np.any(core!=base[115:4211,115:4211],axis=2).sum()),'changedExtendedPixels':int(np.any(ext!=base,axis=2).sum()),'retainedPngCount':len(list(B.rglob('*.png'))),'deletedPngCount':cl['deletedPngCount'],'daySourceUnchanged':True,'nativeGenerationCount':2,'actualModel':None,'actualQuality':None,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False}
write(B/'selected/post-cleanup-verification.json',check)
m['retention']={'status':'cleanup_completed','completedAtUtc':check['createdAtUtc'],'deletedPngCount':cl['deletedPngCount'],'retainedPngCount':check['retainedPngCount'],'keep':'Selected3 game candidate/overview images plus3 technical masks; all text generation/source/QA/process records retained.','cleanupManifest':info(B/'selected/cleanup.manifest.json'),'postCleanupVerification':info(B/'selected/post-cleanup-verification.json'),'sourceSnapshotPngRemovedAfterVerifiedExport':True,'historicalPathsAreProvenanceNotLiveDependencies':True,'dayNorthAndGeneratedImagesOriginalsUntouched':True,'allPreservedHashesVerified':True}
m['qa']['sourceMutationAudit']=info(B/'qa/source-mutation-audit.json')
m['qa']['independentResolvedIssue']='Safe highlight mask originally touched781 source-green pixels; excluded after all manual polygon unions. Independent recheck confirms zero source-green changes and zero outside-mask changes.'
write(mf,m)
with (B/'README.md').open('a',encoding='utf8') as f:f.write('\n已完成清理：删除本块39张来源快照、过程稿与QA裁图，保留6张成品/技术遮罩。全部文字记录保留；[清理清单](selected/cleanup.manifest.json)与[清理后验证](selected/post-cleanup-verification.json)。独立复核发现的781个叶片遮罩像素已恢复，最终为0个源绿叶像素变化。\n')
print(json.dumps({'delivery':info(mf),'qa':info(B/'qa/final-visual-review.json'),'independentQA':info(B/'qa-north-independent/final-review.json'),'postCleanup':info(B/'selected/post-cleanup-verification.json'),'core':m['outputs']['core'],'extended':m['outputs']['extended'],'preview':m['outputs']['preview'],'status':check['status']},ensure_ascii=False))
