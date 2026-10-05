from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
B=R/'full-limb-review-20261004'
def write(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected=[
('run/SW/15','run-SW/15-v1','passed','Original left-support lateral reach reduced; distinct raised right leg preserved; full-canvas framing retained.'),
('run/SW/16','run-SW/16-v3','passed','Left support restored to final support region after v2 over-correction; independent raised boot and ankle pose, reduced original sideways split.'),
('run/NW/15','run-NW-south/15-v2','passed','Lower rod and gold butt now continue upper black-shaft axis through dress/boot occlusion. Minor approximately1.5% head-height difference from original noted for root final sequence review.'),
('run/NW/16','run-NW-south/16-v4','passed','False far-right tail assembly removed. Actual straight lower weapon projects behind thigh/boot. Original head/spearhead anchors preserved in fresh edit.')]
rows=[]
for slot,folder,status,reason in selected:
 p=B/folder/'native.png'; im=Image.open(p); meta=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
 rec={'slot':slot,'file':p.relative_to(R).as_posix(),'status':status,'reason':reason,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode,'alphaExtrema':list(im.getchannel('A').getextrema()),'alphaBBox':list(im.getchannel('A').getbbox()),'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runTimingMs':60,'cycleFrames':16,'actualModel':None,'actualQuality':None,'sourceRecords':meta['references']}
 write(B/folder/'visual-review.json',rec); rows.append(rec)
 meta['status']='visually-approved-awaiting-root-publish';write(Path(str(p)+'.generation.json'),meta)
assert len({r['sha256'] for r in rows})==4
assert all(r['mode']=='RGBA' and r['alphaExtrema']==[0,255] for r in rows)
rejects={'run-SW/16-v1':'whole-sprite enlargement and upward framing drift','run-SW/16-v2':'support boot too far inward, retreats relative to prior phase','run-NW-south/15-v1':'residual lower-weapon offset','run-NW-south/16-v1':'residual lower-weapon offset','run-NW-south/16-v2':'residual lower-weapon offset persists','run-NW-south/16-v3':'lower weapon correctly occluded but upper spearhead moves upward'}
for folder,reason in rejects.items():
 write(B/folder/'visual-review.json',{'status':'rejected','reason':reason})
write(B/'sw-nw-local-qa'/'audit.json',{'scope':'Only targeted SW15/16 and NW15/16; no runtime writes by this agent','currentRunTimingMs':60,'cycleDurationMs':960,'selected':rows,'rejected':rejects,'preservedOriginalSW':['13','14'],'rootOwnsNW':['13','14'],'qa':['sw-candidates.jpg','nw-candidates.jpg']})
print(json.dumps({'selected':len(rows),'uniqueImages':len(set(r['sha256'] for r in rows)),'alpha':'allRGBA0..255','runtimeModified':False}))

