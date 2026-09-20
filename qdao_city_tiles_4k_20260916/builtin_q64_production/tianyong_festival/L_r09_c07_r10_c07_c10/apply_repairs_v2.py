from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parents[1]/'tools'))
from mechanical_join import registered_join
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
out=p/'output_v2';qa=p/'qa_v2';out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True)
source=p/'output/vertical-extended-context.png';canvas=np.array(Image.open(source).convert('RGB'));before=canvas.copy();r=p/'repairs/v2'
placements={'tree_boundary':{'box':(0,3469,1254,4723),'roi':(0,400,550,1000),'edges':('right','top','bottom')},'floor_boundary':{'box':(1200,3270,2454,4524),'roi':(350,180,1254,1050),'edges':('left','right','top','bottom')},'upper_stone_joints':{'box':(1450,200,2704,1454),'roi':(330,350,1150,1030),'edges':('left','right','top','bottom')}}
touched=np.zeros(canvas.shape[:2],bool);reports=[]
for ident,e in placements.items():
 x,y,_,_=e['box'];l,t,rr,b=e['roi'];ex,ey=x+l+115,y+t+115
 raw=np.array(Image.open(r/'native'/f'{ident}.png').convert('RGB'))[t:b,l:rr];h,w=raw.shape[:2];context=canvas[ey:ey+h,ex:ex+w].copy()
 yy,xx=np.indices((h,w),dtype=np.float32);ds={'left':xx,'right':w-1-xx,'top':yy,'bottom':h-1-yy};d=np.minimum.reduce([ds[k] for k in e['edges']]);a=np.clip((d-8)/64,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
 result,flow,correction,report=registered_join(context,raw,mask,edges=e['edges'],max_shift=8,flow_inner=100,flow_full=40,tone_inner=150,tone_full=60)
 canvas[ey:ey+h,ex:ex+w]=result;touched[ey:ey+h,ex:ex+w]|=mask>0
 np.savez_compressed(out/f'{ident}.fields.npz',flow=flow,colorCorrection=correction,mask=mask)
 reports.append({'id':ident,**e,'nativeSha256':sha(r/'native'/f'{ident}.png'),'recordSha256':sha(r/'native'/f'{ident}.record.json'),'registration':report,'fieldsSha256':sha(out/f'{ident}.fields.npz')})
assert np.array_equal(canvas[~touched],before[~touched])
ext=Image.fromarray(canvas);ext.save(out/'vertical-extended-context.png');vertical=ext.crop((115,115,4211,8307));vertical.save(out/'pair_4096x8192_candidate.png')
quadsource=p/'output/row10-extended-context.png';quad=np.array(Image.open(quadsource).convert('RGB'));quad[:,:4326]=canvas[4096:];qe=Image.fromarray(quad);qe.save(out/'row10-extended-context.png');row=qe.crop((115,115,16499,4211));row.save(out/'row10_16384x4096_candidate.png')
files=[]
for ident,im in [('r09_c07',vertical.crop((0,0,4096,4096)))]+[(f'r10_c{c:02}',row.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8,9,10)]:
 f=out/f'{ident}.png';im.save(f);files.append({'tile':ident,'file':str(f.relative_to(p)),'pixels':[4096,4096],'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r{r:02}_c07.png')) for r in (9,10)],axis=0),np.array(vertical))
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r10_c{c:02}.png')) for c in (7,8,9,10)],axis=1),np.array(row))
for ident,e in placements.items(): vertical.crop(e['box']).save(qa/f'{ident}_context.jpg',quality=87)
vertical.resize((750,1500),Image.Resampling.LANCZOS).save(qa/'vertical-overview.jpg',quality=87)
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'targeted_fixes_assembled_pending_visual_review','parent':{'path':str(source),'sha256':sha(source)},'scriptSha256':sha(Path(__file__)),'mechanicalHelperSha256':sha(p.parents[1]/'tools/mechanical_join.py'),'files':files,'newNativeRepairs':3,'sourceArtUpscaled':False,'limitedSeamResampling':True,'pixelsOutsideMasksUnchanged':True,'exactTileRejoinVerified':True,'placements':reports,'runtimePublished':False,'acceptedProductionTiles':0}
(p/'assembly_v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':files,'outsideMaskPixelsUnchanged':True},ensure_ascii=False))
