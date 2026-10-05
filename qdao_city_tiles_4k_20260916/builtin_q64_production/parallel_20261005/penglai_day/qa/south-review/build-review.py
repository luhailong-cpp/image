from pathlib import Path
from PIL import Image
import hashlib,json,datetime,numpy as np
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day')
OUT=ROOT/'qa/south-review';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=[f'p{r}{c}' for r in [3,4] for c in range(1,5)]
ims={n:Image.open(ROOT/'native'/(n+'.png')).convert('RGB') for n in names}
inputs={n:{'file':str(ROOT/'native'/(n+'.png')),'sha256':sha(ROOT/'native'/(n+'.png')),'pixels':ims[n].size}for n in names}
items=[]
def save(name,size,parts,scope,region):
 im=Image.new('RGB',size)
 rec={'id':name,'scope':scope,'tileRectXYWH':region,'output':str(OUT/(name+'.png')),'outputPixels':size,'parts':[],'operation':'Exact integer crops pasted at1:1, no registration, resampling, color correction or feathering'}
 for n,box,pos in parts:
  im.paste(ims[n].crop(box),pos)
  rec['parts'].append({'source':inputs[n],'cropBoxLTRB':box,'pasteXY':pos})
 im.save(rec['output']);rec['sha256']=sha(rec['output']);items.append(rec)
for r in [3,4]:
 for c in [1,2,3]:
  a=f'p{r}{c}';b=f'p{r}{c+1}'
  save(f'v-r{r}-c{c}-{c+1}',(384,1024),[(a,(947,115,1139,1139),(0,0)),(b,(115,115,307,1139),(192,0))],'native vertical seam1024px',(c*1024-192,(r-1)*1024,384,1024))
for c in range(1,5):
 a=f'p3{c}';b=f'p4{c}'
 save(f'h-r3-4-c{c}',(1024,384),[(a,(115,947,1139,1139),(0,0)),(b,(115,115,1139,307),(0,192))],'native horizontal seam1024px',((c-1)*1024,3072-192,1024,384))
for c in [1,2,3]:
 save(f'cross-c{c}-{c+1}',(384,384),[(f'p3{c}',(947,947,1139,1139),(0,0)),(f'p3{c+1}',(115,947,307,1139),(192,0)),(f'p4{c}',(947,115,1139,307),(0,192)),(f'p4{c+1}',(115,115,307,307),(192,192))],'native four-patch crossing',(c*1024-192,3072-192,384,384))
save('corner-bottom-left',(384,384),[('p41',(115,755,499,1139),(0,0))],'outer bottom-left corner, missing southern/left future boundary not accepted',(0,3712,384,384))
save('corner-bottom-right',(384,384),[('p44',(755,755,1139,1139),(0,0))],'outer bottom-right corner, missing southern/east future boundary not accepted',(3712,3712,384,384))
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r09_c13','sourceCoreBoxLTRB':[115,115,1139,1139],'reviewScope':'Only raw southern rows3/4:6vertical+4horizontal1024pxseams,3crossings,2outerbottomcorners','nativeInputs':inputs,'items':items,'wholeTileAccepted':False}
(OUT/'crop-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Created',len(items),'native-scale review images')

