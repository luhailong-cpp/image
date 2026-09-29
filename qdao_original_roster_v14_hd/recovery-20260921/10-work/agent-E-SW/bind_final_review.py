from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parents[1];O=R/'10-delivery-preview/current'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mp=O/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));rows=[]
for k,v in m['frames'].items():
 if not re.fullmatch(r'(E|SW)([0-9]{2}|idle)',k):continue
 p=O/v['file'];assert sha(p)==v['sha256'];assert Image.open(p).size==(1024,1024)
 rows.append({'slot':k,'archive':v['archive'],'sourceSHA256':v['rawSHA256'],'outputSHA256':v['sha256'],'pixelSHA256':v['pixelSHA256'],'output':str(p),'staticDecision':'acceptable_no_blocking_defect_observed'})
assert len(rows)==34
r={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'complete_e_sw','character':'10_crimson_spear_girl','scope':['E','SW'],'manifestCreatedAt':m['createdAt'],'manifestSHA256':sha(mp),'selectionSHA256':m['selectionSHA256'],'conclusion':'Static final export review acceptable; no blocking slot identified. Actual 30ms playback acceptance remains with root reviewer.','checks':{'bothBackgrounds':'All16 frames per direction inspected on final contact light/dark','normalScale':'Final contact384 and prior512 whole sprite','zoom':'Final1024 native-pixel head/feet crops for03-06,SW05-06/13-14,and15-16-01-02; idle viewed whole1024 and on512 light/dark plus detail','identityEquipment':'Consistent face,hair,costume,full spear and hand grips; independent idle both feet planted','alpha':'No conspicuous colored halo,matte or isolated visible specks on actual light/dark composites','E04_E05_registration':'Prior horizontal head/torso drift largely removed; remaining small head bob and local skirt/leg motion are ordinary pose variation, no extra missing-frame finding','SW05_SW06_support':'Same near-left leg remains support while far-right leg passes; larger foot screen travel is visible but no leg duplication or support inversion. Timing observation for root playback, not a static blocker.','SW13_SW14_support':'Far-right support remains while near-left knee advances.14 compact lift has no exaggerated sole kick. Timing observation for root playback, not a static blocker.','seam':'15-16-01-02 maintains lead leg and support topology, progressively lowers lead heel then accepts weight; stable head scale and silhouette'},'boundaryException':'E06 original3right-edge pixels maxalpha65 examined4x; complete metal tip, final entire tip with margin.','blockingSlots':[],'realTimePlaybackPerformedByThisAgent':False,'clientValidation':'not_performed','frames':rows}
(B/'final-export-review-20260928.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(rows),'manifest':m['createdAt'],'decision':r['conclusion']},ensure_ascii=False))
