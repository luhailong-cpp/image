from pathlib import Path
from PIL import Image
import hashlib,json,datetime

root=Path(__file__).resolve().parent.parent
notes={
1:'屏幕右侧腿前伸，鞋尖上翘、后腿屈起；更像入地前摆动，未见承重。',
2:'同侧前伸脚、后脚抬起，宽步悬空；膝踝未形成落地缓冲。',
3:'双腿收起、双脚离开可推定支撑区，是明确短腾空候选，可保留但需重排。',
4:'重复屏幕右侧腿前伸、另一腿后屈；不是异侧落地。',
5:'同侧前伸、另一脚后收，未呈支撑。',
6:'前腿较弯但脚仍前移，双脚悬空线索强；不构成着地。',
7:'前靴底明显朝向观察者，后脚收起；明确入地前/腾空姿态。',
8:'同侧前靴伸出、后跟收起，未见承重。',
9:'衣摆遮住部分髋腿连接；仍见屏幕右侧靴前伸，没有足够证据证明左右腿交换。',
10:'同侧前腿伸出，鞋底可见、脚尖上翘，后脚离地；不是异侧支撑。',
11:'同侧前伸脚与抬起后脚，未见负重腿。',
12:'同侧前伸，不能把提示词半周标签当异侧证据。',
13:'同侧前靴上翘、后脚抬起；未见蹬离。',
14:'本组最接近承重：前靴底较平、膝屈且脚靠近身体下方；仍同侧，需可信地面与前后相位才能确认。',
15:'同侧前伸、靴底可见、另一脚后收，缺接触。',
16:'同侧前伸腿加后屈腿，不能自然接异侧承重。'
}
rows=[]
for n in range(1,17):
 p=root/'generation'/f'run-SE-{n:02d}'/'native.png'
 im=Image.open(p); a=im.getchannel('A') if 'A' in im.getbands() else None
 rows.append(dict(frame=n,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode,alphaExtrema=list(a.getextrema()) if a else None,observed=notes[n],groundContact='possible_unconfirmed' if n==14 else 'not_demonstrated',phase='airborne_tuck' if n==3 else 'possible_load' if n==14 else 'swing_or_airborne',armReview='双手固定握杆可辨，肩肘变化很小，缺与异侧承重同步的反向扭转。',passed=False))
obj=dict(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='reviewed; requires targeted pose repairs',sourceReadOnly=True,sourceCount=16,observedDefects=['没有可信的另一只脚承重半周','未见后腿伸展且前掌蹬地的完整离地姿态','多帧重复同侧前伸腿，腾空比例过高','肩肘/双手随躯干负重的变化不足'],registration=dict(targetCanvas=[1024,1024],targetRoot=[512,942],policy='固定方向统一比例/相机，根点取可信承重姿态的骨盆地面投影；不得逐帧bbox缩放或最低靴底贴线。远脚允许透视y差。当前尚无可信异侧支撑对，最终平移量待修帧后量测。',applied=False),timing=dict(originalMs=480,trialMs=[640,720,800],selectedFinalMs=None,combatTimingUnchanged=True),clientTested=False,entries=rows)
(root/'grounding-SE-work'/'SOURCE_REVIEW.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'count':len(rows),'sizes':sorted(set(tuple(r['nativeSize']) for r in rows)),'review':str(root/'grounding-SE-work'/'SOURCE_REVIEW.json')},ensure_ascii=False))
