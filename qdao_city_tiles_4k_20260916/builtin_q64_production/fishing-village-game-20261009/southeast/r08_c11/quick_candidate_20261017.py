from pathlib import Path
from PIL import Image
import sys,json,hashlib
T=Path(__file__).resolve().parent
pid,version=sys.argv[1:3]
Q=T/'qa'/f'{pid}-{version}'
Q.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(T/'native'/f'{pid}-{version}.png').convert('RGB').crop((115,115,1139,1139))
r,c=int(pid[1]),int(pid[2])
items=[]
for side,dr,dc in [('west',0,-1),('north',-1,0),('east',0,1),('south',1,0)]:
 nr,nc=r+dr,c+dc;tr,tc=8,11
 if nr<1:tr-=1;nr=4
 if nr>4:tr+=1;nr=1
 if nc<1:tc-=1;nc=4
 if nc>4:tc+=1;nc=1
 nt=T.parent/f'r{tr:02d}_c{tc:02d}';sel=nt/'selected-patches.json'
 if not sel.exists():continue
 s=json.loads(sel.read_text(encoding='utf-8-sig'));p=s.get('patches',{}).get(f'p{nr}{nc}')
 if not p:continue
 np=nt/p;n=Image.open(np).convert('RGB').crop((115,115,1139,1139))
 out=Image.new('RGB',(512,1024) if side in ('west','east') else (1024,512))
 if side=='west':out.paste(n.crop((768,0,1024,1024)),(0,0));out.paste(im.crop((0,0,256,1024)),(256,0))
 if side=='east':out.paste(im.crop((768,0,1024,1024)),(0,0));out.paste(n.crop((0,0,256,1024)),(256,0))
 if side=='north':out.paste(n.crop((0,768,1024,1024)),(0,0));out.paste(im.crop((0,0,1024,256)),(0,256))
 if side=='south':out.paste(im.crop((0,768,1024,1024)),(0,0));out.paste(n.crop((0,0,1024,256)),(0,256))
 path=Q/f'{side}.png';out.save(path);items.append({'file':str(path),'sha256':sha(path),'side':side,'neighbor':str(np),'neighborSha256':sha(np),'resized':False})
(Q/'manifest.json').write_text(json.dumps({'tile':'r08_c11','patch':pid,'version':version,'source':str(T/'native'/f'{pid}-{version}.png'),'sourceSha256':sha(T/'native'/f'{pid}-{version}.png'),'evidence':items,'formalAccepted':False},indent=2),encoding='utf-8')
print(json.dumps(items))
