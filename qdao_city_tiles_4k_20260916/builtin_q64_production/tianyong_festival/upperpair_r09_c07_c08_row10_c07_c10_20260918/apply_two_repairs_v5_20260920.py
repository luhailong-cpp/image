from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys,numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[1]/'tools'))
from mechanical_join import registered_join
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
O=P/'output_v5'; Q=P/'qa_v5'; O.mkdir(exist_ok=False);Q.mkdir(exist_ok=False)
source=P/'output_v4/quad-extended-context.png'
canvas=np.array(Image.open(source).convert('RGB')); before=canvas.copy(); touched=np.zeros(canvas.shape[:2],bool)
placements=[]
for ident,box,roi in [('left_lower_bevel',[3469,2760,4723,4014],[110,790,510,1195]),('left_upper_bevel',[3466,2388,4720,3642],[417,417,837,837])]:
    native=P/f'repairs/v5_20260920/native/{ident}.png';rf=native.with_suffix('.record.json');rec=json.loads(rf.read_text())
    assert sha(native)==rec['outputSha256']==sha(rec['sourceOutputPath'])
    assert sha(rec['promptFile'])==rec['promptSha256']
    assert all(sha(e['path'])==e['sha256'] for e in rec['submittedImages'])
    im=Image.open(native);assert im.size==(1254,1254) and im.convert('RGBA').getextrema()[3]==(255,255)
    l,t,r,b=roi;x,y=box[:2];ex,ey=x+l+115,y+t+115
    patch=np.array(im.convert('RGB'))[t:b,l:r];h,w=patch.shape[:2];context=canvas[ey:ey+h,ex:ex+w].copy()
    yy,xx=np.indices((h,w),dtype=np.float32);d=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy]);a=np.clip((d-8)/64,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
    result,flow,tone,report=registered_join(context,patch,mask,max_shift=8,flow_inner=100,flow_full=40,tone_inner=150,tone_full=60)
    canvas[ey:ey+h,ex:ex+w]=result;touched[ey:ey+h,ex:ex+w]|=mask>0
    fields=O/f'{ident}.fields.npz';np.savez_compressed(fields,flow=flow,colorCorrection=tone,mask=mask)
    placements.append({'id':ident,'box':box,'roi':roi,'native':str(native),'nativeSha256':sha(native),'record':str(rf),'recordSha256':sha(rf),'fields':str(fields),'fieldsSha256':sha(fields),'registration':report})
assert np.array_equal(canvas[~touched],before[~touched]);del before,touched
Image.fromarray(canvas).save(O/'quad-extended-context.png')
quad=Image.fromarray(canvas[115:8307,115:8307]);quad.save(O/'quad_8192_candidate.png')
row=np.array(Image.open(P/'output_v4/row10-extended-context.png').convert('RGB'));old_far=row[:,8422:].copy();row[:,:8422]=canvas[4096:]
assert np.array_equal(row[:,8422:],old_far);del canvas,old_far
Image.fromarray(row).save(O/'row10-extended-context.png');rim=Image.fromarray(row[115:4211,115:16499]);rim.save(O/'row10_16384_candidate.png');del row
files=[]
for rr,cs,im in [(9,(7,8),quad),(10,(7,8,9,10),rim)]:
    for c in cs:
        f=O/f'r{rr:02}_c{c:02}.png';im.crop(((c-7)*4096,0,(c-6)*4096,4096)).save(f);files.append({'tile':f.stem,'path':str(f),'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(O/f'r10_c{c:02}.png')) for c in (7,8,9,10)],1),np.array(rim))
assert np.array_equal(np.concatenate([np.concatenate([np.array(Image.open(O/f'r{r:02}_c{c:02}.png')) for c in (7,8)],1) for r in (9,10)],0),np.array(quad))
qa=[]
def save(name,im,box=None):
    f=Q/f'{name}.png';im.save(f);qa.append({'file':str(f),'sha256':sha(f),'box':box})
def board(name,strip):
    im=Image.new('RGB',(1280,1024))
    for i in range(4):im.paste(strip.crop((0,i*1024,320,(i+1)*1024)),(i*320,0))
    save(name,im)
tile=quad.crop((4096,0,8192,4096))
for axis in ('v','h'):
    for pos in (1024,2048,3072):
        strip=tile.crop((pos-160,0,pos+160,4096)) if axis=='v' else tile.crop((0,pos-160,4096,pos+160)).transpose(Image.Transpose.ROTATE_90)
        board(f'internal_{axis}{pos}',strip)
for axis in ('v','h'):
    strip=quad.crop((3936,0,4256,8192)) if axis=='v' else quad.crop((0,3936,8192,4256)).transpose(Image.Transpose.ROTATE_90)
    for half in (0,1):board(f'quad_boundary_{axis}_half{half+1}',strip.crop((0,half*4096,320,(half+1)*4096)))
for c in (1,2,3):board(f'row10_boundary_c{c+7:02}',rim.crop((c*4096-160,0,c*4096+160,4096)))
save('four-tile-junction',quad.crop((3584,3584,4608,4608)))
for e in placements:
    ident=e['id'];save(ident+'_reconnected',quad.crop(e['box']),e['box']);x,y=e['box'][:2];l,t,r,b=e['roi'];l+=x;r+=x;t+=y;b+=y
    boxes={'top':(l-100,t-120,r+100,t+120),'bottom':(l-100,b-120,r+100,b+120),'left':(l-120,t-100,l+120,b+100),'right':(r-120,t-100,r+120,b+100)}
    for edge,box in boxes.items():save(ident+'_'+edge,quad.crop(box),box)
quad.resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'quad-overview.jpg',quality=93)
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'parentAssembly':str(P/'assembly_v4.json'),'parentAssemblySha256':sha(P/'assembly_v4.json'),'parent':str(source),'parentSha256':sha(source),'scriptSha256':sha(__file__),'files':files,'placements':placements,'qa':qa,'status':'native_repairs_placed_pending_visual_review','outsideMasksUnchanged':True,'row10FarRightUnchanged':True,'exactTileRejoinVerified':True,'sourceArtUpscaled':False,'limitedSeamResampling':True,'runtimePublished':False,'accepted':False}
(P/'assembly_v5.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps({'files':len(files),'qa':len(qa),'output':str(O)}))
