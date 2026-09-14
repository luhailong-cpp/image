from pathlib import Path
from PIL import Image
import hashlib,json
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\he_xiangu_natural_walk\directions\N')
src=p/'keys-heels-raw.png';im=Image.open(src).convert('RGBA');assert im.size==(1254,1254)
out=Image.new('RGBA',im.size,(255,0,255,255));items=[]
for dest,k in enumerate([0,3,2,1]):
 box=[k%2*627,k//2*627,k%2*627+627,k//2*627+627]
 out.paste(im.crop(box),(dest%2*627,dest//2*627));items.append(dict(output_phase=[1,3,5,7][dest],source_cell=k+1,source_box=box))
dst=p/'keys-reordered-raw.png';out.save(dst)
dst.with_suffix('.assembly.json').write_text(json.dumps(dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),operation='whole-cell swap of passing poses to use anatomical RIGHT support in phase03, LEFT support in phase07',sources=items,output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest()),indent=2)+'\n')
print(dst)

