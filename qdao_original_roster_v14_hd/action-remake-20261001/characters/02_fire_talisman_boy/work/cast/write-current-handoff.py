import json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2]
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
inv=load(root/'inventory-cast.json');ne=load(root/'inventory-run-ne-cast.json');qa=load(root/'records/cast-qa-20261003.json')
rows=[]
for f in inv['frames']:
 if f['direction']=='E' and f['frame'] in [6,7,8,9,10,11,12,14]:
  r=load(root/f['source_record']);rows.append({'slot':f"cast/E/{f['frame']:02}",'formal':f['path'],'formalSHA':f['sha256'],'native':r['file'],'nativeSHA':r['sha256'],'record':f['source_record'],'visualQA':r['visualQA']})
out={'updatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'castFrames':len(inv['frames']),'ownedNEFrames':len(ne['frames']),'armChainRepaired':rows,'knownHandOwnershipFailures':qa['knownHandOwnershipFailures'],'footAxisRepaired':{'E':list(range(1,17)),'W':list(range(4,13))},'footAxisRetainedReviewed':{'W':[1,2,3,13,14,15,16]},'remaining':'当前SHA正常/慢速整段实播、根点与尺度连续性；客户端未接入。单帧及来源审计不能替代动态。','sourceAudit':'records/cast-and-ne-source-audit-20261003.json','rootFanFixHandoff':'reviews/root-fan-cast-approved-20261003.json','rootIndependentReview':'reviews/root-independent-review-20261003.json','bambooReference':'reviews/bamboo-cast-reference-20261003.md','castTimingMs':720,'runTimingMs':1200,'actualModel':None,'actualQuality':None,'modelEvidence':'配置目标gpt-image-2.5-sunburst/max；内置无选择器，实际型号/质量未确认。'}
(root/'records/cast-current-handoff-20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'slot':r['slot'],'sha256':r['formalSHA']} for r in rows],ensure_ascii=False))
