from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa/r07_c11-west-resume-v2';O=Q/'central-independent-v2';O.mkdir(exist_ok=True)
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rf(p):return {'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p)}
def wr(p,d):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
m=rd(Q/'manifest.json');candidate=Path(m['candidate']['file']);assert sha(candidate)=='988fa152daffc7fdbcf9d7c568c3cbc14efc333fc97e6ae6b1ed948871826e49'
a=Image.open(candidate).convert('RGB');assert a.size==(4096,4096)
rebuild=Image.new('RGB',(4096,4096));inputs=[];sources={}
for e in m['inputs']:
 p=Path(e['path']);assert sha(p)==e['sha256'];im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
 r,c=int(e['patchId'][-2]),int(e['patchId'][-1]);core=im.crop((115,115,1139,1139));rebuild.paste(core,((c-1)*1024,(r-1)*1024));sources[e['patchId']]=p
 inputs.append({'patch':e['patchId'],**rf(p),'nativePixels':list(im.size),'coreRgbSha256':hashlib.sha256(core.tobytes()).hexdigest()})
assert rebuild.tobytes()==a.tobytes()
checks=[]
for e in m['qa']:
 p=Path(e['file']);assert sha(p)==e['sha256'];im=Image.open(p).convert('RGB');assert im.tobytes()==a.crop(e['candidateCropBox']).tobytes();checks.append({'qa':rf(p),'candidateCropBox':e['candidateCropBox'],'exactPixelEquality':True})
wr(O/'mechanical.json',{'candidate':rf(candidate),'selection':rf(m['selection']['path']),'manifest':rf(Q/'manifest.json'),'selectedSourceCount':len(inputs),'sources':inputs,'independentCoreRebuildPixelEquality':True,'all49QAExactCandidateCrops':True,'qa':checks,'nativeUpscale':False,'formalAccepted':False})
neighborSelections=[]
for rel,keep in [('records/r07_c12.selection-closure-v5.json',lambda k:k[-1]=='1'),('records/west_sol/r06_c11.selection-proposed-resume-v2.json',lambda k:k[-2]=='4'),('records/r06_c12.selection-closure-v5.json',lambda k:k.endswith('p41'))]:
 sel=Z/rel;d=rd(sel);patches=d.get('patches',d.get('selected',{}));neighborSelections.append(rf(sel))
 for key,e in patches.items():
  if not keep(key):continue
  p=Path(e['path']);p=p if p.is_absolute() else Z/p;assert sha(p)==e['sha256'];assert Image.open(p).size==(1254,1254);sources[key]=p
items=[]
def qa(name,size,pieces):
 out=Image.new('RGB',size);rr=[]
 for key,box,at in pieces:
  p=sources[key];out.paste(Image.open(p).convert('RGB').crop(box),at);rr.append({'patch':key,**rf(p),'cropBox':box,'pasteAt':at})
 path=O/(name+'.png');assert not path.exists();out.save(path);items.append({'name':name,**rf(path),'size':size,'sources':rr,'operation':'native integer crop and opaque paste only','visualReview':'pending'})
for c in range(1,5):qa(f'north-c{c}',(1024,256),[(f'r06_c11_p4{c}',[115,1011,1139,1139],[0,0]),(f'r07_c11_p1{c}',[115,115,1139,243],[0,128])])
for r in range(1,5):qa(f'east-r{r}',(256,1024),[(f'r07_c11_p{r}4',[1011,115,1139,1139],[0,0]),(f'r07_c12_p{r}1',[115,115,243,1139],[128,0])])
def j(name,keys):
 if not all(k in sources for k in keys):return
 qa(name,(512,512),list(zip(keys,[[883,883,1139,1139],[115,883,371,1139],[883,115,1139,371],[115,115,371,371]],[[0,0],[256,0],[0,256],[256,256]])))
for c in range(1,4):j(f'north-junction-c{c}',[f'r06_c11_p4{c}',f'r06_c11_p4{c+1}',f'r07_c11_p1{c}',f'r07_c11_p1{c+1}'])
for r in range(1,4):j(f'east-junction-r{r}',[f'r07_c11_p{r}4',f'r07_c12_p{r}1',f'r07_c11_p{r+1}4',f'r07_c12_p{r+1}1'])
j('northeast-junction',['r06_c11_p44','r06_c12_p41','r07_c11_p14','r07_c12_p11'])
wr(O/'external-manifest.json',{'candidate':rf(candidate),'neighborSelections':neighborSelections,'qa':items,'count':len(items),'neighborStatus':'Pinned candidate sources only; no formal neighbor/global acceptance claimed','formalAccepted':False})
print(json.dumps({'coreCount':len(inputs),'qaExact':len(checks),'externalCount':len(items),'mechanical':rf(O/'mechanical.json')}))
