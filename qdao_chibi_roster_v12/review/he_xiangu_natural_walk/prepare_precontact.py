from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\he_xiangu_natural_walk');d=p/'precontact-fixes';d.mkdir(exist_ok=True)
sources=[p/'directions/SE/keys-raw.png',p/'directions/SW/keys-final-raw.png']
sheet=Image.new('RGBA',(1254,627),(255,0,255,255));records=[]
for i,src in enumerate(sources):
 im=Image.open(src).convert('RGBA');assert im.size==(1254,1254)
 box=[0,627,627,1254];sheet.paste(im.crop(box),(i*627,0));records.append(dict(path=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_box=box,direction=['SE','SW'][i],source_phase=5))
out=d/'left-contact-references.png';sheet.save(out)
out.with_suffix('.assembly.json').write_text(json.dumps(dict(sources=records,operation='wholecell reference collage only',output_sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
print(out)

