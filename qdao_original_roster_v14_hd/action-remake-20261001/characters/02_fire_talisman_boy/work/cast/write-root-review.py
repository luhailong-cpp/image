import json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2]
snap=json.loads((root/'reviews/root-independent-snapshot-20261003.json').read_text(encoding='utf-8'))
frames=snap['frames'];inv=json.loads((root/'inventory-root.json').read_text(encoding='utf-8'))
for n in [3,12]:
 f=next(f for f in inv['frames'] if f['action']=='attack' and f['direction']=='W' and f['frame']==n)
 frames.append({'action':'attack','direction':'W','frame':n,'path':f['path'],'sha256':hashlib.sha256((root/f['path']).read_bytes()).hexdigest(),'native_evidence':f['native_evidence']})
for f in frames:
 bad=(f['action'],f['direction'],f['frame'])==('attack','E',10) or (f['action']=='run' and f['direction']=='SE' and f['frame'] in [5,6,7,8,9,14,16])
 f['talismanCount']=6 if bad else 5;f['handOwnership']='本次逐张view_image原尺寸观察：可追踪右肩→符腕、左肩→铃腕，未确认新的归属错误'
 f['shoeAxis']='本次未确认明显反向/V字外撇；抬跟露底或正面透视不单独判错'
 f['status']='needs_five_card_repair' if bad else 'single_frame_reviewed_sequence_pending'
findings=[{'severity':'must_fix','slot':f"{f['action']}/{f['direction']}/{f['frame']:02}",'sha256':f['sha256'],'evidence':'原尺寸可数六张完整红色矩形符纸和六个独立金色火纹，非边框误判；应局部删一张并保持姿态。'} for f in frames if f['talismanCount']==6]
out={'reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'reviewer':'cast_key independent root review','scopeCount':56,'method':'先整画布联系表对照，再对56正式PNG逐张view_image原尺寸查看；本报告SHA是审查时快照，后续修订另有记录。','findings':findings,'observationsNotHardFailures':[{'slots':['attack/E/02'],'finding':'新蓄力图五符，右符左铃，双鞋朝右；冠发/铃穗/鞋均留在画布内，未见裁切。'},{'slots':['run/SE/02','run/SE/03'],'finding':'02屈膝受重且后腿折收；03低脚在髋下，异侧膝抬起，支撑相位单图可读。02前掌略上翘，接触滚动需当前序列实播，不将此当外撇。'},{'slots':['attack/W/03'],'finding':'最新修订五符，铜铃红穗完整收在画布内，两鞋朝左；W02→03有持续前送铃/后收符动作。'},{'slots':['attack/W/11','attack/W/12','attack/W/01'],'finding':'W11趋于站高，W12再次明显屈膝张嘴并拉开双脚，再接W01，需实播判断收势回弹。W12本身五符、右符左铃及鞋轴正确。'}],'limitations':'无当前可用IAB，本代理未声明正常/慢速播放通过。手腕/符数/鞋轴单图审查不替代全段动作和统一根点验收。','frames':sorted(frames,key=lambda f:(f['action'],f['direction'],f['frame']))}
(root/'reviews/root-independent-review-20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('56 frames reviewed; 8 six-card findings; sequence pending')
