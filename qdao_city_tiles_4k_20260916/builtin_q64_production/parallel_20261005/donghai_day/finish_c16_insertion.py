from pathlib import Path
import sys,json,shutil,hashlib
from PIL import Image
import numpy as np
import assembly_r08_c16 as a
R=Path(__file__).resolve().parent;D=R/'r08_c16/repairs/west-insertion-finish';S=R/'r08_c16/repairs/integrated-v1/candidate.png';SHA='019617ff62ad49c348bb9f8113800cf90c3516dd5295e96b09544c4fc519622a'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
BOX=[0,1800,1254,3054];ROI=[340,1900,760,2820]
def ref(p,role):return dict(file=str(p),sha256=a.sha(p),role=role)
if sys.argv[1]=='prepare':
 assert a.sha(S)==SHA;D.mkdir(parents=True,exist_ok=True);im=Image.open(S).convert('RGB').crop(BOX);info=a.save_image(D/'input.png',im)
 a.save_json(D/'input.png.generation.json',dict(info,source=ref(S,'frozen integrated candidate'),sourceRectXYXY=BOX,rawSourceRGBSha256=hashlib.sha256(np.asarray(im).tobytes()).hexdigest(),intendedRepairRectsXYXY=[ROI],operation='exact native crop; no transform'))
 prompt='Use case: precise-object-edit. Repair IMAGE 1 at original 1254x1254 size. This is a finished Q-style fishing boat. There is an artificial jagged insertion seam near local x480..570 across the long GOLDEN HORIZONTAL-DIAGONAL BOAT RAIL, approximately local y600..880. Its golden top edge, bright bevel and dark lower edge jump in height where two patches meet. Reconnect that SAME existing rail into ONE continuous natural curved/diagonal rail, matching endpoint height and thickness to the unchanged rail on both the left and right. Also remove the smaller notches on the upper diagonal beam at the same x500 insertion line, local y70..300, preserving its smooth original diagonal silhouette. Correct the narrow adjacent blue-painted panels where the same seam cuts them. Do not add joints, caps or an extra rail. Keep x0..300 and x800..1253 and top50/bottom180 pixels exactly unchanged. Preserve the entire lantern, rope, posts and diagonal wood beam elsewhere. Make only this small rail seam correction with the same rounded bright clean Q-style wood and blue paint; preserve lighting and shadows and fine existing finish. IMAGE 2 is confirmed material/style reference only, no UI. No layout changes, no new objects, no new texture, no blur/resizing/sharpening/global recolor. Native1254 square opaque output.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');a.save_json(D/'references.json',[str(D/'input.png'),str(STYLE)]);print(json.dumps({'prompt':prompt,'references':[str(D/'input.png'),str(STYLE)]}))
else:
 src=Path(sys.argv[2]);im=Image.open(src);assert im.size==(1254,1254);dst=D/'edited-native.png';shutil.copyfile(src,dst);cfg=a.load_json(R.parents[3]/'config/image-generation.json');refs=[ref(D/'input.png','native repair target'),ref(STYLE,'confirmed style')]
 a.save_json(Path(str(dst)+'.generation.json'),dict(file=str(dst),sha256=a.sha(dst),width=1254,height=1254,format='PNG',route='builtin',tool='image_gen.imagegen',generatedAt=a.utc_now(),configSnapshot=cfg,submittedParameters=dict(model=None,quality=None,referenced_image_paths=[r['file'] for r in refs],transparent_background=False),actualModel=None,actualQuality=None,prompt=str(D/'prompt.txt'),promptSha256=a.sha(D/'prompt.txt'),references=refs,evidence=dict(toolResultSourcePath=str(src),toolResultSha256=a.sha(src),selectorsExposed=False,modelQualityReturned=False),resizedAfterGeneration=False,finalArtUpscaled=False))
 print(json.dumps({'file':str(dst),'sha256':a.sha(dst)}))
