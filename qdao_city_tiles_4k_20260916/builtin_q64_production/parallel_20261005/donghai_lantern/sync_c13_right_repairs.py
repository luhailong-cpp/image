"""Convert three actual DAY local edits and replay their exact four-side masks.

Writes only own c13/right-stone-sync. Commands prepare I | record I RAW | compose I.
No geometry optimization, resampling, global state writes or auto acceptance.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
DAY=ROOT.parent/'donghai_day'
DEST=ROOT/'r08_c13/right-stone-sync'
WEST=ROOT/'r08_c13/west-final/output/r08_c12.png'
WEST_SHA='c24b061459e3dc89d45fc101c8ddd9d8606433a35ff8fcc29565bf3cce15ddf6'
EAST=ROOT/'r08_c13/west-final/output/r08_c13.png'
EAST_SHA='68d3edb53d08eeb5474aa9111658f5863abccc5fca212b931258d2d1790999ad'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
TONE=ROOT/'r08_c12/guides/neighbor-tone-native.png'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p,role=None):return {'file':str(Path(p).resolve()),'sha256':sha(p),**({'role':role} if role else {})}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(p,s):assert Path(p).is_file() and sha(p)==s,f'Changed/missing: {p}'
def write(p,obj):
 p=Path(p).resolve();assert p.is_relative_to(DEST.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def img(p):
 im=Image.open(p);im.load();assert im.format=='PNG';return im.convert('RGB')
def save(p,im,meta):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p);r={**info(p),'pixels':list(im.size)};write(str(p)+'.generation.json',{**r,'operation':'native-pixel mechanical crop/composition','resized':False,'generatedByAI':False,'formalAccepted':False,**meta});return r
def base(i):
 check(WEST,WEST_SHA)
 e=EAST if i==1 else DEST/f'step{i-1:02}/output/r08_c13.png'
 s=EAST_SHA if i==1 else read(str(e)+'.generation.json')['sha256'];check(e,s)
 a,b=img(WEST),img(e);assert a.size==b.size==(4096,4096)
 pair=Image.new('RGB',(8192,4096));pair.paste(a,(0,0));pair.paste(b,(4096,0))
 return pair,[info(WEST),info(e)]
def prepare(i):
 assert 1<=i<=3
 d=DAY/f'r08_c13/repairs/right-insertion-stone-{i:02}'
 target=DEST/f'step{i:02}';assert not (target/'native.png').exists()
 dm=read(d/'integration-manifest.json');ir=read(d/'input.png.generation.json')
 for key in ('generatedEdit','generationRecord'):check(dm[key]['file'],dm[key]['sha256'])
 source=img(dm['generatedEdit']['file']);assert source.size==(1254,1254)
 rect=ir['pairRectXYXY'];pair,bs=base(i)
 tone=save(target/'same-window-festival.png',pair.crop(rect),{'pairRectXYXY':rect,'derivedFrom':bs,'finalArt':False,'role':'same-coordinate lighting only; superseded geometry must not be copied'})
 mask_records=[]
 for mm in dm['masks']:
  for key in ('mask','npz'):check(mm[key]['file'],mm[key]['sha256'])
  mask_records.append(mm)
 combined=d/'masks/combined.png';assert combined.is_file()
 refs=[info(dm['generatedEdit']['file'],'PRIMARY DAY repaired geometry; exact edit target'),info(target/'same-window-festival.png','Same-coordinate current festival light/material tone only, not old flawed geometry'),info(STYLE,'Primary confirmed rounded Daoist Q painting style, no UI'),info(TONE,'Established festival rendering sample, lighting only')]
 prompt=f'''Use case: lighting-weather. Asset: 五行奇谈 fishing-village Lantern Festival native map, c13 right insertion repair {i}.
Edit IMAGE 1 into the exact matching festival appearance of IMAGE 2. IMAGE 1 is the exact corrected DAY geometry: preserve every paving slab, curved bevel, diagonal grout line and edge, mottled painted patch, wood contour and shadow silhouette in precisely the same pixel positions, scale and crop. IMAGE 2 is the same world rectangle but its local flawed contours have been superseded: use only its existing warm peach/gold light and lavender painted shaded planes. Match its illumination strength and material identity closely, without additional glow. IMAGE 3 is the primary locked rounded clean hand-painted Daoist Q material/finish reference; do not copy UI or objects. IMAGE 4 is the existing festival finish sample only, never roof geometry or a reason to change paving into blue tiles.
Keep the native 1254x1254 opaque crop, all framing and boundaries. Preserve the repaired stone joints from IMAGE 1; add no new joints, cracks, objects, lanterns, text, flowers or shadow masses. Do not blur, sharpen, rescale, stretch, redesign, add noise or intensify highlights beyond IMAGE 2. Return one image. Highest available finish; actual model and quality remain host managed and unconfirmed.'''
 pp=target/'prompt.txt';pp.write_text(prompt,encoding='utf-8')
 req={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
 plan={'createdAtUtc':now(),'dayManifest':info(d/'integration-manifest.json'),'dayGeneratedEdit':dm['generatedEdit'],'dayRecord':dm['generationRecord'],'dayInputRecord':info(d/'input.png.generation.json'),'dayMasks':mask_records,'combinedMask':info(combined),'pairCropRectXYXY':rect,'pairRepairRectXYXY':dm['pairRepairRectXYXY'],'localC13RepairRectXYXY':dm['localC13RepairRectXYXY'],'festivalBaselines':bs,'references':refs,'prompt':info(pp),'formalAccepted':False}
 write(target/'request.json',req);write(target/'plan.json',plan)
 return req
def record(i,raw):
 target=DEST/f'step{i:02}';p=target/'native.png';assert not p.exists();raw=Path(raw);im=img(raw);assert im.size==(1254,1254)
 plan=read(target/'plan.json');req=read(target/'request.json')
 for r in plan['references']:check(r['file'],r['sha256'])
 shutil.copyfile(raw,p)
 write(str(p)+'.generation.json',{**info(p),'width':1254,'height':1254,'format':'PNG','generatedAt':now(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed builtin exposes no selectors or actual returned model/quality metadata.','evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw),'actualPixels':[1254,1254]},'prompt':plan['prompt']['file'],'promptSha256':plan['prompt']['sha256'],'references':plan['references'],'geometryMatchedTo':plan['dayGeneratedEdit'],'globalRectXYWH':[45056+plan['pairCropRectXYXY'][0],28672+plan['pairCropRectXYXY'][1],1254,1254],'resizedAfterGeneration':False,'finalArtUpscaled':False,'formalAccepted':False})
 return info(p)
def blend(a,b,alpha):
 aa=alpha.astype(np.uint32)[...,None];return ((a.astype(np.uint32)*(255-aa)+b.astype(np.uint32)*aa+127)//255).astype(np.uint8)
def compose(i):
 target=DEST/f'step{i:02}';plan=read(target/'plan.json');rec=read(target/'native.png.generation.json');check(target/'native.png',rec['sha256'])
 for key in ('dayManifest','dayGeneratedEdit','dayRecord','dayInputRecord','combinedMask'):check(plan[key]['file'],plan[key]['sha256'])
 pair,bs=base(i);assert bs==plan['festivalBaselines'];basepix=np.asarray(pair).copy()
 x0,y0,x1,y1=plan['pairRepairRectXYXY'];cx,cy,_,_=plan['pairCropRectXYXY'];w,h=x1-x0,y1-y0
 pixels=np.asarray(img(target/'native.png'))[y0-cy:y1-cy,x0-cx:x1-cx]
 assert pixels.shape==(h,w,3)
 alpha=np.full((h,w),255,np.uint8)
 slices={'left':(slice(None),slice(0,32)),'right':(slice(None),slice(-32,None)),'top':(slice(0,32),slice(None)),'bottom':(slice(-32,None),slice(None))}
 masks=[]
 for mm in plan['dayMasks']:
  for key in ('mask','npz'):check(mm[key]['file'],mm[key]['sha256'])
  part=np.asarray(Image.open(mm['mask']['file']));sl=slices[mm['name']];assert part.shape==alpha[sl].shape
  alpha[sl]=np.minimum(alpha[sl],part)
  for key,suffix in [('mask','png'),('npz','npz')]:
   out=target/'masks'/f'{mm["name"]}.{suffix}';out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(mm[key]['file'],out);check(out,mm[key]['sha256']);masks.append(info(out))
 assert np.array_equal(alpha,np.asarray(Image.open(plan['combinedMask']['file'])))
 assert all(np.all(a==0) for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
 out=basepix.copy();out[y0:y1,x0:x1]=blend(basepix[y0:y1,x0:x1],pixels,alpha)
 exterior=np.ones(out.shape[:2],bool);exterior[y0:y1,x0:x1]=False
 assert np.array_equal(out[exterior],basepix[exterior]) and np.array_equal(out[:,:4096],basepix[:,:4096])
 deps={'derivedFrom':bs+[info(target/'native.png')],'dayGeometryPlan':info(target/'plan.json'),'dayMasksExact':True,'geometryFlow':False,'colorCorrection':False,'outsideRepairExactlyIdentical':True,'pairRepairRectXYXY':[x0,y0,x1,y1],'formalAccepted':False}
 core=save(target/'output/r08_c13.png',Image.fromarray(out[:,4096:]),deps)
 qa=[]
 for name,box in [('repair-return',[max(0,x0-160),max(0,y0-160),min(8192,x1+160),min(4096,y1+160)]),('full-native-return',plan['pairCropRectXYXY'])]:
  qa.append(save(target/'qa'/f'{name}.png',Image.fromarray(out).crop(box),{'derivedFrom':[core,info(WEST)],'pairRectXYXY':box,'pixelScale':1,'visualReview':'pending'}))
 report={**deps,'createdAtUtc':now(),'step':i,'output':core,'masks':masks,'combinedMask':plan['combinedMask'],'nativeSource':info(target/'native.png'),'nativeRecord':info(target/'native.png.generation.json'),'qa':qa,'c12ExactlyUnchanged':True,'outsideChangedPixels':0,'globalStateModified':False,'script':info(__file__)}
 write(target/'output/integration-manifest.json',report)
 return report
if __name__=='__main__':
 command=sys.argv[1];i=int(sys.argv[2])
 value=prepare(i) if command=='prepare' else record(i,sys.argv[3]) if command=='record' else compose(i) if command=='compose' else None
 assert value is not None;print(json.dumps(value,ensure_ascii=False))
