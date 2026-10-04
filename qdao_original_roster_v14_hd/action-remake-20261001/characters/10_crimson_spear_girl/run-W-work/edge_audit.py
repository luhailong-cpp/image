from pathlib import Path
from PIL import Image
import json
d=Path(__file__).parent
s=json.loads((d/'selection.json').read_text())
for slot,f in s['slots'].items():
 im=Image.open(d.parent/f);a=im.getchannel('A');box=a.point(lambda p:255 if p>32 else 0).getbbox()
 print(slot,Path(f).name,box,'rightNontransparent',sum(p>32 for p in list(a.crop((1253,0,1254,1254)).getdata())))

