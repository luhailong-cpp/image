from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).parent;T=D.parents[1];read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cs=read(T/'r07_c11/current/v004/candidate-set.json');s=next(a for a in cs['candidates'] if a['tile']=='r07_c10');new=np.array(Image.open(s['file']).convert('RGB'));old=np.array(Image.open(read(D/'preparation.json')['coupledBottom']['file']).convert('RGB'));j=np.array(Image.open(D/'final-v4/joined.png').convert('RGB'))
print('rightROI current-vs-old mean,max',np.abs(new[:641,4035:].astype(float)-old[:641,4035:]).mean(),np.abs(new[:641,4035:].astype(float)-old[:641,4035:]).max())
a=new[:750,2957:2997].mean(axis=(1,2));b=j[1139:1889,:40].mean(axis=(1,2));ga=np.diff(a);gb=np.diff(b)
for l,r in [(0,130),(130,260),(260,400),(400,550),(0,550)]:
 vals=[]
 for dy in range(-30,31):
  ii=np.arange(max(l,31),min(r,len(ga)-31));v=float(np.mean((ga[ii]-gb[ii-dy])**2));vals.append((v,dy))
 print(l,r,sorted(vals)[:4])
a=Image.open(s['file']).convert('RGB');a.crop((3896,0,4096,750)).save(D/'final-v4/qa/latest-right-edge.png')
