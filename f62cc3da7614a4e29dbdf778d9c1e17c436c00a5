from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import importlib.util,json,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/style-audit-20260909/audit_tools.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
coverage=json.loads((OUT/'coverage.json').read_text(encoding='utf-8'))
page=Image.new('RGB',(1500,1120),'#f3ecdd');d=ImageDraw.Draw(page);f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
rows=[]
for i,p in enumerate(coverage['evidence_changed_after_review']):
    raw=(ROOT/p).read_bytes();sha=hashlib.sha256(raw).hexdigest();im=Image.open(ROOT/p).convert('RGBA')
    x=i%3*500+10;y=i//3*360+20
    page.paste(a.preview(im,480,300),(x,y));d.text((x,y+310),Path(p).name,font=f,fill='#183c30')
    rows.append({'path':p,'sha256':sha,'size':list(im.size),'evidence':'ui/end-changes.jpg','cell':i+1})
page.save(OUT/'ui/end-changes.jpg',quality=95)
(OUT/'ui/end-changes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(rows))
