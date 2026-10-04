from pathlib import Path
import json,hashlib,datetime,shutil
from PIL import Image
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy');out=root/'review/grounding-fourframes';out.mkdir(parents=True,exist_ok=True)
# Preserve the output found after the interrupted S12-v3 call without inventing a tool receipt.
stem='12-v3';folder=root/'generation/run/S';src=Path(r'C:/Users/luyua/.codex/generated_images/01a100fe-b120-7e63-89d7-0c006715b355/exec-a786e6bd-f286-4e81-8299-dc2a2c37774b.png');dst=folder/(stem+'.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not dst.exists():shutil.copy2(src,dst)
reqpath=folder/(stem+'.request.json');req=json.loads(reqpath.read_text(encoding='utf-8-sig'));req['status']='submitted_call_interrupted_output_recovered_by_filesystem';req['startedAt']=None
reqpath.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
receipt={'status':'tool_callback_unavailable_after_interrupt','notRawToolReceipt':True,'recoveredAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostOutput':str(src),'hostOutputSha256':sha(src),'hostFileModifiedAtUtc':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'association':'Only new PNG in this agent host output directory after interrupted S12-v3 call; actual viewed content matches requested S left-support repair. Association is inferred, not a recovered callback.','completedAt':None,'actualModel':None,'actualQuality':None}
recpath=folder/(stem+'.receipt.json');recpath.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(dst)
record={'file':dst.relative_to(root).as_posix(),'sha256':sha(dst),'generatedAt':None,'recordedAt':receipt['recoveredAtUtc'],'nativeSize':list(im.size),'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Tool callback lost when wait was aborted; actual model/quality and exact completion time not disclosed/recovered.','prompt':req['prompt'],'references':req['references'],'evidence':{'request':reqpath.relative_to(root).as_posix(),'requestSha256':sha(reqpath),'receipt':recpath.relative_to(root).as_posix(),'receiptSha256':sha(recpath),'hostOutput':str(src)},'status':'recovered_candidate_with_inferred_output_association'}
Path(str(dst)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
reuse={
'S':{1:'01-v4',2:'02-v5',3:'03-v4',4:'04-v2',9:'09-v1',10:'10-v1',11:'11-v2',12:'12-v3'},
'SE':{1:'01-v5',2:'02-v3',3:'03-v1',9:'09-v2',10:'10-v1',11:'11-v3',12:'12-v4'},
'SW':{1:'01-v1',2:'02-v2',3:'03-v4',9:'08-v4',10:'09-v4',11:'10-v2',12:'11-v2',15:'12-v1'}}
rows=[]
for d in ['S','SE','SW']:
 for f in range(1,17):
  foot='right' if f<=8 else 'left';local=(f-1)%8+1
  spatial='front_contact' if local<=2 else 'under_body_support' if local<=6 else 'rear_push_contact'
  prior=reuse[d].get(f);path=root/'generation/run'/d/(prior+'.png') if prior else None
  rows.append({'direction':d,'frame':f,'durationMs':75,'supportFoot':foot,'positionAlongRunDirection':spatial,'distinctPoseWithinPosition':local if local<=2 else local-2 if local<=6 else local-6,'source':path.relative_to(root).as_posix() if path else None,'sha256':sha(path) if path else None,'status':'provisional_existing_source_to_review' if path else 'native_edit_required','spatialMeaning':'沿跑向前/身体下方/后；不是外侧脚尖，也不是脚跟/全掌/前掌同义词。'})
plan={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'instruction':'Latest explicit user spatial requirement supersedes previous four-contact-only plan.','frameMs':75,'cycleMs':1200,'layout':{'1-2':'right front contact','3-6':'right under-body support, four distinct natural knee/ankle poses','7-8':'right rear push, contact retained','9-10':'left front contact','11-14':'left under-body support, four distinct natural knee/ankle poses','15-16':'left rear push, contact retained'},'rules':['Every selected source used exactly once per direction','No mirror, interpolation, duplicated hold, whole-frame translation or bbox fit','Preserve left gourd/right empty hand/head scale/fixed camera','Existing source assignments are provisional until actually inspected under new spatial rule'],'frames':rows}
(out/'south-plan-middle4-side2-20261004.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved 48 explicit spatial/support slots; 25 native edits planned; recovered S12-v3 with truthful missing-callback evidence.')

