"""Reference-only 4x4 guide preparation. Generated reference is not final art."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil,sys
import numpy as np
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path(sys.argv[1]);dst=P/'references/style-reference.png'
assert not dst.exists(), 'Do not overwrite any source'
im=Image.open(src);assert im.size==(1254,1254)
shutil.copyfile(src,dst)
refs=[P/'references'/n for n in ('layout-input.jpg','bottom-style-input.jpg','left-style-reference.jpg')]
prompt=P/'prompts/style-reference.prompt.txt'
record={'schemaVersion':2,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'role':'Unified structure/style reference only, excluded from native detail source counts.','route':'builtin_image_gen','requestedModel':'gpt-image-2.5-sunburst','requestedQuality':'max','backendModelVerified':False,'actualModel':None,'actualQuality':None,'actualNativePixels':list(im.size),'outputBytes':src.stat().st_size,'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(dst),'outputSha256':sha(dst),'promptFile':str(prompt),'promptSha256':sha(prompt),'promptTransport':'File contents with trailing newline stripped','submittedImages':[{'path':str(r),'sha256':sha(r)} for r in refs],'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':[str(r) for r in refs],'modelSelectorAvailable':False,'qualitySelectorAvailable':False}}
(P/'references/style-reference.record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
canvas=im.convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
layout=json.loads((P/'layout-record.json').read_text())
for e in layout['neighborConstraints']:
 f=Path(e['source']);assert sha(f)==e['sha256'];canvas.paste(Image.open(f).convert('RGB').crop(e['sourceBoxLTRB']),e['pasteXY'])
canvas.save(P/'guides/full-canvas-layout-only.png')
plan=json.loads((P/'plan.json').read_text());plan['status']='native_detail_generation_in_progress_left_neighbor_pending';plan['styleReference']=str(dst);plan['styleReferenceSha256']=sha(dst)
patches=[]
for row in range(4):
 for col in range(4):
  ident=f'r{row+1:02}_c{col+1:02}';box=[col*1024,row*1024,col*1024+1254,row*1024+1254];g=P/'guides'/f'{ident}.layout-only.png';canvas.crop(box).save(g)
  prompt=f'Use case: precise-object-edit. Edit ONLY image 1, the exact square terrain detail crop. Image 2 is the complete unified layout reference for style/context only. Repaint image 1 at native resolution into crisp premium hand-painted Q/chibi Chinese fantasy game map detail. Preserve its exact camera, crop, scale, positions, every curve, paving joint, step count, leaf edge and carved relief outline; this is native detail crop {ident} of Tianyong city tile r09_c10, part of a larger continuous circular ivory-stone plaza. Clean rounded warm cream limestone bevels, restrained smooth mineral shading, sculpted cloud reliefs where already present, cool gray recesses, tidy soft shadows. Develop clear sharp native material detail; do not merely enlarge the reference or add grain. Match the warm light and line weight of image 2. Edges must remain precisely located, especially the outer 115 pixels used as neighbor overlap. Keep all existing open stone areas open. No new motifs, extra paving joints or objects. One fully opaque continuous square terrain crop, no people, text, writing, grid, collage, frames, watermark, transparency or blur.'
  pr=P/'prompts'/f'{ident}.prompt.txt';pr.write_text(prompt,encoding='utf-8')
  patches.append({'id':ident,'row':row,'column':col,'guide':str(g),'guideSha256':sha(g),'fullCanvasBox':box,'outputFile':f'native/{ident}.png','promptFile':str(pr),'submittedImages':[str(g),str(dst)],'selectedTargetImageOneBased':1,'status':'pending','boundaryReady':col!=0})
checks=0
for row in range(4):
 for col in range(4):
  a=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+1:02}.layout-only.png'))
  if col<3:
   b=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+2:02}.layout-only.png'));assert np.array_equal(a[:,-230:],b[:,:230]);checks+=1
  if row<3:
   b=np.array(Image.open(P/'guides'/f'r{row+2:02}_c{col+1:02}.layout-only.png'));assert np.array_equal(a[-230:],b[:230]);checks+=1
plan['patches']=patches;plan['guidePreparation']={'sharedOverlapChecks':checks,'allSharedOverlapPixelsIdentical':True,'resizedReferencesNotDelivery':True,'pendingLeftNeighbor':True};(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'guideCount':len(patches),'sharedOverlapChecks':checks,'status':plan['status'],'referenceSha256':sha(dst)}))
