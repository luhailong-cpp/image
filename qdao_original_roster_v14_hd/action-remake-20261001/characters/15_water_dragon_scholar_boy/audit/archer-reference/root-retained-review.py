from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
groups=[]
notes={
 'run-E':'主审实际查看本角色16帧连图和09同向16帧连图。鞋轴均朝右，01/02与09/10有接触和压膝，04/12蹬离，05–07/13–15短腾空与下降；双手前后互换且扇保持解剖右手。此轮保留16帧；正常1200ms动态另验。',
 'hit-E':'重新实际查看6帧有序连图：双靴向右，支撑膝缓冲、躯干后仰及恢复成立；持扇及空手保留。此次未见需按跑步模板重画的脚向错误。',
 'hit-W':'重新实际查看6帧有序连图：双靴向左，受击缓冲、后仰及恢复成立，保留旧成品。',
 'attack-E':'重新实际查看12帧有序连图：前后靴都朝右，双脚战斗支撑；扇蓄力、前送和收招各阶段可辨，保留旧成品。',
 'attack-W':'重新实际查看12帧有序连图：前后靴都朝左，无反向外撇；右手扇蓄力、出手及收势，保留旧成品。',
 'cast-E':'重新实际查看16帧有序连图：双靴朝右，右扇左诀和释放/收势可辨；保留此前修好的鞋向。历史记录的少量脚缘/底线绘制变化仍保留，不宣称像素锁地。',
 'cast-W':'重新实际查看16帧有序连图：双靴朝左，右扇左诀，聚势/释放/恢复阶段完整；保留旧成品。'
}
for group in manifest['groups']:
    key=group['action']+'-'+group['direction']
    if key not in notes: continue
    rows=[r for r in manifest['frames'] if r['action']==group['action'] and r['direction']==group['direction']]
    contact=ROOT/'preview'/f'{key}-contact.png'
    groups.append({'group':key,'decision':'retain_existing_pixels','method':'root viewed actual ordered contact sheet; run E also compared with actual 09 motion reference','notes':notes[key],'contact':{'file':str(contact.relative_to(ROOT)),'sha256':sha(contact)},'frames':[{'slot':f"{r['action']}-{r['direction']}-{r['frame']:02d}",'file':r['output'],'sha256':sha(ROOT/r['output'])} for r in rows]})
record={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root','scope':'current rejection review, static actual-image retention decisions only','clientIntegration':'not_integrated','userAcceptance':'not_reviewed_after_repair','groups':groups}
(ROOT/'audit/archer-reference/root-retained-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'groups':len(groups),'frames':sum(len(g['frames']) for g in groups)}))
