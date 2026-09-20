import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
R=B/'penglai_joint_c12_batch_20260917'/'audit_20260918';R.mkdir(exist_ok=True)
Q=R/'qa_lossless';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
triple=B/'penglai_day/r09_c10_c11_c12_joint/output/triple-12288x4096.png'
im=Image.open(triple).convert('RGB'); rt=im.crop((8192,0,12288,4096)); artifacts=[]
def save(crop,name,box=None):
 p=Q/name
 assert not p.exists(),p
 crop.save(p);artifacts.append({'file':str(p),'sha256':sha(p),'pixels':list(crop.size),'sourceBox':box,'lossless':True,'resized':False})
for axis in ('x','y'):
 for pos in (1024,2048,3072):
  strip=rt.crop((pos-150,0,pos+150,4096)) if axis=='x' else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
  sheet=Image.new('RGB',(1200,1024))
  for k in range(4):sheet.paste(strip.crop((0,k*1024,300,(k+1)*1024)),(k*300,0))
  save(sheet,f'internal_{axis}{pos}.png')
for y in [0,1024,2048,2842]:
 box=(7565,y,8819,y+1254);save(im.crop(box),f'boundary_y{y:04d}.png',list(box))
for y in [1024,2048,3072]:
 sheet=Image.new('RGB',(1200,400))
 for k,x in enumerate([1024,2048,3072]):sheet.paste(rt.crop((x-200,y-200,x+200,y+200)),(k*400,0))
 save(sheet,f'intersections_y{y}.png')
# Diagnose visible palette/texture transitions without changing art.
for name,box in {'boundary_water_top':(7880,2360,8700,3180),'boundary_water_bottom':(7880,3200,8700,4020),'internal_stone_joint':(10140,2940,10540,3340)}.items():save(im.crop(box),name+'.png',list(box))
checks=[]
for app in ['penglai_day','penglai_mid_autumn']:
 for p in sorted((B/app/'r09_c12/native').glob('*.record.json')):
  rec=json.loads(p.read_text(encoding='utf-8-sig'));out=Path(rec['outputFile']);src=Path(rec['sourceOutputPath'])
  assert sha(out)==rec['outputSha256']==sha(src)
  assert sha(Path(rec['promptFile']))==rec['promptSha256']
  assert sha(Path(rec['guidePath']))==rec['guideSha256']
  refs=rec.get('submittedImages',[])
  for rr in refs:assert sha(Path(rr['path']))==rr['sha256']
  pic=Image.open(out);assert pic.size==(1254,1254);assert pic.mode!='RGBA' or pic.getextrema()[3]==(255,255)
  checks.append({'record':str(p),'outputSha256':sha(out),'sourceByteIdentity':True,'promptAndRefsHashMatch':True,'pixels':list(pic.size),'opaque':True})
assembly=json.loads((triple.parent/'assembly.json').read_text(encoding='utf-8'))
for o in assembly['outputs']:
 p=triple.parent.parent/o['file'];assert sha(p)==o['sha256']
for n in range(3):
 p=triple.parent/f'penglai_day_r09_c{n+10}_4k_joint_candidate.png';assert np.array_equal(np.array(Image.open(p)),np.array(im.crop((n*4096,0,(n+1)*4096,4096))))
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceTriple':str(triple),'sourceSha256':sha(triple),'generatedNativeThisAudit':0,'sourceChecks':checks,'sourceCount':len(checks),'jointOutputHashesMatch':True,'tripleSplitPixelIdentity':True,'qaArtifacts':artifacts,'visualVerdict':'pending_review','formalAccepted':False,'runtimePublished':False}
(R/'mechanical-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'audit':str(R),'sourceCount':len(checks),'qaCount':len(artifacts)}))