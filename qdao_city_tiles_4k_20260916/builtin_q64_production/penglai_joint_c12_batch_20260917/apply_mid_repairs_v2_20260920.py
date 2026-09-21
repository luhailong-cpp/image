import json,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');J=B/'penglai_mid_autumn/r09_c10_c11_c12_joint';R=J/'repairs_v2_20260920';O=J/'output_v2_20260920';Q=J/'qa_v2_20260920'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
plan=read(R/'plan.json');assert sha(plan['source'])==plan['sourceSha256'];assert not O.exists() and not Q.exists()
sp=importlib.util.spec_from_file_location('mj',B/'tools/mechanical_join.py');mj=importlib.util.module_from_spec(sp);sp.loader.exec_module(mj)
old=np.array(Image.open(plan['source']).convert('RGB'));canvas=old.copy();changed=np.zeros(old.shape[:2],bool);records=[]
O.mkdir();Q.mkdir()
for job in plan['jobs']:
    ident=job['id'];native=R/'native'/f'{ident}.png';rp=native.with_suffix('.record.json');rec=read(rp)
    assert sha(native)==rec['outputSha256']==sha(rec['sourceOutputPath']);assert sha(rec['promptFile'])==rec['promptSha256']
    for ref in rec['submittedImages']:assert sha(ref['path'])==ref['sha256']
    patch=np.array(Image.open(native).convert('RGB'));assert patch.shape==(1254,1254,3)
    bx,by,ex,ey=job['sourceCropLTRB'];rx,ry,rex,rey=job['pasteROIInTriple'];context=canvas[by+115:ey+115,bx+115:ex+115].copy()
    yy,xx=np.mgrid[:1254,:1254];gx=xx+bx;gy=yy+by
    distance=np.minimum.reduce([gx-rx,rex-1-gx,gy-ry,rey-1-gy]).astype(float)
    alpha=np.clip(distance/28,0,1);alpha=alpha*alpha*(3-2*alpha);mask=np.uint8(np.rint(alpha*255))
    merged,flow,corr,report=mj.registered_join(context,patch,mask,max_shift=8,flow_inner=150,flow_full=60,tone_inner=150,tone_full=60)
    canvas[by+115:ey+115,bx+115:ex+115]=merged;changed[by+115:ey+115,bx+115:ex+115]|=mask>0
    fields={}
    for name,arr in [('mask',mask),('flow',flow),('colorCorrection',corr)]:
        p=O/(ident+'.'+name+('.png' if name=='mask' else '.npy'))
        if name=='mask':Image.fromarray(arr).save(p)
        else:np.save(p,arr)
        fields[name]={'path':str(p),'sha256':sha(p)}
    records.append({'id':ident,'nativeSource':str(native),'nativeSha256':sha(native),'record':str(rp),'recordSha256':sha(rp),'sourceCropLTRB':job['sourceCropLTRB'],'pasteROIInTriple':job['pasteROIInTriple'],'registrationSupportLTRB':job['sourceCropLTRB'],'joinReport':report,**fields})
assert np.array_equal(old[~changed],canvas[~changed]);assert np.array_equal(old[:,:7565+115],canvas[:,:7565+115])
full=Image.fromarray(canvas);triple=full.crop((115,115,12403,4211));outputs=[];qa=[]
def save(im,p,kind,box=None):
    im.save(p);item={'file':str(p),'pixels':list(im.size),'sha256':sha(p),'kind':kind}
    if box:item['cropLTRB']=box
    (qa if p.parent==Q else outputs).append(item)
def crop(box):return full.crop(tuple(v+115 for v in box))
save(full,O/'extended-context.png','extended');save(triple,O/'triple-12288x4096.png','triple')
for k in range(3):save(triple.crop((4096*k,0,4096*(k+1),4096)),O/f'penglai_mid_autumn_r09_c{k+10}_4k_joint_candidate_v2.png','tile')
assert np.array_equal(np.concatenate([np.array(Image.open(x['file'])) for x in outputs if x['kind']=='tile'],axis=1),np.array(triple))
parent=read(J/'output_v1_20260920/assembly.json')
for e in parent['qa']:
    name=Path(e['file']).name
    if 'cropLTRB' in e:save(crop(e['cropLTRB']),Q/name,'native_crop',e['cropLTRB'])
    elif name.startswith('internal_'):
        axis=name.split('_')[1][0];pos=int(name.split('_')[1][1:-4]);rt=triple.crop((8192,0,12288,4096))
        strip=rt.crop((pos-150,0,pos+150,4096)) if axis=='x' else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
        sheet=Image.new('RGB',(1200,1024))
        for k in range(4):sheet.paste(strip.crop((0,1024*k,300,1024*(k+1))),(k*300,0))
        save(sheet,Q/name,'native_fullseam_panels')
    else:save(triple.resize((2048,683),Image.Resampling.LANCZOS),Q/name,'preview_only')
for job in plan['jobs']:
    ident=job['id'];save(crop(job['sourceCropLTRB']),Q/f'{ident}.joined-support.png','native_crop',job['sourceCropLTRB'])
    x,y,r,b=job['pasteROIInTriple']
    for edge,box in [('top',[x-100,y-120,r+100,y+120]),('bottom',[x-100,b-120,r+100,min(b+120,4211)]),('left',[x-120,y-70,x+120,min(b+70,4211)]),('right',[r-120,y-70,r+120,min(b+70,4211)])]:save(crop(box),Q/f'{ident}.roi-{edge}.png','actual_roi_return_edge',box)
save(crop([7790,3020,8640,3500]),Q/'repair-overlap.png','native_crop',[7790,3020,8640,3500])
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'penglai_mid_autumn','status':'candidate_pending_visual_QA_not_published','runtimePublished':False,'formallyAccepted':False,'parentAssembly':str(J/'output_v1_20260920/assembly.json'),'parentAssemblySha256':sha(J/'output_v1_20260920/assembly.json'),'parentExtendedContext':plan['source'],'parentExtendedContextSha256':plan['sourceSha256'],'scriptPath':str(Path(__file__)),'scriptSha256':sha(__file__),'repairs':records,'sourceArtUpscaled':False,'sourceResampling':'Limited native repair registration, maximum 8 pixels; masks/flow/tone fields retained.','zeroMaskPixelsUnchanged':True,'unchangedC10':True,'splitPixelIdentity':True,'externalNeighbors':'unverified','outputs':outputs,'qa':qa,'visualQa':'pending'}
(O/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'output':str(O),'qa':str(Q),'qaCount':len(qa)}))
