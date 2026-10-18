import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
import numpy as np
tid='r10_c10';ref=Path(read(ROOT/'references.json')[0]['file']);ri=Image.open(ref).convert('RGB')
tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==tid)
assert not list((ROOT/'native').glob(tid+'*.png'))
for p in tile['patches']:
 f=ROOT/'guides'/f"{p['id']}.layout-only.png"
 if f.exists():continue
 ri.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(f)
 write(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sha(f),'generatedAt':now(),'operation':'layout reference fractional crop/enlargement only, never final pixels','derivedFrom':[{'file':str(ref),'sha256':sha(ref)}],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
# Verify exact selected western source strips in the latest eastern neighbor.
nf=ROOT/'tiles'/'r10_c11.candidate-v04.png';ni=Image.open(nf).convert('RGB');checks=[]
for r,v in [(1,'v01'),(2,'v02'),(3,'v02'),(4,'v01')]:
 s=ROOT/'native'/f'r10_c11_p{r}1_{v}.png';a=np.array(ni.crop((0,(r-1)*1024,256,r*1024)));b=np.array(Image.open(s).convert('RGB').crop((115,115,371,1139)));m=int(np.any(a!=b,axis=2).sum());assert m==0
 checks.append({'source':str(s),'sha256':sha(s),'candidateWest256Mismatch':m})
write(ROOT/'qa'/'wall-oct16'/'r10_east_anchor_audit.json',{'neighbor':str(nf),'sha256':sha(nf),'sources':checks,'checkedAt':now()})
print(json.dumps({'tile':tid,'existingNative':0,'eastWest256PixelMismatches':0,'guidesReady':16}))
