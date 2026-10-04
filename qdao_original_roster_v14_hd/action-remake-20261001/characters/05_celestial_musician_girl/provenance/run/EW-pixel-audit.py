from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[2]
rows=[]
for d in ['E','W']:
    for f in sorted((root/'staging/run'/d).glob('*.png')):
        with Image.open(f) as im:
            a=im.getchannel('A')
            b16=a.point(lambda x:255 if x>16 else 0).getbbox()
            b128=a.point(lambda x:255 if x>128 else 0).getbbox()
            edge=max(max(a.crop((0,0,1,im.height)).getdata()),max(a.crop((im.width-1,0,im.width,im.height)).getdata()),max(a.crop((0,0,im.width,1)).getdata()),max(a.crop((0,im.height-1,im.width,im.height)).getdata()))
            row={'file':str(f.relative_to(root)),'size':im.size,'mode':im.mode,'bboxAlphaAbove16':b16,'bboxAlphaAbove128':b128,'canvasEdgeMaxAlpha':edge}
            rows.append(row)
            print(f'{d}/{f.name} A16={b16} A128={b128} EdgeA={edge}')
(root/'provenance/run/EW-pixel-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
