import json,hashlib,shutil,sys,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
for batch in R.glob('provenance/north-bamboo-batch*-receipts.json'):
 for rc in json.loads(batch.read_text(encoding='utf-8')):
  q=rc['q']; ident=q['id']; src=Path(rc['path']); dest=R/'run/staging'/f'{ident}.png'
  if not src.exists(): raise ValueError(src)
  if not dest.exists(): shutil.copy2(src,dest)
  recp=Path(str(dest)+'.generation.json')
  if recp.exists(): continue
  im=Image.open(dest)
  refs=[{'path':p,'sha256':sha(p),'role': ['registered edit target and identity','bamboo movement-only reference','approved style'][i]} for i,p in enumerate(q['params']['referenced_image_paths'])]
  rec={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'generatedAt':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host source file mtime; tool did not disclose time','recordedAt':now(),'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','configSnapshot':config,'submittedParameters':q['params'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in host exposes neither model nor quality selectors or returned values','evidence':{'toolReturnedPath':str(src),'outputHint':rc['hint'],'returnedFields':['image_url','output_hint'],'workspaceCopyShaMatchesSource':sha(src)==sha(dest)},'references':refs,'request':'provenance/'+ident+'.request.json','review':{'status':'pending_visual_review'}}
  recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
selection=R/'provenance/north-bamboo-selection.json'
if '--export' in sys.argv:
 spec=importlib.util.spec_from_file_location('export_frame',R/'tools/export_frame.py'); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for item in json.loads(selection.read_text(encoding='utf-8')):
  ident=item['id'];src=R/'run/staging'/f'{ident}.png'; dest=R/'run'/item['direction']/f"{item['frame']}.png"
  prior=sha(dest);source_rec=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8'))
  mod.run(src,dest)
  rp=Path(str(dest)+'.generation.json');rec=json.loads(rp.read_text(encoding='utf-8'))
  rec['operation']['type']='direct_registered_canvas_redraw'
  rec['operation']['inputRegistration']='Edit target already at character scale 0.8; only full-canvas resolution downsample performed'
  rec['registrationTransform']={'method':'direct_registered_canvas_redraw','globalScale':1.0,'inheritedCharacterScale':0.8,'sourceRoot':[512,942],'targetRoot':[512,942],'outputSha256':sha(dest),'inputRegisteredReferenceSha256':source_rec['references'][0]['sha256'],'noSecondScale':True}
  rec['review']={'status':'visual_pass','notes':item['review']}
  rec['actualModel']=None;rec['actualQuality']=None
  rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
  source_rec['review']={'status':'selected_final','finalDerivative':dest.relative_to(R).as_posix(),'notes':item['review']}
  Path(str(src)+'.generation.json').write_text(json.dumps(source_rec,ensure_ascii=False,indent=2),encoding='utf-8')
print('Records saved; export='+str('--export' in sys.argv))

