from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np
from PIL import Image
import assembly_r08_c16 as a
R=Path(__file__).resolve().parent;D=R/'r08_c16/repairs/west-rail-second';S=R/'r08_c16/repairs/integrated-v2/candidate.png';SHA='25036828e7d9b8e26ffc022cf5ac9719a18c0701004e92e5000eb200a56a04f4'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png';BOX=[300,1900,1554,3154];ROI=[590,2370,1040,2840]
def ref(p,role):return dict(file=str(p),sha256=a.sha(p),role=role)
if sys.argv[1]=='prepare':
 assert a.sha(S)==SHA;D.mkdir(parents=True,exist_ok=True);im=Image.open(S).convert('RGB').crop(BOX);info=a.save_image(D/'input.png',im)
 a.save_json(D/'input.png.generation.json',dict(info,source=ref(S,'frozen integrated v2 candidate'),sourceRectXYXY=BOX,rawSourceRGBSha256=hashlib.sha256(np.asarray(im).tobytes()).hexdigest(),intendedRepairRectsXYXY=[ROI],operation='exact native crop; no transform'))
 prompt='Precise localized seam edit of IMAGE 1. Keep this original1254 square image composition, colors and exact object outlines everywhere except a narrow band local x300..650 around the obvious zigzag artificial splice in the gold front rail, around local y600..870. Correct the step locally by smoothly connecting BOTH fixed endpoints of the SAME golden boat rail. LEFT rail at local x280 and RIGHT rail at local x680 are both immutable endpoints: match their current top contour, highlighted bevel and bottom contour EXACTLY. Do NOT flatten or tilt the whole rail, do NOT move or thicken the rail outside that small central band. Preserve the natural slanted shape and the true rounded joint at local x600..730; do not invent any splice. Preserve every pixel outside local x280..740,y480..980 as closely as possible. The narrow blue panel immediately below the step must also reconnect without a notch. Leave the rope, lantern, tall mast, diagonal upper beam, and all other surrounding shapes untouched. IMAGE 2 is only the established bright clean rounded Q-style material reference, no UI. No global relighting, no new decoration, no texture additions, blur, crop or resampling. Output one opaque1254x1254 image.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');a.save_json(D/'references.json',[str(D/'input.png'),str(STYLE)]);print(json.dumps({'prompt':prompt,'references':[str(D/'input.png'),str(STYLE)]}))
else:
 src=Path(sys.argv[2]);im=Image.open(src);assert im.size==(1254,1254);dst=D/'edited-native.png';shutil.copyfile(src,dst);refs=[ref(D/'input.png','native repair target'),ref(STYLE,'confirmed style')]
 a.save_json(Path(str(dst)+'.generation.json'),dict(file=str(dst),sha256=a.sha(dst),width=1254,height=1254,format='PNG',route='builtin',tool='image_gen.imagegen',generatedAt=a.utc_now(),configSnapshot=a.load_json(R.parents[3]/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,referenced_image_paths=[r['file'] for r in refs],transparent_background=False),actualModel=None,actualQuality=None,prompt=str(D/'prompt.txt'),promptSha256=a.sha(D/'prompt.txt'),references=refs,evidence=dict(toolResultSourcePath=str(src),toolResultSha256=a.sha(src),selectorsExposed=False,modelQualityReturned=False),resizedAfterGeneration=False,finalArtUpscaled=False))
 print(json.dumps({'file':str(dst),'sha256':a.sha(dst)}))
