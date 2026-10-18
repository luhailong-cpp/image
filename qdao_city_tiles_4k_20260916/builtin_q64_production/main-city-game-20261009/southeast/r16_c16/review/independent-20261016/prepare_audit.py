from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parent;T=R.parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verified(r):assert sha(r['path'])==r['sha256'];im=Image.open(r['path']).convert('RGB');assert im.size==(4096,4096);return im
L=read(T/'candidate/latest-assembly.json');I=verified(L['candidate'])
E=[]
def save(name,im,box,kind):
 p=R/(name+'.png');assert not p.exists();im.save(p);E.append({'name':name,'path':str(p),'sha256':sha(p),'coreBox':box,'size':list(im.size),'kind':kind,'scale':1})
for pos in [1024,2048,3072]:
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  for ax in ['v','h']:
   box=[pos-200,a,pos+200,b] if ax=='v' else [a,pos-200,b,pos+200]
   save(f'{ax}{pos}-q{q}',I.crop(box),box,'internal_seam')
for x in [1024,2048,3072]:
 for y in [1024,2048,3072]:
  box=[x-450,y-450,x+450,y+450];save(f'junction-{x}-{y}',I.crop(box),box,'junction')
neighbors={}
for edge,tile in [('north','r15_c16'),('west','r16_c15')]:
 L2=read(T.parent/tile/'candidate/latest-assembly.json');neighbors[edge]=L2;N=verified(L2['candidate'])
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  if edge=='north':
   C=Image.new('RGB',(1024,640));C.paste(N.crop((a,3776,b,4096)),(0,0));C.paste(I.crop((a,0,b,320)),(0,320));box=[a,-320,b,320]
  else:
   C=Image.new('RGB',(640,1024));C.paste(N.crop((3776,a,4096,b)),(0,0));C.paste(I.crop((0,a,320,b)),(320,0));box=[-320,a,320,b]
  save(f'external-{edge}-q{q}',C,box,'actual_neighbor_core_only')
save('p03_04-course-turn',I.crop((3000,1940,3650,2570)),[3000,1940,3650,2570],'specific_watch')
ov=I.copy();ov.thumbnail((1024,1024));p=R/'overview-preview-only.png';assert not p.exists();ov.save(p)
(R/'audit-inputs.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':L,'neighbors':neighbors,'crops':E,'overview':{'path':str(p),'previewOnly':True,'scale':.25}},indent=2),encoding='utf-8')
print(json.dumps({'candidate':L['candidate'],'manifest':L['manifest'],'north':neighbors['north']['candidate'],'west':neighbors['west']['candidate'],'nativeQaCrops':len(E),'auditIndex':str(R/'audit-inputs.json')}))
