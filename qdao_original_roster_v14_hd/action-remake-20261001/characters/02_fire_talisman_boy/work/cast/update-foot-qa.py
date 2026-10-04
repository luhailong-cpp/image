import json,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]
now=datetime.now(ZoneInfo('America/New_York')).isoformat()
inv=json.loads((root/'inventory-cast.json').read_text(encoding='utf-8'))
tech=json.loads((root/'records/cast-technical-20261003.json').read_text(encoding='utf-8'))
metrics={(x['direction'],x['frame']):x for x in tech['frames']}
rows=[]
for f in inv['frames']:
 d,n=f['direction'],f['frame']; edited=d=='E' or 4<=n<=12
 notes='两只鞋的跟到尖轴均朝'+('屏幕右' if d=='E' else '屏幕左')+'，未见明显V字/相反方向外撇；膝踝鞋连接可读。五张红符与左右持物归属已复核。'
 if (d,n)==('E',3):notes+=' 从E02重新画起势，已纠正上一轮整体缩小/鞋底过高。'
 if (d,n) in [('E',5),('E',12)]:notes+=' 本轮重画小腿膝踝延伸至虚拟地面；未移动整张切图或按bbox贴地。'
 if (d,n)==('W',11):notes+=' 从W10重新画收势，纠正上一轮头部变大；不判整段尺度验收通过。'
 qa={'status':'foot_axis_reviewed_sequence_pending','reviewedAt':now,'method':'每次工具返回原图目视＋当前完整联系表＋32帧鞋部QA裁片；另复看E01/E09/W04/W11原尺寸图','singleFrameFindings':notes,'footAxisPassed':True,'talismanCount':5,'dynamicPassed':False,'registrationPassed':False,'clientStatus':'not_integrated'}
 rp=root/f['source_record'];r=json.loads(rp.read_text(encoding='utf-8-sig'));r['visualQA']=qa;rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 f['visual_status']=qa['status']
 rows.append({'direction':d,'frame':n,'path':f['path'],'sha256':f['sha256'],'source_record':f['source_record'],'footRepairThisBatch':edited,'status':qa['status'],'findings':notes,'bounds_alpha_gt16':metrics[(d,n)]['bounds_alpha_gt16']})
summary={'reviewedAt':now,'slots':32,'nativeAllAtLeast1024':True,'singleFrameAnatomyReviewed':32,'footAxisReviewed':32,'footAxisRepainted':25,'completeSequencesPassed':0,'dynamicStatus':'本代理本轮cua.createBrowserTab(iab)返回Browser is not available: iab；listBrowsers=[]。主代理另有可用入口，接手当前版本正常/慢速实播；不可用旧预览结果替代。','client_status':'not_integrated','sourceAudit':'records/cast-and-ne-source-audit-20261003.json'}
inv['qa_summary']=summary;(root/'inventory-cast.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'summary':summary,'repaired':{'E':list(range(1,17)),'W':list(range(4,13))},'retainedAfterFootAxisReview':{'W':[1,2,3,13,14,15,16]},'currentKnownFootAxisFailures':[],'fullSequencePassed':False,'remainingChecks':[{'frames':'cast E01-16 / W01-16','issue':'整段头部尺度、根点稳定、起势/释放/收势衔接需当前版本正常及慢速实播；静态单帧不等同全段通过。'},{'frames':'cast E01-02,06,11,13-15 对 E07-10；W01-06,12-16 对 W07-10','issue':'联系表中鞋底高度仍有约数十像素变化，需判断脚前后深度与自然姿态，不能按最低像素统一贴地。'},{'frames':'cast E11→12→13 与 W10→11→12','issue':'最新收势已重画；相邻头部投影尺度和重心回收需重点播放复核。'}],'timing':{'frame_duration_ms':45,'duration_ms':720,'changed':False},'modelEvidence':'配置目标gpt-image-2.5-sunburst/max；内置入口无选择器，实际提交model/quality及返回版本/质量未确认。','frames':rows}
(root/'records/cast-qa-20261003.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
