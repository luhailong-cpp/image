import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
z=Path(__file__).resolve().parent.parent
tile='r03_c14';tag='east-candidate-v2-20261016'
sel=json.loads((z/'records'/f'{tile}.working-selection.json').read_text(encoding='utf-8-sig'))
assert len(sel)==16
pending={}
qa=z/'qa'/tile/tag;qa.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return {'path':str(p).replace('\\','/'),'sha256':sha(p),'role':role}
cores={};sources=[];native_items=[]
out=Image.new('RGB',(4096,4096))
for r in range(1,5):
 for c in range(1,5):
  p=f'{tile}_p{r}{c}';f=z/'native'/sel[p];im=Image.open(f).convert('RGB');assert im.size==(1254,1254)
  generation=Path(str(f)+'.generation.json');g=json.loads(generation.read_text(encoding='utf-8-sig'));assert g['sha256']==sha(f)
  core=im.crop((115,115,1139,1139));cores[(r,c)]=core;out.paste(core,((c-1)*1024,(r-1)*1024))
  s={'patchId':p,**ref(f,'native source'),'nativeSize':[1254,1254],'cropBox':[115,115,1139,1139],'pasteAt':[(c-1)*1024,(r-1)*1024],'quickSelection':p not in pending,'pendingIssue':pending.get(p,{}).get('issue'),'generationRecord':ref(generation,'native generation evidence'),'actualModel':g.get('actualModel')}
  sources.append(s);native_items.append({'kind':'native','patchId':p,**ref(f,'full1254 native'),'status':'pending independent whole-block review'})
fout=z/'tiles'/f'{tile}.{tag}.png';assert not fout.exists();out.save(fout)
for (r,c),im in cores.items():assert ImageChops.difference(out.crop(((c-1)*1024,(r-1)*1024,c*1024,r*1024)),im).getbbox() is None
items=list(native_items)
for r in range(1,5):
 for c in range(1,4):
  im=Image.new('RGB',(256,1024));im.paste(cores[r,c].crop((896,0,1024,1024)),(0,0));im.paste(cores[r,c+1].crop((0,0,128,1024)),(128,0))
  f=qa/f'edge-h-p{r}{c}-p{r}{c+1}.png';im.save(f);items.append({'kind':'edge','axis':'horizontal neighbors','patches':[f'p{r}{c}',f'p{r}{c+1}'],**ref(f,'native1:1 seam'),'seamX':128,'status':'pending'})
for r in range(1,4):
 for c in range(1,5):
  im=Image.new('RGB',(1024,256));im.paste(cores[r,c].crop((0,896,1024,1024)),(0,0));im.paste(cores[r+1,c].crop((0,0,1024,128)),(0,128))
  f=qa/f'edge-v-p{r}{c}-p{r+1}{c}.png';im.save(f);items.append({'kind':'edge','axis':'vertical neighbors','patches':[f'p{r}{c}',f'p{r+1}{c}'],**ref(f,'native1:1 seam'),'seamY':128,'status':'pending'})
for r in range(1,4):
 for c in range(1,4):
  im=out.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256));f=qa/f'junction-r{r+1}c{c+1}.png';im.save(f);items.append({'kind':'junction',**ref(f,'native1:1 junction'),'seam':[256,256],'status':'pending'})
assert len(items)==49
preview=z/'qa'/f'{tile}.{tag}.preview1024.png';assert not preview.exists();out.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
manifest={'tile':tile,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':None,'status':'candidate16_native_16_quick_selected_pending_independent49','formalAccepted':False,'tileInternalReview':'pending independent49','quickSelectedCoreCount':16,'provisionalNativeCoreCount':16,'candidate':ref(fout,'4096 integer assembly of native1024 cores'),'candidateSize':[4096,4096],'noResizeNoBlendNoPaint':True,'pixelIdentityCheck':'all16 core pixels identical','sources':sources,'knownPending':pending,'reviewItems':items,'preview':ref(preview,'downscaled overview only, not native art')}
write(z/'records'/f'{tile}.{tag}.manifest.json',manifest);write(qa/'review-index.json',manifest);write(Path(str(preview)+'.derived.json'),{'purpose':'overview only','source':ref(fout,'native-core candidate'),'operation':'4096 to1024 LANCZOS downscale only, never native deliverable'})
print(json.dumps({'candidate':ref(fout,'pending candidate'),'manifest':str(z/'records'/f'{tile}.{tag}.manifest.json'),'qa':str(qa),'quickSelected':16,'nativeCores':16,'formalAccepted':False}))

