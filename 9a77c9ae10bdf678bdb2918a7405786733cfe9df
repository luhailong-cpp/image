from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
TOP=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
HELPER=TOP/'tools/mechanical_join.py'
spec=importlib.util.spec_from_file_location('registered',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.asarray(Image.open(p).convert('RGB')).copy()
for variant in ['lanxian_day','lanxian_spring']:
 root=TOP/variant/'r08_c06'; rep=root/'repairs/v3';plan=read(rep/'plan.json');base=Path(plan['base'])
 a=arr(base);outside=np.ones(a.shape[:2],bool);sources=[];qa=[];reg=root/'repairs/v4-registration';reg.mkdir(exist_ok=True)
 dest=root/'output'/f'{variant}_r08_c06_q64_4k_candidate_v4.png';assert not dest.exists()
 for ident,item in plan['patches'].items():
  file=rep/'native'/f'{ident}.png';rec=read(rep/'native'/f'{ident}.record.json');native=arr(file)
  assert sha(file)==rec['outputSha256']==sha(Path(rec['sourceOutputPath']))
  box=item['rect'] if variant=='lanxian_day' else item['focusRect']
  gx,gy,_,_=item['rect'];x,y,x1,y1=box;new=native[y-gy:y1-gy,x-gx:x1-gx];old=a[y:y1,x:x1].copy()
  h,w=old.shape[:2];yy,xx=np.mgrid[:h,:w];dist=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])
  mask=np.clip(dist/(64 if variant=='lanxian_day' else 24)*255,0,255).astype(np.uint8)
  opts={} if variant=='lanxian_day' else {'flow_inner':72,'flow_full':24,'tone_inner':96,'tone_full':36}
  result,flow,correction,report=m.registered_join(old,new,mask,**opts)
  a[y:y1,x:x1]=result;outside[y:y1,x:x1]=False
  fp=reg/f'{ident}.registration-fields.npz';np.savez_compressed(fp,flow=flow,correction=correction,mask=mask)
  rp=reg/f'{ident}.registration.json';rp.write_text(json.dumps(report,indent=2),encoding='utf8')
  sources.append({'id':ident,'file':str(file),'sha256':sha(file),'record':str(rep/'native'/f'{ident}.record.json'),'compositeRect':box,'guideRect':item['rect'],'registration':str(rp),'registrationSha256':sha(rp),'fields':str(fp),'fieldsSha256':sha(fp)})
  fx,fy,fx1,fy1=item['focusRect'];cx=(fx+fx1)//2;cy=(fy+fy1)//2
  qa.append({'id':ident,'rect':[max(0,cx-450),max(0,cy-450),min(4096,cx+450),min(4096,cy+450)]})
 assert np.array_equal(a[outside],arr(base)[outside])
 Image.fromarray(a).save(dest)
 ext=arr(root/'output/extended-context-v2.png');ext[115:4211,115:4211]=a;extp=root/'output/extended-context-v4.png';Image.fromarray(ext).save(extp)
 for item in qa:
  x,y,x1,y1=item['rect'];file=root/'qa'/f"v4_{item['id']}_100pct.png";Image.fromarray(a[y:y1,x:x1]).save(file);item.update(file=str(file),sha256=sha(file),resized=False)
 for ident,item in plan['patches'].items():
  x,y,x1,y1=item['rect'];file=root/'qa'/f"v4_{ident}_full_context_100pct.png";Image.fromarray(a[y:y1,x:x1]).save(file);qa.append({'id':ident+'_full_context','file':str(file),'sha256':sha(file),'rect':item['rect'],'resized':False})
 Image.fromarray(a).resize((1024,1024),Image.Resampling.LANCZOS).save(root/'qa/v4_overview_1024.png')
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':str(base),'baseSha256':sha(base),'sources':sources,'output':{'file':str(dest),'sha256':sha(dest),'size':[4096,4096]},'extendedContext':{'file':str(extp),'sha256':sha(extp),'size':[4326,4326]},'method':'native repair with <=8px tapered optical-flow registration and bounded local color matching at return edges; no size upscale','finalArtUpscaled':False,'sourceResampling':'subpixel alignment only','helper':str(HELPER),'helperSha256':sha(HELPER),'qa':qa,'formalTileAcceptance':False,'runtimePublished':False,'visualQA':'pending','scriptSha256':sha(Path(__file__))}
 (root/'output/repair-v4-assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(variant,sha(dest))

