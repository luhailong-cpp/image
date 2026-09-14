from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(r'E:\work\image\qdao_chibi_roster_v12\review\he_xiangu_natural_walk')
im=Image.open(P/'idle-eight-raw.png').convert('RGBA')
native=im.size
im=im.resize((1772,886),Image.Resampling.LANCZOS)
records=[]
for i,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
    dest=P/'directions'/d
    dest.mkdir(parents=True,exist_ok=True)
    box=(i%4*443,i//4*443,i%4*443+443,i//4*443+443)
    cell=im.crop(box)
    out=dest/'idle-source-cell.png';cell.save(out)
    records.append(dict(direction=d,file=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_box_normalized=box))
(P/'idle-source-extraction.json').write_text(json.dumps(dict(source=str(P/'idle-eight-raw.png'),source_sha256=hashlib.sha256((P/'idle-eight-raw.png').read_bytes()).hexdigest(),native_size=native,normalized_sheet_size=[1772,886],normalization='whole sheet equal grid only; no individual sprite bbox fitting',cells=records),indent=2)+'\n')
print('Extracted eight independent idle source cells.')

