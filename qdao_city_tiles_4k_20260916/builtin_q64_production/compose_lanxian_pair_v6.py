from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def w(p,m):Path(p).write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
s=importlib.util.spec_from_file_location('r',P/'tools/mechanical_join.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
for v,prev in [('lanxian_day','v4'),('lanxian_spring','v5')]:
 d=P/v/'pair_r08_c06_c07';out=d/'output';qa=d/'qa';fd=d/'registration-v6';fd.mkdir(exist_ok=True)
 a=np.array(Image.open(out/f'pair-{prev}.png').convert('RGB'));original=a.copy();rep=d/'repairs/fullseam_top_v6';rec=j(rep/'native/top.record.json');native=np.array(Image.open(rep/'native/top.png').convert('RGB'));assert sha(rep/'native/top.png')==rec['sourceOutputSha256']==sha(rec['sourceOutputPath']);records=[]
 regions=[('right',[700,0,1200,500])]
 if v=='lanxian_day':regions.insert(0,('left',[0,0,400,330]))
 for label,box in regions:
  l,t,rr,b=box;n=native[t:b,l:rr].copy();h,ww=n.shape[:2];x,y=6136+l,t;yy,xx=np.mgrid[:h,:ww];mask=np.uint8(np.clip(np.minimum.reduce([xx,ww-1-xx,h-1-yy])/32,0,1)*255)
  res,flow,col,report=r.registered_join(a[y:y+h,x:x+ww].copy(),n,mask,edges=('left','right','bottom'),flow_inner=100,flow_full=32,tone_inner=120,tone_full=48)
  a[y:y+h,x:x+ww]=res;np.savez_compressed(fd/f'{label}.fields.npz',flow=flow,colorCorrection=col,mask=mask);w(fd/f'{label}.json',report)
  records.append({'sourceCropNativeXYXY':box,'rectPairXYXY':[x,y,x+ww,y+h],'registration':report,'fields':str(fd/f'{label}.fields.npz')})
 assert np.array_equal(a[:,:4096],original[:,:4096])
 art=Image.fromarray(a);pair=out/'pair-v6.png';art.save(pair);ext=Image.open(out/f'pair-extended-{prev}.png').convert('RGB');ext.paste(art,(115,115));ext.save(out/'pair-extended-v6.png')
 manifest=j(out/f'pair-{prev}-assembly.json');manifest.update({'previousAssembly':str(out/f'pair-{prev}-assembly.json'),'previousAssemblySha256':sha(out/f'pair-{prev}-assembly.json'),'pair':str(pair),'pairSha256':sha(pair),'visualQA':'full_seams_final_patch_pending','fullSeamTopRepair':{'record':str(rep/'native/top.record.json'),'nativeSha256':rec['outputSha256'],'crops':records}})
 for i,c in enumerate(manifest['candidates']):
  f=out/f"{v}_{c['tile']}_q64_4k_candidate_pair_v6.png";im=art.crop((4096*i,0,4096*(i+1),4096));im.save(f);ep=out/f"{c['tile']}-extended-context-v6.png";ex=ext.crop((4096*i,0,4096*i+4326,4326));ex.save(ep);assert np.array_equal(np.array(ex)[115:4211,115:4211],np.array(im));c.update({'file':str(f),'sha256':sha(f),'extendedContext':str(ep),'extendedContextSha256':sha(ep)})
 w(out/'pair-v6-assembly.json',manifest)
 art.crop((6036,0,7490,650)).save(qa/'fullseam-top-v6-context_100pct.png');art.resize((1600,800),Image.Resampling.LANCZOS).save(qa/'pair-v6-overview.jpg',quality=75)
 print(v,[(c['tile'],c['sha256']) for c in manifest['candidates']])
