from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;Q=P/'qa/external-v8';Q.mkdir(parents=True,exist_ok=False)
V=P/'repairs/versions/external-v8';f=V/'r09_c10.png';tile=Image.open(f).convert('RGB');a=np.array(tile)
OLD=P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
leftpath=P.parent/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png';bottompath=OLD/'r10_c10.png';cornerpath=OLD/'r10_c09.png'
left=np.array(Image.open(leftpath).convert('RGB'));bottom=np.array(Image.open(bottompath).convert('RGB'));corner=np.array(Image.open(cornerpath).convert('RGB'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[]
def save(name,im,role):
 if isinstance(im,np.ndarray):im=Image.fromarray(im)
 path=Q/name;im.save(path);files.append({'file':str(path),'sha256':sha(path),'pixels':list(im.size),'role':role,'resized':False})
def board(name,strip,role):
 assert strip.shape==(4096,320,3)
 save(name,np.concatenate([strip[i*1024:(i+1)*1024] for i in range(4)],axis=1),role)
board('left-full4096-100pct.png',np.concatenate([left[:,-160:],a[:,:160]],axis=1),'Actual left boundary full4096, 4 sequential source-y segments')
bs=np.concatenate([a[-160:],bottom[:160]],axis=0)
board('bottom-full4096-100pct.png',np.transpose(bs,(1,0,2)),'Actual bottom boundary full4096, axes transposed, 4 sequential source-x segments')
board('left-treatment-return-x215-100pct.png',a[:,55:375],'Left initial treatment return x=215')
board('bottom-treatment-return-y3881-100pct.png',np.transpose(a[3721:4041],(1,0,2)),'Bottom initial treatment return y=3881, axes transposed')
four=np.concatenate([np.concatenate([left[-512:,-512:],a[-512:,:512]],axis=1),np.concatenate([corner[:512,-512:],bottom[:512,:512]],axis=1)],axis=0)
save('four-tile-junction-100pct.png',four,'Real four cores, southwest junction')
save('southwest-treatment-return-100pct.png',a[3440:,:720],'Southwest return and corner')
save('bottom-repair-and-return-100pct.png',np.concatenate([a[3469:,797:2051],bottom[:627,797:2051]],axis=0),'Full native bottom repair region with exact fixed neighboring core and repair returns')
save('left-repair-and-return-100pct.png',np.concatenate([left[853:2107,-512:],a[853:2107,:742]],axis=1),'Full native left repair region with exact fixed neighboring core and repair returns')
for axis in ('vertical','horizontal'):
 for index in range(1,4):
  out=Image.new('RGB',(920,1024) if axis=='vertical' else (1024,920))
  for n in range(4):
   c=index*1024;box=(c-115,n*1024,c+115,(n+1)*1024) if axis=='vertical' else (n*1024,c-115,(n+1)*1024,c+115)
   out.paste(tile.crop(box),(n*230,0) if axis=='vertical' else (0,n*230))
  save(f'internal-{axis}-{index}-100pct.png',out,f'Complete internal {axis} seam {index}')
out=Image.new('RGB',(690,690))
for y in range(1,4):
 for x in range(1,4):out.paste(tile.crop((x*1024-115,y*1024-115,x*1024+115,y*1024+115)),((x-1)*230,(y-1)*230))
save('nine-internal-intersections-100pct.png',out,'All nine internal source-cell intersections')
tile.resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-preview-only.jpg',quality=96)
ext=Image.open(P/'external-v5/output/extended-context.png').convert('RGB');ext.paste(tile,(115,115));ext.save(V/'extended-context.png')
record={'candidate':{'file':str(f),'sha256':sha(f)},'record':{'file':str(V/'repair.json'),'sha256':sha(V/'repair.json')},'neighbors':[{'file':str(p),'sha256':sha(p)} for p in [leftpath,bottompath,cornerpath]],'files':files,'extendedContext':{'file':str(V/'extended-context.png'),'sha256':sha(V/'extended-context.png'),'method':'v8 core at115,115 over v5 reference-only halo, no enlargement'},'status':'pending_visual_review','productionAccepted':False}
(Q/'evidence-index.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps({'candidateSha':sha(f),'qaFiles':len(files),'qaDirectory':str(Q)}))
