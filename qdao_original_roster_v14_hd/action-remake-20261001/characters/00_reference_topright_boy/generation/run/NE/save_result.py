from pathlib import Path
import sys,json,hashlib,shutil,datetime
from PIL import Image
root=Path(__file__).resolve().parent
slot=sys.argv[1]
source=Path(sys.argv[2])
dest=root/(slot+'.png')
req=json.loads((root/(slot+'.request.json')).read_text(encoding='utf-8-sig'))
receipt=root/(slot+'.tool-result.json')
if dest.exists(): raise RuntimeError('Refusing to overwrite existing PNG')
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(source,dest)
im=Image.open(dest)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[{'path':p,'sha256':sha(Path(p)),'role':('edit/primary scale target' if i==0 else 'supporting reference; see actual prompt')} for i,p in enumerate(req['submittedParameters']['referenced_image_paths'])]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
record={'schemaVersion':1,'file':str(dest).replace('\\','/'),'slot':slot,'sha256':sha(dest),'generatedAt':now,'generatedAtEvidence':'Observed copy time in UTC; provider generation timestamp not returned','recordedAt':now,'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号/质量；无model/quality选择器，配置目标不能代替实测。','evidence':{'toolResultRecord':str(receipt).replace('\\','/'),'toolOutputPath':str(source),'copyOperation':'Byte-for-byte shutil.copyfile; no image processing','copiedSourceShaMatches':sha(source)==sha(dest)},'prompt':str(root/(slot+'.prompt.txt')).replace('\\','/'),'references':refs,'review':{'status':'new_candidate_pending_visual_review','runtimeReady':False},'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None}
(root/(slot+'.png.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':record['sha256'],'nativeSize':[im.width,im.height],'mode':im.mode},ensure_ascii=False))
