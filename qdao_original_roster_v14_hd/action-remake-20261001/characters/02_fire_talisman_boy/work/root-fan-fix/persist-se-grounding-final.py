import json,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2];dest=root/'work/root-ground-fix';dest.mkdir(exist_ok=True)
rows=[]
for n,a in [(1,40),(9,40),(15,41)]:
 id=f'run-SE-{n:02}-20261003-attempt-{a}';rp=root/'records'/f'{id}.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));receipt=root/'records'/f'{id}.receipt.json';re=json.loads(receipt.read_text(encoding='utf-8-sig'));host=Path(re['nativePath']);native=dest/f'{id}-native.png';shutil.copyfile(host,native);im=Image.open(native);sha=hashlib.sha256(native.read_bytes()).hexdigest()
 note='五卡/右扇左铃及两袖连续；前右腿屏左下鞋底基本平、后左腿屏右折起。01为16落平后的同脚支撑延续，避免再露宽棕底假落地。' if n==1 else '五卡/右扇左铃及两袖连续；前左腿屏右下鞋底基本平、后右腿屏左折起。09为08落平后的同脚支撑延续，保留膝踝承重。' if n==9 else '五卡/正确持手保持，前右脚屏左下基本平，后左腿已修回屏右折起；共两腿两鞋，初触形态与16同腿支撑相接。'
 status='single_frame_reviewed_parent_review_pending'
 r.update(status='candidate_generated_not_formal',endedAt=re['returnedAt'],actualModel=None,actualQuality=None,unverifiedReason='内置宿主管理无model/quality选择器，实际型号质量未确认',candidate={'file':native.relative_to(root).as_posix(),'sha256':sha,'width':im.width,'height':im.height,'mode':im.mode,'hostPath':str(host),'hostSha256':hashlib.sha256(host.read_bytes()).hexdigest()},visualReview={'status':status,'reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'cardCount':5,'findings':note,'fullSequencePassed':False})
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows.append({'slot':f'run/SE/{n:02}','native':str(native),'host':str(host),'record':rp.relative_to(root).as_posix(),'sha256':sha,'status':status})
previous=json.loads((root/'reviews/root-se-grounding-attempt40-handoff.json').read_text(encoding='utf-8'))
accepted=[r for r in previous if not r['slot'].endswith('/15')]+rows
accepted.sort(key=lambda x:x['slot'])
out={'readyForRootImport':accepted,'rejectedDoNotImport':[r for r in previous if r['slot'].endswith('/15')],'normalRunMs':1200,'frameMs':75,'fullSequencePassed':False,'notes':'只生成候选，未改inventory-root或正式SE图；前脚上鞋面与金侧缘可读，鞋长轴沿SE，单后腿悬空。01/09追加同脚支撑续帧避免二次假落地。实际内置型号质量未确认。'}
(root/'reviews/root-se-grounding-final-handoff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sheet=Image.new('RGB',(1800,600),'#263142');draw=ImageDraw.Draw(sheet)
for i,(n,a) in enumerate([(7,40),(8,40),(9,40),(15,41),(16,40),(1,40)]):
 p=dest/f'run-SE-{n:02}-20261003-attempt-{a}-native.png';im=Image.open(p).convert('RGBA');im=im.resize((300,300),Image.Resampling.LANCZOS);sheet.paste(im,(i*300,0),im);draw.text((i*300+8,305),f'SE{n:02} attempt{a} / native1254',fill='white')
 with Image.open(p) as original:
  crop=original.crop((0,700,1254,1254));crop.thumbnail((300,260));sheet.paste(crop,(i*300,335),crop)
sheet.save(dest/'grounding-six-candidates.jpg',quality=96)
print(json.dumps(accepted,ensure_ascii=False))
