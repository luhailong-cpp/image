from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;D=N/'full-review-v016';D.mkdir(exist_ok=False)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
cp=read(T/'source-checkpoint.json');src=cp['fragment'];assert src['tile']=='r08_c11' and src['fullyPainted'];A=Image.open(src['file']).convert('RGBA');assert sha(src['file'])==src['sha256'] and np.all(np.asarray(A)[:,:,3]==255)
sources={s['tile']:s for s in cp['candidateSet']};records=[]
for j,y in enumerate([0,1280,2560]):
 for i,x in enumerate([0,1280,2560]):
  box=[x,y,x+1536,y+1536];p=D/f'full-{j+1}{i+1}.png';A.crop(box).save(p);records.append(dict(ref(p),kind='full-native-coverage',ownLTRB=box,pixels=[1536,1536],nativeScale=1))
west=Image.open(sources['r08_c10']['file']).convert('RGBA');north=Image.open(sources['r07_c11']['file']).convert('RGBA')
W=Image.new('RGBA',(640,4096));W.paste(west.crop((3776,0,4096,4096)),(0,0));W.paste(A.crop((0,0,320,4096)),(320,0))
V=Image.new('RGBA',(4096,640));V.paste(north.crop((0,3776,4096,4096)),(0,0));V.paste(A.crop((0,0,4096,320)),(0,320))
for i,p0 in enumerate([0,1280,2560]):
 for kind,im,box in [('west',W,[0,p0,640,p0+1536]),('north',V,[p0,0,p0+1536,640])]:
  p=D/f'{kind}-{i+1}.png';im.crop(box).save(p);records.append(dict(ref(p),kind=kind,nativeScale=1,assembledLTRB=box,boundaryAt=320))
used={k:v for k,v in sources.items() if k in ['r08_c11','r08_c10','r07_c11','r07_c10','r07_c12','r09_c10']}
for name,(gx,gy) in {'nw':(40960,28672),'ne':(45056,28672),'sw':(40960,32768)}.items():
 C=Image.new('RGBA',(768,768));cx,cy=gx-384,gy-384
 for tile,s in used.items():
  assert sha(s['file'])==s['sha256'];ox=(int(tile[5:7])-1)*4096;oy=(int(tile[1:3])-1)*4096;C.alpha_composite(Image.open(s['file']).convert('RGBA'),(ox-cx,oy-cy))
 p=D/f'corner-{name}.png';C.save(p);records.append(dict(ref(p),kind='corner-'+name,worldLTRB=[cx,cy,cx+768,cy+768],nativeScale=1,missingPixels=int((np.asarray(C)[:,:,3]==0).sum())))
save(D/'root-checkpoint-frozen.json',cp)
save(D/'native-crop-index.json',{'source':src,'sources':used,'rootCheckpoint':ref(D/'root-checkpoint-frozen.json'),'crops':records,'coveragePixels':16777216,'pendingExternalChecks':['r08_c12 east unbuilt','r09_c11 south unbuilt','whole256 city and client runtime'],'formalAccepted':False})
print(json.dumps({'directory':str(D),'source':src,'cropCount':len(records)}))
