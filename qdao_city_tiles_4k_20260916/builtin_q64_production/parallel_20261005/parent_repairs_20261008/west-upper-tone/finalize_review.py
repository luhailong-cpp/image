from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
m=load(R/'final-manifest.json');out=m['outputs']
for q in m['qa']:
 q['actuallyViewed']=True;q['reviewResult']='pass_limited_native_scope';q['reviewedAtUtc']=now
 save(q['file']+'.generation.json',{'file':q['file'],'sha256':sha(q['file']),'createdAtUtc':now,'operation':'Native1:1 crop of final joined outputs; no resize','cropLTRB':q['cropLTRB'],'derivedFrom':m['joined']})
for n in ['joined.png','final-joined.png','mask.png','trim-mask.png']:
 p=R/n
 save(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'createdAtUtc':now,'operation':'Deterministic native-scale assembly or alpha mask; image pixels are not resampled/blurred','derivedFrom':[{'file':str(R/'context.png'),'sha256':sha(R/'context.png')},{'file':str(R/'native.png'),'sha256':sha(R/'native.png'),'generationRecord':str(R/'native.png.generation.json')},{'file':str(R/'trim-gap/native.png'),'sha256':sha(R/'trim-gap/native.png'),'generationRecord':str(R/'trim-gap/native.png.generation.json')}],'script':str(R/'assemble.py')})
review={'reviewedAtUtc':now,'reviewer':'root','actuallyViewed':[m['joined'],*m['qa']],'findings':['Gray stone face is continuous across the former vertical brightness/texture seam.','The small step in the diagonal white highlight near context(627,255) has been removed.','Native inspection of upper relief, gold and gray contour, left/right and lower returns found no new hard stitch or doubled contour.'],'acceptedScope':'Only the eight listed native crop regions and changed local return support. Tile-top missing neighbor and whole-tile/city/runtime remain unreviewed.','independentReview':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/parent_audit_20261008/west-upper-tone-independent-review.json','outputs':out,'newCoordinates':0,'formalAccepted':False,'wholeCityComplete':False}
save(R/'final-review.json',review)
m.update(status='limited_native_scopes_reviewed_ready_as_parent_repair_candidate',review={'file':str(R/'final-review.json'),'sha256':sha(R/'final-review.json')})
save(R/'final-manifest.json',m)
save(R/'trim-repair/review.json',{'status':'rejected_not_selected','reason':'Native crop still shows the original notch in the white highlight; superseded by masked trim-gap fill','nativeSha256':sha(R/'trim-repair/native.png'),'reviewedAtUtc':now})
print(json.dumps({'manifest':str(R/'final-manifest.json'),'manifestSha256':sha(R/'final-manifest.json'),'review':str(R/'final-review.json'),'reviewSha256':sha(R/'final-review.json')}))
