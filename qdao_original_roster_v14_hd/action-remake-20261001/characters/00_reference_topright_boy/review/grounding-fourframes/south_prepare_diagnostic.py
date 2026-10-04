from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy');out=root/'review/grounding-fourframes';out.mkdir(parents=True,exist_ok=True)
sel= json.loads((root/'selected-new.json').read_text(encoding='utf-8-sig'))
rows=[x for x in sel if x['action']=='run' and x['direction'] in ['S','SE','SW']]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for d in ['S','SE','SW']:
 canvas=Image.new('RGB',(1800,1100),(235,235,235));draw=ImageDraw.Draw(canvas)
 for i,x in enumerate(sorted([r for r in rows if r['direction']==d],key=lambda x:x['frame'])):
  p=root/x['source'];im=Image.open(p).convert('RGBA')
  x['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();x['size']=list(im.size)
  crop=im.crop((200,760,1100,1254)).resize((450,247),Image.Resampling.LANCZOS)
  px=i%4*450;py=i//4*275
  canvas.paste(crop,(px,py+28),crop)
  draw.text((px+6,py+3),f'{d}{x["frame"]:02d} '+p.name+' '+x['sha256'][:8],font=font,fill='black')
 canvas.save(out/f'south-initial-{d}-lower.jpg',quality=94)
snapshot={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requirement':{'frames':16,'frameMs':75,'cycleMs':1200,'minimumContinuousContactFramesPerFoot':4},'initialContactSegments':{'S':{'right':[1,2,3],'left':[9,10,11],'uncertain':[4,12]},'SE':{'right':[1,2,3],'left':[9,10,11],'uncertain':[4,12]},'SW':{'firstSupport':[1,2,3],'secondSupport':[8,9,10,11],'uncertain':[4]}},'frames':rows}
(out/'south-initial-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print('48 source hashes captured.')

