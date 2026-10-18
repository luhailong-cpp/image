from pathlib import Path
from PIL import Image
import json,sys,hashlib
R=Path(__file__).resolve().parents[1];stem,ver=sys.argv[1:3];tile=stem[:7];row=int(stem[9:11]);col=int(stem[12:14]);sel=json.loads((R/'selected-revisions.json').read_text(encoding='utf-8-sig'));q=R/'qa'/f'{stem}_{ver}';q.mkdir(exist_ok=True)
def core(r,c):
 s=f'{tile}_s{r:02d}_{c:02d}';p=R/'native'/f'{s}_{ver if s==stem else sel.get(s,"a01")}.png';return Image.open(p).crop((115,115,1139,1139)),str(p),hashlib.sha256(p.read_bytes()).hexdigest()
a,ap,ah=core(row,col);rec=[]
for name,r,c in [('north',row-1,col),('west',row,col-1),('east',row,col+1),('south',row+1,col)]:
 if not (1<=r<=4 and 1<=c<=4):continue
 b,bp,bh=core(r,c)
 if name in ['north','south']:
  out=Image.new('RGB',(1024,256));top,bot=(b,a) if name=='north' else (a,b);out.paste(top.crop((0,896,1024,1024)),(0,0));out.paste(bot.crop((0,0,1024,128)),(0,128))
 else:
  out=Image.new('RGB',(256,1024));left,right=(b,a) if name=='west' else (a,b);out.paste(left.crop((896,0,1024,1024)),(0,0));out.paste(right.crop((0,0,128,1024)),(128,0))
 out.save(q/f'{name}.png');rec.append({'edge':name,'sources':[ap,bp],'hashes':[ah,bh]})
(q/'inputs.json').write_text(json.dumps(rec,indent=2));print(q)
