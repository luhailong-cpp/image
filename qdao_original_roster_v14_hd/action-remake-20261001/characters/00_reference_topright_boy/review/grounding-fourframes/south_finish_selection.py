from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2];out=root/'review/grounding-fourframes'
maps={
 'S':['01-v4','02-v5','05-v2','04-v3','04-v2','06-v2','07-v3','08-v2','09-v1','10-v1','13-v2','11-v2','12-v3','14-v2','15-v3','16-v2'],
 'SE':['01-v5','02-v3','03-v1','04-v3','05-v3','06-v3','07-v2','08-v2','09-v2','10-v1','12-v5','14-v3','11-v3','13-v5','15-v6','16-v5'],
 'SW':['01-v1','02-v2','03-v4','04-v4','05-v6','06-v6','07-v6','08-v8','08-v4','09-v4','10-v2','11-v2','13-v4','14-v4','12-v1','16-v4']}
obs={
 'S':[
 '右脚在前初触，另一腿后折，右空臂后侧。','右膝屈曲缓冲，鞋尖朝前、鞋掌向下。','右脚在髋下，左摆腿膝上提、鞋仍垂直。','右脚全掌支撑，左腿由收腿转向前摆。','右腿继续支撑，左膝前抬、鞋底朝前下。','右踝继续受力，左前摆腿进一步伸出。','右脚后移并屈踝，左腿前摆，右空臂前摆。','右脚在身后保留前掌接触，左腿向前待落地。','左脚在前初触，右腿后折。','左膝缓冲，脚掌压实朝前，右空臂开始后摆。','左脚髋下承重，右膝上抬、鞋仍垂直。','左脚全掌支撑，右腿开始前伸。','左踝持续承重，右腿前摆鞋底可见。','左脚髋下偏后承重，右腿继续前摆。','左脚后方支撑，右膝前抬。','左脚后推保留前掌，右腿前摆准备下一圈。'],
 'SE':[
 '右脚在人物前方初触，鞋尖朝右下。','右膝缓冲，鞋掌朝下，另一腿后收。','右腳髋下承重，左腿抬起通过。','右膝更弯、左腿前摆，右空臂从后向前。','右脚中撑，左腿前伸、露少量鞋底。','右脚略后撑，左腿更伸展，鞋长轴顺右下。','右脚在画面左后方前掌支撑，左腿前摆。','右前掌后撑，左腿向右下伸出待落地。','左脚前触，右腿后收，右空臂前侧。','左腿缓冲承重，右腿开始回摆。','左脚中撑，右腿屈膝后收。','左脚继续中撑，右膝上提准备通过。','左脚中撑，右腿由屈曲转向前摆。','左脚略后撑，右腿前摆可见鞋底。','左脚在左后方压地、膝微屈，右腿前摆。','左脚后推前掌接触，右腿进一步向右下伸出。'],
 'SW':[
 '右脚前触，鞋尖朝左下，左腿后折。','右腿前撑缓冲，鞋底朝地面。','右脚在髋下承重，左腿收膝。','右膝弯曲缓冲，左腿向前回收。','右脚中撑，另一膝抬高通过，右空臂前摆。','右脚中撑末段，脚踝仍承重。','右后撑脚在身体右后方、左腿前摆在前遮挡。','右前掌后撑，左摆腿比07更向左下伸出。','左脚前触接棒，右腿后折。','左膝缓冲，鞋前掌朝左下。','左脚髋下承重，右腿折膝回收。','左脚中撑，右膝前通过。','左脚继续支撑，右腿由回收到前摆。','左脚中撑末段，右鞋向前摆出。','左脚后撑，右腿前摆鞋底可见。','左脚后方前掌接触，右腿更向前伸出。']}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
all_rows=[]
for d,stems in maps.items():
 rows=[];full=Image.new('RGB',(1200,1320),'#dedede');lower=Image.new('RGB',(1600,880),'#dedede');fd=ImageDraw.Draw(full);ld=ImageDraw.Draw(lower)
 for i,stem in enumerate(stems):
  p=root/'generation/run'/d/(stem+'.png');im=Image.open(p);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert im.size==(1254,1254) and im.mode=='RGBA'
  local=i%8;pos='front' if local<2 else 'middle' if local<6 else 'rear';pair=local//2+1
  rec=Path(str(p)+'.generation.json');assert rec.exists()
  row={'action':'run','direction':d,'frame':i+1,'source':p.relative_to(root).as_posix(),'sourceSha256':sha,'supportFoot':'right' if i<8 else 'left','position':pos,'spatialPair':pair,'durationMs':75,'status':'static_reviewed_candidate_recommended_with_limitations','nativeSize':list(im.size),'observation':obs[d][i],'dynamicVerified':False,'contactEvidence':'支撑膝踝、鞋掌朝向、前后姿态静态形状证据；无客户端世界地面标定。','actualModel':None,'actualQuality':None,'generationRecord':rec.relative_to(root).as_posix()}
  rows.append(row)
  thumb=im.resize((300,300),Image.Resampling.LANCZOS);x=i%4*300;y=i//4*330;full.paste(thumb,(x,y+27),thumb);fd.text((x+4,y+3),f'{d}{i+1:02d} {stem} {row["supportFoot"]} P{pair}',font=font,fill='black')
  crop=im.crop((200,780,1150,1254)).resize((400,200),Image.Resampling.LANCZOS);x=i%4*400;y=i//4*220;lower.paste(crop,(x,y+20),crop);ld.text((x+4,y+1),f'{d}{i+1:02d} {stem} {sha[:8]}',font=font,fill='black')
 assert len({x['sourceSha256'] for x in rows})==16
 (root/'generation/run'/d/'selection-middle4-side2-20261004.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 full.save(out/f'{d}-south-final-candidate-full.jpg',quality=94);lower.save(out/f'{d}-south-final-candidate-lower.jpg',quality=95)
 all_rows+=rows
rejections={'SE/16-v4':'头身放大，头顶由158上移83，拒用','SE/15-v5':'支撑脚未后移，不能作为后撑段','SE/13-v4':'第三只靴，拒用','SE/05-v2':'头身放大/步幅异常','SE/06-v2':'头身放大/步幅异常','SW/05-v4':'头身放大','SW/05-v5':'头身放大','SW/06-v5':'头身放大且支撑侧异常','SW/07-v4':'头身比例放大','SW/07-v5':'头身比例放大','SW/08-v5':'仍处于前侧支撑，不能作后撑','SW/08-v6':'头身放大','SW/08-v7':'实际1133x1388错误尺寸，禁止缩放为1254冒充原生'}
report={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':['S','SE','SW'],'status':'48_static_candidates_ready_for_independent_review','technical':{'count':48,'uniqueNativeSourceSha256':len({x['sourceSha256'] for x in all_rows}),'allNative1254RGBA':True,'allHaveGenerationRecord':True,'frameMs':75,'cycleMs':1200,'noDuplicatedSource':True},'contactFramesByDirection':{d:{'right':list(range(1,9)),'left':list(range(9,17))} for d in maps},'pairLayout':{'right':[[1,2],[3,4],[5,6],[7,8]],'left':[[9,10],[11,12],[13,14],[15,16]]},'reviewNotes':['中段4帧分为两个连续2帧姿态段，既有正确原生帧保留且单源只用一次。','S中段摆腿次序已将垂足收腿放在前摆之前；SE左支撑中段将后收腿放在前摆之前。','SW后撑透视中前摆腿遮挡后撑腿上端，不能把画面左右固定当作解剖左右。','仅静态候选建议；实际动态播放、循环观感及客户端地面接触未验证。','现有01/02及部分相位头部有自然/历史轻微差异；没有使用逐帧缩放拟合消除。'],'remainingUnverified':['normal-speed visual playback','client world-ground/locomotion sync'],'rejectedCandidates':rejections,'frames':all_rows}
(out/'south-static-evidence-middle4-side2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# S / SE / SW 两帧一段静态候选复核','', '48张原生1254RGBA、48个唯一来源，75ms/帧、1200ms/圈。右支撑01–08、左支撑09–16；每两帧是一段独立姿态。当前是静态候选，真实动态/客户端尚未验证。','', '|方向|帧|来源|支撑|位置段|观察|','|---|---:|---|---|---|---|']
for x in all_rows:lines.append(f'|{x["direction"]}|{x["frame"]:02d}|{Path(x["source"]).stem}|{x["supportFoot"]}|{x["position"]} {x["spatialPair"]}|{x["observation"]}|')
(out/'south-static-evidence-middle4-side2.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('48 source-unique static candidate selections and evidence tables saved; global selection unchanged.')
