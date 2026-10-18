import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=json.loads((Q/'pair-r14c05-r14c06-v1-trace.json').read_text(encoding='utf-8-sig'))
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
stem='r14_c05_c06_join_foliage_repair_v1';box=[3584,3072,4838,4326]
source=Q/'r14c05-c06-foliage-source-native-v1.png'
with Image.open(t['context']['path']) as im:im.crop(box).save(source)
prompt='Use case: precise-object-edit. Image 1 is an exact native 1254x1254 crop from the existing two-tile game map. Repair the artificial straight vertical source boundary at x512, especially where it cuts a rock face and foliage in the lower half. Repaint only a narrow central transition region x360..780 to reconnect the individual leaves, their stems, overlapping shadows and adjacent rounded rock planes so the existing rocks and shrub canopy form one uninterrupted hand-painted scene. Keep the exact overall rock silhouettes, large canopy outlines, perspective, daylight, colors and material scale. Remove straight sliced leaf edges, cut-off stone facets and vertical tone transitions at x512; connect each leaf naturally to its original branch and preserve the spatial relation of shrubs overlapping rocks. No blurred seam, no extra objects, no vegetation moved into stone, no new holes or water. Keep leftmost and rightmost 280 pixels unchanged and preserve top and bottom edge continuity. Fine Daoist Q hand-painted broad rounded leaves, yellow-green sunlit tips, jade middle planes and deep cool green leafy recesses; natural warm beige and blue-gray rocks. Images 2,3,4 are approved layout/material/painterly style references; never copy UI, architecture, figures, text or night lighting into this local edit. Exactly1254x1254 native pixels, all opaque, no resizing or frame.'
rlist=[{**ref(source),'role':'exact native crop, localized edit target'}]+refs
req={'stem':stem,'tile':'r14_c05+r14_c06','patch':'foliage','coordinates':{'role':'localized native seam repair at shared boulder foliage boundary','globalContextBox':[box[0]+16269,box[1]+53133,box[2]+16269,box[3]+53133],'pairContextBox':box,'expectedNativeDimensions':[1254,1254]},'references':rlist,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'rulesRead':{'agents':sha(Path('D:/work/image/AGENTS.md')),'split':sha(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'))}}
write(Z/f'native/{stem}.request.json',req);(Z/f'native/{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
job={'id':'foliage','stem':stem,'contextBox':box,'repairBounds':[320,0,850,1254],'margin':65,'source':ref(source),'prompt':prompt,'references':[r['path'] for r in rlist]}
write(Q/'r14c05-c06-foliage-repair-job-v1.json',job)
write(Q/'pair-r14c05-r14c06-v1-art-audit-v1.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'repair_required','trace':ref(Q/'pair-r14c05-r14c06-v1-trace.json'),'qaViewedNative':t['qa'],'issues':[{'id':'lower-rock-foliage-vertical-cut','severity':'required','description':'Straight source boundary around pair context x4096 cuts rock/leaf continuity in lower section; visible part05 x230.'}],'internalAuditsReused':[ref(Q/'r14_c05-internal-visual-audit-v1.json'),ref(Q/'pair-r14c06-r14c07-v3-art-audit-v1.json')],'formalAcceptance':False})
print(json.dumps(job))

