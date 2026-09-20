from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,sys
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[1]/'tools'))
from mechanical_join import registered_join
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
O=P/'output_partial_v2';Q=P/'qa_partial_v2'
O.mkdir(exist_ok=False);Q.mkdir()
source=P/'output_v1/quad-extended-context.png'
canvas=np.array(Image.open(source).convert('RGB'));before=canvas.copy()
plan=json.loads((P/'repairs/v2/plan.json').read_text())
ids=('internal_curved_rails','internal_upper_trim')
reports=[];touched=np.zeros(canvas.shape[:2],dtype=bool)
for e in plan['entries']:
 if e['id'] not in ids:continue
 ident=e['id'];native=P/'repairs/v2/native'/f'{ident}.png'
 record=native.with_suffix('.record.json');rec=json.loads(record.read_text())
 assert sha(native)==rec['outputSha256']==sha(rec['sourceOutputPath'])
 with Image.open(native) as im:
  im.load();assert im.size==(1254,1254)
  assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
  rawfull=np.array(im.convert('RGB'))
 x,y,_,_=e['box'];l,t,r,b=e['roi'];ex,ey=x+l+115,y+t+115
 raw=rawfull[t:b,l:r];h,w=raw.shape[:2];context=canvas[ey:ey+h,ex:ex+w].copy()
 yy,xx=np.indices((h,w),dtype=np.float32);d=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])
 a=np.clip((d-8)/64,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
 result,flow,correction,report=registered_join(context,raw,mask,max_shift=8,flow_inner=100,flow_full=40,tone_inner=150,tone_full=60)
 canvas[ey:ey+h,ex:ex+w]=result;touched[ey:ey+h,ex:ex+w]|=mask>0
 fields=O/f'{ident}.fields.npz';np.savez_compressed(fields,flow=flow,colorCorrection=correction,mask=mask)
 Image.fromarray(rawfull).save(Q/f'{ident}_native.jpg',quality=95,subsampling=0)
 reports.append({'id':ident,'box':e['box'],'roi':e['roi'],'native':str(native),'nativeSha256':sha(native),'recordSha256':sha(record),'registration':report,'fields':str(fields),'fieldsSha256':sha(fields)})
assert np.array_equal(canvas[~touched],before[~touched]);del before,touched
ext=Image.fromarray(canvas);ext.save(O/'quad-extended-context.png')
qim=ext.crop((115,115,8307,8307));qim.save(O/'quad_8192_candidate.png')
rowsource=P/'output_v1/row10-extended-context.png';row=np.array(Image.open(rowsource).convert('RGB'))
assert np.array_equal(row[:,:8422],canvas[4096:]);del canvas
# Both available repairs affect row09 only. Preserve the row10 source byte-for-byte.
import shutil
shutil.copyfile(rowsource,O/rowsource.name)
rim=Image.fromarray(row).crop((115,115,16499,4211));del row
rim.save(O/'row10_16384_candidate.png')
files=[]
for r,c,im in [(9,c,qim.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8)]+[(10,c,rim.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8,9,10)]:
 f=O/f'r{r:02}_c{c:02}.png';im.save(f);files.append({'tile':f.stem,'path':str(f),'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(O/f'r10_c{c:02}.png')) for c in (7,8,9,10)],axis=1),np.array(rim))
assert np.array_equal(np.concatenate([np.concatenate([np.array(Image.open(O/f'r{r:02}_c{c:02}.png')) for c in (7,8)],axis=1) for r in (9,10)],axis=0),np.array(qim))
for e in plan['entries']:
 if e['id'] in ids:qim.crop(e['box']).save(Q/f"{e['id']}_reconnected.jpg",quality=96,subsampling=0)
qim.resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'quad-overview.jpg',quality=92)
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'partial_repairs_2_of_5_pending_visual_reconnection_and_3_native_repairs','parent':{'path':str(source),'sha256':sha(source)},'scriptSha256':sha(__file__),'files':files,'placements':reports,'pendingRepairIds':[e['id'] for e in plan['entries'] if e['id'] not in ids],'outsideMasksUnchanged':True,'row10ExtendedContextBytesUnchanged':True,'exactTileRejoinVerified':True,'sourceArtUpscaled':False,'limitedSeamResampling':True,'runtimePublished':False,'accepted':False}
(P/'assembly_partial_v2.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'status':report['status'],'files':len(files),'pending':report['pendingRepairIds']}))
