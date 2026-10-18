from pathlib import Path
from PIL import Image
import json,hashlib,sys
from datetime import datetime,timezone
p=Path(__file__).resolve().parent;z=p.parent
name=sys.argv[1];patch=name.split('-')[0];native=p/'native'/f'{name}.png'
h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
selpath=p/'selected-native.json';sel=json.loads(selpath.read_text()) if selpath.exists() else {}
sel[patch]=native.name;selpath.write_text(json.dumps(sel,indent=2)+'\n')
q=p/'qa'/name;q.mkdir(exist_ok=True)
cur=Image.open(native).convert('RGB').crop((115,115,1139,1139))
tr,tc=map(int,[p.name[1:3],p.name[5:7]]);r,c=map(int,patch[1:]);refs=[]
for d,dr,dc in [('east',0,1),('south',1,0),('west',0,-1),('north',-1,0)]:
 nr,nc=r+dr,c+dc;rr,cc=tr,tc
 if nr<1:rr-=1;nr=4
 if nr>4:rr+=1;nr=1
 if nc<1:cc-=1;nc=4
 if nc>4:cc+=1;nc=1
 other=z/f'r{rr:02}_c{cc:02}';np=f'p{nr}{nc}'
 sp=other/'selected-native.json';osel=json.loads(sp.read_text()) if sp.exists() else {}
 nf=other/'native'/osel.get(np,np+'.png')
 if not nf.exists():continue
 prog=other/'tile-progress.json';v=json.loads(prog.read_text()) if prog.exists() else {}
 cf=Path(v.get('candidate',str(other/'candidates'/f'{other.name}.candidate.png')))
 if other!=p and cf.exists():
  base=Image.open(cf).convert('RGB');neighbor=base.crop(((nc-1)*1024,(nr-1)*1024,nc*1024,nr*1024));used=cf
 else:neighbor=Image.open(nf).convert('RGB').crop((115,115,1139,1139));used=nf
 if d in ['east','west']:
  im=Image.new('RGB',(384,1024))
  if d=='east':im.paste(cur.crop((832,0,1024,1024)),(0,0));im.paste(neighbor.crop((0,0,192,1024)),(192,0))
  else:im.paste(neighbor.crop((832,0,1024,1024)),(0,0));im.paste(cur.crop((0,0,192,1024)),(192,0))
 else:
  im=Image.new('RGB',(1024,384))
  if d=='south':im.paste(cur.crop((0,832,1024,1024)),(0,0));im.paste(neighbor.crop((0,0,1024,192)),(0,192))
  else:im.paste(neighbor.crop((0,832,1024,1024)),(0,0));im.paste(cur.crop((0,0,1024,192)),(0,192))
 out=q/f'{d}-join.png';assert not out.exists();im.save(out)
 refs.append({'direction':d,'file':str(out),'sha256':h(out),'current':str(native),'currentSha256':h(native),'neighbor':str(used),'neighborSha256':h(used),'neighborPatch':np,'status':'unreviewed','operation':'integer native core crops only'})
(q/'joins.json').write_text(json.dumps(refs,indent=2)+'\n')
f=p/'tile-progress.json';v=json.loads(f.read_text()) if f.exists() else {}
v.update(tile=p.name,status='native_patch_production',selectedCoreCount=len(sel),nativePatchCount=len(sel),remainingCoreCount=16-len(sel),completeCandidateCount=0,internalPassed4kCount=0,formalAcceptedCount=0,lastSavedNative=native.name,inflightGeneration=None,actualModel=None,updatedAt=datetime.now(timezone.utc).isoformat())
f.write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({'selected':len(sel),'joins':[x['file'] for x in refs]}))

