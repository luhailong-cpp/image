from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
check=json.loads((P/'qa/left-neighbor-check.json').read_text());src=Path(check['leftCandidateSource']);assert sha(src)==check['sha256']
canvas=Image.open(P/'guides/full-canvas-layout-only.png').convert('RGB')
canvas.paste(Image.open(src).convert('RGB').crop((4096,0,4326,4096)),(0,0))
out=P/'guides/full-canvas-left-provisional-layout-only.png';canvas.save(out)
plan=json.loads((P/'plan.json').read_text())
for patch in plan['patches']:
 if patch['column']==0:
  assert patch['status']=='pending'
  g=P/'guides'/f"{patch['id']}.left-provisional-layout-only.png";canvas.crop(patch['fullCanvasBox']).save(g)
  patch['guide']=str(g);patch['guideSha256']=sha(g);patch['submittedImages'][0]=str(g);patch['boundaryReady']=False;patch['boundaryStatus']='left_provisional_geometry_bottom_left_intersection_needs_repair'
plan['guidePreparation']['provisionalLeftConstraint']={'source':str(src),'sha256':sha(src),'sourceBoxLTRB':[4096,0,4326,4096],'pasteXY':[0,0],'status':'unreviewed_temporary_geometry_constraint','bottomLeftCornerReworkRequired':True}
plan['guidePreparation']['sharedOverlapChecks']=None
plan['guidePreparation']['allSharedOverlapPixelsIdentical']=None
plan['guidePreparation']['note']='Left guide replacements preserve internal guide overlap but external bottom-left corner has failed exact equality; not QA passed.'
(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print('Four left guides prepared using provisional neighbor geometry; bottom-left corner remains repair-required.')
