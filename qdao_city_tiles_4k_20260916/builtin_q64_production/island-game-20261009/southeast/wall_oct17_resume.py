import os,sys
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
from PIL import ImageFilter
if sys.argv[1]=='recover':
 rows=[]
 for key in ['v24_v01','h42_v01']:
  stem='r10_c10_ov_'+key; f=ROOT/'native'/f'{stem}.png'; rec=read(Path(str(f)+'.generation.json'))
  assert sha(f)==rec['sha256'] and Image.open(f).size==(1254,1254)
  receipt=read(Path(rec['receipt'])); src=Path(receipt['sourceFile'])
  assert sha(f)==receipt['copiedNativeSha256']==receipt['sourceSha256']
  if src.exists():assert sha(src)==sha(f)
  q=ROOT/'qa'/'wall-oct16'/stem/'review.json'; d=read(q)
  assert sha(Path(d['candidate']))==d['candidateSha256']
  for e in d['entries']:assert sha(Path(e['file']))==e['sha256']
  d.update(reviewedAt=now(),reviewer='wall_oct17',status='passed_local_repair' if key=='v24_v01' else 'not_passed')
  d['note']='Post corner and inset frame now continuous. All four actual replacement edges viewed: no new geometry breaks; existing h33 paving issue outside repair remains.' if key=='v24_v01' else 'Main h42 paving endpoint repaired, but upper partial stone boundaries stop inside the replacement at native y~230. Four outside edges connect; v33/top interior remains NOTpassed. One further local repair permitted.'
  for e in d['entries']:e['status']='passed_actual_native_visual' if key=='v24_v01' or e['kind'] in ['left','right','bottom'] else 'not_passed_inner_upper_paving_endpoint'
  write(q,d);rows.append({'source':str(f),'sha256':sha(f),'dimensions':[1254,1254],'status':d['status'],'review':str(q)})
 write(ROOT/'qa'/'wall-oct16'/'restart-recovery-wall-oct17.json',{'checkedAt':now(),'recoveredSavedSources':rows,'noRepeatedGeneration':True,'pendingRequests':[],'formalAccepted':False})
 print(json.dumps(rows))
elif sys.argv[1]=='prepare':
 stem='r10_c10_ov_h42_v02'; old=read(ROOT/'prompts'/'r10_c10_ov_h42_v01.overlay.json')
 f=ROOT/'native'/'r10_c10_ov_h42_v01.png'; guide=ROOT/'guides'/f'{stem}.png'; assert not guide.exists()
 im=Image.open(f).convert('RGB'); im.save(guide)
 old.update(key='h42_v02',guide=str(guide),guideSha256=sha(guide),guideMask=None,repairInput=str(f),repairInputSha256=sha(f))
 write(ROOT/'prompts'/f'{stem}.overlay.json',old)
 prompt='Use case: precise-object-edit. Output exactly1254x1254 opaque pixels. Image1 is the exact crop to correct. Keep camera, all four outer115px strips, and the lower two-thirds completely fixed. Repair ONLY the upper central paving region around x300..1050,y160..430: two stone slab joints currently end in the middle of unbroken stone at y230, making an impossible cut-off slab. Complete their natural diagonal outlines into a consistent interlocking slab pattern. Keep the existing perspective, stone scale, and pale blue-grey hand-painted shading; every stone joint must connect to another joint or continue out of the image, never stop abruptly in the middle of a stone. Preserve all clear existing joints around the sides and bottom. Do not introduce new large objects, lines crossing over stone faces, changed stone scale, new framing, text, labels, UI, people or watermark. Native crisp painterly Q Daoist game-art close-up, no blur and no enlargement.'
 args={'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False}
 write(ROOT/'prompts'/f'{stem}.args.json',args);write(ROOT/'prompts'/f'{stem}.request.json',{'submittedArguments':args,'actualModel':None,'actualQuality':None,'guideProvenance':old})
 print(guide)
