from pathlib import Path
import json,hashlib,datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy')
rows=[]
for action,count in [('hit',6),('attack',12),('cast',16)]:
 for d in ['E','W']:
  p=root/'review/animations'/f'{action}-{d}-contact.png'
  rows.append({'contact':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'action':action,'direction':d,'frameCount':count,'verdict':'keep_no_clear_opposite_foot_direction_or_twisted_ankle','finding':'联系表静态可见范围内，鞋掌随E右/W左身向，前后开立属于动作站姿；未见鞋掌反向或踝部反折的明确硬伤。'})
report={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'只读检查6组联系表共68帧的脚掌朝向与明显扭踝；不是原生逐像素复验，不是动态通过。','contacts':rows,'mustRegenerate':[],'dynamicApproved':False,'sourceModified':False}
(root/'review/moon-comparison/combat-foot-contact-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('6 combat contacts / 68 poses inspected; no new clear foot-direction hard failures.')

