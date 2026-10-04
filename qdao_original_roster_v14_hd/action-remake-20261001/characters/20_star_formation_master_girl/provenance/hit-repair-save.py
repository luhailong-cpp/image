"""Save independent AI hit repairs; select only the explicit repaired slot."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 assert p.resolve().is_relative_to(ROOT)
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('--direction',choices=('E','W'),required=True)
p.add_argument('--frame',type=int,required=True)
p.add_argument('--version',type=int,required=True)
p.add_argument('--receipt',required=True)
p.add_argument('--review',required=True)
p.add_argument('--status',default='candidate')
a=p.parse_args()
rp=ROOT/a.receipt
r=json.loads(rp.read_text(encoding='utf-8-sig'))
t=datetime.now(ZoneInfo('America/New_York')).isoformat()
cfg=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig'))
r['recordedAt']=t;r['configSnapshot']=cfg
save(rp,r)
assert r['status']=='succeeded'
src=Path(r['hostOutput']);dest=ROOT/f'generation/hit/{a.direction}/{a.frame:02d}-v{a.version}.png'
assert not dest.exists()
shutil.copy2(src,dest)
im=Image.open(dest);im.load()
assert im.mode=='RGBA' and im.format=='PNG' and min(im.size)>=1024
alpha=im.getchannel('A')
assert alpha.getextrema()==(0,255)
meta={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'generatedAt':t,'generatedAtMeaning':'本地接收保存时间，服务端时间未披露','width':im.width,'height':im.height,'format':'PNG','mode':'RGBA','tool':'image_gen__imagegen','route':'builtin','slot':{'action':'hit','direction':a.direction,'frame':a.frame},'configSnapshot':cfg,'submittedParameters':r['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，无model/quality选择器，返回未披露；配置目标不能代表实测','prompt':r['prompt'],'promptSha256':sha(ROOT/r['prompt']),'references':[{'path':v,'role':role,'sha256':sha(Path(v))} for v,role in zip(r['submittedParameters']['referenced_image_paths'],r['referenceRoles'])],'evidence':{'receipt':a.receipt,'hostOutput':str(src),'returnedKeys':r['returnedKeys']},'review':{'status':a.status,'staticFindings':a.review,'dynamicAcceptance':False,'clientIntegration':'not_integrated'},'technicalValidation':{'nativePixelsUnmodified':True,'sourceCopySha256Matches':sha(src)==sha(dest),'alphaExtrema':[0,255],'alpha128BoundsForInspectionOnly':list(alpha.point(lambda x:255 if x>=128 else 0).getbbox())}}
sidecar=Path(str(dest)+'.generation.json');save(sidecar,meta)
sp=ROOT/('hit-W-selection.json' if a.direction=='W' else 'hit-selection.json')
sel=json.loads(sp.read_text(encoding='utf-8-sig'))
selected={'action':'hit','direction':a.direction,'frame':a.frame,'source':meta['file'],'generationRecord':sidecar.relative_to(ROOT).as_posix(),'sourceSha256':meta['sha256'],'status':a.status,'visualReview':'static_checked_candidate','dynamicReview':'not_verified'}
sel['frames']=[f for f in sel['frames'] if not(f['frame']==a.frame and f['direction']==a.direction)]+[selected]
sel['frames'].sort(key=lambda f:(f['direction'],f['frame']))
sel['dynamicAcceptance']=False
sel['dynamicReview']='not_verified_after_repair'
sel['status']='repaired_candidates_pending_sequence_review'
save(sp,sel)
print(json.dumps({'saved':meta['file'],'sha256':meta['sha256'],'size':im.size,'bounds':meta['technicalValidation']['alpha128BoundsForInspectionOnly']},ensure_ascii=False))

