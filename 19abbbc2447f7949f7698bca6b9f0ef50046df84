from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
TOP=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
HELPER=Path(r'E:/work/image/tianyong_festival_hd_20260910/seam_helpers.py')
spec=importlib.util.spec_from_file_location('seams',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.asarray(Image.open(p).convert('RGB')).copy()
for variant in ['lanxian_day','lanxian_spring']:
 root=TOP/variant/'r08_c06'; rep=root/'repairs/v3';plan=read(rep/'plan.json')
 base=Path(plan['base']); assert sha(base)==plan['baseSha256']
 a=arr(base);outside=np.ones(a.shape[:2],bool);sources=[];qa=[]
 dest=root/'output'/f'{variant}_r08_c06_q64_4k_candidate_v3.png'
 assert not dest.exists()
 for ident,item in plan['patches'].items():
  file=rep/'native'/f'{ident}.png'; rec=read(rep/'native'/f'{ident}.record.json')
  assert sha(file)==rec['outputSha256']==sha(Path(rec['sourceOutputPath']))
  assert sha(rep/'prompts'/f'{ident}.prompt.txt')==rec['promptSha256']
  assert sha(rep/'guides'/f'{ident}.layout-only.png')==rec['guideSha256']
  new=arr(file);assert new.shape==(1254,1254,3)
  gx,gy,_,_=item['rect'];x,y,x1,y1=item['focusRect'];new=new[y-gy:y1-gy,x-gx:x1-gx];old=a[y:y1,x:x1].copy()
  band=40;h,w=old.shape[:2];xx=np.arange(w)[None,:];yy=np.arange(h)[:,None]
  left=m._minimum_vertical_seam(old[:,:band],new[:,:band]);right=m._minimum_vertical_seam(old[:,-band:],new[:,-band:])+w-band
  top=m._minimum_vertical_seam(old[:band].transpose(1,0,2),new[:band].transpose(1,0,2));bottom=m._minimum_vertical_seam(old[-band:].transpose(1,0,2),new[-band:].transpose(1,0,2))+h-band
  mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
  a[y:y1,x:x1]=np.where(mask[...,None],new,old);outside[y:y1,x:x1]=False
  sources.append({'id':ident,'file':str(file),'sha256':sha(file),'record':str(rep/'native'/f'{ident}.record.json'),'focusRect':item['focusRect'],'guideRect':item['rect'],'selectedNativePixels':int(mask.sum())})
  cx=(x+x1)//2;cy=(y+y1)//2;qbox=[max(0,cx-450),max(0,cy-450),min(4096,cx+450),min(4096,cy+450)]
  qa.append({'id':ident,'rect':qbox})
 assert np.array_equal(a[outside],arr(base)[outside])
 Image.fromarray(a).save(dest)
 ext=arr(root/'output/extended-context-v2.png');ext[115:4211,115:4211]=a;extp=root/'output/extended-context-v3.png';Image.fromarray(ext).save(extp)
 for item in qa:
  x,y,x1,y1=item['rect'];file=root/'qa'/f"v3_{item['id']}_100pct.png";Image.fromarray(a[y:y1,x:x1]).save(file);item.update(file=str(file),sha256=sha(file),resized=False)
 overview=root/'qa/v3_overview_1024.png';Image.fromarray(a).resize((1024,1024),Image.Resampling.LANCZOS).save(overview)
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':str(base),'baseSha256':sha(base),'sources':sources,'output':{'file':str(dest),'sha256':sha(dest),'size':[4096,4096]},'extendedContext':{'file':str(extp),'sha256':sha(extp),'size':[4326,4326]},'method':'focused defect area native-only hard minimum seam; no resize/tone/blur','band':40,'finalArtUpscaled':False,'sourceResampling':'none','outsideFocusedRegionsUnchanged':True,'qa':qa,'formalTileAcceptance':False,'runtimePublished':False,'visualQA':'pending','scriptSha256':sha(Path(__file__))}
 (root/'output/repair-v3-assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(variant,sha(dest))

