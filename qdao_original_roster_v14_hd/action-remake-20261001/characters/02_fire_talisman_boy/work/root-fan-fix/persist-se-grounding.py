import json,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2];dest=root/'work/root-ground-fix';dest.mkdir(exist_ok=True)
rows=[]
for n in [7,8,15,16]:
 id=f'run-SE-{n:02}-20261003-attempt-40';rp=root/'records'/f'{id}.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));receipt=root/'records'/f'{id}.receipt.json';re=json.loads(receipt.read_text(encoding='utf-8-sig'));host=Path(re['nativePath']);native=dest/f'{id}-native.png';shutil.copyfile(host,native);im=Image.open(native);sha=hashlib.sha256(native.read_bytes()).hexdigest()
 note='五卡、右扇左铃和两臂保持；前左腿屏右下鞋底基本平，后右腿屏左仍折起，07初触、08前脚回收到身下并压膝' if n in [7,8] else '五卡/持手保持，前右鞋基本平，但后左腿被挪到屏左后方，与原腿序不符，需要修正' if n==15 else '五卡/持手保持，前右腿屏左下鞋底基本平，后左腿屏右折起；前膝向承重弯曲'
 status='rejected_rear_leg_side' if n==15 else 'single_frame_reviewed_parent_review_pending'
 r.update(status='candidate_generated_not_formal',endedAt=re['returnedAt'],actualModel=None,actualQuality=None,unverifiedReason='内置宿主管理无model/quality选择器，实际型号质量未确认',candidate={'file':native.relative_to(root).as_posix(),'sha256':sha,'width':im.width,'height':im.height,'mode':im.mode,'hostPath':str(host),'hostSha256':hashlib.sha256(host.read_bytes()).hexdigest()},visualReview={'status':status,'reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'cardCount':5,'findings':note,'fullSequencePassed':False})
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows.append({'slot':f'run/SE/{n:02}','native':str(native),'host':str(host),'record':rp.relative_to(root).as_posix(),'sha256':sha,'status':status})
(root/'reviews/root-se-grounding-attempt40-handoff.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))
