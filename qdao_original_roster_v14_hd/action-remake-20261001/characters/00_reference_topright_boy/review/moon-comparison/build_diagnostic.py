from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy')
out=root/'review/moon-comparison'
out.mkdir(parents=True,exist_ok=True)
selpath=root/'selected-new.json'
selbytes=selpath.read_bytes()
sel=json.loads(selbytes.decode('utf-8-sig'))
records=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for direction in ['E','S','SE','SW']:
 items=sorted([x for x in sel if x.get('action')=='run' and x.get('direction')==direction],key=lambda x:x['frame'])
 for start in [0,8]:
  canvas=Image.new('RGB',(1600,740),(232,232,232))
  draw=ImageDraw.Draw(canvas)
  for i,item in enumerate(items[start:start+8]):
   src=root/item['source']; data=src.read_bytes(); sha=hashlib.sha256(data).hexdigest()
   im=Image.open(src).convert('RGBA')
   crop=im.crop((180,650,1120,1254)).resize((400,257),Image.Resampling.LANCZOS)
   x=(i%4)*400;y=(i//4)*370
   canvas.paste(crop,(x,y+40),crop)
   draw.text((x+10,y+5),f'{direction}{item["frame"]:02d} {src.name} {sha[:10]}',font=font,fill=(0,0,0))
   records.append({'direction':direction,'frame':item['frame'],'source':item['source'],'sha256':sha,'size':list(im.size),'mode':im.mode})
  canvas.save(out/f'{direction}-lower-{start+1:02d}-{start+8:02d}.jpg',quality=95)
snapshot={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selectedNewSha256':hashlib.sha256(selbytes).hexdigest(),'criteria':'Independent shoe long-axis toe-out and knee/ankle alignment; moon reference is NOT a passed standard; no dynamic approval.','diagnosticTransform':{'fixedCrop':[180,650,1120,1254],'uniformResize':[400,257],'assetModification':False},'frames':records}
(out/'source-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),'count':len(records),'sizes':sorted({str(x['size']) for x in records})}))

