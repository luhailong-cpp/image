from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
d=Path(__file__).parent;base=d.parent
selected={1:'01',2:'02',3:'03',5:'05',6:'06-v3'}
phases={1:'A pre-contact, both boots airborne',2:'A initial contact, shallow knee',3:'A compression, lowered hip/head',4:'A support/reference from ROOT',5:'A late support, mild heel rise',6:'A forefoot push, clear raised heel'}
audit=[];slots={};sheet=Image.new('RGB',(960,704),'#e9e8e1');draw=ImageDraw.Draw(sheet)
for j,i in enumerate(range(1,7)):
 p=(base/'generation/run-SW-04/native.png') if i==4 else d/f'run-SW-{selected[i]}.png'
 im=Image.open(p).convert('RGBA');h=hashlib.sha256(p.read_bytes()).hexdigest();a=im.getchannel('A');bbox=a.point(lambda x:255 if x>32 else 0).getbbox()
 thumb=im.resize((320,320),Image.Resampling.LANCZOS);x=j%3*320;y=j//3*352;sheet.paste(thumb,(x,y),thumb)
 draw.text((x+5,y+322),f'{i:02d} '+p.parent.name+'/'+p.name,fill='#222');draw.text((x+5,y+336),phases[i],fill='#555')
 item={'slot':f'run/SW/{i:02d}','file':p.relative_to(base).as_posix(),'sha256':h,'nativeSize':list(im.size),'mode':im.mode,'alphaContentBBoxThreshold32':bbox,'actualPhase':phases[i],'durationMs':75,'isOwnedDeliverable':i!=4}
 audit.append(item)
 if i!=4:
  slots[item['slot']]=item['file']
  m=d/(p.name+'.generation.json');meta=json.loads(m.read_text(encoding='utf8'));meta['visualReview']={'status':'static-reviewed','document':'REVIEW_20261003.md','actualPhase':phases[i],'dynamicValidation':False};m.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
sheet.save(d/'contact-first-half.jpg',quality=95)
(d/'contact-first-half.jpg.generation.json').write_text(json.dumps({'operation':'Diagnostic contact: equal full native canvas resized1254to320; no per-frame bbox scaling or shifts','sources':audit},indent=2),encoding='utf8')
(d/'selection.json').write_text(json.dumps({'status':'five_owned_slots_static_reviewed_for_ROOT_merge','slots':slots},indent=2),encoding='utf8')
(d/'frames-audit.json').write_text(json.dumps({'selectedOwned':5,'uniqueOwned':len({f['sha256'] for f in audit if f['isOwnedDeliverable']}),'referenceSlots':[4],'frames':audit},indent=2),encoding='utf8')
(d/'timing-grounding.json').write_text(json.dumps({'cycleMs':1200,'frameMs':75,'phaseWeightsApplied':False,'requiredFrames':16,'ownedFrames':5,'allowFullLoop':False,'note':'Partial contribution only; ROOT assembles remaining11 slots and confirms all16 before full-loop playback. Combat timings unchanged.'},indent=2),encoding='utf8')
print('5 selected native RGBA, unique',len({f['sha256'] for f in audit if f['isOwnedDeliverable']}))

