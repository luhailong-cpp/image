from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,shutil,importlib.util
from datetime import datetime,timezone
p=Path(__file__).resolve().parent;r=p/'seam_repair_v3'
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
src=Path(json.loads((r/'sources.json').read_text(encoding='utf-8'))['stairs'])
native=r/'native/stairs.png';shutil.copyfile(src,native)
assert Image.open(native).size==(1254,1254)
rec={'id':'stairs','route':'builtin_image_gen','backendModelVerified':False,'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputSha256':sha(native),'actualNativePixels':[1254,1254],'finalArtUpscaled':False,'resizedAfterGeneration':False,'promptSha256':sha(r/'prompts/stairs.prompt.txt'),'guideSha256':sha(r/'guides/stairs.png')}
(r/'native/stairs.record.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
basefile=p/'output_v2/extended-context.png'
base=np.asarray(Image.open(basefile).convert('RGB')).copy()
sourcebox=[4096,2842,5350,4096]
x,y=sourcebox[0]+115,sourcebox[1]+115
patch=np.asarray(Image.open(native).convert('RGB'))
context=base[y:y+1254,x:x+1254].copy()
assert np.array_equal(context,np.asarray(Image.open(r/'guides/stairs.png').convert('RGB')))
spec=importlib.util.spec_from_file_location('existing_assembly',p.parent/'r10_c08/assemble_builtin.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);seam=mod.load_seam_helper()
mask=np.full((1254,1254),255,np.uint8);w=230;axis=np.arange(w)[None,:]
for side in ['left','right','top']:
 if side=='left':
  path=seam(context[:,:w],patch[:,:w]);mask[:,:w]=np.minimum(mask[:,:w],np.uint8(axis>=path[:,None])*255)
 if side=='right':
  path=seam(context[:,-w:],patch[:,-w:]);mask[:,-w:]=np.minimum(mask[:,-w:],np.uint8(axis<=path[:,None])*255)
 if side=='top':
  path=seam(context[:w].transpose(1,0,2),patch[:w].transpose(1,0,2))
  mask[:w]=np.minimum(mask[:w],(np.uint8(axis>=path[:,None])*255).T)
mask=np.asarray(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(2))).copy()
mask[:2]=0;mask[:,:2]=0;mask[:,-2:]=0
blend=mod.blend_exact(context,patch,mask)
base[y:y+1254,x:x+1254]=blend
Image.fromarray(mask).save(r/'placement-mask.png')
out=p/'output_v3';qa=p/'qa_v3';out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
Image.fromarray(base).save(out/'extended-context.png')
canvas=Image.fromarray(base[115:4211,115:8307].copy())
canvas.save(out/'pair_8192x4096_candidate.png')
a=canvas.crop((0,0,4096,4096));b=canvas.crop((4096,0,8192,4096));a.save(out/'r10_c07.png');b.save(out/'r10_c08.png')
assert np.array_equal(np.concatenate([np.asarray(a),np.asarray(b)],axis=1),np.asarray(canvas))
canvas.resize((1600,800),Image.Resampling.LANCZOS).save(qa/'overview-preview.jpg',quality=75)
qaEntries=[]
boxes={'repair_context_100pct':sourcebox,'repair_left_transition_100pct':[3900,2842,4700,4096],'repair_right_transition_100pct':[4900,2842,5700,4096],'repair_top_transition_100pct':[4096,2642,5350,3142]}
for i,yy in enumerate([0,799,1598,2397,3196],1):boxes[f'cross_4k_seam_{i:02}_100pct']=[3446,yy,4746,yy+900]
for row in range(1,4):
 for col in range(1,4):
  cx,cy=4096+col*1024,row*1024
  boxes[f'r10_c08_junction_x{col*1024}_y{cy}']=[cx-450,cy-450,cx+450,cy+450]
for name,box in boxes.items():
 im=canvas.crop(box);f=qa/f'{name}.png';im.save(f);im.save(f.with_suffix('.jpg'),quality=80)
 qaEntries.append({'file':f.name,'box':box,'size':list(im.size),'scale':1,'sha256':sha(f)})
files=[{'file':str(f.relative_to(p)).replace('\\','/'),'pixels':list(Image.open(f).size),'sha256':sha(f)} for f in out.glob('*.png')]
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'parentAssembly':'assembly_v2.json','parentAssemblySha256':sha(p/'assembly_v2.json'),'newNativeRepairCount':1,'nativeRepair':rec,'placementBoxInFinal':sourcebox,'sourceResampling':False,'globalBlur':False,'colorMatching':False,'seamMaskFeatherRadiusPixels':2,'placementMaskSha256':sha(r/'placement-mask.png'),'scriptSha256':sha(Path(__file__)),'files':files,'qa':qaEntries,'tilesRejoinExactly':True,'runtimePublished':False,'wholeCityComplete':False,'visualQaPassed':False}
(p/'assembly_v3.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'qaCrops':len(qaEntries),'nativeRepairPixels':[1254,1254],'rejoinedExactly':True},indent=2))
