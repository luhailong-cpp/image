import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
at=datetime.now(timezone.utc).isoformat()
# Reorder independently generated anticipation frames once, preserving their source records.
marker=root/'records/attack_E_reorder_02_03.json'
if not marker.exists():
 paths=[root/'runtime/attack/E'/f'{i:02d}.png' for i in (2,3)]
 data=[p.read_bytes() for p in paths]
 recs=[json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8')) for p in paths]
 swaps=[]
 for dst,srcidx in zip(paths,(1,0)):
  old=paths[srcidx].relative_to(root).as_posix()
  dst.write_bytes(data[srcidx])
  rec=recs[srcidx]; rec['file']=dst.relative_to(root).as_posix()
  rec['sequenceReorder']={'at':at,'originalExportSlot':old,'reason':'实际杖头轨迹采用低后摆→较高后摆→竖杖，避免原02/03上/下/上回跳；仅重排原生独立姿态，未镜像、变形或插值'}
  dst.with_name(dst.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  source_rec=root/rec['derivedFrom'][0]['generationRecord']
  source=json.loads(source_rec.read_text(encoding='utf-8')); source['originalExportPath']=source['exportPath']; source['exportPath']=rec['file']; source['sequenceReorder']=rec['sequenceReorder']
  source_rec.write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  swaps.append({'from':old,'to':rec['file'],'sha256':sha(dst)})
 marker.write_text(json.dumps({'at':at,'swaps':swaps},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=root/'review'; review.mkdir(exist_ok=True)
audit={'checkedAt':at,'action':'attack','expected':24,'durationMs':360,'frameDurationMs':30,'impactFrame':6,'dynamicPassed':False,'clientIntegrated':False,'frames':[]}
for direction in ('E','W'):
 images=[]
 board=Image.new('RGB',(1536,1164),'#eeeeec'); draw=ImageDraw.Draw(board)
 for i in range(12):
  p=root/'runtime/attack'/direction/f'{i:02d}.png'; im=Image.open(p).convert('RGBA'); images.append(im)
  rec=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
  assert im.size==(1024,1024) and im.getchannel('A').getextrema()==(0,255)
  assert sha(p)==rec['sha256']
  origin=rec['derivedFrom'][0]
  assert (root/origin['generationRecord']).exists()
  audit['frames'].append({'file':p.relative_to(root).as_posix(),'sha256':sha(p),'mode':im.mode,'size':list(im.size),'alphaExtrema':im.getchannel('A').getextrema(),'alphaBBox':im.getchannel('A').getbbox(),'source':origin})
  thumb=im.resize((384,384),Image.Resampling.LANCZOS); x=(i%4)*384;y=(i//4)*388
  board.paste(thumb,(x,y),thumb); draw.text((x+8,y+8),f'{direction} {i:02d}',fill='#333333')
 board.save(review/f'attack_{direction}_sequence.png')
 previews=[]
 for im in images:
  bg=Image.new('RGBA',(512,512),'#e7e8e4');bg.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
  previews.append(bg.convert('RGB'))
 for name,duration in [('normal',30),('slow',120)]:
  previews[0].save(review/f'attack_{direction}_{name}.gif',save_all=True,append_images=previews[1:],duration=duration,loop=0,disposal=2)
audit['actual']=len(audit['frames']);audit['technicalPassed']=True
(review/'attack_technical_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':audit['actual'],'technicalPassed':True,'dynamicPassed':False,'reorderedE':[2,3]},ensure_ascii=False))
