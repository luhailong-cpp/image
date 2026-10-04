from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
from PIL import Image,ImageDraw
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy')
sys.path.insert(0,str(B/'tools'))
from build_delivery import inspect,pixel_sha
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
M=read(B/'manifest.json')
old={(x['direction'],x['frame']):x for x in M['frames'] if x['action']=='run' and x['direction'] in ['NE','W']}
NE={4:'grounding-v1',5:'grounding-v2',6:'grounding-v2',7:'grounding-v1',8:'grounding-v1',9:'archer-v1',10:'grounding-v1',12:'grounding-v2',13:'grounding-v2',14:'grounding-v4',15:'grounding-v5',16:'grounding-v2'}
W={3:'grounding-v2',4:'grounding-v2',5:'grounding-v2',6:'grounding-v2',7:'grounding-v3',11:'grounding-v1',12:'grounding-v2',13:'grounding-v2',14:'grounding-v3',15:'grounding-v1'}
rows=[];errors=[];previews=[]
for d,mapping in [('NE',NE),('W',W)]:
 canvas=Image.new('RGB',(1280,1408),'#eef1f3')
 draw=ImageDraw.Draw(canvas);anim=[]
 for f in range(1,17):
  oldrow=old[d,f];slot=f'run-{d}-{f:02d}'
  support='left' if f in [16,1,2,3,4,5,6,7] else 'right'
  step=0 if f in [16,1,8,9] else 1 if f in [2,3,10,11] else 2 if f in [4,5,12,13] else 3
  row={'slot':slot,'action':'run','direction':d,'frame':f,'durationMs':75,'supportFoot':support,'positionSegment':step,'staticReview':'reviewed','animationApproval':'pending_root_dynamic_review'}
  if f in mapping:
   key=f'{slot}-{mapping[f]}';path=B/f'sources/new/{key}.png';record=B/f'provenance/generation/{key}.json';g=read(record)
   row.update(candidateKey=key,decision='replace',source=path.relative_to(B).as_posix(),sha256=sha(path),generationRecord=record.relative_to(B).as_posix(),supersedes=oldrow['derivedFrom'])
   assert row['sha256']==g['sha256']
   for attr in ['actualModel','actualQuality']: assert g[attr] is None
   try:im,info=inspect(path);row['inspection']=info
   except Exception as e:errors.append({'slot':slot,'error':str(e)});im=Image.open(path).convert('RGBA')
   alpha=im.getchannel('A');im.putalpha(alpha.point(lambda a:0 if a<=8 else a))
   full=Image.new('RGBA',(1024,1024));full.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  else:
   path=B/oldrow['output'];full=Image.open(path).convert('RGBA')
   row.update(decision='retain',runtime=oldrow['output'],runtimeSha256=sha(path),source=oldrow['source'],sha256=oldrow['derivedFrom']['sha256'],generationRecord=oldrow['derivedFrom']['generationRecord'],originalSource=oldrow['derivedFrom'])
  row['previewVisiblePixelSha256']=pixel_sha(full)
  rows.append(row)
  x=((f-1)%4)*320;y=((f-1)//4)*352
  tile=full.resize((320,320),Image.Resampling.LANCZOS);canvas.paste(tile,(x,y+28),tile)
  draw.text((x+5,y+5),f'{d} {f:02d} | {support} P{step+1} | '+row['decision'],fill='#172333')
  draw.line((x,y+28+294,x+320,y+28+294),fill='#b4c2cb')
  anim.append(tile)
 path=B/f'audit/archer-reference/ne-w-{d}-grounding-selected-contact.png';canvas.save(path)
 frames=[]
 for im in anim:
  bg=Image.new('RGBA',(320,320),'#eef1f3');bg.alpha_composite(im);frames.append(bg)
 apng=B/f'audit/archer-reference/ne-w-{d}-grounding-selected.apng'
 frames[0].save(apng,format='PNG',save_all=True,append_images=frames[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
 previews.append({'direction':d,'contact':path.relative_to(B).as_posix(),'sha256':sha(path),'apng':apng.relative_to(B).as_posix(),'apngSha256':sha(apng),'operation':'all native1254 ->940 at(42,49)on1024, then fullcanvas320; retained runtime is unchanged'})
pairs=[]
for d in ['NE','W']:
 for side,sets in [('left',[[16,1],[2,3],[4,5],[6,7]]),('right',[[8,9],[10,11],[12,13],[14,15]])]:
  for i,nums in enumerate(sets):
   pairs.append({'direction':d,'supportFoot':side,'frames':nums,'durationMs':150,'spacePosition':(['落点相对身体偏前，开始承重','身体靠近支撑脚上方，屈膝缓冲','身体经过支撑脚，足相对移到身下偏后','支撑脚留在身体后方，踝抬跟并蹬离'][i]),'screenTravel':'支撑脚相对髋沿右上→左下的运动轴逐步后移，膝踝鞋掌保持东北轴' if d=='NE' else '支撑脚相对髋从画面左前逐渐走到右后，靴尖始终朝左；位置段不表示脚尖侧撇'})
report={'schemaVersion':1,'character':'15_water_dragon_scholar_boy','generatedAt':datetime.now(timezone.utc).isoformat(),'status':'static_review_complete_pending_root_dynamic','frames':rows,'selectedCount':sum(x['decision']=='replace' for x in rows),'retainedCount':sum(x['decision']=='retain' for x in rows),'positionPairs':pairs,'previews':previews,'technicalErrors':errors,'timing':{'cycleMs':1200,'frameMs':75,'frames':16},'notes':['沿已有图精修，不全量重画；所有替换均有独立生成记录、宿主回执与真实参考。','NE12–15右支撑足已连续向画面左后局部调整，左腿维持抬起；错误换足及额外落脚版本未选。','W03扇在腹前、W04扇过腰侧并保留前襟、W05扇后摆；W11回前为既有反向过渡。','W后蹬接地点仍有约10–20原生像素的高度变化；选择关节/足别正确且较贴地版本，未用全图移动或最低像素吸地。主审须以正常与慢放检查它是否可接受。','当前仅静态原图及contact复核，未宣称完整动态或客户端通过。']}
out=B/'audit/archer-reference/ne-w-grounding-selection.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
review={'createdAt':report['generatedAt'],'selection':out.relative_to(B).as_posix(),'selectionSha256':sha(out),'staticCheckedSlots':[x['slot'] for x in rows],'rejected':['run-NE-01-grounding-v1:three boots','run-NE-14-grounding-v3:lowered wrong leg','run-NE-15-grounding-v2:wrong supporting foot','run-NE-15-grounding-v3:wrong supporting foot','run-W-03-grounding-v1:altered hands fan and face'],'technicalErrors':errors,'dynamicStatus':'pending_root_dynamic_review','userAcceptance':'not_claimed','clientIntegration':'not_integrated','notes':report['notes']}
(B/'audit/archer-reference/ne-w-grounding-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':report['selectedCount'],'retained':report['retainedCount'],'technicalErrors':errors},ensure_ascii=True))

