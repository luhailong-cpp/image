import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
A=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/penglai_joint_c12_batch_20260917/audit_20260918')
B=A.parent.parent
mode=sys.argv[1];idx=int(sys.argv[2]);src=Path(sys.argv[3]);hint=sys.argv[4]
q=json.loads((A/('day-repair-queue.json' if mode=='repair' else 'mid-autumn-resume-queue.json')).read_text(encoding='utf-8'));j=q['jobs'][idx]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if mode=='repair':
 d=A/'repairs/native';d.mkdir(parents=True,exist_ok=True);out=d/(j['id']+'.png');prompt=Path(j['promptFile']);guide=Path(j['reference']['path']);role='native_local_seam_repair'
else:
 d=B/j['appearance']/j['tile'];out=d/'native'/(j['id']+'.png');out.parent.mkdir(exist_ok=True);prompt=d/'prompts'/(j['id']+'.prompt.txt');guide=d/'guides'/(j['id']+'.layout-only.png');role='native_4K_tile_patch'
assert not out.exists(),out
im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
if mode!='repair':
 if prompt.exists():
  archive=A/'pre-path-prompt-archive';archive.mkdir(exist_ok=True);p=archive/prompt.name;assert not p.exists();shutil.copy2(prompt,p)
 prompt.write_text(j['toolArgs']['prompt'],encoding='utf-8')
shutil.copy2(src,out);assert sha(out)==sha(src)
refs=[{'path':p,'sha256':sha(Path(p))} for p in j['toolArgs']['referenced_image_paths']]
r={'schemaVersion':1,'id':j['id'],'role':role,'route':'builtin_image_gen','backendModelVerified':False,'requestedProduct':'ChatGPT Images 2.5','actualNativePixels':list(im.size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'promptFile':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':refs,'selectedTargetReferenceIndex':1,'finalArtUpscaled':False,'resizedAfterGeneration':False,'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':j['toolArgs']['referenced_image_paths'],'prompt':j['toolArgs']['prompt'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'toolOutputHint':hint,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'visualStatus':'pending_composite_review','queueFile':str(A/('day-repair-queue.json' if mode=='repair' else 'mid-autumn-resume-queue.json')),'queueIndex':idx}
if mode=='repair':r.update({'sourceCropLTRB':j['sourceCropLTRB'],'proposedPasteROIInTriple':j['proposedPasteROIInTriple']})
out.with_suffix('.record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'saved':str(out),'sha256':sha(out),'pixels':list(im.size)}))