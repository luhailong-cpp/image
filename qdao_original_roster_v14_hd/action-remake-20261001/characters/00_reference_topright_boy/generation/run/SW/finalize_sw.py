from pathlib import Path
import json, hashlib, datetime
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
V={1:1,2:1,3:2,4:3,5:3,6:4,7:3,8:4,9:4,10:2,11:2,12:1,13:3,14:3,15:2,16:1}
phases=['right_contact','right_loading','right_midstance','right_toeoff','left_initial_flight','left_flight_apex','left_flight_descending','left_precontact','left_contact','left_loading','left_midstance','left_toeoff','right_initial_flight','right_flight_apex','right_flight_descending','right_precontact']
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
sheet=Image.new('RGB',(1600,1680),(226,230,233)); d=ImageDraw.Draw(sheet)
entries=[]
for n,v in V.items():
 f=P/f'{n:02d}-v{v}.png'; im=Image.open(f); assert im.size==(1254,1254) and im.mode=='RGBA'; assert im.getchannel('A').getextrema()==(0,255)
 meta=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8-sig')); assert meta['sha256']==sha(f)
 i=n-1; thumb=im.resize((400,400)); sheet.paste(thumb,((i%4)*400,(i//4)*420),thumb)
 d.text(((i%4)*400+8,(i//4)*420+402),f'{n:02d} v{v}  {phases[i]}',fill='black')
 entries.append({'slot':f'{n:02d}','phase':phases[i],'version':v,'file':f.name,'sha256':sha(f),'generationRecord':f.name+'.generation.json','durationMs':30,'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':[0,255],'status':'provisional_selected_pending_sequence_review'})
sheet.save(P/'contact-selected.png')
record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'direction':'SW','action':'run','expectedCount':16,'selectedCount':16,'durationMs':30,'cycleMs':480,'nativeSize':[1254,1254],'status':'provisional_selection_not_visual_or_dynamic_approval','entries':entries,'contactSheet':'contact-selected.png','dynamicReview':'not_performed','clientValidation':'not_performed','exportPerformed':False,'actualModel':None,'actualQuality':None,'modelNote':'Host managed builtin; selectors and actual model/quality absent. See independent generation records.','remainingIssues':[]}
record['remainingIssues']=[
 {'slots':['03'],'severity':'needs_correction','issue':'03-v2 right boot supports under pelvis but head/body remain substantially enlarged relative to 09-v4 and neighbors. A final bounded attempt 03-v3 used 09-v4 as scale authority and 03-v2 as pose-only reference, but still enlarged head/body and moved the supporting foot lower; retain 03-v2 as best in-progress candidate. It is NOT visually approved and must not be treated as a mere dynamic-review item. No further retries in this bounded subtask.'},
 {'slots':['05','06','07','08','09'],'severity':'review_required','issue':'Left-leading leg identity is readable across first flight and left landing. 08-v4 now preserves 09-v4 head/body scale and changes precontact boot position. Remaining head/root trajectory and cycle timing need sequence review; do not foot-lock or bounding-box fit to conceal issues.'},
 {'slots':['01','16'],'severity':'review_required','issue':'16-v1 has a larger head/upper body than 01-v1 and may pop at the loop seam. 16-v2 was rejected because scale correction enlarged the character further.'},
 {'slots':['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16'],'severity':'not_verified','issue':'Contact-sheet review only. Full-speed 30ms and slow-motion loop review, export alignment, transparent edge review against multiple backgrounds, and client integration have not been performed.'}
]
record['staticObservations']=['05-09 left-leading and 13-16 right-leading now read as alternating halves; no mirroring used.','03-v2 right boot supports under pelvis, but the head/body scale defect remains after one final 03-v3 attempt.','04-v3 now preserves the 09-v4 head/body scale and retains correct right trailing toeoff with left knee forward; replaces enlarged 04-v2.','08-v4 preserves 09-v4 head/body scale; 08-v3 size drift superseded.','Left hand retains one golden taiji gourd and headband knot retains anatomical left side (viewer right).','Empty right arm moves from forward swing in 04-09 to backward swing in 10-16; 13-v3 fixes wrong-side rear sleeve/hand.','14-v3 replaces 14-v1 extra rear sleeve and excessive scale.','All selected PNGs retain native 1254 square RGBA, real transparent alpha, no image processing performed on deliverable PNGs.']
(P/'selection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
derived={'file':'contact-selected.png','sha256':sha(P/'contact-selected.png'),'operation':'QA contact sheet only, full-canvas uniform thumbnail resize, no source edits or per-frame bounding-box fitting','derivedFrom':[{'file':e['file'],'sha256':e['sha256'],'generationRecord':e['generationRecord']} for e in entries]}
(P/'contact-selected.png.derivation.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':16,'allMetadataHashVerified':True,'allNativeRGBA':True,'contactSheet':str(P/'contact-selected.png')},ensure_ascii=False))
