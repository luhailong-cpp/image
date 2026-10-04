import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
allitems=[]
for direction in ['E','W']:
 files=sorted((ROOT/'runtime/run'/direction).glob('*.png'))
 if not files: continue
 thumb=256
 contact=Image.new('RGB',(4*thumb,4*(thumb+28)),(33,49,55));cd=ImageDraw.Draw(contact)
 animations=[]
 sources=[]
 for idx,p in enumerate(files):
  im=Image.open(p);im.load()
  a=im.getchannel('A')
  rec=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
  item={'file':p.relative_to(ROOT).as_posix(),'direction':direction,'frame':int(p.stem),'sha256':sha(p),'width':im.width,'height':im.height,'mode':im.mode,'alphaExtrema':list(a.getextrema()),'alphaBBoxDiagnosticOnly':list(a.getbbox()),'native':rec['native'],'visualReview':rec['visualReview'],'record':p.with_name(p.name+'.generation.json').relative_to(ROOT).as_posix()}
  allitems.append(item);sources.append(item)
  bg=Image.new('RGB',(448,448),(38,57,61))
  dd=ImageDraw.Draw(bg)
  for y in range(0,448,28):
   for x in range(0,448,28):
    if ((x+y)//28)%2:dd.rectangle((x,y,x+27,y+27),fill=(43,63,66))
  small=im.resize((448,448),Image.Resampling.LANCZOS);bg.paste(small,(0,0),small)
  dd=ImageDraw.Draw(bg);dd.line((0,412,447,412),fill=(192,170,94),width=1);dd.text((10,9),direction+' / '+p.stem,fill=(250,240,214));animations.append(bg)
  x=(int(p.stem)%4)*thumb;y=(int(p.stem)//4)*(thumb+28)
  ci=im.resize((thumb,thumb),Image.Resampling.LANCZOS);contact.paste(ci,(x,y),ci);cd.line((x,y+235,x+255,y+235),fill=(150,141,84));cd.text((x+9,y+thumb+6),direction+' / '+p.stem,fill=(250,240,214))
 cp=ROOT/'review'/f'run_{direction}_contact.png';contact.save(cp)
 previews=[]
 for name,duration in [('normal',[70 if i%2==0 else 80 for i in range(len(animations))]),('slow',180)]:
  op=ROOT/'review'/f'run_{direction}_{name}.gif'
  animations[0].save(op,save_all=True,append_images=animations[1:],duration=duration,loop=0,disposal=2,optimize=False)
  g=Image.open(op);durations=[]
  for j in range(g.n_frames):g.seek(j);durations.append(g.info.get('duration'))
  previews.append({'file':op.relative_to(ROOT).as_posix(),'sha256':sha(op),'frameCount':g.n_frames,'durationsMs':durations,'totalDurationMs':sum(durations)})
 info={'direction':direction,'sources':sources,'previews':previews,'contact':{'file':cp.relative_to(ROOT).as_posix(),'sha256':sha(cp)},'operation':'Preview only: full-canvas uniform downsample, alpha composite over checkerboard, diagnostic fixed ground line at y=.92. Runtime PNG unchanged.','dynamicReview':'not_performed_by_model: browser iab unavailable and CUA inventory empty','completeSlots':len(files)==16}
 (ROOT/'review'/f'run_{direction}_preview.generation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory={'scope':'run E/W delegated task only','target':32,'exported':len(allitems),'completeDirections':[d for d in ['E','W'] if sum(x['direction']==d for x in allitems)==16],'artFinalPassed':False,'dynamicPassed':False,'clientIntegrated':False,'files':allitems,'missing':[f'{d}/{i:02d}' for d in ['E','W'] for i in range(16) if not (ROOT/'runtime/run'/d/f'{i:02d}.png').exists()]}
(ROOT/'review/run_EW_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'E':sum(x['direction']=='E' for x in allitems),'W':sum(x['direction']=='W' for x in allitems),'uniqueSHA':len({x['sha256'] for x in allitems}),'all1024RGBA':all(x['width']==1024 and x['height']==1024 and x['mode']=='RGBA' for x in allitems)},ensure_ascii=False))


import run_timing_1200; run_timing_1200.update()

