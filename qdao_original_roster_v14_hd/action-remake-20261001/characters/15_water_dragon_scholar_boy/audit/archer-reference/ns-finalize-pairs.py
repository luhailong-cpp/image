from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2]
A=B/'audit/archer-reference'
rows=json.loads((A/'ns-current-native.json').read_text(encoding='utf-8'))
chosen={
'N':{3:'groundstep-v1',4:'groundstep-v1',5:'groundpairs-v1',6:'groundpairs-v1',12:'groundstep-v1',13:'groundpairs-v2',14:'groundpairs-v2',15:'ground242-v1',16:'ground242-v2'},
'S':{1:'ground242-v1',3:'groundstep-v1',4:'groundpairs-v1',5:'groundpairs-v1',6:'groundpairs-v1',7:'ground242-v3',8:'ground242-v2',9:'ground242-v1',11:'groundpairs-v1',12:'groundstep-v1',13:'ground242-v1',14:'groundpairs-v1',15:'ground242-v2',16:'groundpairs-v1'}}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
allrows=[]; selected=[]; errs=[]
for d in ['N','S']:
 for f in range(1,17):
  old=next(r for r in rows if r['direction']==d and r['frame']==f)
  key=f'run-{d}-{f:02}-'+chosen[d][f] if f in chosen[d] else Path(old['generationRecord']).stem
  p=B/'sources/new'/f'{key}.png' if f in chosen[d] else Path(old['path'])
  rec=B/'provenance/generation'/f'{key}.json'
  if not p.exists():raise ValueError('pending '+str(p))
  g=json.loads(rec.read_text(encoding='utf-8-sig'))
  im=Image.open(p);h=sha(p)
  assert im.size==(1254,1254) and im.mode=='RGBA'
  assert h==g['sha256']
  foot='left' if f in [15,16,1,2,3,4,5,6] else 'right'
  # Read-only support-boot region measurements, never used as a transform.
  if d=='N':box=(475,1030,660,1254) if foot=='left' else (625,1030,830,1254)
  else:box=(640,1000,820,1254) if foot=='left' else (460,1000,645,1254)
  al=im.getchannel('A').crop(box).point(lambda x:255 if x>8 else 0);bb=al.getbbox()
  y=box[1]+bb[3]-1
  line=al.crop((0,bb[3]-4,al.width,bb[3]))
  xs=[x for x in range(line.width) if any(line.getpixel((x,z))>0 for z in range(4))]
  x=round(box[0]+sum(xs)/len(xs))
  rt=B/f'runtime/run/{d}/{f:02}.png'
  r={'action':'run','direction':d,'frame':f,'key':key,'source':p.relative_to(B).as_posix() if p.is_relative_to(B) else str(p),'sha256':h,'generationRecord':rec.relative_to(B).as_posix(),'retainedCurrent':f not in chosen[d],'supportFoot':foot,'supportVisiblePointNative':[x,y],'supportMeasureRegion':box,'measureNote':'可见支撑靴底像素位置；已按解剖足别看图选区，只用于检查前后透视，不用于贴地或缩放。','oldRuntimeSHA256':sha(rt),'reviewStatus':'static_sequence_checked_parent_dynamic_pending','nativeCanvas':[1254,1254],'frameMs':75}
  allrows.append(r)
  if f in chosen[d]:selected.append(r)
assert len({r['sha256'] for r in allrows})==32
pairs=[]
for d in ['N','S']:
 for foot,groups in [('left',[[15,16],[1,2],[3,4],[5,6]]),('right',[[7,8],[9,10],[11,12],[13,14]])]:
  for i,fs in enumerate(groups):
   rr=[r for r in allrows if r['direction']==d and r['frame']in fs]
   pairs.append({'direction':d,'supportFoot':foot,'positionSegment':i+1,'frames':fs,'durationMs':150,'space':['前方接入','接近重心','身体经过后','后侧蹬离前'][i],'visibleSupportPointsNative':{str(r['frame']):r['supportVisiblePointNative'] for r in rr},'spatialDirection':'支撑靴沿N轴相对身体逐段向画面下方后移' if d=='N' else '支撑靴沿S轴相对身体逐段向画面上方远处后移','sameImageRepeated':False,'sha256':[r['sha256'] for r in rr]})
review={'character':'15_water_dragon_scholar_boy','reviewedAt':now,'reviewer':'finish_ns_pairs','status':'static_pairs_checked_parent_dynamic_pending','scope':'N/S 32帧，逐张完整原生图 + 连续接地图静态比较','frameMs':75,'cycleMs':1200,'frames':allrows,'pairs':pairs,'replacements':len(selected),'retained':32-len(selected),'actualModel':None,'actualQuality':None,'clientIntegrated':False,'dynamicReviewed':False,'staticFindings':['每只足连续8帧支撑，四个两帧空间段，手、膝、悬空腿姿态独立变化。','N画面下方代表相对身体更靠后的近地；S画面上方代表相对身体更靠后的远地。没有把旁边解释为外八。','右手持扇，左手空闲，左右足从正确胯部连接；支撑靴沿N/S纵轴，未见侧撇。','最终采用整张1254→940并放置(42,49)的固定导出，未按接地点改变整帧变换。'],'rejectedSpecific':['run-S-15-groundpairs-v1虽然脚向正确，但把前侧接地改短到y1167，与前侧空间段冲突；选既有ground242-v2。','run-N-13/14-groundpairs-v1未形成足够后移，v2已实图追加延伸并保持躯干。'],'remainingChecks':['需要父线程正常1×、0.25×连播与首尾检查，尤其N10/11/12扇手过渡和S14→15换脚；本静态审阅不冒充动态通过。'],'technicalErrors':errs}
(A/'ns-pairs-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
(A/'ns-pairs-selection.json').write_text(json.dumps({'character':review['character'],'reviewedAt':now,'notFormalSelection':True,'status':review['status'],'frames':selected,'retained':[r for r in allrows if r['retainedCurrent']],'pairs':pairs,'review':'audit/archer-reference/ns-pairs-review.json'},ensure_ascii=False,indent=2),encoding='utf-8')
for d in ['N','S']:
 ims={}
 for r in allrows:
  if r['direction']!=d:continue
  p=Path(r['source']);p=p if p.is_absolute() else B/p
  im=Image.open(p).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v))
  runtime=Image.new('RGBA',(1024,1024));runtime.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  ims[r['frame']]=runtime
 for foot,fs in [('left',[15,16,1,2,3,4,5,6]),('right',[7,8,9,10,11,12,13,14])]:
  board=Image.new('RGB',(1600,860),(225,228,226));draw=ImageDraw.Draw(board)
  for i,f in enumerate(fs):
   x=(i//2)*400;y=(i%2)*430
   im=ims[f].resize((400,400),Image.Resampling.LANCZOS);board.paste(im,(x,y+28),im)
   r=next(r for r in allrows if r['direction']==d and r['frame']==f)
   draw.text((x+6,y+6),f'{d} {f:02} {foot} P{i//2+1} 75ms - native {r["supportVisiblePointNative"]}',fill='black')
  board.save(A/f'ns-{d}-{foot}-pairs.png')
 for label,ms in [('1200ms',75),('slow',300)]:
  anim=[]
  for f in range(1,17):
   im=ims[f].resize((384,384),Image.Resampling.LANCZOS)
   bg=Image.new('RGBA',(384,408),(225,228,226,255));bg.alpha_composite(im,(0,24))
   ImageDraw.Draw(bg).text((8,5),f'{d} {f:02}/16  {ms}ms',fill='black');anim.append(bg)
  anim[0].save(A/f'ns-{d}-pairs-{label}.apng',save_all=True,append_images=anim[1:],duration=ms,loop=0,disposal=0,blend=0)
print(json.dumps({'selected':len(selected),'retained':32-len(selected),'pairs':pairs},ensure_ascii=True,indent=2))
