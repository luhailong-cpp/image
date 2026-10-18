import sys,json,hashlib
from pathlib import Path
from PIL import Image
B=Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-production-20261013\city-tower-north')
sys.path.insert(0,str(B/'tools'))
import receipt_register as rr
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 with p.open('x',encoding='utf-8') as f: json.dump(o,f,ensure_ascii=False,indent=2)
sel=B/'selections/right-r04c14-candidate-overlay-v007.json'; d=json.loads(sel.read_text('utf-8'))
verified=[]
for item in d['repairIntegrations']:
 p=Path(item['file']);assert sha(p)==item['sha256'];i=json.loads(p.read_text('utf-8'));r=json.loads(Path(i['receipt']['file']).read_text('utf-8'));prov=r['provenance'];s,rec,h=rr.completed_event(Path(prov['sessionLog']),prov['eventId']);assert h==i['nativeRepair']['sha256'];assert sha(i['nativeRepair']['file'])==h
 verified.append({'integration':str(p),'sourceSha256':h,'receiptBytesVerified':True,'eventId':prov['eventId']})
p=Path(d['candidate']['file']);assert sha(p)==d['candidate']['sha256'];assert Image.open(p).size==(4096,4096)
write(B/'qa/right-r04c14-reboot-recovery-v001.json',{'tile':'r04_c14','verifiedCandidate':d['candidate'],'nativeCount':16,'formalAcceptedCount':0,'verifiedRepairEvents':verified,'latestCheckpointNoInFlight':True,'unsubmittedDraft':'right-r04c14-p22-v003.UNSUBMITTED.json','unsubmittedDraftNotSent':True,'returnedUnregisteredSourceFound':False,'basis':'Latest checkpoint plus exact two selected overlay event replay; latest right-r04c14 request is finialv002 and completed integration exists.'})
prompt='Use case: precise-object-edit. Edit this exact 1254x1254 native image. Repair only the small broken timber jamb immediately LEFT of the big red column, inside x575..725 y430..720. The narrow vertical wood jamb has an orphan little angled ledge at x626..655 y475..512 and an abrupt horizontal cutoff at y512. Remove that orphan ledge and join the same slim vertical timber smoothly to the existing timber continuation below around x595..650 y650..690. Preserve the existing top jamb width, lower jamb base, diagonal sill, and perspective. The jamb should look like one uninterrupted constructed wood frame with crisp continuous vertical grain and edge, without a floating short ledge or block-like cutoff. Keep all gold plaques, their corners and flourishes, big red column, gold plinth, floor, and all wood outside that very small repair rectangle fixed in position. Do not move the lower structures to meet the upper. Do not touch the separate broad horizontal patch join at y627 outside the targeted jamb. Preserve the exact Daoist Q high-definition hand-painted material and daylight. Output exactly 1254x1254 opaque RGB PNG, no resizing, crop, zoom, warp, blur, new decoration or text.'
p=B/'prompts/right-r04c14-east-jamb-v001.txt';p.open('x',encoding='utf-8').write(prompt)
req={'tile':'r04_c14','kind':'native-local-jamb-repair','prompt':prompt,'referenced_image_paths':[str(B/'versions/right-r04c14-east-jamb-prepare-v001/repair-input.png')],'transparent_background':False,'nativePixels':[1254,1254],'actualModel':None}
write(B/'requests/right-r04c14-east-jamb-v001.request.json',req)
print(json.dumps({'recoveryVerified':True,'candidateSha256':d['candidate']['sha256'],'request':str(B/'requests/right-r04c14-east-jamb-v001.request.json')}))