from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
H=Path(__file__).resolve().parent;G=H.parents[1]/'10-generation';s=json.loads((H/'selection.json').read_text())
keys=['NE01','NE05','NE09','NE13'];out=Image.new('RGB',(1800,850),'#e8e8e4');d=ImageDraw.Draw(out)
for n,k in enumerate(keys):
 p=G/s[k]['archive']/'raw.png';im=Image.open(p).convert('RGBA');preview=im.resize((430,430),Image.Resampling.LANCZOS);out.paste(preview,(n*450+10,25),preview);crop=im.crop((450,750,1020,1254));crop.thumbnail((430,370));out.paste(crop,(n*450+10,465),crop);d.text((n*450+12,8),s[k]['archive'],fill='black')
dest=H/'qa-key-comparison.png';out.save(dest)
(H/'qa-key-comparison.json').write_text(json.dumps({'purpose':'review-only contact and leg crops; never usable game frames','sources':[{'slot':k,'attempt':s[k]['archive'],'sha256':hashlib.sha256((G/s[k]['archive']/'raw.png').read_bytes()).hexdigest()} for k in keys]},indent=2))
print(dest)
