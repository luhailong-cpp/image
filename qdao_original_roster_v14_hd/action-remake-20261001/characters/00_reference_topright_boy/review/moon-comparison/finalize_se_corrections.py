from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy')
out=root/'review/moon-comparison'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=json.loads((out/'source-snapshot.json').read_text(encoding='utf-8'))
old_names=['11-v2','12-v2','13-v2','14-v1','15-v2','16-v1']
new_names=['11-v3','12-v4','13-v3','14-v2','15-v3','16-v2']
entries=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def info(stem):
 p=root/'generation/run/SE'/(stem+'.png');im=Image.open(p)
 m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
 assert sha(p)==m['sha256']
 assert im.size==(1254,1254) and im.mode=='RGBA'
 for key in ['request','receipt']:
  q=root/m['evidence'][key];assert sha(q)==m['evidence'][key+'Sha256']
 return {'source':p.relative_to(root).as_posix(),'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaExtrema':list(im.getchannel('A').getextrema()),'generationRecord':p.relative_to(root).as_posix()+'.generation.json','headAlphaBBox':list(im.getchannel('A').crop((0,0,1254,600)).point(lambda a:255 if a>32 else 0).getbbox())}
for i,(old,new) in enumerate(zip(old_names,new_names)):
 oi=info(old);ni=info(new)
 entries.append({'frame':i+11,**ni,'before':oi,'status':'recommended_static_shoe_direction_corrected_pending_dynamic_review','finding':'前鞋白鞋头位于踝部右下，原向左外翻已消除；膝踝相接，未见多脚/断踝。','scope':'局部鞋踝修正；每帧自身原图保留姿态、上身、手臂、葫芦和镜头。','dynamicApproved':False})
report={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'direction':'SE','frames':entries,'rejected':[{'source':'generation/run/SE/12-v3.png','sha256':sha(root/'generation/run/SE/12-v3.png'),'reason':'改到右下另一只鞋，目标左下前鞋仍向外，不推荐。'}],'actualModel':None,'actualQuality':None,'recordPolicy':'每图prompt/request/receipt/png.generation.json齐全；未知实际型号/质量为null。','remaining':'本轮六张未见明确脚掌继续外撇。全方向相位、接地、根点与720ms实播仍由总控复核；不因本轮静态修正宣称动态通过。','globalSelectionModified':False}
save(out/'se-foot-corrections.json',report)
allprovs=[]
for part,start in enumerate([0,3],1):
 canvas=Image.new('RGB',(1200,700),(232,232,232));draw=ImageDraw.Draw(canvas);derived=[]
 for i in range(3):
  for row,names in enumerate([old_names,new_names]):
   stem=names[start+i];p=root/'generation/run/SE'/(stem+'.png');im=Image.open(p).convert('RGBA')
   crop=im.crop((180,650,1120,1254)).resize((400,257),Image.Resampling.LANCZOS)
   x=i*400;y=row*350;canvas.paste(crop,(x,y+44),crop)
   draw.text((x+12,y+10),('BEFORE ' if row==0 else 'AFTER ')+stem+' '+sha(p)[:10],fill='black',font=font)
   derived.append({'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(root).as_posix()+'.generation.json'})
 name=f'SE-{start+11:02d}-{start+13:02d}-before-after.jpg';p=out/name;canvas.save(p,quality=95)
 save(Path(str(p)+'.generation.json'),{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'derivedFrom':derived,'operation':'Diagnostic only: fixed crop [180,650,1120,1254], resize each to 400x257, labeled montage. No source asset changed.','modelGeneration':False})
canvas=Image.new('RGB',(1200,880),(232,232,232));draw=ImageDraw.Draw(canvas);derived=[]
for i,stem in enumerate(new_names):
 p=root/'generation/run/SE'/(stem+'.png');im=Image.open(p).convert('RGBA').resize((400,400),Image.Resampling.LANCZOS)
 x=i%3*400;y=i//3*440;canvas.paste(im,(x,y+36),im);draw.text((x+12,y+9),stem+' '+sha(p)[:10],fill='black',font=font)
 derived.append({'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(root).as_posix()+'.generation.json'})
p=out/'SE-recommended-full-canvas.jpg';canvas.save(p,quality=95)
save(Path(str(p)+'.generation.json'),{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'derivedFrom':derived,'operation':'Diagnostic only: complete native 1254x1254 canvas uniformly scaled to 400x400 per cell; no bbox fitting, translation or source edit.','modelGeneration':False})
for direction in ['E','S','SE','SW']:
 for start in [1,9]:
  p=out/f'{direction}-lower-{start:02d}-{start+7:02d}.jpg'
  derived=[{'file':r['source'],'sha256':r['sha256'],'generationRecord':r['source']+'.generation.json'} for r in snapshot['frames'] if r['direction']==direction and start<=r['frame']<start+8]
  save(Path(str(p)+'.generation.json'),{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'derivedFrom':derived,'operation':'Diagnostic only: fixed crop [180,650,1120,1254], uniform 400x257 per cell with labels; no source edit.','modelGeneration':False})
lines=['# 00 跑步脚向独立静态复核与 SE 定向修复','',
'依据用户最新要求独立看鞋掌长轴、膝踝衔接与跑向；月影07不作为已通过模板。逐帧输入SHA及64帧判断在 foot-direction-audit.json，原选表快照在 source-snapshot.json。','',
'- E：16帧未见明确鞋掌向外扭，保留。后腿屈膝足尖下垂不能按脚尖屏幕位置误判外八。',
'- S：保留。03–08与11–16抬脚有轻微斜鞋底/外偏观察，但静态证据不足以认定与跑向相反，不扩大为必须重画。',
'- SW：16帧保留。08–12放大后鞋尖实际仍向左下；16-v3保留。',
'- SE：原01、02、11–16屏幕左侧前鞋明显朝左，与右下跑向冲突。01/02由root处理；本代理完成11–16。','',
'## 推荐交接','',
'| 帧 | 原生推荐 | SHA256 |','|---|---|---|']
for e in entries:lines.append(f'| {e["frame"]:02d} | {e["source"]} | {e["sha256"]} |')
lines+=['','六张均1254×1254透明RGBA，逐图prompt/request/receipt/png.generation.json齐全。实际型号与质量未披露，均null；配置目标单独保存。12-v3改错脚，拒用；12-v4已修正。','',
'本轮实际看图可见鞋头转到踝部右下，未见继续向左外翻、断踝或多脚；各自身姿态与上身保留。原生图未做程序缩放、贴地、镜像或平移。','',
'前后对照：SE-11-13-before-after.jpg、SE-14-16-before-after.jpg；完整原生画布联系表：SE-recommended-full-canvas.jpg。联系表仅作诊断均匀缩放，来源记录齐全。','',
'仅为静态推荐，未改selected-new、manifest或导出。720ms为主比较语境，本轮没有实时播放或客户端接地验收；相位/接地/根点连续性仍须总控检查，不能据此宣称动作全部通过。']
(out/'FOOT_DIRECTION_HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'recommended':[{'frame':e['frame'],'source':e['source'],'sha256':e['sha256'],'headBBoxBefore':e['before']['headAlphaBBox'],'headBBoxAfter':e['headAlphaBBox']} for e in entries]},ensure_ascii=False))

