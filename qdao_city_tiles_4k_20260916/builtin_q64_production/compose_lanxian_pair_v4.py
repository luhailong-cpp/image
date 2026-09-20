from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
sp=importlib.util.spec_from_file_location('r',P/'tools/mechanical_join.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
for v in ('lanxian_day','lanxian_spring'):
 d=P/v/'pair_r08_c06_c07';out=d/'output';qa=d/'qa';fields=d/'registration-v4';fields.mkdir(exist_ok=True)
 old=out/'pair-v3.png';a=np.array(Image.open(old).convert('RGB'));rep=d/'repairs/curve_return_v4';n=np.array(Image.open(rep/'native/return.png').convert('RGB'));rec=j(rep/'native/return.record.json')
 assert n.shape==(1254,1254,3) and sha(rep/'native/return.png')==rec['outputSha256']==sha(Path(rec['sourceOutputPath']))
 x,y=6938,390;yy,xx=np.mgrid[:1254,:1254];mask=np.uint8(np.clip(np.minimum.reduce([xx,yy,1253-yy])/48,0,1)*255)
 res,flow,col,report=r.registered_join(a[y:y+1254,x:x+1254].copy(),n,mask,edges=('left','top','bottom'),flow_inner=180,flow_full=70,tone_inner=210,tone_full=90)
 a[y:y+1254,x:x+1254]=res
 np.savez_compressed(fields/'return.fields.npz',flow=flow,colorCorrection=col,mask=mask);(fields/'return.json').write_text(json.dumps(report,indent=2))
 art=Image.fromarray(a);pair=out/'pair-v4.png';art.save(pair)
 ext=Image.open(out/'pair-extended-v3.png').convert('RGB');ext.paste(art,(115,115));ext.save(out/'pair-extended-v4.png')
 manifest=j(out/'pair-v3-assembly.json');manifest.update({'previousAssembly':str(out/'pair-v3-assembly.json'),'previousAssemblySha256':sha(out/'pair-v3-assembly.json'),'pair':str(pair),'pairSha256':sha(pair),'visualQA':'pending_final_review','finalRepair':{'rect':[6938,390,8192,1644],'record':str(rep/'native/return.record.json'),'nativeSha256':rec['outputSha256'],'registration':report,'fields':str(fields/'return.fields.npz')}})
 for i,c in enumerate(manifest['candidates']):
  f=out/f"{v}_{c['tile']}_q64_4k_candidate_pair_v4.png";cro=art.crop((i*4096,0,(i+1)*4096,4096));cro.save(f);c.update({'file':str(f),'sha256':sha(f)})
  e=ext.crop((i*4096,0,i*4096+4326,4326));ep=out/f"{c['tile']}-extended-context-v4.png";e.save(ep);assert np.array_equal(np.array(e)[115:4211,115:4211],np.array(cro));c['extendedContext']=str(ep);c['extendedContextSha256']=sha(ep)
 (out/'pair-v4-assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 art.resize((1600,800),Image.Resampling.LANCZOS).save(qa/'pair-v4-overview.jpg',quality=75)
 art.crop((6838,300,8192,1744)).save(qa/'curve-return-v4-full_100pct.png')
 for i,y in enumerate((0,1024,2048)):art.crop((3470,y,4724,y+1254)).save(qa/f'boundary-full-v4-{i}_100pct.png')
 print(v,[(c['tile'],c['sha256']) for c in manifest['candidates']])

