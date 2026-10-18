from pathlib import Path
import json,hashlib,sys
from PIL import Image
T=Path(__file__).resolve().parent
v=sys.argv[1]; W=250
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=read(T/'records'/(v+'.preparation.json'))
src=T/'native'/(v+'.png')
with Image.open(src) as im: target=im.convert('RGB')
cb=prep['coordinates']['coreBox']; origin=prep['coordinates']['contextBox'][:2]
out=T/'review'/('quick-'+v);out.mkdir(exist_ok=True)
evidence=[]
def cut(im,box,org):return im.crop((box[0]-org[0],box[1]-org[1],box[2]-org[0],box[3]-org[1]))
for a in prep['anchors']:
 other=Path(a['path']);assert sha(other)==a['sha256']
 with Image.open(other) as im: near=im.convert('RGB')
 org=a['sourceGlobalBox'][:2]
 d=a['direction']
 if d in ('left','right'):
  seam=cb[0] if d=='left' else cb[2]
  own=[seam,seam] # overwritten below
  own=[cb[0],cb[1],cb[0]+W,cb[3]] if d=='left' else [cb[2]-W,cb[1],cb[2],cb[3]]
  oth=[cb[0]-W,cb[1],cb[0],cb[3]] if d=='left' else [cb[2],cb[1],cb[2]+W,cb[3]]
  left,right=(cut(near,oth,org),cut(target,own,origin)) if d=='left' else (cut(target,own,origin),cut(near,oth,org))
  result=Image.new('RGB',(W*2,1024));result.paste(left,(0,0));result.paste(right,(W,0))
 else:
  own=[cb[0],cb[1],cb[2],cb[1]+W] if d=='top' else [cb[0],cb[3]-W,cb[2],cb[3]]
  oth=[cb[0],cb[1]-W,cb[2],cb[1]] if d=='top' else [cb[0],cb[3],cb[2],cb[3]+W]
  top,bottom=(cut(near,oth,org),cut(target,own,origin)) if d=='top' else (cut(target,own,origin),cut(near,oth,org))
  result=Image.new('RGB',(1024,W*2));result.paste(top,(0,0));result.paste(bottom,(0,W))
 for box,o,img in ((own,origin,target),(oth,org,near)):
  assert 0<=box[0]-o[0]<box[2]-o[0]<=img.width and 0<=box[1]-o[1]<box[3]-o[1]<=img.height
 path=out/(d+'-actual-core-join.png')
 with path.open('xb') as f:result.save(f,format='PNG')
 evidence.append({'direction':d,'path':str(path),'sha256':sha(path),'size':list(result.size),'ownGlobalBox':own,'neighborGlobalBox':oth,'neighbor':other.as_posix(),'neighborSha256':sha(other),'resized':False})
record={'tile':T.name,'version':v,'native':str(src),'nativeSha256':sha(src),'evidence':evidence,'reviewStatus':'pending_actual_view','formalAccepted':False}
with (out/'evidence.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps(record))

