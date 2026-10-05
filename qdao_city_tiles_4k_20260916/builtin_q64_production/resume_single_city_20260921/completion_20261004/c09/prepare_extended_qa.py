from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1];A=S.parents[1]
O=R/'tone-candidate-v1';Q=O/'qa-returns';Q.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=O/'r08_c09.png';im=Image.open(source).convert('RGB')
entries=[]
def save(crop,name,scope):
 p=Q/(name+'.png');crop.save(p)
 entries.append({'file':str(p),'sha256':sha(p),'scope':scope,'pixelScale':'1:1','viewed':False})
for axis in ('x','y'):
 for at in (1024,2048,3072):
  for half in range(2):
   board=Image.new('RGB',(1024,1024));boxes=[]
   for i in range(2):
    seg=2*half+i;box=(at-256,seg*1024,at+256,(seg+1)*1024) if axis=='x' else (seg*1024,at-256,(seg+1)*1024,at+256)
    part=im.crop(box)
    if axis=='x':part=part.transpose(Image.Transpose.ROTATE_90)
    board.paste(part,(0,i*512));boxes.append(box)
   save(board,f'{axis}{at}-returns-half{half+1}',{'axis':axis,'at':at,'source':str(source),'boxes':boxes,'rotation90':axis=='x'})
lower=S/'continuation_20261004/c09-pair-v2/r09_c09.png'
lowerim=Image.open(lower).convert('RGB')
right=R.parent/'c10-seed/joined-v1/r09_c10.png'
bottom=A/'builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c09.png'
edges=[('shared-c09-south',np.concatenate([np.array(im)[-256:],np.array(lowerim)[:256]],axis=0),'horizontal',[source,lower]),('r09-right',np.concatenate([np.array(lowerim)[:,-256:],np.array(Image.open(right).convert('RGB'))[:,:256]],axis=1),'vertical',[lower,right]),('r09-bottom',np.concatenate([np.array(lowerim)[-256:],np.array(Image.open(bottom).convert('RGB'))[:256]],axis=0),'horizontal',[lower,bottom])]
for name,edge,direction,sources in edges:
 for half in range(2):
  board=Image.new('RGB',(1024,1024))
  for i in range(2):
   seg=2*half+i
   part=Image.fromarray(edge[:,seg*1024:(seg+1)*1024] if direction=='horizontal' else edge[seg*1024:(seg+1)*1024])
   if direction=='vertical':part=part.transpose(Image.Transpose.ROTATE_90)
   board.paste(part,(0,i*512))
  save(board,f'{name}-half{half+1}',{'side':name,'half':half+1,'sources':[{'file':str(p),'sha256':sha(p)} for p in sources]})
(Q/'index.json').write_text(json.dumps({'source':{'file':str(source),'sha256':sha(source)},'evidence':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qa':str(Q),'count':len(entries)}))
