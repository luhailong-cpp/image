from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c10').resolve()
Q=(B/'early-horizontal-qa').resolve()
assert Q.parent==B
Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
images={};sources={}
for row in range(1,4):
 for col in range(1,5):
  cell=f'r{row:02d}_c{col:02d}';p=B/'native'/f'{cell}.png';g=p.with_suffix('.png.generation.json')
  meta=json.loads(g.read_text(encoding='utf-8-sig'));digest=sha(p);assert digest==meta['sha256']
  im=Image.open(p);assert im.format=='PNG' and im.size==(1254,1254) and im.mode in ('RGB','RGBA')
  if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
  images[cell]=im.convert('RGB')
  sources[cell]={'file':str(p),'sha256':digest,'generationRecord':str(g),'generationRecordSha256':sha(g)}
checks=[]
for seam in (1,2):
 for col in range(1,5):
  upper=f'r{seam:02d}_c{col:02d}';lower=f'r{seam+1:02d}_c{col:02d}'
  im=Image.new('RGB',(1024,256))
  maps=[{'cell':upper,'sourceBox':[115,1011,1139,1139],'destinationXY':[0,0]},{'cell':lower,'sourceBox':[115,115,1139,243],'destinationXY':[0,128]}]
  for m in maps:im.paste(images[m['cell']].crop(m['sourceBox']),m['destinationXY'])
  name=f'horizontal_{seam}_col{col}';p=Q/(name+'.png');assert not p.exists();im.save(p)
  checks.append({'id':name,'kind':'core_assembly_horizontal_seam','file':str(p),'sha256':sha(p),'pixels':[1024,256],'targetCoreBox':[(col-1)*1024,seam*1024-128,col*1024,seam*1024+128],'seamGlobalY':seam*1024,'pixelMappings':maps,'operation':'integer crop and paste; no resampling','actualViewPerformed':False})
  im=images[lower].crop((115,166,1139,294))
  name=f'guide_horizontal_{seam}_col{col}';p=Q/(name+'.png');assert not p.exists();im.save(p)
  checks.append({'id':name,'kind':'guide_soft_context_interior_boundary','file':str(p),'sha256':sha(p),'pixels':[1024,128],'targetCoreBox':[(col-1)*1024,seam*1024+51,col*1024,seam*1024+179],'guideBoundaryGlobalY':seam*1024+115,'pixelMappings':[{'cell':lower,'sourceBox':[115,166,1139,294],'destinationXY':[0,0]}],'operation':'integer crop; no resampling','actualViewPerformed':False})
manifest=Q/'manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r09_c10','sources':sources,'checks':checks,'count':len(checks),'formalAccepted':False,'fullTileInspected':False,'scope':'First two assembly horizontal seams plus their next-row guide-interior boundaries, each split across4 columns. Reusable for final candidate only if corresponding crop pixels match exactly.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(manifest),'nativeSources':len(sources),'nativeCrops':len(checks)}))

