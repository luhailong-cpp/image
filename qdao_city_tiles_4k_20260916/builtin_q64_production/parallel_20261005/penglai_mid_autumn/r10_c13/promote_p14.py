from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r10_c13';n=f/'native';q=f/'repairs/p14-surface'
assert not (n/'p24.request.json').exists(),'Refuse changing a dependency already consumed.'
old=read(q/'input-history.generation.json');assert sha(n/'p14.png')==old['sha256']==sha(q/'input.png')
old['file']=str(q/'input.png');old['formerFile']=str(n/'p14.png');old['status']='superseded_surface_brush_density';write(q/'input-history.generation.json',old)
c=read(q/'call.json');pp=q/'prompt.txt';pp.write_text(c['prompt'],encoding='utf-8')
s=Path('C:/Users/luyua/.codex/generated_images/01a10ba7-d61e-7742-870d-85174acc5a1e/exec-5452aee4-7ca5-4ad8-b6ae-ef9be64e051e.png');assert Image.open(s).size==(1254,1254)
dst=n/'p14.png';shutil.copy2(s,dst)
r=dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**c),actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin lacks model/quality selectors and returned metadata.',evidence=dict(sourceOutputPath=str(s),sourceOutputSha256=sha(s),resultId=s.stem),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=p,sha256=sha(p)) for p in c['referenced_image_paths']],globalPatchXYWH=old['globalPatchXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,status='native_detail_pending_full_seam_QA',formalAccepted=False,supersedes=dict(sha256=old['sha256'],record=str(q/'input-history.generation.json')),rootVisualReview=dict(checkedAt=now(),actuallyViewed=True,scope='crop/geometry/style only',result='Same stone boundaries and crop retained, fine mosaic reduced to calmer broad painted planes; full seams pending.'))
write(str(dst)+'.generation.json',r);print(r['sha256'])
