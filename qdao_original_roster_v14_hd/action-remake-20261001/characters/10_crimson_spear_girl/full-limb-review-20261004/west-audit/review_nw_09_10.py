from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime
r=Path(__file__).resolve().parents[2]; out=r/'full-limb-review-20261004/west-audit'
paths=[r/'full-limb-review-20261004/run-NW/inputs/gun09-1254.png',r/'full-limb-review-20261004/run-NW/09-v4/native.png',r/'full-limb-review-20261004/run-NW/inputs/gun10-1254.png',r/'full-limb-review-20261004/run-NW/10-v3/native.png']
labels=['09 original','09-v4 selected','10 original','10-v3 selected']
for kind in ['full','lower']:
 size=(420,440) if kind=='full' else (550,410)
 board=Image.new('RGB',(size[0]*4,size[1]),(238,235,224));draw=ImageDraw.Draw(board)
 for i,(p,label) in enumerate(zip(paths,labels)):
  im=Image.open(p)
  if kind=='lower': im=im.crop((425,830,975,1220))
  else: im=im.resize((420,420),Image.Resampling.LANCZOS)
  board.paste(im,(i*size[0],20),im);draw.text((i*size[0]+5,3),label,fill=(20,20,20))
 p=out/f'NW09-10-selected-{kind}.jpg';board.save(p,quality=97)
 p.with_suffix('.jpg.generation.json').write_text(json.dumps({'kind':'visual-QA-derivative','method':'fixed full canvas resize / fixed crop, no asset edits','inputs':[{'file':str(x),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in paths]},indent=2),encoding='utf-8')
data={'scope':'NW09/10 local black-shaft alignment edits; runtime unchanged','currentPlaybackRule':{'frames':16,'frameDurationMs':60,'loopDurationMs':960},'slots':{},'reviews':[]}
for slot,version in [('09','09-v4'),('10','10-v3')]:
 p=r/'full-limb-review-20261004/run-NW'/version/'native.png';rel=p.relative_to(r).as_posix();data['slots']['run/NW/'+slot]=rel
 data['reviews'].append({'slot':'run/NW/'+slot,'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'passed-visible-limbs-and-shaft','upperShaftNativeCenterSamples':[[378 if slot=='09' else 378.5,500],[403 if slot=='09' else 403.5,540]],'lowerShaftNativeCenterSample':[657 if slot=='09' else 663,945],'horizontalProjectionResidualApproxPx':1 if slot=='09' else 6,'observation':'Actual exposed black rod center is aligned; lower rod passes behind lifted boot. Original near support leg and independent knee/ankle pose retained; upper canvas/head/two visible grip regions stable.','limits':'Sleeve/long hair/raised boot occlude parts of elbow and shaft; continuity of hidden pixels is not claimed. Measurement uses clean actual black rod segments, excludes hair, gold ornaments, fist and spear-blade tip.'})
(out/'NW09-10-selection-handoff.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
