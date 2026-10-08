from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
OUT=(ROOT/'r09_c08/early-east-qa').resolve()
assert OUT.is_relative_to(ROOT)
OUT.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgbsha(im): return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
sources=[]
column=Image.new('RGB',(1024,4096))
for row in range(1,5):
 p=ROOT/f'r09_c08/native/r{row:02}_c04.png'
 g=Path(str(p)+'.generation.json')
 rec=json.loads(g.read_text(encoding='utf-8-sig'))
 assert sha(p)==rec['sha256']
 im=Image.open(p).convert('RGB'); assert im.size==(1254,1254)
 core=im.crop((115,115,1139,1139))
 column.paste(core,(0,(row-1)*1024))
 sources.append({'path':str(p),'sha256':sha(p),'generationRecord':str(g),'generationRecordSha256':sha(g),'sourceOutputPath':rec['evidence']['sourceOutputPath'],'width':1254,'height':1254,'row':row,'coreCrop':[115,115,1139,1139],'columnPaste':[0,(row-1)*1024,1024,row*1024],'rgbSha256':rgbsha(im)})
ep=ROOT/'r09_c09/selected/core4096.png'
east=Image.open(ep).convert('RGB'); assert east.size==(4096,4096)
eastsrc={'path':str(ep),'sha256':sha(ep),'width':4096,'height':4096,'rgbSha256':rgbsha(east)}
def ownmaps(box,offset=(0,0)):
 x0,y0,x1,y1=box; out=[]
 for s in sources:
  start=(s['row']-1)*1024; sy0=max(y0,start); sy1=min(y1,start+1024)
  if sy1>sy0:
   out.append({'sourcePath':s['path'],'sourceSha256':s['sha256'],'sourceCrop':[115+x0,115+sy0-start,115+x1,115+sy1-start],'destinationBox':[offset[0],offset[1]+sy0-y0,offset[0]+x1-x0,offset[1]+sy1-y0],'tileCoreBox':[3072+x0,sy0,3072+x1,sy1]})
 return out
scopes=[]
def save(name,kind,im,mappings,loc):
 p=OUT/(name+'.png'); assert not p.exists()
 im.save(p)
 scopes.append({'id':name,'kind':kind,'path':str(p),'sha256':sha(p),'width':im.width,'height':im.height,'rgbSha256':rgbsha(im),'sourceMappings':mappings,'location':loc,'actualViewCompleted':False,'automaticAcceptance':False})
for row in range(1,5):
 y0=(row-1)*1024; y1=row*1024
 ownbox=(768,y0,1024,y1)
 im=Image.new('RGB',(512,1024)); im.paste(column.crop(ownbox),(0,0)); im.paste(east.crop((0,y0,256,y1)),(256,0))
 mappings=ownmaps(ownbox)+[{'sourcePath':str(ep),'sourceSha256':sha(ep),'sourceCrop':[0,y0,256,y1],'destinationBox':[256,0,512,1024]}]
 save(f'east-r{row:02}','externalEast',im,mappings,{'tileBoundaryX':4096,'displayJoinX':256,'tileY':[y0,y1]})
 box=(845,y0,973,y1)
 save(f'guide-x3981-r{row:02}','guideVertical',column.crop(box),ownmaps(box),{'tileCoreBox':[3917,y0,4045,y1],'displayGuideX':64,'guideTileX':3981})
for i in range(1,4):
 y=1024*i; box=(0,y-128,1024,y+128)
 save(f'internal-y{y}-c04','internalHorizontal',column.crop(box),ownmaps(box),{'tileCoreBox':[3072,y-128,4096,y+128],'displayJoinY':128,'joinTileY':y})
 g=y+115; box=(0,g-64,1024,g+64)
 save(f'guide-y{g}-c04','guideHorizontal',column.crop(box),ownmaps(box),{'tileCoreBox':[3072,g-64,4096,g+64],'displayGuideY':64,'guideTileY':g})
manifest={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r09_c08','scope':'First completed native column c04 only; no resampling or edits','sourceNative':sources,'eastSelected':eastsrc,'assembly':{'dimensions':[1024,4096],'tileCoreBox':[3072,0,4096,4096],'rgbSha256':rgbsha(column),'operation':'Each native crop [115,115,1139,1139] pasted in row order. RGB unchanged. No interpolation.'},'scopeCount':len(scopes),'scopes':scopes,'reviewStatus':'pending actual image inspection; export is not acceptance','excluded':'North row1 internal guide y115: north source is core-only and has no 230px native overlap.'}
assert len(scopes)==14
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scopeCount':len(scopes),'manifestSha256':sha(OUT/'manifest.json'),'scopeIds':[s['id'] for s in scopes]},indent=2))
