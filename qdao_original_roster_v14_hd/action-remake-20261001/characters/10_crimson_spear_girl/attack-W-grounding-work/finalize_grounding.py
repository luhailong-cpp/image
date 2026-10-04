from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
d=Path(__file__).parent;base=d.parent
chosen={4:'04-ground-v3',5:'05-ground-v1',6:'06-ground-v4',7:'07-ground-v2',8:'08-ground-v2'}
slots={f'attack/W/{i:02d}':f'attack-W-grounding-work/attack-W-{n}.png' for i,n in chosen.items()}
phases={4:'forward thrust builds',5:'thrust approaches contact',6:'horizontal contact candidate',7:'follow-through absorbs impact',8:'near-horizontal early withdrawal'}
selection={'status':'static_grounding_reviewed_dynamic_pending','slots':slots,'note':'5 independently regenerated native pose candidates. ROOT merges with attack-work selection. No image-wise translate/scale, combat unchanged.'}
(d/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf8')
measure=json.loads((d/'ground-measurements.json').read_text())
measureBy={r['file'].replace('\\','/'):r for r in measure['frames']}
audit=[];sheet=Image.new('RGB',(1600,696),'#e9e8e1');dr=ImageDraw.Draw(sheet)
snapshot=json.loads((d/'input-selection-snapshot.json').read_text())
old={f['slot']:Path(f['file']) for f in snapshot['sources']}
for j,(slot,rel) in enumerate(slots.items()):
 p=base/rel;im=Image.open(p).convert('RGBA');h=hashlib.sha256(p.read_bytes()).hexdigest()
 a=im.getchannel('A');bbox=a.point(lambda x:255 if x>32 else 0).getbbox()
 assert im.size==(1254,1254) and a.getextrema()==(0,255) and 0<bbox[0]<bbox[2]<1254 and 0<bbox[1]<bbox[3]<1254
 for row,source in enumerate([old[slot],p]):
  src=Image.open(source).convert('RGBA');thumb=src.resize((320,320));x=j*320;y=row*348
  sheet.paste(thumb,(x,y),thumb);dr.line((x,y+1120*320/1254,x+320,y+1120*320/1254),fill='#b96650')
  dr.text((x+5,y+322),('BEFORE ' if row==0 else 'AFTER ')+slot,fill='#222')
  dr.text((x+5,y+336),source.name,fill='#555')
 item={'slot':slot,'file':rel,'sha256':h,'nativeSize':[1254,1254],'alphaBBoxThreshold32':bbox,'actualFootSoleY':measureBy[rel]['groundBottoms'],'actualModel':None,'actualQuality':None,'phase':phases[int(slot[-2:])]}
 audit.append(item)
 mf=p.with_name(p.name+'.generation.json');m=json.loads(mf.read_text(encoding='utf8'));assert m['sha256']==h and m['actualModel'] is None and m['actualQuality'] is None
 m['status']='native_static_grounding_reviewed_dynamic_pending';m['visualReview']={'document':'REVIEW_20261004.md','selectedSlot':slot,'actualSoleY':item['actualFootSoleY'],'sourceNativeNotPostTranslated':True,'naturalShortLegs':True,'shoeAxis':'heelRIGHT/toeLEFT checked from knee-ankle-toe','hands':'exactly two on same straight spear, anatomical frontLEFT/rearRIGHT','dynamicValidated':False}
 mf.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
sheet.save(d/'before-after-contact.jpg',quality=95)
(d/'before-after-contact.jpg.generation.json').write_text(json.dumps({'operation':'Diagnostic equal full1254 canvas downsample320; no per-frame shifts/bbox scaling','before':snapshot['sources'],'after':audit},indent=2),encoding='utf8')
allsel=json.loads((base/'attack-work/selection.json').read_text(encoding='utf8'))['slots'];allsel.update(slots)
sheet=Image.new('RGB',(1280,1044),'#e9e8e1');dr=ImageDraw.Draw(sheet);combined=[]
for i in range(1,13):
 slot=f'attack/W/{i:02d}';p=base/allsel[slot];im=Image.open(p).convert('RGBA');c=Image.new('RGBA',(1024,1024));c.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),(0,174))
 thumb=c.resize((320,320));x=(i-1)%4*320;y=(i-1)//4*348;sheet.paste(thumb,(x,y),thumb);rx=x+160;ry=y+942*320/1024
 dr.line((rx-12,ry,rx+12,ry),fill='#b96650');dr.line((rx,ry-6,rx,ry+6),fill='#b96650')
 dr.text((x+5,y+322),slot,fill='#222');dr.text((x+5,y+336),p.name,fill='#555')
 combined.append({'slot':i,'file':'../'+allsel[slot],'phase':phases.get(i,'current attack-work selected pose'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(set(f['sha256'] for f in audit))==5
sheet.save(d/'combined-W-fixed-registration.jpg',quality=95)
(d/'combined-W-fixed-registration.jpg.generation.json').write_text(json.dumps({'operation':'Diagnostic all12 same scale860/1254, fixedtranslation(0,174); no per-frame position corrections','sources':combined},indent=2),encoding='utf8')
report={'selectedOwned':5,'uniqueOwned':5,'frames':audit,'registrationProposal':{'nativeVirtualRoot':[512/(860/1254),1120],'scale':860/1254,'translation':[0,174],'virtualRoot':[512,942],'basis':'attack_frames revised common-direction x estimate to prevent left spear clipping. ROOT decides final application.'},'targetGround':1120,'actualSoleBand':[min(y for f in audit for y in f['actualFootSoleY']),max(y for f in audit for y in f['actualFootSoleY'])],'frameMs':30,'segmentMs':360,'contactFrame':6,'dynamicValidated':False,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(d/'grounding-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
html='''<!DOCTYPE html><meta charset="utf-8"><title>W普攻接地复核</title><style>body{font:16px system-ui;background:#e9e8e1;margin:20px}canvas{width:480px;max-width:95vw}button,select{padding:8px;margin:4px}p{max-width:900px}</style><h2>W普攻 · 接地修复候选</h2><p>12×30ms＝360ms，战斗时长未改。统一倍率860/1254，整方向固定位置(0,174)，根点(512,942)。新04–08与attack-work其余选中帧组合供复核，未声称客户端验收。</p><button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="1">正常</option><option value=".5">慢放0.5×</option><option value=".25">慢放0.25×</option></select><label><input type="checkbox" id="root" checked>根点</label><p id="label"></p><canvas width="1024" height="1024"></canvas><script>
const data=DATA,ims=data.map(f=>{const a=new Image();a.src=f.file;return a}),q=s=>document.querySelector(s),ctx=q('canvas').getContext('2d');let ready=false,playing=false,idx=5,elapsed=150,last=null;
function draw(){ctx.fillStyle='#e9e8e1';ctx.fillRect(0,0,1024,1024);if(ready)ctx.drawImage(ims[idx],0,174,860,860);if(q('#root').checked){ctx.strokeStyle='#b96650';ctx.beginPath();ctx.moveTo(500,942);ctx.lineTo(524,942);ctx.moveTo(512,930);ctx.lineTo(512,954);ctx.stroke()}q('#label').textContent=ready?(idx+1)+'/12 '+data[idx].phase:'读取中或缺帧，整段禁播'}
function stop(){playing=false;q('#play').textContent='播放'}
q('#play').onclick=()=>{if(!ready)return;playing=!playing;elapsed=idx*30;q('#play').textContent=playing?'暂停':'播放'};
q('#prev').onclick=()=>{stop();idx=(idx+11)%12;draw()};q('#next').onclick=()=>{stop();idx=(idx+1)%12;draw()};
Promise.all(ims.map(im=>new Promise((res,rej)=>{if(im.complete&&im.naturalWidth)res();else{im.onload=res;im.onerror=rej}}))).then(()=>{ready=ims.length===12;draw()}).catch(()=>{ready=false;stop();q('#play').disabled=true;draw()});
function tick(t){if(last!==null&&ready&&playing){elapsed+=(t-last)*Number(q('#speed').value);idx=Math.floor(elapsed/30)%12}last=t;draw();requestAnimationFrame(tick)}requestAnimationFrame(tick);
</script>'''.replace('DATA',json.dumps(combined))
(d/'grounding-preview.html').write_text(html,encoding='utf8')
print('Selected5 unique5; actual foot range',report['actualSoleBand'],'native; fixed combined12 preview. Combat30ms.')

