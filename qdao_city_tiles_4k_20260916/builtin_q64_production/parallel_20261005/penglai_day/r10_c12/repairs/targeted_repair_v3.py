from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib,datetime,shutil,sys
import numpy as np
D=Path(__file__).resolve().parent
V='v5'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
SOURCE=D/'r10_c12-candidate-v2.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
CONFIG=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
SPECS={'wood1024': {'box':[2023,473,3277,1727],'axis':'y','localSeam':551},'wood2048':{'box':[2813,1421,4067,2675],'axis':'y','localSeam':627},'wood3072':{'box':[793,2445,2047,3699],'axis':'y','localSeam':627}}
SPECS['roof1024']={'box':[2842,397,4096,1651],'axis':'y','localSeam':627}
def prepare():
 im=Image.open(SOURCE)
 for name,s in SPECS.items():
  dst=D/(name+'-input-v3.png');im.crop(s['box']).save(dst)
  write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'derivedFrom':[{'file':str(SOURCE),'sha256':sha(SOURCE),'record':str(D/'candidate-record-v2.json')}],'operation':'exact integer crop; no resize','crop':s['box'],'nativePixels':[1254,1254]})
  prompt=f"Use case: precise-object-edit. Asset: native-resolution game-map seam repair. Image 1 is the exact edit target; image 2 is the approved PRIMARY STYLE reference only. Preserve image 1's exact full square framing, all geometry, every object position, contours, material colours and illumination. Heal ONLY the accidental processing seam across native horizontal row y={s['localSeam']} in image 1: tiny stepped contours and abruptly interrupted painted wood highlights where the upper and lower native tiles joined. Continue each existing wood face and highlight smoothly across this row without adding wood joints, cracks or changing its physical shape. Preserve the roof, canopy stripe order, ropes, pottery, foliage and paving wherever present. Restrict edits to the narrow band within about 70 pixels above/below that row; everything outside stays identical. Existing distinct beam joints stay in place. For smooth surfaces continue the existing small clean painterly brushwork, no flat smudging. Bright rounded clean Taoist Q handpainted game art matching the approved reference's quality and image 1's already-established material. No new objects, UI, text, border or watermark. No zoom, rotation, warp, camera change or whole-image relighting. Exact same 1254-square native crop."
  (D/(name+'-v3.prompt.txt')).write_text(prompt,encoding='utf-8')
  write(D/(name+'-v3.call.json'),{'prompt':prompt,'referenced_image_paths':[str(dst).replace('\\','/'),str(STYLE)],'transparent_background':False})
def ingest(name,src):
 src=Path(src);dst=D/(name+'-ai-v3.png');shutil.copy2(src,dst)
 call=json.loads((D/(name+'-v3.call.json')).read_text(encoding='utf-8'))
 im=Image.open(dst);im.verify()
 rec={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'generatedAtEvidence':'local tool output mtime; service timestamp unavailable','width':im.width,'height':im.height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','toolResultPath':str(src),'configSnapshot':CONFIG,'submittedParameters':dict(call,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selectors or returned model/quality metadata.','prompt':str(D/(name+'-v3.prompt.txt')),'evidence':str(D/(name+'-v3.tool-result.json')),'references':[{'file':p,'sha256':sha(p),'role':'exact native edit target' if i==0 else 'approved primary painting style'}for i,p in enumerate(call['referenced_image_paths'])]}
 write(str(dst)+'.generation.json',rec)
 print(json.dumps({'file':str(dst),'sha256':sha(dst),'pixels':im.size}))
def combine():
 im=Image.open(SOURCE).convert('RGB');out=np.array(im);records=[];Q=D/('qa-'+V);Q.mkdir(exist_ok=True)
 # Local rectangular masks are returned only in matching native context. All y<900 remain byte-identical.
 masks={'wood1024':[(670,427,862,714,10,28)],'wood2048':[(666,490,885,790,10,36),(143,261,278,405,28,28)],'roof1024':[(478,535,720,730,30,30),(810,518,1040,714,30,30)]}
 for name,rects in masks.items():
  s=SPECS[name];p=D/(name+'-ai-v3.png');a=np.array(Image.open(p).convert('RGB'),dtype=np.float32);old=np.array(Image.open(D/(name+'-input-v3.png')).convert('RGB'),dtype=np.float32)
  h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w];alpha=np.zeros((h,w),np.float32)
  for x0,y0,x1,y1,fx,fy in rects:
   dist=np.minimum.reduce([(xx-x0)/fx,(yy-y0)/fy,(x1-xx)/fx,(y1-yy)/fy])
   t=np.clip(dist,0,1);alpha=np.maximum(alpha,t*t*(3-2*t))
  alpha[s['box'][1]+np.arange(h)<900]=0
  x0,y0,x1,y1=s['box'];dst=out[y0:y1,x0:x1].astype(np.float32);mix=np.rint(dst*(1-alpha[:,:,None])+a*alpha[:,:,None]).astype(np.uint8);out[y0:y1,x0:x1]=mix
  mp=D/(name+'-'+V+'-mask.npz');np.savez_compressed(mp,alphaAI=alpha)
  rect=(min(r[0]for r in rects)-30,min(r[1]for r in rects)-30,max(r[2]for r in rects)+30,max(r[3]for r in rects)+30)
  oldim=Image.fromarray(old.astype(np.uint8)).crop(rect);newim=Image.fromarray(mix).crop(rect);board=Image.new('RGB',(oldim.width*2,oldim.height+24),'#303030');board.paste(oldim,(0,24));board.paste(newim,(oldim.width,24));ImageDraw.Draw(board).text((4,4),'before / after native 1:1',fill='white');qp=Q/(name+'-before-after-native.png');board.save(qp)
  records.append({'source':str(p),'sourceSHA256':sha(p),'sourceRecord':str(p)+'.generation.json','globalCrop':s['box'],'mask':str(mp),'maskSHA256':sha(mp),'rectangles':rects,'operation':'same-coordinate native pixels; smoothstep alpha only in bounded rectangle returns; no resize, displacement, added color field or image blur','qa':str(qp),'actuallyViewed':False})
 dst=D/('r10_c12-candidate-'+V+'.png');Image.fromarray(out).save(dst)
 original=np.array(im);changed=np.any(original!=out,axis=2);ys,xs=np.where(changed)
 write(D/('candidate-record-'+V+'.json'),{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(dst),'sha256':sha(dst),'pixels':[4096,4096],'derivedFrom':[{'file':str(SOURCE),'sha256':sha(SOURCE),'record':str(D/'candidate-record-v2.json')}],'repairs':records,'changedPixelCount':int(changed.sum()),'changedXYXY':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'rowsBefore900Unchanged':bool(not changed[:900].any()),'formalAccepted':False,'clientAccepted':False})
 print(json.dumps({'file':str(dst),'sha256':sha(dst),'changedPixels':int(changed.sum()),'minY':int(ys.min())}))
def qa():
 im=Image.open(D/('r10_c12-candidate-'+V+'.png')).convert('RGB');Q=D/('qa-'+V);Q.mkdir(exist_ok=True);entries=[]
 for axis in ['x','y']:
  for v in [1024,2048,3072]:
   crop=im.crop((v-160,0,v+160,4096))if axis=='x'else im.crop((0,v-160,4096,v+160)).transpose(Image.Transpose.ROTATE_90)
   s=Image.new('RGB',(1280,1048),'#303030');draw=ImageDraw.Draw(s)
   for i in range(4):
    s.paste(crop.crop((0,i*1024,320,(i+1)*1024)),(i*320,24));draw.text((i*320+2,3),f'{axis}{v} part{i+1} native',fill='white')
   p=Q/f'{axis}{v}-full-native.png';s.save(p);entries.append({'file':str(p),'sha256':sha(p),'scale':'1:1','scope':f'full4096 {axis}{v} +/-160','actuallyViewed':False})
 s=Image.new('RGB',(1152,1224),'#303030');draw=ImageDraw.Draw(s)
 for ri,y in enumerate([1024,2048,3072]):
  for ci,x in enumerate([1024,2048,3072]):
   s.paste(im.crop((x-192,y-192,x+192,y+192)),(ci*384,ri*408+24));draw.text((ci*384+3,ri*408+3),f'junction{x},{y} native',fill='white')
 p=Q/'nine-junctions-native.png';s.save(p);entries.append({'file':str(p),'sha256':sha(p),'scale':'1:1','scope':'nine junctions','actuallyViewed':False})
 im.resize((1254,1254),Image.Resampling.LANCZOS).save(D/('preview-'+V+'.png'))
 rec=json.loads((D/('candidate-record-'+V+'.json')).read_text(encoding='utf-8'));rec['qa']=entries
 write(D/('candidate-record-'+V+'.json'),rec)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='combine':combine()
 elif sys.argv[1]=='qa':qa()
