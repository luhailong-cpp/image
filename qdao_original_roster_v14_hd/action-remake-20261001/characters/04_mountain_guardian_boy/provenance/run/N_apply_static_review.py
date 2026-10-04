from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];stamp=datetime.now(timezone.utc).isoformat()
obs={1:'屏左腿后伸露大鞋底，屏右腿远处接触；右杖臂较低后摆。',2:'屏右靴平底支撑，屏左靴抬高回收且露底缩小。',3:'屏右继续支撑，屏左屈膝靴向身下回收；肩肘接近中间。',4:'屏右腿转为后蹬露斜底，屏左较小靴向前收；右杖肩上摆、左盾下摆。',5:'屏右后腿延伸、屏左膝向远处驱动，右臂前摆。',6:'屏右大鞋底向后、屏左小靴在前，短暂腾空前半。',7:'屏左小靴较06下降，屏右后腿回收，右杖保持前摆。',8:'屏左靴继续趋向着地，屏右大底在后。',9:'与01相反，屏右腿后伸露大底、屏左腿远处接触，右杖臂前摆。',10:'屏左靴平底承重，屏右后靴向上回收露底缩小。',11:'屏左继续支撑，屏右屈膝靴向身下收，右肘回落。',12:'屏左腿转后蹬，屏右膝向远处前驱；右杖后摆、左盾前摆。',13:'屏左靴斜底/前掌蹬离，屏右小靴在前，手臂相反摆动。',14:'屏左后腿屈膝回收，屏右小靴在前；短暂腾空。',15:'屏右靴下落趋向接触，屏左仍在后方露底。',16:'与01同侧回环：屏左后伸露底、屏右远处小靴趋向接触，独立绘制。'}
records=[]
for n,note in obs.items():
 p=ROOT/'frames/run/N'/f'frame_{n:02}.png';sc=p.with_suffix('.generation.json');d=json.loads(sc.read_text(encoding='utf-8-sig'));sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==d['sha256']
 with Image.open(p) as im:
  assert im.size==(1024,1024) and im.mode=='RGBA'
  box=im.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox()
  assert box[0]>2 and box[1]>2 and box[2]<1022 and box[3]<1022
 d['review']={'status':'visual_passed','automaticallyApproved':False,'reviewedAt':stamp,'scope':'single_frame_and_contact_sheet','note':note,'dynamicSequenceStatus':'pending_root_browser_review','clientStatus':'not_integrated'}
 sc.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 records.append({'frame':n,'file':p.relative_to(ROOT).as_posix(),'sha256':sha,'alphaOver127Bounds':box,'observedPose':note,'singleFrameStatus':'visual_passed'})
out=ROOT/'provenance/run/N_static_review_20261003.json'
out.write_text(json.dumps({'reviewedAt':stamp,'timezone':'America/New_York','reviewer':'finish_se_cast','method':'all native outputs viewed plus 16-frame contact sheet; hashes are source binding not pose proof','singleFramePassed':16,'dynamicSequenceStatus':'pending_root_browser_review','clientIntegration':'not_integrated','notes':['01和09实际异侧腿；02/03与10/11有不同侧平底支撑。','北向远近脚有屏幕深度差，不把鞋底贴统一y。','根锚点(512,928)仅声明，动态接地和640/720/800ms比较仍待主审。'],'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'singleFramePassed':16,'dynamicPassed':0,'edgeClipping':0}))
