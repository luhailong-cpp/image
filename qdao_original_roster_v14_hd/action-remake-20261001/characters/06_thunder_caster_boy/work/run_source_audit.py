from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
issues=[];items=[]
for d in ['E','W']:
 for p in sorted((ROOT/'runtime/run'/d).glob('*.png')):
  r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
  source=r['derivedFrom'][0];n=ROOT/source['file'];nrp=ROOT/source['generationRecord'];nr=json.loads(nrp.read_text(encoding='utf-8'))
  im=Image.open(p);nim=Image.open(n)
  errs=[]
  if sha(p)!=r['sha256']:errs.append('runtime SHA mismatch')
  if sha(n)!=source['sha256'] or sha(n)!=nr['sha256']:errs.append('native SHA mismatch')
  if im.size!=(1024,1024) or im.mode!='RGBA':errs.append('runtime format')
  if min(nim.size)<1024 or nim.mode!='RGBA':errs.append('native format')
  if nr['actualModel'] is not None or nr['actualQuality'] is not None:errs.append('host actual version/quality incorrectly claimed')
  if [Path(x).resolve() for x in nr['submittedParameters']['referenced_image_paths']]!=[Path(x['path']).resolve() for x in nr['references']]:errs.append('reference paths mismatch')
  for ref in nr['references']:
   rp=Path(ref['path'])
   if not rp.exists():errs.append('reference missing:'+str(rp))
   elif sha(rp)!=ref['sha256']:errs.append('reference SHA mismatch:'+str(rp))
  if d in ['E','W'] and r.get('cameraRegistration',{}).get('matrixNativeToRuntime')!=[[901/1254,0,61],[0,901/1254,97],[0,0,1]]:errs.append(d+' global camera matrix mismatch')
  if errs:issues.append({'file':str(p),'issues':errs})
  items.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'source':source,'nativeSize':nim.size,'mode':im.mode,'exported':True,'visualFinalPassed':False})
data={'date':'2026-10-03','scope':'E/W only','items':items,'issues':issues,'uniqueRuntimeHashes':len({x['sha256'] for x in items}),'allSourcesIndependent':len({x['source']['sha256'] for x in items})==len(items),'note':'技术来源核验不替代画面/动画验收；逐帧相位/持手/足轴另有人工记录。'}
(ROOT/'review/run_EW_source_audit_20261003.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(items),'issues':issues,'uniqueNative':data['allSourcesIndependent']},ensure_ascii=False))

