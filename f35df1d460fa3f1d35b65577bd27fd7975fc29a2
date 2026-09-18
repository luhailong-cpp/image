from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');d=P/'lanxian_day/r08_c08'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
source=d/'native/regional.png';target=d/'regional-reference/native.png'
if source.exists():
 assert not target.exists();source.rename(target);rec=j(d/'native/regional.record.json');rec.update({'outputPath':str(target),'role':'regional_layout_reference_only_not_final_4K'});(d/'regional-reference/native.record.json').write_text(json.dumps(rec,indent=2));(d/'native/regional.record.json').unlink()
canvas=Image.open(target).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
leftfile=P/'lanxian_day/pair_r08_c06_c07/output/r08_c07-extended-context-v6.png'
left=Image.open(leftfile).convert('RGB');canvas.paste(left.crop((4096,0,4211,4326)),(0,0));canvas.save(d/'guides/layout-canvas-only.png')
plan=j(d/'plan.json');entries=[];arrays={}
for r in range(4):
 for c in range(4):
  ident=f'r{r+1:02d}_c{c+1:02d}';box=[c*1024,r*1024,c*1024+1254,r*1024+1254];g=canvas.crop(box);p=d/f'guides/{ident}.layout-only.png';g.save(p);arrays[(r,c)]=np.array(g);entries.append({'id':ident,'row':r,'column':c,'guide':str(p),'guideSha256':sha(p),'fullCanvasBox':box,'guideOnly':True})
checks=0
for r in range(4):
 for c in range(4):
  if c<3:assert np.array_equal(arrays[r,c][:,-230:],arrays[r,c+1][:,:230]);checks+=1
  if r<3:assert np.array_equal(arrays[r,c][-230:],arrays[r+1,c][:230]);checks+=1
plan.update({'status':'sixteen_native_detail_patches_required','patches':entries,'guidePreparation':{'status':'ready','guideCount':16,'motherSource':str(target),'motherSha256':sha(target),'motherPixels':[1254,1254],'canvasPixels':[4326,4326],'method':'Full expanded region mother resampled for layout guidance only; left115 from completed c07 native core','sharedOverlapChecks':checks,'allSharedOverlapPixelsIdentical':True,'finalArtResampling':False},'leftNeighborBoundary':{'tile':'r08_c07','file':str(leftfile),'sha256':sha(leftfile),'coreConstraintPixels':115,'guideOnly':True}})
(d/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('day 16 guides ready, 24 overlaps identical, regional native separated from base count')
