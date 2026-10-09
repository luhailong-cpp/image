from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/final-rail-insertion';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
S=T/'repairs/final-west-joint/candidate.png';W=R/'r07_c15/output/r07_c15.png';SO=R/'r08_c16/output/r08_c16.png';SW=R/'r08_c15/output/r08_c15.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
EXPECTED={S:'9fc40b0c5a545f92f921e200f01a3c3e3633343ece3ed89aab0e9ea5c2766d30',W:'4e9e6677f9f456422de5d1acceb359d63bd8908656784f44c30acc20118eff4b',SO:'3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de',SW:'70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'}
def prepare():
 for p,s in EXPECTED.items():assert sha(p)==s
 D.mkdir(parents=True,exist_ok=True);assert not (D/'input.png').exists()
 im=Image.new('RGB',(1254,1254))
 for p,box,origin in [(W,(4020,3428,4096,4096),(0,0)),(S,(0,3428,1178,4096),(76,0)),(SW,(4020,0,4096,586),(0,668)),(SO,(0,0,1178,586),(76,668))]:im.paste(Image.open(p).convert('RGB').crop(box),origin)
 im.save(D/'original-crop.png');rgba=np.asarray(im.convert('RGBA')).copy();rgba[595:657,596:670,3]=0;Image.fromarray(rgba).save(D/'input.png')
 meta=dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),sourceRectInFourTilePairXYXY=[4020,3428,5274,4682],sourceRectRelativeC16XYXY=[-76,3428,1178,4682],rawSourceRGBSha256=hashlib.sha256(im.tobytes()).hexdigest(),originalCrop=dict(file=str(D/'original-crop.png'),sha256=sha(D/'original-crop.png')),derivedFrom=[dict(file=str(p),sha256=s) for p,s in EXPECTED.items()],transparentHoleNativeXYXY=[596,595,670,657],transparentHoleC16XYXY=[520,4023,594,4085],immutableBottomRows=[668,1254],resized=False,operation='Exact native1254 four-tile crop with small transparent hole across known rail highlight insertion step.')
 js(D/'input.png.generation.json',meta)
 prompt='Precise local repair of IMAGE1, a native1254 map crop with a small transparent hole centered near x633,y626. Fill only that hole. It removes a few-pixel step in the UPPER beveled bright edge of the existing straight diagonal orange wooden rail. Reconnect that SAME rail contour and long bright bevel as one natural continuous straight edge through the missing area, matching the visible endpoints on BOTH sides. Preserve the rail width, axis, lower face, original shading and existing wood planes. Do not introduce a bend, notch, second bright stripe, dark line, extra grain, new rope or new object. Preserve the blue surface immediately above the edge without new texture. All opaque pixels outside the small hole are fixed context. The entire lower586 rows, local y668..1253, are immutable finished adjacent tiles and must remain exactly as shown. Do not move or repaint the cream rope, existing gold wrapping, blue cloth, or any wood outside the hole. IMAGE2 is the confirmed bright clean rounded Q-style finish only; no UI. Output one fully opaque native1254x1254 corrected IMAGE1, unchanged camera, crop and pixel scale. No blur, resampling, upscaling, global color changes, added detail or text.'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');refs=[dict(file=str(D/'input.png'),sha256=sha(D/'input.png'),role='native target, small transparent rail-edge hole only'),dict(file=str(STYLE),sha256=sha(STYLE),role='confirmed Q-style finish reference only')];js(D/'references.json',refs);print(json.dumps(dict(prompt=prompt,references=[x['file'] for x in refs])))
def record(source):
 source=Path(source);out=D/'edited-native.png';assert not out.exists()
 with Image.open(source) as im:assert im.size==(1254,1254)
 shutil.copyfile(source,out);refs=load(D/'references.json')
 js(Path(str(out)+'.generation.json'),dict(file=str(out),sha256=sha(out),width=1254,height=1254,format='PNG',generatedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=load(R.parents[3]/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[x['file'] for x in refs]),actualModel=None,actualQuality=None,unverifiedReason='Host tool exposes neither model/quality selectors nor returned model/quality evidence.',evidence=dict(toolResultSourcePath=str(source),toolResultSha256=sha(source)),prompt=str(D/'prompt.txt'),promptSha256=sha(D/'prompt.txt'),references=refs,resizedAfterGeneration=False,finalArtUpscaled=False,formalAccepted=False))
 print(json.dumps(dict(file=str(out),sha256=sha(out))))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='record':record(sys.argv[2])
