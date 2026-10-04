from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parents[1]
sources=['01-v2','02-v3','03-v6','04-v8','05-v5','06-v1','07-v1','08-v1','09-v6','10-v6','11-v7','12-v6','13-v2','14-v1','15-v1','16-v1']
notes=[
'近侧前脚踵/中足初接触候选，鞋尖朝E略背屈，后腿折叠；原图保留。是否已触地须对虚拟地面复核。',
'近侧承重缓冲候选，前靴底较平、膝踝有弯曲；原图保留。与01足点前后位移较小，须动态排查滑步。',
'支撑足过躯干下方、对侧膝前摆；复用本机03-v6卡片中间摆位修正版。靴尖E向，支撑足到04的轨迹仍待动态。',
'新局部修复：支撑腿后伸收短、后跟抬起、前掌有短水平接触段，靴尖更纯E侧面。另一腿折叠离地。接地与整体动画尚未通过。',
'承接已有05-v4早期腾空收腿，再局部修正前靴朝镜头的宽正面；新05-v5靴尖更侧向E，前脚保持抬高。双足离地时间宜短。',
'伸展腾空：前脚背屈、后膝折叠，双方均离虚拟地面；原图保留，不应长停。',
'伸展末端至下降：前靴开始下落，后靴折叠；原图保留，不视为支撑。',
'落地前伸腿，前靴接近虚拟地面；原图保留。不能因鞋底低就标已承重。',
'另一半圈初接触候选：前靴从前伸回收至较平，另一腿后折；原图保留。对侧身份连续性还需与08及10实播复核。',
'另一半圈承重缓冲：前靴底平、膝弯曲；复用本机10-v6卡片回摆中间帧。支撑足向后移动有限，动态滑步未排除。',
'过中支撑/摆腿收折候选：靴底平且腿在躯干下，另一腿屈膝前收；复用11-v7。11-v8留有空袖口拒选。',
'新局部修复：旧后伸脚收回，后跟抬起、前掌短段平底并指向E，异侧腿前摆。AI有轻微上身轮廓重描，须主窗口和相邻帧动态复核。',
'另一半圈早期腾空：复用本机13-v2前摆靴抬高版；双脚离地清楚，前靴侧向E。',
'第二次伸展腾空：前伸后折，脚尖E向，无需仅为数量重绘。原图保留。',
'第二次下降前伸，脚尖E向；原图保留，短时播放。',
'临接触：前靴降下、后膝折叠；原图保留，检查16到01衔接。'
]
frames=[]
for i,(s,n) in enumerate(zip(sources,notes),1):
 rel='generation/run/E/'+s+'.png'
 p=B/rel
 rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 assert actual==rec['sha256'],(p,actual,rec['sha256'])
 frames.append(dict(action='run',direction='E',frame=i,source=rel,generationRecord=rel+'.generation.json',sha256=actual,width=rec['width'],height=rec['height'],actualModel=rec.get('actualModel'),actualQuality=rec.get('actualQuality'),status='static_candidate',visualReview=n,dynamicReview='not_verified',newInThisPass=i in [4,5,12]))
out=dict(schema=1,character='20_star_formation_master_girl',action='run',direction='E',generatedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),purpose='供主窗口合并的独立选表；原run-selection、STATUS、预览未修改',frames=frames,dynamicAcceptance=False,staticReview='provenance/run-foot-E-static-review-20261003.json',newFrameCount=3,reusedFrameCount=13,runTiming=dict(status='trial_only',comparisonLoopMs=[640,720,800],suggestedWeighted720Ms=[65,85,75,45,20,20,25,25]*2),rejected=[dict(source='generation/run/E/04-v7.png',reason='未收回后伸支撑腿，轨迹仍跳变'),dict(source='generation/run/E/11-v8.png',reason='卡片移回后留下空袖口，复用v7')],remaining=['动态观察足点轨迹、近远腿连续和手持物连续','客户端位移、滑步、根点、碰撞未验收','其他7方向无本批跑步通过结论'])
(B/'run-foot-selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(frames=len(frames),newFrames=3,reused=13,shaValidated=True,dynamicAcceptance=False),ensure_ascii=False))

