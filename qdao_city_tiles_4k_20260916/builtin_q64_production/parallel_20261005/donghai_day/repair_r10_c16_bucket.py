from pathlib import Path
import json,hashlib,sys,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parent;T=R/'r10_c16';D=T/'repairs/internal-bucket';S=T/'repairs/internal-color-match/candidate.png';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
 assert sha(S)=='83bda970e93c68ad09a5eb6fe76b432b3fc343b16e0515bda0659261608ca0f4'
 D.mkdir(exist_ok=True);assert not (D/'input.png').exists()
 im=Image.open(S).convert('RGB').crop((500,500,1754,1754));im.save(D/'original-crop.png');arr=np.asarray(im).astype(np.int16);water=(arr[:,:,2]>arr[:,:,0]+35)&(arr[:,:,1]>arr[:,:,0]+12)
 eligible=np.asarray(Image.fromarray(water.astype(np.uint8)*255).filter(ImageFilter.MinFilter(5)))
 Image.fromarray(eligible).save(D/'water-only-eligibility.png');hole=np.zeros((1254,1254),bool);hole[210:545,580:760]=True;hole&=eligible>0
 rgba=np.asarray(im.convert('RGBA')).copy();rgba[hole,3]=0;Image.fromarray(rgba).save(D/'input.png')
 js(D/'input.png.generation.json',dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),source=dict(file=str(S),sha256=sha(S)),sourceRectXYXY=[500,500,1754,1754],rawSourceRGBSha256=hashlib.sha256(im.tobytes()).hexdigest(),transparentHoleRequestedNativeXYXY=[580,210,760,545],transparentHoleWaterOnly=True,minimumCoreY=710,originalCrop=dict(file=str(D/'original-crop.png'),sha256=sha(D/'original-crop.png')),eligibility=dict(file=str(D/'water-only-eligibility.png'),sha256=sha(D/'water-only-eligibility.png')),resized=False))
 prompt='Edit IMAGE1 exactly in its native1254x1254 crop. Repair only the small transparent WATER region inside the existing wooden bucket. A straight vertical guide-strip color boundary runs down through the blue water near native x662 and must disappear. Reconnect the same calm blue water color, gentle broad reflection/shadow and existing partially submerged wooden pole reflection naturally across that line. Preserve the pale reflections at the left and preserve the dark existing pole reflection shape and placement; only make its fade and water shading continuous. No new ripple, extra foam, fine waves, grid, texture, fish or object. Keep the entire bucket circular rim, metal bands, timber staves, wood post, rope and surrounding floor exactly as shown. The hole is water only x580..759,y210..544; all opaque pixels are fixed anchors. No changes above y200. IMAGE2 is the confirmed bright clean rounded Q-style rendering reference only, no UI elements. Output one fully opaque native1254x1254 corrected IMAGE1 at unchanged crop, viewpoint, pixel scale, colors and lighting. No blur, resizing, upscaling, sharpening, registration, extra detail or text.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),role='native target water-only narrow guide-strip repair hole'),dict(file=str(STYLE),sha256=sha(STYLE),role='confirmed bright clean rounded Q style')];js(D/'references.json',refs);print(json.dumps(dict(prompt=prompt,references=[x['file'] for x in refs])))
def record(source):
 p=Path(source);o=D/'edited-native.png';assert not o.exists();assert Image.open(p).size==(1254,1254);shutil.copyfile(p,o);refs=load(D/'references.json')
 js(Path(str(o)+'.generation.json'),dict(file=str(o),sha256=sha(o),width=1254,height=1254,format='PNG',generatedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=load(R.parents[3]/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[x['file'] for x in refs]),actualModel=None,actualQuality=None,unverifiedReason='Host tool does not expose model/quality selector or actual returned evidence.',evidence=dict(toolResultSourcePath=str(p),toolResultSha256=sha(p)),prompt=str(D/'prompt.txt'),promptSha256=sha(D/'prompt.txt'),references=refs,resizedAfterGeneration=False,finalArtUpscaled=False,formalAccepted=False))
 print(json.dumps(dict(file=str(o),sha256=sha(o))))
if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else record(sys.argv[2])
