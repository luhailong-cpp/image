from pathlib import Path
from PIL import Image
import sys,numpy as np
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
def a(f):return np.asarray(Image.open(f).convert('RGB'))
D=R/'joint-v4';D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True)
spec=p.read(R/'evidence/inputs.json')
north=a(R/'joint-v1/north-stage.png').copy();west=a(R/'joint-v1/west-stage.png').copy();south=a(R/'joint-v1/south-stage.png').copy()
# Tiny cap correction from actual AI; apply only native65px support.
prev=R/'joint-v2/n-return3-composite.png';old=a(prev);new=a(R/'native/n-return3-tiny.png')
yy,xx=np.mgrid[:1254,:1254];alpha=np.clip(np.minimum(np.minimum(xx-627,696-xx),np.minimum(yy-581,657-yy))/10,0,1)
tiny=np.rint(old*(1-alpha[:,:,None])+new*alpha[:,:,None]).astype(np.uint8)
tf=D/'n-return3-final-composite.png';Image.fromarray(tiny).save(tf);np.savez_compressed(D/'tiny-alpha.npz',alpha=alpha)
p.derived(tf,[prev,R/'native/n-return3-tiny.png'],{'method':'native coordinate bounded local alpha','rectLTRB':[627,581,697,658],'edgeRamp':10,'mask':str(D/'tiny-alpha.npz'),'formalAccepted':False})
records=p.read(R/'joint-v2/return-composites.json');patchproof=[]
for item in records:
    name=item['name'];old=a(item['file']);patch=tiny if name=='n-return3'else a(item['composite']);mask=np.any(patch!=old,axis=2)
    x0,y0,x1,y1=item['boxLTRB']
    context=np.concatenate([north[3469:],south[:1800]],axis=0) if item['axis']=='north'else np.concatenate([west[:,3469:],south[:,:1800]],axis=1)
    roi=context[y0:y1,x0:x1]
    conflict=np.any(roi!=old,axis=2)&mask
    assert not conflict.any(),f'Conflicting staged change in {name}'
    roi[mask]=patch[mask]
    if item['axis']=='north':north[3469:]=context[:627];south[:1800]=context[627:]
    else:west[:,3469:]=context[:,:627];south[:,:1800]=context[:,627:]
    Image.fromarray(context[y0:y1,x0:x1]).save(Q/f'{name}-final-native.png')
    patchproof.append({'name':name,'changedPixels':int(mask.sum()),'conflictPixels':0,'alpha':item['alpha'],'tinySupplement':str(D/'tiny-alpha.npz')if name=='n-return3'else None})
internal=B/'r10_c14/repairs/internal/r10_c14-internal-candidate-v5.png'
assert p.sha(internal)=='e5b7d099b7612ab9c30702de3684b9a805c586e5e1e8d0e87f76918787be179c'
before=a(spec['internal']['file']);after=a(internal);imask=np.any(after!=before,axis=2);rootmask=np.any(south!=before,axis=2)
assert not (imask&rootmask).any(),'Internal/external changes conflict'
south[imask]=after[imask]
sources={'r09_c14':spec['north']['file'],'r10_c13':spec['west']['file'],'r10_c14':str(internal)}
outputs={}
for tile,value in [('r09_c14',north),('r10_c13',west),('r10_c14',south)]:
    f=D/f'{tile}-candidate.png';Image.fromarray(value).save(f)
    base=a(sources[tile]);mask=np.any(value!=base,axis=2)
    mf=D/f'{tile}-change-mask.png';Image.fromarray(mask.astype(np.uint8)*255).save(mf)
    p.derived(f,[sources[tile],R/'joint-v1/north-joint.png',R/'joint-v1/west-joint.png']+[Path(x['composite'])for x in records]+[tf],{'method':'exact changed-pixel propagation of native joint and return repairs; disjoint internal-v5 delta integrated','changeMask':str(mf),'resample':False,'formalAccepted':False})
    outputs[tile]={'file':str(f),'sha256':p.sha(f),'base':sources[tile],'baseSha256':p.sha(sources[tile]),'mask':str(mf),'maskSha256':p.sha(mf),'changedPixels':int(mask.sum()),'outsideMaskChangedPixels':0,'status':'external_shared_edges_and_returns_native_review_pending'}
northjoint=np.concatenate([north[3469:],south[:627]],axis=0);westjoint=np.concatenate([west[:,3469:],south[:,:627]],axis=1)
for direction,joint in [('north',northjoint),('west',westjoint)]:
    Image.fromarray(joint).save(D/f'{direction}-joint.png')
    for i in range(4):Image.fromarray(joint[:,i*1024:(i+1)*1024]if direction=='north'else joint[i*1024:(i+1)*1024]).save(Q/f'{direction}-s{i+1}.png')
    for i,v in enumerate([1139,2163,3290],1):Image.fromarray(joint[:,v-160:v+160]if direction=='north'else joint[v-160:v+160]).save(Q/f'{direction}-junction{i}.png')
    Image.fromarray(joint[:,430:830]if direction=='north'else joint[430:830]).save(Q/f'{direction}-corner-return.png')
# Reconstruct the accepted four-tile junction with its new full southeast.
ov=p.read(B/'tiles/current/current-overrides.json')['tiles'];nw=a(ov['r09_c13']['file'])
corner=np.concatenate([np.concatenate([nw[3469:,3469:],north[3469:,:627]],axis=1),np.concatenate([west[:627,3469:],south[:627,:627]],axis=1)],axis=0)
Image.fromarray(corner).save(Q/'four-corner-final-native.png')
record={'createdAt':p.stamp(),'outputs':outputs,'returnPatchProof':patchproof,'internalDelta':{'file':str(internal),'sha256':p.sha(internal),'changedPixels':int(imask.sum()),'conflictPixels':0},'qa':str(Q),'nativeScale':True,'formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False,'status':'native_visual_review_pending'}
p.write(D/'integration.json',record);print({k:v['sha256'] for k,v in outputs.items()})

