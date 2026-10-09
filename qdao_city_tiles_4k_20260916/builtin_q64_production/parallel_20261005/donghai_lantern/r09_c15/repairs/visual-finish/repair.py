"""Local visual repairs; writes only this visual-finish directory. No API calls."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;T=B.parent.parent;OWN=T.parent
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
BASE=T/'tone-assembly/output/extended-context.png'
BASE_SHA='2b0371501e4c7efa47e3f227b7882709e82f61625767ef89633741cc4ab622bb'
CORE=T/'tone-assembly/output/r09_c15.png'
CORE_SHA='e6988dea63f51a80fedd04d2ed1a02e05c9f1a0992cf122161b402af0f2c4462'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);assert p.resolve().is_relative_to(B.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role=None):return {'file':str(p),'sha256':sha(p),**({'role':role}if role else{})}
def now():return datetime.now(timezone.utc).isoformat()
def plans():return read(B/'plan.json')['patches']
def img(p):return np.array(Image.open(p).convert('RGB'))
def save(p,a):
 p=Path(p);assert p.resolve().is_relative_to(B.resolve());p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.stem+'.writing.png');Image.fromarray(a).save(tmp);tmp.replace(p)
def init():
 assert sha(BASE)==BASE_SHA and sha(CORE)==CORE_SHA
 c=read(T/'source-contract.json');d=c['dayExtended'];assert sha(d['file'])==d['sha256']
 if not (B/'contract.json').exists():
  write(B/'contract.json',{'createdAtUtc':now(),'baseExtended':ref(BASE),'baseCore':ref(CORE),'dayExtended':d,'sourceContract':ref(T/'source-contract.json'),'style':ref(STYLE),'northImmutable':ref(OWN/'r08_c15/west-common-edge-v3/output/r08_c15.png'),'baseManifest':ref(T/'tone-assembly/output/tone-assembly-manifest.json'),'operations':[],'mechanicalColorFieldMaxRGB':0,'imageBlur':False,'imageResampling':False,'dayWritten':False,'globalRegistryModified':False,'formalAccepted':False})
 if not (B/'output/extended-context.png').exists():save(B/'output/extended-context.png',img(BASE));save(B/'output/r09_c15.png',img(CORE))
 return read(B/'contract.json')
def prepare(name):
 c=init();p=next(x for x in plans()if x['id']==name);assert not (B/'native'/f'{name}.png').exists()
 x,y=p['origin'];box=[x+115,y+115,x+1369,y+1369];assert min(box)>=0 and max(box)<=4326
 current=B/'output/extended-context.png';target=B/'guides'/f'{name}-current.png';day=B/'guides'/f'{name}-day.png'
 save(target,np.array(Image.open(current).convert('RGB').crop(box)));save(day,np.array(Image.open(c['dayExtended']['file']).convert('RGB').crop(box)))
 snap={'operation':'exact1254 current-pixel crop; no resizing','parentCandidateSha256':sha(current),'sourceCropXYXY':box,'sourceCoreOriginXY':[x,y],'appliedOperations':[z['id']for z in c['operations']],'derivedFrom':[c['baseExtended']]+[z['native']for z in c['operations']]}
 write(str(target)+'.generation.json',{**ref(target),**snap});write(str(day)+'.generation.json',{**ref(day),'operation':'exact1254 locked DAY same-window geometry crop','sourceCropXYXY':box,'derivedFrom':[c['dayExtended']],'resized':False})
 refs=[ref(target,'PRIMARY CURRENT EDIT TARGET, exact1254 same window; keep current palette and layout'),ref(day,'locked DAY geometry only; never copy daylight colors'),ref(STYLE,'confirmed rounded clean Q painting style only; no UI or props')]
 boxes=[[a-x,b-y,d-x,e-y]for a,b,d,e in p['regions']]
 prompt=f"""Use case: precise-object-edit.
Asset: 五行奇谈 Lantern Festival map r09_c15. Repair local paint/lighting seams in an existing completed map.
Image1 is the PRIMARY EDIT TARGET: reproduce this exact1254x1254 current image and palette. Image2 is locked DAY geometry at the identical world window, used only to keep structure and existing reflection silhouettes. Never copy its daylight colors. Image3 is confirmed rendering style only; ignore its UI and objects.
Repair ONLY the unnatural jagged patch boundaries in these image pixel regions: {boxes}. {p['detail']}
Match immediately adjacent current material colors smoothly and retain the same broad hand-painted brushwork. Remove the torn-paper/zigzag boundary by repainting natural continuous illumination and wood grain or smooth water across it; not by blurring. Do not recolor or relight the whole scene. Preserve every plank joint, post outline, cap, water ring, real cast-shadow silhouette, occlusion and edge crossing exactly. Existing natural dark shadows and wood grain remain distinct. Do not delete natural shading to make everything flat.
Plain water stays smooth blue with no new clouds, shapes, reflections, ripples or sparkle. Existing DAY reflected silhouettes may remain at the same positions; do not invent reflected structures. Preserve all areas outside the listed repair regions and their narrow100px transition unchanged. Keep every edge and object contour at the crop boundary fixed.
Return one opaque1254x1254 PNG at identical crop and native pixels. No zoom, resize, blur, grain, text, labels, border, UI or watermark. Configured target gpt-image-2.5-sunburst/max is host-managed; no exposed selector."""
 rq={'prompt':prompt,'referenced_image_paths':[r['file']for r in refs],'transparent_background':False}
 pp=B/'prompts'/f'{name}.txt';pp.parent.mkdir(exist_ok=True);pp.write_text(prompt,encoding='utf-8');write(B/'prompts'/f'{name}.request.json',rq)
 write(B/'prompts'/f'{name}.prepared.json',{'id':name,'origin':p['origin'],'regions':p['regions'],'feather':p.get('feather',100),'references':refs,'prompt':ref(pp),'request':ref(B/'prompts'/f'{name}.request.json'),'parentCandidateSha256':sha(current),'configuration':read(OWN/'batch-model-check.json')['configSnapshot']})
 return rq
def record(name,raw):
 pre=read(B/'prompts'/f'{name}.prepared.json');rq=read(B/'prompts'/f'{name}.request.json')
 for r in pre['references']+[pre['prompt'],pre['request']]:assert sha(r['file'])==r['sha256']
 raw=Path(raw);im=Image.open(raw);im.load();assert im.size==(1254,1254);assert im.mode in ('RGB','RGBA');assert im.mode=='RGB' or im.getchannel('A').getextrema()==(255,255)
 dest=B/'native'/f'{name}.png';assert not dest.exists();dest.parent.mkdir(exist_ok=True);shutil.copyfile(raw,dest)
 rec={**ref(dest),'generatedAtUtc':now(),'width':1254,'height':1254,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':pre['configuration'],'submittedParameters':{'model':None,'quality':None,**rq},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; no model or quality selector/return metadata.','evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw)},'references':pre['references'],'prompt':pre['prompt'],'request':pre['request'],'sourceBytesPreserved':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'originTileXY':pre['origin'],'visualReview':'pending actual return and integration'}
 write(str(dest)+'.generation.json',rec);return ref(dest)
def apply(name):
 c=init();assert name not in [z['id']for z in c['operations']];pre=read(B/'prompts'/f'{name}.prepared.json');current=B/'output/extended-context.png';assert sha(current)==pre['parentCandidateSha256']
 native=B/'native'/f'{name}.png';rec=read(str(native)+'.generation.json');assert sha(native)==rec['sha256'];a=img(current);patch=img(native)
 x,y=pre['origin'];yy,xx=np.mgrid[y:y+1254,x:x+1254];alpha=np.zeros((1254,1254),np.float32);f=pre['feather']
 for x0,y0,x1,y1 in pre['regions']:
  dx=np.maximum(np.maximum(x0-xx,xx-(x1-1)),0);dy=np.maximum(np.maximum(y0-yy,yy-(y1-1)),0);d=np.sqrt(dx*dx+dy*dy);v=np.where(d>=f,0,.5+.5*np.cos(np.pi*np.minimum(d/f,1)));alpha=np.maximum(alpha,v)
 edge=np.ones((1254,1254),np.float32)
 for dist,active in [(xx-x,x>-115),(x+1253-xx,x+1254<4211),(yy-y,y>-115),(y+1253-yy,y+1254<4211)]:
  if active:edge*=.5-.5*np.cos(np.pi*np.clip(dist/64,0,1))
 alpha*=edge
 alpha=np.round(alpha*65535).astype(np.uint16);mask=B/'masks'/f'{name}.npz';mask.parent.mkdir(exist_ok=True);np.savez_compressed(mask,alpha=alpha,origin=np.array([x,y]),regions=np.array(pre['regions']),feather=np.array(f))
 save(B/'masks'/f'{name}.png',np.round(alpha/257).astype(np.uint8))
 sub=a[y+115:y+1369,x+115:x+1369];v=alpha.astype(np.float32)/65535
 out=np.rint(sub.astype(np.float32)*(1-v[...,None])+patch.astype(np.float32)*v[...,None]).clip(0,255).astype(np.uint8)
 before=sha(current);sub[:]=out;save(current,a);save(B/'output/r09_c15.png',a[115:4211,115:4211])
 operation={'id':name,'native':ref(native),'record':ref(str(native)+'.generation.json'),'mask':ref(mask),'maskPNG':ref(B/'masks'/f'{name}.png'),'originTileXY':[x,y],'regionsTileXYXY':pre['regions'],'featherPixels':f,'maskMethod':'continuous half-cosine Euclidean fade outside repair ROIs; no hard DAY DP mask','preCandidateSha256':before,'postCandidateSha256':sha(current),'sourcePixelBlur':False,'sourcePixelResampling':False,'mechanicalRGBFieldApplied':False}
 c['operations'].append(operation);c['candidate']=ref(B/'output/r09_c15.png');c['extendedContext']=ref(current);c['updatedAtUtc']=now();write(B/'contract.json',c)
 return operation
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='init':r=init()
 elif cmd=='prepare':r=prepare(sys.argv[2])
 elif cmd=='record':r=record(sys.argv[2],sys.argv[3])
 elif cmd=='apply':r=apply(sys.argv[2])
 else:raise ValueError(cmd)
 print(json.dumps(r,ensure_ascii=False))

