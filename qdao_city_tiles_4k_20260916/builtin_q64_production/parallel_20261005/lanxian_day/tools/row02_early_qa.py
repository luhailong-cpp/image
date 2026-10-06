from pathlib import Path
from PIL import Image
import hashlib,json
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c10')
Q=B/'row02-early-qa';Q.mkdir(exist_ok=True)
srcs=['r02_c01','r02_c02','r01_c02']
ims={k:Image.open(B/'native'/f'{k}.png').convert('RGB') for k in srcs}
maps={
'c01-c02-seam':[('r02_c01',[1011,115,1139,1139],[0,0]),('r02_c02',[115,115,243,1139],[128,0])],
'c02-north-seam':[('r01_c02',[115,1011,1139,1139],[0,0]),('r02_c02',[115,115,1139,243],[0,128])]
}
checks=[]
for n,mp in maps.items():
 im=Image.new('RGB',(256,1024) if n=='c01-c02-seam' else (1024,256))
 for k,box,xy in mp: im.paste(ims[k].crop(box),xy)
 f=Q/(n+'.png');im.save(f)
 checks.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pixelMappings':mp,'operation':'integer crop and paste, no resize','actualViewPerformed':False})
(Q/'manifest.json').write_text(json.dumps({'sources':[{'cell':k,'sha256':hashlib.sha256((B/'native'/f'{k}.png').read_bytes()).hexdigest()} for k in srcs],'checks':checks,'formalAccepted':False},indent=2)+'\n')
print(Q)

