from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,sys,shutil
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[1]/'tools'))
from mechanical_join import registered_join
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
O=P/'output_partial_v3';Q=P/'qa_partial_v3'
O.mkdir(exist_ok=False);Q.mkdir()
source=P/'output_partial_v2/quad-extended-context.png'
originalsource=P/'output_v1/quad-extended-context.png'
canvas=np.array(Image.open(source).convert('RGB'));before=canvas.copy()
plan=json.loads((P/'repairs/v2/plan.json').read_text())
e=next(e for e in plan['entries'] if e['id']=='internal_curved_rails')
ident=e['id'];native=P/'repairs/v2/native'/f'{ident}.png';record=native.with_suffix('.record.json');rec=json.loads(record.read_text())
assert sha(native)==rec['outputSha256']==sha(rec['sourceOutputPath'])
with Image.open(native) as im:
 im.load();assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255);rawfull=np.array(im.convert('RGB'))
x,y,_,_=e['box'];roi=[360,180,1180,1080];l,t,r,b=roi;ex,ey=x+l+115,y+t+115
raw=rawfull[t:b,l:r];h,w=raw.shape[:2]
# Reconnect against the original pre-repair pixels, so the previous registration never becomes a new guide.
context=np.array(Image.open(originalsource).convert('RGB').crop((ex,ey,ex+w,ey+h)))
yy,xx=np.indices((h,w),dtype=np.float32);d=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])
a=np.clip((d-8)/64,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
result,flow,correction,registration=registered_join(context,raw,mask,max_shift=8,flow_inner=260,flow_full=50,tone_inner=150,tone_full=60)
canvas[ey:ey+h,ex:ex+w]=result
touched=np.zeros(canvas.shape[:2],dtype=bool);touched[ey:ey+h,ex:ex+w]=mask>0
assert np.array_equal(canvas[~touched],before[~touched])
upper=next(q for q in plan['entries'] if q['id']=='internal_upper_trim');ux0,uy0,ux1,uy1=upper['box'];upperbox=(ux0+115,uy0+115,ux1+115,uy1+115)
assert np.array_equal(canvas[upperbox[1]:upperbox[3],upperbox[0]:upperbox[2]],before[upperbox[1]:upperbox[3],upperbox[0]:upperbox[2]])
del before,touched
fields=O/f'{ident}.fields.npz';np.savez_compressed(fields,flow=flow,colorCorrection=correction,mask=mask)
Image.fromarray(mask).save(Q/f'{ident}_mask.png')
Image.fromarray(rawfull).save(Q/f'{ident}_native.jpg',quality=96,subsampling=0)
ext=Image.fromarray(canvas);ext.save(O/'quad-extended-context.png')
qim=ext.crop((115,115,8307,8307));qim.save(O/'quad_8192_candidate.png')
rowsource=P/'output_partial_v2/row10-extended-context.png';row=np.array(Image.open(rowsource).convert('RGB'))
assert np.array_equal(row[:,:8422],canvas[4096:]);del canvas
shutil.copyfile(rowsource,O/rowsource.name)
rim=Image.fromarray(row).crop((115,115,16499,4211));del row
rim.save(O/'row10_16384_candidate.png')
files=[]
for rr,cc,im in [(9,cc,qim.crop(((cc-7)*4096,0,(cc-6)*4096,4096))) for cc in (7,8)]+[(10,cc,rim.crop(((cc-7)*4096,0,(cc-6)*4096,4096))) for cc in (7,8,9,10)]:
 f=O/f'r{rr:02}_c{cc:02}.png';im.save(f);files.append({'tile':f.stem,'path':str(f),'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(O/f'r10_c{cc:02}.png')) for cc in (7,8,9,10)],axis=1),np.array(rim))
assert np.array_equal(np.concatenate([np.concatenate([np.array(Image.open(O/f'r{rr:02}_c{cc:02}.png')) for cc in (7,8)],axis=1) for rr in (9,10)],axis=0),np.array(qim))
qim.crop(e['box']).save(Q/f'{ident}_reconnected.jpg',quality=96,subsampling=0)
qim.crop(e['box']).save(Q/f'{ident}_reconnected.png')
for kind,box in [('left',(l-40,t,l+120,b)),('right',(r-140,t,r+40,b)),('top',(l,t-40,r,t+120)),('bottom',(l,b-120,r,b+40))]:
 qim.crop(e['box']).crop(box).save(Q/f'{ident}_{kind}_edge.jpg',quality=96,subsampling=0)
qim.resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'quad-overview.jpg',quality=92)
prior=json.loads((P/'assembly_partial_v2.json').read_text())
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'partial_repairs_2_of_5_reconnected_v3_pending_visual_QA_and_3_native_repairs','parent':{'path':str(source),'sha256':sha(source)},'registrationContext':{'path':str(originalsource),'sha256':sha(originalsource)},'scriptSha256':sha(__file__),'files':files,'replacedPlacement':{'id':ident,'box':e['box'],'roi':roi,'priorRoi':e['roi'],'native':str(native),'nativeSha256':sha(native),'recordSha256':sha(record),'registration':registration,'fields':str(fields),'fieldsSha256':sha(fields),'mask':str(Q/f'{ident}_mask.png'),'maskSha256':sha(Q/f'{ident}_mask.png')},'inheritedUpperTrim':{'priorAssembly':str(P/'assembly_partial_v2.json'),'sha256':sha(P/'assembly_partial_v2.json'),'pixelUnchanged':True,'regenerated':False},'pendingRepairIds':prior['pendingRepairIds'],'outsideMasksUnchanged':True,'row10ExtendedContextBytesUnchanged':True,'exactTileRejoinVerified':True,'sourceArtUpscaled':False,'limitedSeamResampling':True,'runtimePublished':False,'accepted':False}
(P/'assembly_partial_v3.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'status':report['status'],'files':len(files),'pending':report['pendingRepairIds'],'flow':registration}))
