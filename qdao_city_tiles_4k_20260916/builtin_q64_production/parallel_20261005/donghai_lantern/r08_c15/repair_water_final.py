from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
ROOT=T.parent
BASE=T/'repairs/approved-sync/output/r08_c15.png'
EXPECT='908df2ad815315cac373cf0ace48c0f2493e45b981b729ee28741cae5da82fa9'
JOBS={
 'internal': {'window':[450,2500,1704,3754], 'rois':[[1030,2890,1435,3085],[815,3120,990,3370]], 'description':'Repair the two artificial water paint splice defects only: (1) a long sawtooth/triangular horizontal splice across crop x580..985,y390..585, and (2) a narrow vertical dark zigzag cutoff through a warm reflection at crop x365..540,y620..870. The surrounding surface is continuous blue water with softly irregular rounded ripples and peach-gold lantern reflections. Repaint just those two scars into continuous natural hand-painted ripples and reflection brushwork, without a triangular edge, sawtooth, straight cutoff, new object or hard new outline.'},
 'west': {'window':[0,2600,1254,3854], 'rois':[[128,3090,520,3320]], 'description':'Repair only the artificial perfectly horizontal image-crop line in water near crop y587, across x128..520. Continue existing rounded blue ripples and peach-gold reflected brushwork naturally across that line. Preserve the exact boardwalk and timber-post silhouettes and all other composition. Do not create any additional cutoff, wave border, object or straight line.'}
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'file':str(p),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,d):
 p=Path(p); assert p.resolve().is_relative_to(T.resolve()); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def save(p,im,meta):
 p=Path(p); assert not p.exists(); p.parent.mkdir(parents=True,exist_ok=True); im.save(p)
 e={**ref(p),'pixels':list(im.size),**meta};write(str(p)+'.generation.json',e);return e
def prepare(job):
 assert sha(BASE)==EXPECT
 cfg=JOBS[job]; R=T/f'repairs/water-final-{job}'; w=cfg['window']
 if (R/'request.json').exists(): print(json.dumps(read(R/'request.json')));return
 contract=read(T/'source-contract-v2/source-contract.json'); day=Path(contract['dayGeometrySnapshot']['snapshot']['file'])
 assert sha(day)==contract['dayGeometrySnapshot']['snapshot']['sha256']
 fest=save(R/'festival-target.png',Image.open(BASE).convert('RGB').crop(w),{'source':ref(BASE),'cropXYXY':w,'resized':False})
 geom=save(R/'day-geometry.png',Image.open(day).convert('RGB').crop(w),{'source':ref(day),'cropXYXY':w,'resized':False})
 style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
 refs=[{**fest,'role':'edit target; current festival same-window exact native pixels'},{**geom,'role':'same-window authoritative DAY geometry; no color transfer'},{**ref(style),'role':'confirmed rounded rich Q hand-painted style; no UI transfer'}]
 prompt='Use case: precise-object-edit. Image 1 is an exact native 1254 by 1254 crop of a Lantern Festival game map. '+cfg['description']+' The only changes are water color and brushwork continuity in these limited areas. Keep every existing object, boat, dock, post, shoreline, silhouette, edge coordinate, shadow shape, perspective and camera fixed. Image 2 is only the same-window DAY scene geometry authority; never copy its daytime palette or add shapes from outside the window. Image 3 is only the confirmed clean, rounded, saturated hand-painted Daoist Q art style. Preserve the target deep royal blue water and warm gold/pink lantern reflections. No blur, global recolor, warp, resize, zoom, text, UI, new lanterns or repetitive patterns. Return one opaque native 1254 by 1254 image with exactly the same field of view.'
 write(R/'references.json',refs);(R/'prompt.txt').write_text(prompt,encoding='utf8')
 write(R/'request.json',{'prompt':prompt,'referenced_image_paths':[e['file'] for e in refs],'transparent_background':False})
 write(R/'prepared.json',{'base':ref(BASE),'windowXYXY':w,'roisXYXY':cfg['rois'],'references':refs,'prompt':ref(R/'prompt.txt'),'geometryChanged':False})
 print(json.dumps(read(R/'request.json')))
def record(job,raw):
 R=T/f'repairs/water-final-{job}';p=R/'native.png';raw=Path(raw);assert not p.exists();assert Image.open(raw).size==(1254,1254);shutil.copyfile(raw,p)
 write(str(p)+'.generation.json',{**ref(p),'pixels':[1254,1254],'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**read(R/'request.json')},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no actual model or quality metadata or selectors.','evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw)},'prompt':ref(R/'prompt.txt'),'request':ref(R/'request.json'),'references':read(R/'references.json'),'resizedAfterGeneration':False,'geometryChangeAllowed':False})
 print(json.dumps(ref(p)))
def patch(job):
 assert sha(BASE)==EXPECT
 R=T/f'repairs/water-final-{job}';cfg=JOBS[job];w=cfg['window'];x,y,_,_=w
 n=np.asarray(Image.open(R/'native.png').convert('RGB'));old=np.asarray(Image.open(BASE).convert('RGB').crop(w));yy,xx=np.mgrid[:1254,:1254];a=np.zeros((1254,1254),np.uint8)
 for l,t,r,b in cfg['rois']:
  d=np.minimum.reduce((xx+x-l,yy+y-t,r-1-xx-x,b-1-yy-y)).astype(np.float32);z=np.clip(d/48,0,1);np.maximum(a,np.rint(z*z*(3-2*z)*255).astype(np.uint8),out=a)
 m=save(R/'mask.png',Image.fromarray(a),{'windowXYXY':w,'roisXYXY':cfg['rois'],'featherPixels':48,'operation':'bounded local smoothstep mask'})
 v=((old.astype(np.uint32)*(255-a[:,:,None])+n.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
 assert np.array_equal(v[a==0],old[a==0]);out=save(R/'patched-window.png',Image.fromarray(v),{'base':ref(BASE),'native':ref(R/'native.png'),'mask':m,'windowXYXY':w,'outsideMaskPixelIdentical':True})
 full=Image.open(BASE).convert('RGB');full.paste(Image.fromarray(v),(x,y));qa=[save(R/'qa/full1254.png',Image.fromarray(v),{'pixelScale':1})]
 for i,(l,t,r,b) in enumerate(cfg['rois']):
  for side,box in {'left':[max(0,l-96),t-96,l+96,b+96],'right':[r-96,t-96,r+96,b+96],'top':[max(0,l-96),t-96,r+96,t+96],'bottom':[max(0,l-96),b-96,r+96,b+96]}.items():qa.append(save(R/f'qa/roi{i+1}-{side}.png',full.crop(box),{'cropXYXY':box,'pixelScale':1,'resized':False}))
 write(R/'completion.json',{'base':ref(BASE),'native':ref(R/'native.png'),'mask':m,'patchedWindow':out,'windowXYXY':w,'roisXYXY':cfg['rois'],'outsideMaskPixelIdentical':True,'geometryChangeAllowed':False,'qa':qa,'formalAccepted':False})
 print(json.dumps(out))
if __name__=='__main__':
 job,action=sys.argv[1:3]
 {'prepare':lambda:prepare(job),'record':lambda:record(job,sys.argv[3]),'patch':lambda:patch(job)}[action]()
