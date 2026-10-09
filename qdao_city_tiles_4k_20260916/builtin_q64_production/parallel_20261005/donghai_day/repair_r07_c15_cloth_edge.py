from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified/south-straight/s4-cloth-edge';SRC=D.parent/'s4-clean-cloth/edited-native.png';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
 D.mkdir(parents=True,exist_ok=True);assert not (D/'input.png').exists()
 im=Image.open(SRC).convert('RGBA');assert im.size==(1254,1254);rgb=np.asarray(im)[:,:,:3].astype(np.int16)
 water=(rgb[:,:,2]>rgb[:,:,0]+30)&(rgb[:,:,1]>rgb[:,:,0]+15)
 eligible=np.asarray(Image.fromarray((water*255).astype(np.uint8)).filter(ImageFilter.MinFilter(17)))
 hole=np.zeros((1254,1254),np.uint8);hole[750:905,900:1254]=eligible[750:905,900:1254]
 pixels=np.asarray(im).copy();pixels[hole>0,3]=0;Image.fromarray(pixels).save(D/'input.png');Image.fromarray(hole).save(D/'repair-mask.png')
 js(D/'input.png.generation.json',dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),sourceFile=str(SRC),sourceSha256=sha(SRC),sourceRecordSha256=sha(Path(str(SRC)+'.generation.json')),rawSourceRGBSha256=hashlib.sha256(Image.open(SRC).convert('RGB').tobytes()).hexdigest(),resized=False,operation='Native target with transparent small cloth-only hole; eight-pixel erosion protects rope and wood edges.',mask=dict(file=str(D/'repair-mask.png'),sha256=sha(D/'repair-mask.png')),allowedNativeRectXYXY=[900,750,1254,905],sourcePlacementInSouthPairXYXY=[2842,3140,4096,4394]))
 prompt='Precise local edit of IMAGE1, an original1254x1254 game-map crop. Fill ONLY the small transparent hole in the blue canopy cloth near the right edge. This hole removes an accidental hard horizontal cut at original y841 in the cloth shading beneath the orange rope. Reconnect the SAME broad curved blue cloth folds and existing soft rope-shadow/shading through that hole so no artificial horizontal step, cut reflection, rectangular color patch or discontinuous shadow remains. The cloth is a quiet smooth broad turquoise/blue surface: do not create fine ripples, grain, noise, mesh, wrinkles, stripes, new bright highlights, extra shadow or objects. Preserve the orange rope contour and its existing soft shadow, preserve the wooden frame and beam, and preserve every opaque pixel outside the hole as faithfully as possible. No material or lighting change. IMAGE2 is the confirmed bright clean rounded Q-style rendering quality only; do not introduce UI. Output a fully opaque1254x1254 version of IMAGE1, same camera, composition, crop and pixel scale. No registration, resampling, blur, sharpening, new decoration or text.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),role='native1254 edit target; only cloth material hole editable'),dict(file=str(STYLE),sha256=sha(STYLE),role='primary confirmed bright rounded Q-style reference')];js(D/'references.json',refs)
 print(json.dumps(dict(prompt=prompt,references=[x['file'] for x in refs])))
def record(src):
 src=Path(src);out=D/'edited-native.png';assert not out.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,out);refs=load(D/'references.json')
 js(Path(str(out)+'.generation.json'),dict(file=str(out),sha256=sha(out),width=1254,height=1254,format='PNG',generatedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=load(R.parents[3]/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[x['file'] for x in refs]),actualModel=None,actualQuality=None,unverifiedReason='Host built-in tool exposes neither model/quality selectors nor returned model/quality metadata.',evidence=dict(toolResultSourcePath=str(src),toolResultSha256=sha(src)),prompt=str(D/'prompt.txt'),promptSha256=sha(D/'prompt.txt'),references=refs,resizedAfterGeneration=False,finalArtUpscaled=False,formalAccepted=False))
 print(json.dumps(dict(file=str(out),sha256=sha(out))))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':record(sys.argv[2])
