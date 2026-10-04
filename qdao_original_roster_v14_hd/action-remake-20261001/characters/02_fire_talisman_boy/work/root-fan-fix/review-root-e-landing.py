import json,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
root=Path(__file__).resolve().parents[2]
rows=[]
for n in [7,8,15,16]:
 rp=root/f'records/run-E-{n:02}-20261003-attempt-30.receipt.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));p=Path(r['nativePath']);im=Image.open(p);a=im.getchannel('A');right=list(a.crop((im.width-1,0,im.width,im.height)).getdata());border=[y for y,v in enumerate(right) if v>16]
 rows.append({'slot':f'run/E/{n:02}','receipt':rp.relative_to(root).as_posix(),'native':str(p),'nativeSHA':hashlib.sha256(p.read_bytes()).hexdigest(),'size':im.size,'cardCount':5,'handOwnership':'近右肩完整连接符扇腕，远左肩连接铜铃，已实际查看','contact':'前鞋基本落平、上鞋面与金侧缘可读，后腿折叠悬空；08/16膝踝弯曲较07/15明显','rightEdgeAlphaGt16Count':len(border),'rightEdgeYRange':[min(border),max(border)] if border else None,'finding':'E15铃穗右端实际碰到画布边缘并裁断，应收回穗子以保留构图' if n==15 else '未见明确新增缺陷','passedExceptFraming':True,'fullSequencePassed':False})
for item in rows:
 if item['slot']=='run/E/15':
  item['finding']='铃穗逼近右边缘，但无实证裁断：alpha>16的bbox右边为1245/1254，仅余9px原生（约7px/1024）；右边界alpha>16像素0。需按相邻帧留白判断是否局部收穗。'
  item['rightPaddingAlphaGt16']=9
out={'reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'scope':'实际读取attempt30 receipt指向的4张原生图，非旧正式图','frames':rows,'dynamicStatus':'静态独立审阅；未播放当前序列'}
(root/'reviews/root-e-landing-attempt30-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'slot':x['slot'],'rightEdgeAlphaGt16Count':x['rightEdgeAlphaGt16Count'],'rightEdgeYRange':x['rightEdgeYRange']} for x in rows],ensure_ascii=False))
