from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;ROOT=T.parent;R=T/'repairs/wood-color-final'
BASE=T/'water-repaired/output/r08_c14.png';EXPECT='02319f7664c691de68d1f4ccfbb6d9661642653548ff3dc51a66a156f2765d5b'
CROP=[397,1421,1651,2675];ROI=[900,1900,1140,2320]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,im,m):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p);r={**ref(p),'pixels':list(im.size),**m};write(str(p)+'.generation.json',r);return r
def prepare():
 assert sha(BASE)==EXPECT
 day=ROOT.parent/'donghai_day/tiles/r08_c14.png';style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
 f=save(R/'festival-target.png',Image.open(BASE).convert('RGB').crop(CROP),{'source':ref(BASE),'cropXYXY':CROP,'resized':False})
 d=save(R/'day-geometry.png',Image.open(day).convert('RGB').crop(CROP),{'source':ref(day),'cropXYXY':CROP,'resized':False})
 refs=[{**f,'role':'edit target; festival geometry and warm tones'},{**d,'role':'same window DAY geometry only'},{**ref(style),'role':'confirmed Q hand-painted rendering style only'}]
 prompt='Use case: precise-object-edit. Edit image 1, an exact 1254 by 1254 native crop of the Lantern Festival fishing-village game map. Remove ONLY the artificial nearly vertical jagged color discontinuity crossing the horizontal wooden railing and dock planks at crop x~610-660, y~500-850. This is a patch-paste lighting/paint seam: the continuous boards become abruptly warmer on the right in a wavy vertical cutoff. Repaint that small color boundary to form natural smoothly continuous orange-brown wooden shading and continuous horizontal wood brush strokes across the seam. Keep every plank edge, black joint, bevel, wood grain structure, shadow contour, basket, water boundary, railing silhouette and object position exactly unchanged. Image 2 is only the same-window DAY geometry reference; do not copy its daytime color or alter geometry to match its lighting. Image 3 is only the confirmed rounded, rich, clean hand-painted Daoist Q style; do not add UI elements. Preserve the festival target colors and warm highlights everywhere else. Correct paint continuity only, without adding a line, new joint, crack, band, object, lantern, text, blur, camera change, resizing, zoom, sharpening or global tint. Output one opaque native 1254 by 1254 image with precisely the same field of view. The only authorized change is local color/brushwork continuity in the narrow vertical defect across the wood.'
 write(R/'references.json',refs);(R/'prompt.txt').write_text(prompt,encoding='utf8');write(R/'request.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False});print(json.dumps(read(R/'request.json')))
def record(raw):
 raw=Path(raw);p=R/'native.png';assert not p.exists();assert Image.open(raw).size==(1254,1254);shutil.copyfile(raw,p)
 write(str(p)+'.generation.json',{**ref(p),'pixels':[1254,1254],'generatedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**read(R/'request.json')},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no actual model/quality metadata or selector.','evidence':{'toolResultSourcePath':str(raw),'sha256':sha(raw)},'prompt':ref(R/'prompt.txt'),'references':read(R/'references.json'),'resizedAfterGeneration':False,'geometryChangeAllowed':False})
 print(json.dumps(ref(p)))
def patch():
 assert sha(BASE)==EXPECT
 base=Image.open(BASE).convert('RGB');n=np.asarray(Image.open(R/'native.png').convert('RGB'));x,y,_,_=CROP;l,t,r,b=ROI
 yy,xx=np.mgrid[:1254,:1254];d=np.minimum.reduce((xx+x-l,yy+y-t,r-1-xx-x,b-1-yy-y)).astype(np.float32);a=np.clip(d/48,0,1);a=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
 m=save(R/'integration-mask.png',Image.fromarray(a),{'operation':'48px local smoothstep return','cropXYXY':CROP,'roiXYXY':ROI})
 old=np.asarray(base.crop(CROP));v=((old.astype(np.uint32)*(255-a[:,:,None])+n.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
 output=save(R/'patched-window.png',Image.fromarray(v),{'derivedFrom':[ref(BASE),ref(R/'native.png')],'mask':m,'cropXYXY':CROP,'roiXYXY':ROI,'outsideMaskPixelIdentical':bool(np.array_equal(v[a==0],old[a==0]))})
 full=base.copy();full.paste(Image.fromarray(v),(x,y));qa=[]
 for name,box in {'full1254':CROP,'left':[l-96,t-96,l+96,b+96],'right':[r-96,t-96,r+96,b+96],'top':[l-96,t-96,r+96,t+96],'bottom':[l-96,b-96,r+96,b+96]}.items():qa.append(save(R/'qa'/(name+'.png'),full.crop(box),{'cropXYXY':box,'resized':False,'fromWindow':output}))
 write(R/'integration.json',{'base':ref(BASE),'native':ref(R/'native.png'),'mask':m,'cropXYXY':CROP,'roiXYXY':ROI,'patchedWindow':output,'qa':qa,'geometryChangeAllowed':False,'formalAccepted':False})
 print(json.dumps(output))
if __name__=='__main__':{'prepare':prepare,'record':lambda:record(sys.argv[2]),'patch':patch}[sys.argv[1]]()
