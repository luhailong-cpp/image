import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
xs=[540,540,553,565,555,555,550,553,530,545,552,560,558,555,550,542]
frames=[]
for i,x in enumerate(xs,1):
 p=R/'run/W'/f'{i:02}.png'
 frames.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'srcRoot':[x,960],'basis':'人工逐图以腰胯及支撑平衡中心判断x；组内支撑帧01/02/03/09/10/11观察采用统一虚拟地面960，保留飞行脚高与蹲伸','confidence':'manual approx +/-10 px; final dynamics pending global normalization'})
reg={'schemaVersion':1,'coordinateSpace':'current whole-canvas 1024x1024 exports, before global normalization','globalScale':0.8,'targetRoot':[512,942],'applyTransform':False,'method':'人工整帧与逐步contact审查，x为解剖髋/支撑中心，y全组统一960；非最低像素逐帧贴地，无bbox拟合。','frames':frames}
(R/'run/W/registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
review={'status':'static_review_passed_dynamic_registration_pending','technical':{'frames':16,'individualNativeSources':16,'size':[1024,1024],'mode':'RGBA'},'observed':'01落地、02压低、03膝前摆与支撑、04后伸蹬地，05-08腾空到落地前；09-16为另半步，右掌雪晶在前后摆位间运动，左狐臂肩肘随躯干运动。W07-15已修短发短袍。逐帧两手两脚与持物连续通过；最终根锚与动态首尾尚由根统一审查。','frames':frames}
(R/'run/W/review-final-subtask.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')

