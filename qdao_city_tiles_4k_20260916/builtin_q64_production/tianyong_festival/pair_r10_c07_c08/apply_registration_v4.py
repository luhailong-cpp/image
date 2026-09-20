from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
helper=p.parents[1]/'tools/mechanical_join.py'
spec=importlib.util.spec_from_file_location('mechanical_join',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
basefile=p/'output_v2/extended-context.png';native=p/'seam_repair_v3/native/stairs.png';maskfile=p/'seam_repair_v3/placement-mask.png'
base=np.asarray(Image.open(basefile).convert('RGB')).copy();before=base.copy()
raw=np.asarray(Image.open(native).convert('RGB'));mask=np.asarray(Image.open(maskfile).convert('L'))
x,y=4211,2957;context=base[y:y+1254,x:x+1254].copy()
joined,flow,correction,report=m.registered_join(context,raw,mask,edges=('left','right','top'))
base[y:y+1254,x:x+1254]=joined
assert np.array_equal(base[:y],before[:y])
assert np.array_equal(base[y:,:x],before[y:,:x]);assert np.array_equal(base[y:,x+1254:],before[y:,x+1254:])
out=p/'output_v4';qa=p/'qa_v4';out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
np.savez_compressed(out/'registration-fields.npz',flow=flow,colorCorrection=correction,mask=mask)
Image.fromarray(base).save(out/'extended-context.png')
canvas=Image.fromarray(base[115:4211,115:8307].copy());canvas.save(out/'pair_8192x4096_candidate.png')
a=canvas.crop((0,0,4096,4096));b=canvas.crop((4096,0,8192,4096));a.save(out/'r10_c07.png');b.save(out/'r10_c08.png')
assert np.array_equal(np.concatenate([np.asarray(a),np.asarray(b)],axis=1),np.asarray(canvas))
canvas.resize((1600,800),Image.Resampling.LANCZOS).save(qa/'overview-preview.jpg',quality=80)
boxes={'registered_stairs_100pct':[4096,2842,5350,4096],'right_transition_100pct':[4900,2842,5700,4096],'left_transition_100pct':[3900,2842,4700,4096],'top_transition_100pct':[4096,2642,5350,3142],'affected_junction_100pct':[4670,2622,5570,3522]}
for name,box in boxes.items():
 im=canvas.crop(box);im.save(qa/f'{name}.png');im.save(qa/f'{name}.jpg',quality=85)
files=[{'file':str(f.relative_to(p)).replace('\\','/'),'pixels':list(Image.open(f).size),'sha256':sha(f)} for f in out.glob('*.png')]
record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'method':'Previously generated native repair, localized subpixel geometric registration and low-frequency seam color matching; no new image generation','baseAssembly':'assembly_v2.json','baseAssemblySha256':sha(p/'assembly_v2.json'),'parentRepairAssembly':'assembly_v3.json','parentRepairAssemblySha256':sha(p/'assembly_v3.json'),'nativeRepairSource':str(native),'nativeRepairSourceSha256':sha(native),'placementBoxInFinal':[4096,2842,5350,4096],'maskSha256':sha(maskfile),'registration':report,'fieldFile':'output_v4/registration-fields.npz','fieldSha256':sha(out/'registration-fields.npz'),'helperSha256':sha(helper),'scriptSha256':sha(Path(__file__)),'files':files,'outsidePlacementUnchanged':True,'twoTilesRejoinExactly':True,'newNativeGenerationCount':0,'finalArtUpscaled':False,'sourceResampling':True,'resamplingPurpose':'Subpixel seam alignment only, unchanged dimensions','visualQaPassed':False,'wholeCityComplete':False,'runtimePublished':False}
(p/'assembly_v4.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'registration':report,'newNativeGenerationCount':0},indent=2))
