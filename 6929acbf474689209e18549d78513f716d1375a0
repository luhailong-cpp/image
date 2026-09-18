from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parents[1]/'tools'))
from mechanical_join import registered_join
out=p/'output_v2';qa=p/'qa_v2'
out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=p/'output/extended-context.png'
canvas=np.array(Image.open(source).convert('RGB'));before=canvas.copy()
r=p/'repairs/v2'
plan=json.loads((r/'plan.json').read_text(encoding='utf-8'))
placements={e['id']:e['box'] for e in plan['inputs']}
selected=['boundary_top','boundary_middle','stairs_boundary','stairs_internal1','stairs_internal2','stairs_internal3']
reports=[];touched=np.zeros(canvas.shape[:2],bool)
yy,xx=np.indices((1254,1254),dtype=np.float32)
for ident in selected:
    x,y,_,_=placements[ident];ex,ey=x+115,y+115
    context=canvas[ey:ey+1254,ex:ex+1254].copy()
    raw=np.array(Image.open(r/'native'/f'{ident}.png').convert('RGB'))
    edges=['left','right']
    if y>0:edges.append('top')
    if y+1254<4096:edges.append('bottom')
    distances=[xx,1253-xx]
    if 'top' in edges:distances.append(yy)
    if 'bottom' in edges:distances.append(1253-yy)
    d=np.minimum.reduce(distances)
    a=np.clip((d-16)/164,0,1);mask=np.rint((a*a*(3-2*a))*255).astype(np.uint8)
    result,flow,correction,report=registered_join(context,raw,mask,edges=tuple(edges),max_shift=8,flow_inner=270,flow_full=110,tone_inner=300,tone_full=130)
    canvas[ey:ey+1254,ex:ex+1254]=result
    touched[ey:ey+1254,ex:ex+1254]|=mask>0
    np.savez_compressed(out/f'{ident}.fields.npz',flow=flow,colorCorrection=correction,mask=mask)
    Image.fromarray(result).save(qa/f'{ident}_placed.png')
    Image.fromarray(result).save(qa/f'{ident}_placed.jpg',quality=87)
    reports.append({'id':ident,'finalPixelBox':placements[ident],'nativeSha256':sha(r/'native'/f'{ident}.png'),'recordSha256':sha(r/'native'/f'{ident}.record.json'),'registration':report,'fieldsSha256':sha(out/f'{ident}.fields.npz')})
assert np.array_equal(canvas[~touched],before[~touched])
ext=Image.fromarray(canvas);ext.save(out/'extended-context.png')
im=ext.crop((115,115,12403,4211));im.save(out/'triple_12288x4096_candidate.png')
files=[]
for i,c in enumerate((7,8,9)):
    f=out/f'r10_c{c:02}.png';im.crop((4096*i,0,4096*(i+1),4096)).save(f)
    files.append({'file':str(f.relative_to(p)),'pixels':[4096,4096],'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r10_c{c:02}.png')) for c in (7,8,9)],axis=1),np.array(im))
im.resize((1800,600),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=87)
im.crop((7500,2750,12288,4096)).resize((1600,450),Image.Resampling.LANCZOS).save(qa/'stairs_strip_preview.jpg',quality=87)
for i,x in enumerate((8192,9216,10240,11264)):
    box=(x-627,2842,x+627,4096);im.crop(box).save(qa/f'stairs_{i}_100pct.jpg',quality=87)
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'targeted_repairs_assembled_pending_visual_review','parent':{'path':str(source),'sha256':sha(source)},'scriptSha256':sha(Path(__file__)),'mechanicalHelperSha256':sha(p.parents[1]/'tools/mechanical_join.py'),'pixels':[12288,4096],'extendedPixels':[12518,4326],'files':files,'combinedSha256':sha(out/'triple_12288x4096_candidate.png'),'extendedSha256':sha(out/'extended-context.png'),'retainedNativeRepairGenerations':7,'selectedNativeRepairs':6,'rejectedNativeRepairs':['boundary_lower'],'sourceArtUpscaled':False,'limitedSeamResampling':True,'pixelsOutsideMasksUnchanged':True,'exactTileRejoinVerified':True,'placements':reports,'runtimePublished':False,'acceptedProductionTiles':0}
(p/'assembly_v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'selectedRepairs':6,'rejectedRepairs':1,'outsideMasksUnchanged':True},ensure_ascii=False))
