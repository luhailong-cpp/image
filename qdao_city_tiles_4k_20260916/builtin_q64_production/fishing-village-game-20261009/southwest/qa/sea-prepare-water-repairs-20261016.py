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
t=json.loads((Q/'pair-r14c06-r14c07-v1-trace.json').read_text())
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
jobs=[]
with Image.open(t['context']['path']) as im:
 for n,y in enumerate([0,1024,2048,3072],1):
  name=f'water{n}';stem=f'r14_c06_c07_join_water{n}_repair_v1';box=[3584,y,4838,y+1254]
  source=Q/f'r14c06-c07-{name}-source-native-v1.png';assert not source.exists();im.crop(box).save(source)
  prompt='Use case: precise-object-edit. Image 1 is an exact native 1254x1254 crop from the shared edge of two existing game-map tiles. Repair the artificial vertical wavy join through the central column around x550..730, which currently divides smaller darker water ripples on the left from larger lighter ripples on the right. Repaint only a narrow central transition region x330..940 so both sides become a single coherent stretch of turquoise seawater: match the existing round ripple rhythm naturally across the join, connect the oblique white glints continuously, gradually vary ripple size across the width and eliminate the vertical tone wall. The result must not have a straight or wavy dividing line, patch edge, mirrored pattern, extra thick white foam stripe, or blurred seam. Preserve all existing foam branches, water colour, daylight, framing and perspective. Keep leftmost and rightmost 250 pixels unchanged and preserve the upper and lower edge continuity. Retain crisp detailed Daoist Q hand-painted water with softly shaded blue wave cells and tiny white glints, no dense noise or plastic sheen. Images 2,3,4 are layout/material/approved painterly style references; never copy architecture, UI, figures, night lighting or new objects into this all-water edit. Exactly 1254x1254 native pixels, no resizing, no text or frame, all pixels opaque.'
  rlist=[{**ref(source),'role':'exact native edit target, integer crop from current pair'}]+refs
  req={'stem':stem,'tile':'r14_c06+r14_c07','patch':name,'coordinates':{'role':'localized native shared-water seam repair','globalContextBox':[box[0]+20365,box[1]+53133,box[2]+20365,box[3]+53133],'pairContextBox':box,'expectedNativeDimensions':[1254,1254]},'references':rlist,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
  write(Z/f'native/{stem}.request.json',req)
  (Z/f'native/{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
  jobs.append({'id':name,'stem':stem,'contextBox':box,'repairBounds':[280,0,980,1254],'margin':65,'source':ref(source),'prompt':prompt,'references':[a['path'] for a in rlist]})
write(Q/'r14c06-c07-water-repair-jobs-v1.json',jobs)
write(Q/'pair-r14c06-r14c07-v1-art-audit-v1.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'repair_required','trace':ref(Q/'pair-r14c06-r14c07-v1-trace.json'),'qaViewedNative':t['qa'],'issues':[{'id':'vertical-water-tone-and-scale-transition','severity':'required','description':'Shared seam forms a wavy vertical colour and ripple-size discontinuity; strongest in upper segment, extends along join.'}],'internalAuditsReused':[ref(Q/'r14_c06-internal-visual-audit-v1.json'),ref(Q/'r14_c07-internal-visual-audit-v2.json')],'formalAcceptance':False})
print(json.dumps(jobs))

