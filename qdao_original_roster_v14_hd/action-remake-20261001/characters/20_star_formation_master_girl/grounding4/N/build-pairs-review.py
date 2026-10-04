import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Each value denotes an actually inspected independent PNG, never a duplicated frame.
MAP={
'N':{4:'04-v1',5:'06-v1',6:'06-v2',7:'07-v2',8:'08-v4',12:'12-v1',13:'13-v2',14:'14-v1',15:'15-v3',16:'16-v3'},
'S':{5:'05-v3',6:'06-v2',7:'07-v3',8:'08-v1',13:'13-v2',14:'14-v2',15:'15-v1',16:'16-v3'}}
out={'schemaVersion':2,'createdAt':datetime.now(timezone.utc).isoformat(),'character':'20_star_formation_master_girl','latestRequirement':'同一脚连续支撑8帧；沿跑向4个空间位置各两张独立姿态，再换脚。','frameCount':16,'frameDurationMs':75,'loopMs':1200,'transform':'AI原生1254完整画布等比缩至1024；不裁剪、不按包围盒对齐、不移动全图。','configurationTarget':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'unconfirmedReason':'宿主管理内置image_gen没有model/quality选择器，工具返回未披露。','directions':{},'selected':[],'replacements':[],'clientIntegration':'not_integrated','clientValidation':'not_run','userAccepted':False}
for d in ['N','S']:
 rows=[];frames=[]
 for i in range(1,17):
  changed=i in MAP[d]
  rel=f'grounding4/{d}/{MAP[d][i]}.png' if changed else f'runtime/run/{d}/{i:02d}.png'
  p=BASE/rel;rpath=Path(str(p)+'.generation.json')
  assert p.exists() and rpath.exists(),p
  rec=json.loads(rpath.read_text(encoding='utf-8-sig'))
  with Image.open(p) as im:
   assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
   frames.append(im.copy())
  row={'direction':d,'frame':i,'selectedSource':rel,'absolutePath':p.as_posix(),'sha256':sha(p),'generationRecord':rpath.relative_to(BASE).as_posix(),'generationRecordSha256':sha(rpath),'inputIsFinalExport':True,'decision':'replace_local_legs' if changed else 'retain_existing_correct','supportLeg':'left' if i<=8 else 'right','supportSide':('screenLeft' if i<=8 else 'screenRight') if d=='N' else('screenRight' if i<=8 else 'screenLeft'),'requestedSlot':rec.get('frame',i)}
  if changed:
   native=BASE/rec['nativeFile'];nr=Path(str(native)+'.generation.json')
   assert sha(p)==rec['exportSha256'] and sha(native)==rec['nativeSha256']
   row.update({'nativeSource':rec['nativeFile'],'nativeSha256':sha(native),'nativeRecord':nr.relative_to(BASE).as_posix(),'nativeRecordSha256':sha(nr),'nativeSize':rec['nativeSize']})
   out['replacements'].append(dict(row))
  else: row['preservedPriorRecord']=rec
  rows.append(row);out['selected'].append(row)
 assert len(set(r['sha256'] for r in rows))==16
 compact=[]
 for row in rows:
  compact.append({'frame':row['frame'],'exportFile':row['selectedSource'],'nativeFile':row.get('nativeSource',row['selectedSource']),'generationRecord':row['generationRecord'],'sha256':row['sha256'],'supportFoot':row['supportLeg'],'position':['front_landing','under_hip','behind_hip','rear_push'][((row['frame']-1)%8)//2],'mode':'retain' if row['decision'].startswith('retain') else 'replace_or_rephase','visualStaticReviewed':True,'requestedSlot':row['requestedSlot']})
 (BASE/f'grounding4/{d}/selected.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2),encoding='utf-8')
 positions=['前侧初落地','身体经过支撑脚的身下位置','身体已经超过支撑脚的后侧位置','最后方推进、准备异脚落地']
 pairs=[]
 for k in range(8):
  leg='left' if k<4 else'right';side=('screenLeft' if k<4 else'screenRight') if d=='N' else('screenRight' if k<4 else'screenLeft')
  pairs.append({'frames':[2*k+1,2*k+2],'supportLeg':leg,'supportSide':side,'position':positions[k%4],'durationMs':150,'actualPoseNote':('背面北向：沿画面纵深由较远处向观者侧后移，膝踝始终顺北向轴，支撑鞋跟后面可辨。' if d=='N' else '正面南向：由观者侧前方朝身体后方退入纵深，后侧支撑靴看鞋面，摆动脚在前方时可以投影更低。')})
 sheet=Image.new('RGB',(1536,1664),(235,232,220));dr=ImageDraw.Draw(sheet)
 feet=Image.new('RGB',(1536,512),(235,232,220));fd=ImageDraw.Draw(feet)
 previews=[]
 for i,im in enumerate(frames):
  small=im.resize((384,384));x=i%4*384;y=i//4*416;sheet.paste(small,(x,y),small);dr.text((x+10,y+390),f'{d}{i+1:02d} '+Path(rows[i]['selectedSource']).name,fill='black')
  crop=im.crop((320,630,710,1020)).resize((192,192));fx=i%8*192;fy=i//8*256;feet.paste(crop,(fx,fy+12),crop);fd.text((fx+8,fy+220),f'{d}{i+1:02d}',fill='black')
  pv=Image.new('RGBA',(320,360),(235,232,220,255));a=im.resize((320,320));pv.alpha_composite(a);ImageDraw.Draw(pv).text((8,330),f'{d} {i+1:02d} / 16',fill='black');previews.append(pv)
 sheet.save(BASE/f'grounding4/{d}/selected-contact.png');feet.save(BASE/f'grounding4/{d}/selected-feet.png')
 for label,ms in [('normal',75),('slow',300)]:
  previews[0].save(BASE/f'grounding4/{d}/selected-{label}.png',save_all=True,append_images=previews[1:],duration=[ms]*16,loop=0,disposal=0,blend=0)
 out['directions'][d]={'staticReviewedFrames':16,'positionPairs':pairs,'selected':rows,'staticAccepted':True,'normalPreviewReady':True,'normalPlaybackReviewedByThisAgent':False,'awaitingRootDynamicReview':True,'notes':'已实际查看完整16连图及腿脚局部连图，同一支撑腿连续八帧。真实独立姿态，未重复图、镜像或插值。','knownRemainingStaticIssues':[],'contactSheet':f'grounding4/{d}/selected-contact.png','feetSheet':f'grounding4/{d}/selected-feet.png','normalPreview':f'grounding4/{d}/selected-normal.png','slowPreview':f'grounding4/{d}/selected-slow.png'}
out['retainedCount']=sum(r['decision'].startswith('retain') for r in out['selected']);out['replacedCount']=len(out['replacements'])
out['rejectedCandidates']=[{'file':'grounding4/S/16-v1.png','reason':'root复核发现右腿后折如离地，不能凭纵深解释为持续右支撑，已替换。'},{'file':'grounding4/S/16-v2.png','reason':'支撑腿正确但腰以下拉长、构图与接地位置相对S15突跳，未采用。'},{'file':'grounding4/N/08-v3.png','reason':'支撑鞋向右露出鞋尖侧面，已用08-v4修到北向轴。'}]
(BASE/'provenance/grounding-pairs-N-S.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(out['selected']),'replaced':out['replacedCount'],'retained':out['retainedCount'],'report':'provenance/grounding-pairs-N-S.json'},ensure_ascii=False))
