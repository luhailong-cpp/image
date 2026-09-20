from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival')
p=root/'triple_r10_c07_c09';p.mkdir(exist_ok=True)
for n in ('output','qa','repairs'): (p/n).mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('assembler',root/'r10_c09/assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
left=root/'pair_r10_c07_c08/output_v4/extended-context.png'
right=root/'r10_c09/output/extended-context.png'
a=np.array(Image.open(left).convert('RGB'));b=np.array(Image.open(right).convert('RGB'))
result,metric=m.append_patch(a,b,m.load_seam_helper(),'join_c08_c09')
assert result.shape==(4326,12518,3)
ext=Image.fromarray(result);ext.save(p/'output/extended-context.png')
im=ext.crop((115,115,12403,4211));im.save(p/'output/triple_12288x4096_candidate.png')
files=[]
for i,c in enumerate((7,8,9)):
    f=p/'output'/f'r10_c{c:02}.png';im.crop((i*4096,0,(i+1)*4096,4096)).save(f)
    files.append({'file':str(f.relative_to(p)),'pixels':[4096,4096],'sha256':sha(f)})
joined=np.concatenate([np.array(Image.open(p/'output'/f'r10_c{c:02}.png')) for c in (7,8,9)],axis=1)
assert np.array_equal(joined,np.array(im))
im.resize((1800,600),Image.Resampling.LANCZOS).save(p/'qa/overview.jpg',quality=85)
crops={}
for y in (0,1024,2048,2842):
    crops[f'new_boundary_y{y}']=(8192-627,y,8192+627,y+1254)
for x in (8192+1024,8192+2048,8192+3072):
    crops[f'stairs_x{x}']=(x-450,2842,x+450,4096)
for name,box in crops.items():
    cut=im.crop(box);cut.save(p/'qa'/f'{name}.png');cut.save(p/'qa'/f'{name}.jpg',quality=85)
(p/'assembly.json').write_text(json.dumps({'schemaVersion':1,'status':'candidate_pending_visual_qa','updatedAtUtc':datetime.now(timezone.utc).isoformat(),'parents':[{'path':str(left),'sha256':sha(left)},{'path':str(right),'sha256':sha(right)}],'nativeBaseSources':48,'newNativeSourcesInThisMechanicalJoin':0,'pixels':[12288,4096],'extendedPixels':[12518,4326],'files':files,'combinedSha256':sha(p/'output/triple_12288x4096_candidate.png'),'extendedSha256':sha(p/'output/extended-context.png'),'seamMetric':metric,'resamplingInThisJoin':False,'parentIncludesLimitedSeamRegistration':True,'finalArtUpscaled':False,'exactTileRejoinVerified':True,'qa':crops,'runtimePublished':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'combined':str(p/'output/triple_12288x4096_candidate.png'),'newTileCount':1,'files':files},ensure_ascii=False))
