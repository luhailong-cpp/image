from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
import numpy as np
P=Path(__file__).resolve().parent;src=Path(sys.argv[1]);dst=P/'style-reference.png'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert not dst.exists();im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
shutil.copyfile(src,dst)
refs=[P/n for n in ('layout-input.jpg','left-style-input.jpg','bottom-style-input.jpg')]
rec={'schemaVersion':2,'role':'unified structure/style reference only; excluded from native detail counts','route':'builtin_image_gen','requestedModel':'gpt-image-2.5-sunburst','requestedQuality':'max','backendModelVerified':False,'actualModel':None,'actualQuality':None,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(dst),'outputSha256':sha(dst),'promptFile':str(P/'style-reference.prompt.txt'),'promptSha256':sha(P/'style-reference.prompt.txt'),'promptTransport':'file text with trailing newline stripped','submittedImages':[{'path':str(f),'sha256':sha(f)} for f in refs],'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':[str(f) for f in refs],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'createdAtUtc':datetime.now(timezone.utc).isoformat()}
(P/'style-reference.record.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
canvas=Image.open(dst).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
layout=json.loads((P/'layout-record.json').read_text())
for e in layout['neighborConstraints']:
 f=Path(e['source']);assert sha(f)==e['sha256'];canvas.paste(Image.open(f).crop(e['sourceBoxLTRB']),e['pasteXY'])
canvas.save(P/'guides/full-canvas-layout-only.png')
plan=json.loads((P/'plan.json').read_text());plan.update({'styleReferenceSha256':sha(dst),'status':'native_detail_generation_in_progress','worldRect':{'x':50,'z':0,'width':300,'height':300},'guidePreparation':{'status':'ready_unified_style_reference','method':'reference-only resize and exact230px neighbor constraints; output art must be generated natively','canvasPixels':[4326,4326],'guidePixelsNotDelivery':True,'neighborConstraints':layout['neighborConstraints']}})
patches=[]
for row in range(4):
 for col in range(4):
  ident=f'r{row+1:02}_c{col+1:02}';box=[col*1024,row*1024,col*1024+1254,row*1024+1254];g=P/'guides'/f'{ident}.layout-only.png';canvas.crop(box).save(g)
  prompt=f'Edit ONLY image 1, the exact square terrain detail crop. Image 2 is the complete unified layout reference for style/context only. Repaint image 1 at native resolution into crisp premium hand-painted Q/chibi Chinese fantasy game map detail. Preserve its exact camera, crop, scale, positions, every curve, slab joint, step count and relief outline; this is detail crop {ident} of a larger continuous circular ivory-stone platform. Clean rounded warm cream limestone bevels, restrained warm mineral shading, sculpted cloud-scroll and angular geometric ornamental reliefs, dark cool stair recesses, tidy soft shadows. Develop clear sharp native material detail; do not merely enlarge the reference or add busy grain. Match the warm light and line weight of image 2. Edges must remain precisely located, especially the outer 115 pixels used as neighbor overlap. Keep all existing open stone areas open. No new motifs or extra seams. One fully opaque continuous square terrain crop, no people, text, readable writing, grid, collage, frames, watermarks, transparency or blur.'
  (P/'prompts'/f'{ident}.prompt.txt').write_text(prompt,encoding='utf-8')
  patches.append({'id':ident,'row':row,'column':col,'guide':str(g),'guideSha256':sha(g),'fullCanvasBox':box,'outputFile':f'native/{ident}.png','promptFile':f'prompts/{ident}.prompt.txt','submittedImages':[str(g),str(dst)],'selectedTargetImageOneBased':1})
checks=0
for row in range(4):
 for col in range(4):
  a=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+1:02}.layout-only.png'))
  if col<3:
   b=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+2:02}.layout-only.png'));assert np.array_equal(a[:,-230:],b[:,:230]);checks+=1
  if row<3:
   b=np.array(Image.open(P/'guides'/f'r{row+2:02}_c{col+1:02}.layout-only.png'));assert np.array_equal(a[-230:],b[:230]);checks+=1
plan['patches']=patches;plan['guidePreparation'].update({'sharedOverlapChecks':checks,'allSharedOverlapPixelsIdentical':True})
(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
code=(P.parent/'r09_c08/assemble_builtin.py').read_text(encoding='utf-8').replace('r09_c08','r09_c09').replace('GPT Image 2.0 (host builtin)','gpt-image-2.5-sunburst (configured target; actual unverified)')
code=code.replace('if len(references) != 4 or record["toolCall"]["num_last_images_to_include"] != 4:', 'if len(references) != 2 or record["toolCall"]["referenced_image_paths"] != [r["path"] for r in references]:')
code=code.replace('if record["selectedTargetImageOneBased"] != column:', 'if record["selectedTargetImageOneBased"] != 1:')
(P/'assemble_builtin.py').write_text(code,encoding='utf-8')
print('16 guides ready; 24 shared overlap checks passed; structure reference excluded from detail source count')
