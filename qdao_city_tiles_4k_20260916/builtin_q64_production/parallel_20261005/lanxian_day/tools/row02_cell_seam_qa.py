from pathlib import Path
from PIL import Image
import hashlib,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('col',type=int);a=parser.parse_args();col=a.col
assert 2<=col<=4
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c10');Q=B/'row02-early-qa';Q.mkdir(exist_ok=True)
own=f'r02_c{col:02d}';west=f'r02_c{col-1:02d}';north=f'r01_c{col:02d}'
srcs=[own,west,north];ims={k:Image.open(B/'native'/f'{k}.png').convert('RGB') for k in srcs}
maps={
f'c{col-1:02d}-c{col:02d}-seam':[(west,[1011,115,1139,1139],[0,0]),(own,[115,115,243,1139],[128,0])],
f'c{col:02d}-north-seam':[(north,[115,1011,1139,1139],[0,0]),(own,[115,115,1139,243],[0,128])]
}
checks=[]
for n,mp in maps.items():
 im=Image.new('RGB',(1024,256) if 'north' in n else (256,1024))
 for k,box,xy in mp: im.paste(ims[k].crop(box),xy)
 f=Q/(n+'.png');assert not f.exists();im.save(f)
 checks.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pixelMappings':mp,'operation':'integer crop and paste, no resize','actualViewPerformed':False})
mp=Q/f'c{col:02d}-manifest.json';assert not mp.exists()
mp.write_text(json.dumps({'sources':[{'cell':k,'sha256':hashlib.sha256((B/'native'/f'{k}.png').read_bytes()).hexdigest()} for k in srcs],'checks':checks,'formalAccepted':False},indent=2)+'\n')
print(mp)

