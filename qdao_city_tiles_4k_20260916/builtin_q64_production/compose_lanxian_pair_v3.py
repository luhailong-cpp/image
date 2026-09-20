from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
reg=module(P/'tools/mechanical_join.py','reg')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def source(p):
 r=j(p);im=Path(r['outputPath']);assert sha(im)==r['outputSha256']==sha(Path(r['sourceOutputPath']));a=np.array(Image.open(im).convert('RGB'));assert a.shape==(1254,1254,3)
 return a,{'record':str(p),'recordSha256':sha(p),'sourceOutputPath':r['sourceOutputPath'],'sourceSha256':r['outputSha256'],'native':str(im)}
for v in ('lanxian_day','lanxian_spring'):
 d=P/v/'pair_r08_c06_c07';out=d/'output';qa=d/'qa';fields=d/'registration-v3';fields.mkdir(exist_ok=True)
 initial=out/'pair-v1.png';a=np.array(Image.open(initial).convert('RGB'));entries=[]
 def paste(native,rect,edges,label,sources):
  nonlocal_dummy=None
  x0,y0,x1,y1=rect;h,w=native.shape[:2];assert (x1-x0,y1-y0)==(w,h)
  yy,xx=np.mgrid[:h,:w];dist={'left':xx,'right':w-1-xx,'top':yy,'bottom':h-1-yy};di=np.minimum.reduce([dist[e] for e in edges])
  mask=np.uint8(np.clip(di/64,0,1)*255)
  result,flow,color,report=reg.registered_join(a[y0:y1,x0:x1].copy(),native,mask,edges=edges)
  a[y0:y1,x0:x1]=result
  np.savez_compressed(fields/f'{label}.fields.npz',flow=flow,colorCorrection=color,mask=mask)
  (fields/f'{label}.json').write_text(json.dumps(report,indent=2))
  entries.append({'label':label,'rect':rect,'sources':sources,'registration':report,'fields':str(fields/f'{label}.fields.npz')})
  Image.fromarray(result).save(qa/f'{label}-after_v3_100pct.png')
 curve=P/v/'r08_c07/repairs/curved_paving';nat,src=source(curve/'native/curve.record.json')
 paste(nat,[6736,390,7990,1644],('left','top','bottom'),'curve',[src])
 rep=d/'repairs/boundary_v2';plan=j(rep/'plan.json')
 if v=='lanxian_spring':
  m=module(P/v/'r08_c07/assemble_builtin.py','ass');arrays=[];sources=[];metrics=[]
  for e in plan['entries']:
   n,s=source(rep/f"native/{e['id']}.record.json");arrays.append(n);sources.append(s)
  strip=arrays[0]
  for i,n in enumerate(arrays[1:],2):
   tmp,metric=m.append_patch(strip.transpose(1,0,2),n.transpose(1,0,2),m.load_seam_helper(),f'spring-boundary-{i}')
   if i==3:
    strip=np.concatenate((strip,n[230:]),axis=0);metric['selectionOverride']='last overlap all upper native; lower native dead-ended grout excluded';metric['seamFixed']=230
   else:strip=tmp.transpose(1,0,2)
   metrics.append(metric)
  Image.fromarray(strip).save(out/'boundary-native-joined-1254x3302.png')
  paste(strip,[3470,0,4724,3302],('left','right','bottom'),'boundary-strip',sources);entries[-1]['nativeJoinMetrics']=metrics
 else:
  for e in plan['entries']:
   n,s=source(rep/f"native/{e['id']}.record.json");edges=('left','right','top') if e['rect'][3]==4096 else ('left','right','top','bottom')
   paste(n,e['rect'],edges,e['id'],[s])
 art=Image.fromarray(a);pair=out/'pair-v3.png';art.save(pair)
 ext=Image.open(out/'pair-extended-v1.png').convert('RGB');ext.paste(art,(115,115));ext.save(out/'pair-extended-v3.png')
 candidates=[]
 for i,c in enumerate((6,7)):
  tile=f'r08_c{c:02d}';f=out/f'{v}_{tile}_q64_4k_candidate_pair_v3.png';crop=art.crop((i*4096,0,(i+1)*4096,4096));crop.save(f)
  assert np.array_equal(np.array(crop),a[:,i*4096:(i+1)*4096])
  ex=ext.crop((i*4096,0,i*4096+4326,4326));ex.save(out/f'{tile}-extended-context-v3.png')
  candidates.append({'tile':tile,'file':str(f),'sha256':sha(f),'size':[4096,4096],'finalPixelRectXYWH':[20480+i*4096,28672,4096,4096],'worldRect':{'x':143.75+i*18.75,'z':150,'width':18.75,'height':18.75}})
 art.resize((1600,800),Image.Resampling.LANCZOS).save(qa/'pair-v3-overview.jpg',quality=80)
 for i,y in enumerate((0,800,1600,2400,3196)):art.crop((3646,y,4546,y+900)).save(qa/f'boundary-v3-{i}_100pct.png')
 manifest={'appearance':v,'initialPair':str(initial),'initialSha256':sha(initial),'inputAssembly':str(out/'pair-v1-assembly.json'),'repairs':entries,'sourceResampling':'subpixel alignment only; native dimensions retained; local color matching','sourceUpscaledTo4K':False,'allGeneratedNativeSourcesPreserved':True,'pair':str(pair),'pairSha256':sha(pair),'pairSize':[8192,4096],'candidates':candidates,'splitPixelIdentityPassed':True,'formalAcceptance':False,'visualQA':'pending','wholeCityAccepted':False,'nearestGameplayCameraAccepted':False,'crossAppearancePixelGeometryAccepted':False}
 (out/'pair-v3-assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print(v,sha(pair))
# enrich rejected-source record for explicit non-base accounting
q=P/'lanxian_day/r08_c07/rejected/r04_c02-transparent-v1'
r=j(q/'record.json');r.update({'id':'r04_c02-transparent-v1','outputPath':str(q/'native.png'),'promptPath':str(q/'prompt.txt'),'actualNativePixels':list(Image.open(q/'native.png').size),'resizedAfterGeneration':False,'guidePath':str(P/'lanxian_day/r08_c07/guides/r04_c02.layout-only.png')});r['guideSha256']=sha(Path(r['guidePath']));(q/'native.record.json').write_text(json.dumps(r,indent=2))

