from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone
R=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(im,name,sources,operation):
 p=R/name; im.save(p)
 p.with_name(p.name+'.generation.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'createdAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':'PNG','derivedFrom':[{'file':str(s),'sha256':sha(s),'generationRecord':str(s)+'.generation.json'} for s in sources],'operation':operation,'productionPixels':False,'purpose':'QA only; not 4K tile'},indent=2)+'\n')
paths=[R/f'p3{i}.png' for i in range(1,5)]
ims=[Image.open(p).convert('RGB') for p in paths]
row=Image.new('RGB',(4096,1024))
for i,im in enumerate(ims): row.paste(im.crop((115,115,1139,1139)),(i*1024,0))
save(row,'row3-core-strip-qa.png',paths,{'kind':'unaltered_core_crops_side_by_side','scale':1,'coreLTRB':[115,115,1139,1139],'notFinalAssembly':True})
save(row.resize((1536,384),Image.Resampling.LANCZOS),'row3-preview.png',paths,{'kind':'QA_downsample','scale':0.375})
seams=Image.new('RGB',(1536,1024))
for i in range(3): seams.paste(row.crop((1024*(i+1)-256,0,1024*(i+1)+256,1024)),(i*512,0))
save(seams,'internal-seams-100pct.png',paths,{'kind':'three_vertical_seams','scale':1,'seamPositionsWithinColumns':[256,768,1280]})
corners=Image.new('RGB',(2048,512))
for i,im in enumerate(ims):
 for k,b in enumerate([(0,0,256,256),(998,0,1254,256),(0,998,256,1254),(998,998,1254,1254)]):
  corners.paste(im.crop(b),((i*2+k%2)*256,(k//2)*256))
save(corners,'all-patch-corners-100pct.png',paths,{'kind':'16_corner_crops','scale':1,'patchColumns':4,'eachPatchArrangement':'topLeft/topRight then bottomLeft/bottomRight','crossRowJunctionVerified':False})
print('Saved row3 QA images')
