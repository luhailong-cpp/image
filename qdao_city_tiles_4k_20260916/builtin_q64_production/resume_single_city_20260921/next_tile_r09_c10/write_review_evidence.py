from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
tile=Image.open(P/'output/r09_c10.candidate.png').convert('RGB')
for name,box in {'internal-v1-ring-step':(774,1270,1274,1770),'internal-h2-highlight-step':(300,1798,800,2298),'internal-h3-band-step':(3000,2822,3500,3322)}.items(): tile.crop(box).save(P/'qa'/f'defect-{name}-100pct.png')
left=json.loads((P/'qa/left-neighbor-check.json').read_text());im=Image.open(left['leftCandidateSource']).convert('RGB').crop((115,115,4211,4211))
V=P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
bl=Image.open(V/'r10_c09.png').convert('RGB');br=Image.open(V/'r10_c10.png').convert('RGB')
out=Image.new('RGB',(600,600));out.paste(im.crop((3796,3796,4096,4096)),(0,0));out.paste(tile.crop((0,3796,300,4096)),(300,0));out.paste(bl.crop((3796,0,4096,300)),(0,300));out.paste(br.crop((0,0,300,300)),(300,300));out.save(P/'qa/external-four-tile-bottom-left-intersection-100pct.png')
print('Native-pixel defect crops and true four-tile intersection prepared.')
