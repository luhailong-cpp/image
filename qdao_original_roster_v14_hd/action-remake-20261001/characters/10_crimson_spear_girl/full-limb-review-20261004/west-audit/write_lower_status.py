from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
o=Path(__file__).resolve().parent;r=o.parents[1]
sources=json.loads((o/'source-snapshot.json').read_text(encoding='utf8'))['sources']
upper=json.loads((o/'upper-status.json').read_text(encoding='utf8'))
uppermap={x['frame']:x for x in upper['rows']}
rows=[];combined=[]
for item in sources:
    _,direction,num=item['frame'].split('/');n=int(num);status='passed'
    if direction=='W':
        if 9<=n<=12:
            status='fail';reason='W07/08低支撑腿在悬空腿前景；09起原近侧膝靴改成高抬前景腿，低腿转为远侧。09–12需重绘髋膝遮挡归属，不能靠phase标签或重排。靴尖总体朝屏左，问题主要是腿身份连续性。'
        elif n in (13,14):
            status='uncertain';reason='前方低靴和膝踝可读且鞋头朝屏左；裙摆遮住近端髋口，不能单独由该两帧确定解剖左右。保留并连15/16及首尾复核，不盲改自然侧视踝屈。'
        elif n<=4:
            reason='完整16循环中01/02后支撑、03/04更后推蹬的可见膝踝连接连续，靴头保持屏左，未見足掌横向转向镜头或左右突然反转。04→05为计划中的正常换脚边界，不作提前换脚错误。'
        elif n<=8:
            reason='05–08近側腿在前景承重，远侧屈腿在后，支撑膝踝靴连接及鞋头朝向处于侧面跑动平面；06新版多余后踢已消除。'
        else:
            reason='15/16低靴在身体下，前景回摆膝自然屈曲；可见腿连接与16→01接续未见明确外撇。13/14遮挡归属另记uncertain。'
    elif direction=='NW':
        if n in (11,12):
            status='fail';reason='同近侧支撑连接已连续，但10→11从短屈腿突变为长斜腿，髋相对低靴向右下的跨度陡增，11/12膝伸及踝区显得过度拉长。需收回幅度、保留自然后蹬与第四连续位置两独立帧。'
        elif n in (1,2,3,4):
            reason='后侧三分之四视角中小腿向右下、鞋跟上提/露底可由NW后蹬解释；未仅按二维踝角、鞋底可见或腿不竖直判外翻。四帧可见关节归属连续。'
        elif n<=10:
            reason='05–10同近侧支撑腿保持前景连接，远侧高靴在右后；09/10新版不再提前换脚。膝踝靴朝向在NW运动平面内，无明确孤立侧拧；11/12跨度另列fail。'
        else:
            reason='13开始换为另一脚低位承重，14–16前后景归属连续；低靴呈后侧透视、抬靴露底本身不构成外翻。'
    else:
        if n in (15,16):
            status='fail';reason='SW15/16相对12/14支撑大腿和小腿向屏右扩展过大，膝踝侧向跨度变长，整体读为宽开胯跨步。不是仅由髋到脚二维连线定外翻；已与全身比例及前后帧一起看。交根指定SW修图代理复核并修。'
        elif n in (13,14):
            status='uncertain';reason='支撑腿从12进一步向右伸展，鞋头仍朝SW左下，单帧可由后蹬解释，但需连15/16审查是否侧向开胯过度；不凭对角线单独判错。'
        elif n<=8:
            reason='01–08低位靴持续同侧，膝踝与鞋头朝向一致于SW斜向平面，高屈腿保持在后侧；07/08当前修图未见旧版提前换腿。'
        else:
            reason='09换脚后10–12同一支撑侧继续，膝踝及鞋头朝SW左下，髋下腿长与抬腿关系自然，未见明确外八或脚掌横转。'
    p=Path(item['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
    row={**item,'status':status,'reason':reason,'method':'Current runtime fixed full-canvas and native lower-limb contact sheets actually viewed this review; suspect W08/09, NW05, SW15 additionally viewed as original PNGs; no previous report substituted'}
    rows.append(row)
    up=uppermap[direction+num];assert up['sha256']==item['sha256']
    overall='fail' if 'fail' in (status,up['status']) else ('uncertain' if 'uncertain' in (status,up['status']) else 'passed')
    combined.append({**item,'status':overall,'lower':{'status':status,'reason':reason},'upper':{'status':up['status'],'reason':up['reason'],'checks':up['checks']}})
def write(name,data):(o/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
stamp=datetime.now(timezone.utc).isoformat()
write('lower-status.json',{'reviewedAt':stamp,'scope':'current runtime/run/W,NW,SW 48 frame lower limbs; pre-repair snapshot','rows':rows})
write('frame-status.json',{'reviewedAt':stamp,'scope':'48 frame current runtime combined limb and weapon audit; pre-repair states retained, repairs reviewed separately','rows':combined})
print('48 lower + 48 combined SHA-classified records saved')
