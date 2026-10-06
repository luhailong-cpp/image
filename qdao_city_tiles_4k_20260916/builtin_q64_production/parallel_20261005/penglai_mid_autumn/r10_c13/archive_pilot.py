from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r10_c13';n=f/'native';a=f/'pilot-transparent';a.mkdir(exist_ok=True)
for p in n.iterdir():
    if p.is_file():shutil.copy2(p,a/p.name)
source=Path('C:/Users/luyua/.codex/generated_images/01a10ba7-d61e-7742-870d-85174acc5a1e/exec-275ecf6d-6b92-4fde-bac1-1cc82d187b4b.png')
out=a/'p11-rejected.png';assert not out.exists();shutil.copy2(source,out)
r=read(a/'p11.request.json');r['prompt']=str(a/'p11.prompt.txt')
r['references'][0]['file']=str(a/'p11-context.png')
rec=dict(file=str(out),sha256=sha(out),generatedAt=now(),width=1254,height=1254,tool='image_gen.imagegen',route='builtin',configSnapshot=r['configSnapshot'],submittedParameters=r['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed; no model/quality selectors or returned metadata.',evidence=dict(sourceOutputPath=str(source),sourceOutputSha256=sha(source)),prompt=r['prompt'],promptSha256=sha(r['prompt']),references=r['references'],status='rejected_geometry_and_crop_drift',reason='Completed left lower eave corner and added foliage where exact structure guide continues roof beyond the frame; visible context and framing changed.',sourceUpscaled=False,productionPixels=False,formalAccepted=False)
write(str(out)+'.generation.json',rec)
write(a/'review.json',dict(checkedAt=now(),actuallyViewed=True,accepted=False,rootDecision=rec['reason'],nextMethod='Full same-frame layout with native strips composited into edit target; no transparent hole.'))
print(str(out))
