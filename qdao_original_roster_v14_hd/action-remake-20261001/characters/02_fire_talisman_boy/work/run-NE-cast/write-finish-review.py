import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[2]
ip=B/'inventory-run-ne-cast.json';inv=json.loads(ip.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[('RIGHT',[16,1],'central','右足位于髋部下方，直立接触到轻屈膝承重'),('RIGHT',[2,3],'slight_rear','同一右足支撑，身体经过足上方，膝踝关系稍后移'),('RIGHT',[4,5],'rear','右足承重点继续在身体后方，左腿仍独立离地'),('RIGHT',[6,7],'rear_push','右前掌持续接地、提踵；07左小腿开始收回'),('LEFT',[8,9],'central','左足落于髋下，09屈膝承重，右腿抬起'),('LEFT',[10,11],'slight_rear','同一左足承重，重心向前通过足上方'),('LEFT',[12,13],'rear','左足移至身后支撑，两帧腿和衣摆各自不同'),('LEFT',[14,15],'rear_push','左前掌支撑提踵，15右小腿回收接向16落地')]
lookup={f:(s,pos,notes) for s,fs,pos,notes in pairs for f in fs}
rows=[]
for e in sorted(inv['frames'],key=lambda x:x['frame']):
    p=B/e['path'];actual=sha(p);assert actual==e['sha256']
    rec=json.loads((B/e['source_record']).read_text(encoding='utf-8-sig'))
    native=B/rec['file'];im=Image.open(p);assert im.size==(1024,1024) and im.mode=='RGBA';assert min(e['native_size'])>=1024
    if rec.get('export'):assert rec['export']['sha256']==actual
    assert sha(native)==rec['sha256']
    f=e['frame'];side,pos,notes=lookup[f]
    rows.append({'frame':f,'file':e['path'],'sha256':actual,'supportFoot':side,'position':pos,'visualNotes':notes,'sourceRecord':e['source_record'],'native':rec['file'],'nativeSHA256':rec['sha256'],'nativeSize':e['native_size'],'size':[1024,1024],'mode':'RGBA','actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'alphaBounds':list(im.getchannel('A').getbbox()),'status':'offline_visual_review_pass'})
    e['visual_status']='offline_visual_review_pass';e['client_status']='not_integrated';e['sequence_review']='reviews/run-NE-eight-support-final-review-20261004.json'
assert len(rows)==16 and len({e['sha256'] for e in rows})==16
report={'character':'02_fire_talisman_boy','action':'run','direction':'NE','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'offline_visual_review_pass','formalCount':16,'newRevisedSlots':[1,2,3,4,5,6,7,8,9,12,13,14,15],'retainedSlots':[10,11,16],'frameDurationMs':75,'cycleMs':1200,'slowCycleMs':4800,'method':['实际查看整帧接触表全部16帧及固定下半身裁图','原生07/15补修图实际查看；首轮擅自换腿候选拒绝，第二轮保持原支撑脚后才导入','浏览器正常1200ms/160px、慢放4800ms/384px切换，连续播放画面取样','浏览器逐帧检查07→08与15→16→01换脚/首尾','逐图SHA、原生来源SHA、正式尺寸/模式、16张独立SHA检查'],'observationLimit':'动态工具以连续播放状态的屏幕取样及逐帧检查为证据，未进行客户端运行验收。','supportPairs':[{'foot':s,'frames':fs,'position':pos,'durationMs':150,'notes':notes,'sha256':[next(r['sha256'] for r in rows if r['frame']==f) for f in fs]} for s,fs,pos,notes in pairs],'frames':rows,'previews':{'html':'work/run-NE-cast/eight-support-review.html','contact':'work/run-NE-cast/eight-support-contact.jpg','lowerBody':'work/run-NE-cast/eight-support-lower-body.jpg','normal':'work/run-NE-cast/eight-support-normal.apng','slow':'work/run-NE-cast/eight-support-slow.apng'},'browserEvidence':['reviews/run-NE-final-browser-normal.png','reviews/run-NE-final-browser-step07.png','reviews/run-NE-final-browser-step15.png'],'knownUnresolvedArtFailures':[],'clientStatus':'not_integrated','modelQuality':'目标GPT Image2.5 Sunburst/max；宿主管理，未披露实际版本/质量。'}
(B/'reviews/run-NE-eight-support-final-review-20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv['qa_summary']={'ownedSlots':16,'formalCount':16,'nativeMin':min(min(e['native_size']) for e in inv['frames']),'technicalStatus':'16张独立原生图整画布下采样1024 RGBA；SHA逐图匹配','dynamicStatus':'正常1200ms/160px、慢放4800ms/384px屏幕取样与逐帧接缝检查完成；见独立复核报告','completeSequencePassed':True,'clientStatus':'not_integrated','review':'reviews/run-NE-eight-support-final-review-20261004.json'}
inv['target_frames']=16;inv['updatedAt']=report['reviewedAt']
ip.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in rows:print(f"{r['frame']:02d} {r['sha256']}")

