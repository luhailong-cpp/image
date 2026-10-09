from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np
from PIL import Image
import assembly_r07_c16 as a
R=Path(__file__).resolve().parent;D=R/'r07_c16/repairs/south-spar-edit';N=R/'r07_c16/repairs/south-thin/candidate.png';S=R/'r08_c16/output/r08_c16.png'
NS='2a527f5e6fa7f35cc7dda8a9abf716a1c6847e1ea463e390fcdb8b8d010e85e2';SS='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png';BOX=[1250,3469,2504,4723];ROI=[1400,3800,1650,4050]
def ref(p,role):return dict(file=str(p),sha256=a.sha(p),role=role)
if sys.argv[1]=='prepare':
 assert a.sha(N)==NS and a.sha(S)==SS;D.mkdir(parents=True,exist_ok=True)
 pair=Image.new('RGB',(4096,8192));pair.paste(Image.open(N),(0,0));pair.paste(Image.open(S),(0,4096));im=pair.crop(BOX);info=a.save_image(D/'input.png',im)
 a.save_json(D/'input.png.generation.json',dict(info,derivedFrom=[ref(N,'editable north candidate'),ref(S,'immutable finished south core')],sourceRectInPairXYXY=BOX,rawSourceRGBSha256=hashlib.sha256(np.asarray(im).tobytes()).hexdigest(),intendedRepairRectsXYXY=[ROI],operation='exact native vertical joint crop; no transform'))
 prompt='Surgical correction of IMAGE 1, one native1254 square. Everything is already correct except one tiny compositing step on the lower silhouette of the diagonal wooden spar in the left area, near local x250,y470. The SAME brown wooden spar runs from lower left to its golden wooden collar near x330,y300. Its lower edge currently has a little stair/notch at x250,y470. Smoothly reconnect that existing straight/slightly rounded diagonal contour through the tiny notch, over x160..400 and y350..580, preserving its existing width, material, location and golden edge shading. Do not alter the collar or the rope. The current diagonal gold rope is ALREADY correct in thickness and endpoint. Keep ALL rope pixels and their twist spacing exactly unchanged. The wooden collar is already correct. Keep it unchanged. Keep all areas outside the small spar-edge repair unchanged, including all pixels below y600. Keep quiet cyan water unchanged: no new texture, ripples, caustics, objects or colors. IMAGE2 is the confirmed bright clean rounded Q style reference only; add no UI. No crop, resize, rotation, blur or global color adjustment. Return one opaque original1254x1254 image with only the tiny spar silhouette notch repaired.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');a.save_json(D/'references.json',[str(D/'input.png'),str(STYLE)]);print(json.dumps({'prompt':prompt,'references':[str(D/'input.png'),str(STYLE)]}))
else:
 src=Path(sys.argv[2]);im=Image.open(src);assert im.size==(1254,1254);dst=D/'edited-native.png';shutil.copyfile(src,dst);refs=[ref(D/'input.png','native local spar repair target'),ref(STYLE,'confirmed style')]
 a.save_json(Path(str(dst)+'.generation.json'),dict(file=str(dst),sha256=a.sha(dst),width=1254,height=1254,format='PNG',route='builtin',tool='image_gen.imagegen',generatedAt=a.utc_now(),configSnapshot=a.load_json(R.parents[3]/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,referenced_image_paths=[r['file'] for r in refs],transparent_background=False),actualModel=None,actualQuality=None,prompt=str(D/'prompt.txt'),promptSha256=a.sha(D/'prompt.txt'),references=refs,evidence=dict(toolResultSourcePath=str(src),toolResultSha256=a.sha(src),selectorsExposed=False,modelQualityReturned=False),resizedAfterGeneration=False,finalArtUpscaled=False))
 print(json.dumps({'file':str(dst),'sha256':a.sha(dst)}))
