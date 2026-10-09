from helper import *
import numpy as np
src=BASE/'r09_c14/repairs/internal/r09_c14-internal-candidate-v5.png'
assert p.sha(src)=='770c25915eff3ca348c2db00c68c128d52bcbb9050dc3956a10751088220d436'
joint=BASE/'r09_c14/repairs/west/output/joint-quilt-native-v1.png';mask=BASE/'r09_c14/repairs/west/output/joint-quilt-mask-v1.png'
a=np.array(Image.open(src).convert('RGB'));j=np.array(Image.open(joint).convert('RGB'))[:,627:];m=np.array(Image.open(mask))[:,627:]>0;a[:,:627][m]=j[m]
dest=ROOT/'references/north-source-combined-v5.png';Image.fromarray(a).save(dest);p.derived(dest,[src,joint,mask],{'method':'native binary joint mask onto internalv5','destinationXY':[0,0],'jointCropLTRB':[627,0,1254,4096],'noResampling':True,'contextOnlyNotDeliverable':True})
anchor=ROOT/'references/north-115-combined-v5-native.png';Image.fromarray(a).crop((0,3981,4096,4096)).save(anchor);p.derived(anchor,[dest],{'method':'exact north bottom115 crop','boxLTRB':[0,3981,4096,4096]})
state=p.read(ROOT/'evidence/boundary-state.json');old=state['north'];oldpixels=np.array(Image.open(old['anchor']).convert('RGB'));newpixels=a[3981:]
proof={'method':'pixel equality','oldAnchor':old['anchor'],'oldSha256':p.sha(old['anchor']),'newAnchor':str(anchor),'newSha256':p.sha(anchor),'p11p12CoreAndHalosUnchanged':bool(np.array_equal(oldpixels[:,:2163],newpixels[:,:2163]))};assert proof['p11p12CoreAndHalosUnchanged'];p.write(ROOT/'evidence/north-v5-anchor-change.json',proof)
state['north']={'source':str(dest),'sha256':p.sha(dest),'anchor':str(anchor),'anchorSha256':p.sha(anchor),'stable':True,'confirmation':'fabric_repairs lockedv5 bottom115; root approved local exact mask combination'}
canvas=Image.open(ROOT/'references/layout-canvas-only.png').convert('RGB');canvas.paste(Image.open(anchor).convert('RGB'),(115,0));cp=ROOT/'references/layout-canvas-v5-only.png';canvas.save(cp);p.derived(cp,[ROOT/'references/layout-canvas-only.png',anchor],{'method':'replace only top115 native anchor, layout-only all other pixels unchanged'})
state['guideOverrides']={}
for c in [3,4]:
    n=f'p1{c}';box=((c-1)*1024,0,(c-1)*1024+1254,1254);fp=ROOT/'guides'/f'{n}-v5.png';canvas.crop(box).save(fp);p.derived(fp,[cp],{'method':'integer guide crop only','boxLTRB':box,'neverFinalArt':True});state['guideOverrides'][n]=str(fp)
p.write(ROOT/'evidence/boundary-state.json',state);print(json.dumps(proof))
