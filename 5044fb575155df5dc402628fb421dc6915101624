from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parents[1]/'tools'))
from mechanical_join import registered_join
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
out=p/'output_v2';qa=p/'qa_v2'
out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
source=p/'output/extended-context.png'
canvas=np.array(Image.open(source).convert('RGB'));before=canvas.copy()
r=p/'repairs/v2'
placements={'boundary_lower':{'box':(11661,2048,12915,3302),'roi':(350,630,1030,1254)},'stairs_boundary':{'box':(11661,2842,12915,4096),'roi':(330,0,1040,1254)}}
touched=np.zeros(canvas.shape[:2],bool);reports=[]
for ident,e in placements.items():
    x,y,_,_=e['box'];l,t,rr,b=e['roi'];ex,ey=x+l+115,y+t+115
    raw=np.array(Image.open(r/'native'/f'{ident}.png').convert('RGB'))[t:b,l:rr]
    h,w=raw.shape[:2];context=canvas[ey:ey+h,ex:ex+w].copy()
    yy,xx=np.indices((h,w),dtype=np.float32);d=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])
    a=np.clip((d-8)/64,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
    result,flow,correction,report=registered_join(context,raw,mask,max_shift=8,flow_inner=100,flow_full=40,tone_inner=150,tone_full=60)
    canvas[ey:ey+h,ex:ex+w]=result;touched[ey:ey+h,ex:ex+w]|=mask>0
    np.savez_compressed(out/f'{ident}.fields.npz',flow=flow,colorCorrection=correction,mask=mask)
    reports.append({'id':ident,**e,'nativeSha256':sha(r/'native'/f'{ident}.png'),'recordSha256':sha(r/'native'/f'{ident}.record.json'),'registration':report,'fieldsSha256':sha(out/f'{ident}.fields.npz')})
    Image.fromarray(result).save(qa/f'{ident}_roi_100pct.png')
    Image.fromarray(result).save(qa/f'{ident}_roi_100pct.jpg',quality=90)
assert np.array_equal(canvas[~touched],before[~touched])
ext=Image.fromarray(canvas);ext.save(out/'extended-context.png')
im=ext.crop((115,115,16499,4211));im.save(out/'quad_16384x4096_candidate.png')
files=[]
for i,c in enumerate((7,8,9,10)):
    f=out/f'r10_c{c:02}.png';im.crop((i*4096,0,(i+1)*4096,4096)).save(f)
    files.append({'file':str(f.relative_to(p)),'pixels':[4096,4096],'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r10_c{c:02}.png')) for c in (7,8,9,10)],axis=1),np.array(im))
for ident,e in placements.items():
    crop=im.crop(e['box']);crop.save(qa/f'{ident}_context.png');crop.save(qa/f'{ident}_context.jpg',quality=87)
im.resize((2000,500),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=87)
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'targeted_fixes_assembled_pending_visual_review','parent':{'path':str(source),'sha256':sha(source)},'scriptSha256':sha(Path(__file__)),'mechanicalHelperSha256':sha(p.parents[1]/'tools/mechanical_join.py'),'pixels':[16384,4096],'files':files,'combinedSha256':sha(out/'quad_16384x4096_candidate.png'),'extendedSha256':sha(out/'extended-context.png'),'newNativeRepairs':2,'sourceArtUpscaled':False,'limitedSeamResampling':True,'pixelsOutsideMasksUnchanged':True,'exactTileRejoinVerified':True,'placements':reports,'runtimePublished':False,'acceptedProductionTiles':0}
(p/'assembly_v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'outsideMaskPixelsUnchanged':True},ensure_ascii=False))
