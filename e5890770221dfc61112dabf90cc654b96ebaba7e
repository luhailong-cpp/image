from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\r09_c07');src=Path(r'C:\Users\luyua\.codex\generated_images\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\exec-cc99a898-4049-486b-a92b-bd3f148eab8a.png');dst=p/'style-reference.png'
assert not dst.exists();assert Image.open(src).size==(1254,1254);shutil.copyfile(src,dst)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
refs=[p/'layout-input.jpg',p/'neighbor-style-input.jpg'];prompt=p/'style-reference.prompt.txt'
record={'route':'builtin_image_gen','role':'unified layout/style reference only, excluded from detail counts','backendModelVerified':False,'actualNativePixels':[1254,1254],'requestedPixels':[4326,4326],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(dst),'outputSha256':sha(dst),'promptSha256':sha(prompt),'submittedImages':[{'path':str(f),'sha256':sha(f)} for f in refs],'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':2},'createdAtUtc':datetime.now(timezone.utc).isoformat()}
(p/'style-reference.record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
canvas=Image.open(dst).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
neighbor=p.parent/'quad_r10_c07_c10/output_v2/extended-context.png'
canvas.paste(Image.open(neighbor).convert('RGB').crop((0,0,4326,230)),(0,4096))
canvas.save(p/'guides/full-canvas-layout-only.png')
plan=json.loads((p/'plan.json').read_text());plan['styleReferenceSha256']=sha(dst);plan['status']='reference_ready_native_detail_production_in_progress'
plan['guidePreparation']={'status':'ready_unified_style_reference','canvasPixels':[4326,4326],'method':'Reference-only1254to4326 resize with exact230px native below-tile overlap, then regenerate each1254patch natively','guidePixelsNotDelivery':True,'bottomOverlapSource':str(neighbor),'bottomOverlapSourceSha256':sha(neighbor),'bottomOverlapSourceBox':[0,0,4326,230],'bottomPasteXY':[0,4096]}
patches=[]
for row in range(4):
 for col in range(4):
  ident=f'r{row+1:02}_c{col+1:02}';box=[col*1024,row*1024,col*1024+1254,row*1024+1254];g=p/'guides'/f'{ident}.layout-only.png';cut=canvas.crop(box);cut.save(g);cut.save(p/'guides'/f'{ident}.input-preview.jpg',quality=80)
  patches.append({'id':ident,'row':row,'column':col,'guide':str(g),'guideSha256':sha(g),'fullCanvasBox':box,'outputFile':f'native/{ident}.png','promptFile':f'prompts/{ident}.prompt.txt'})
checks=0
for row in range(4):
 for col in range(4):
  a=np.array(Image.open(p/'guides'/f'r{row+1:02}_c{col+1:02}.layout-only.png'))
  if col<3:
   b=np.array(Image.open(p/'guides'/f'r{row+1:02}_c{col+2:02}.layout-only.png'));assert np.array_equal(a[:,-230:],b[:,:230]);checks+=1
  if row<3:
   b=np.array(Image.open(p/'guides'/f'r{row+2:02}_c{col+1:02}.layout-only.png'));assert np.array_equal(a[-230:],b[:230]);checks+=1
plan['patches']=patches;plan['guidePreparation']['sharedOverlapChecks']=checks;plan['guidePreparation']['allSharedOverlapPixelsIdentical']=True
(p/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print('Mother retained;16 reference-only guides ready;24 overlap identity checks passed.')
