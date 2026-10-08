from helper import *
import numpy as np
src=BASE/'r09_c14/repairs/internal/r09_c14-internal-candidate-v3.png'
assert p.sha(src)=='65908a88978bdc7dadd74304a52d6684e0f7534cc18af56f14585c0225f8a1d0'
joint=BASE/'r09_c14/repairs/west/output/joint-quilt-native-v1.png';mask=BASE/'r09_c14/repairs/west/output/joint-quilt-mask-v1.png'
a=np.array(Image.open(src).convert('RGB'));j=np.array(Image.open(joint).convert('RGB'))[:,627:];m=np.array(Image.open(mask))[:,627:]>0;a[:,:627][m]=j[m]
dest=ROOT/'references/north-source-combined-v3.png';Image.fromarray(a).save(dest);p.derived(dest,[src,joint,mask],{'method':'native binary joint mask onto current internal candidate','destinationXY':[0,0],'jointCropLTRB':[627,0,1254,4096],'noResampling':True,'parentWillIntegrateSameOperation':True,'contextOnlyNotDeliverable':True})
anchor=ROOT/'references/north-115-combined-v3-native.png';Image.fromarray(a).crop((0,3981,4096,4096)).save(anchor);p.derived(anchor,[dest],{'method':'exact north bottom115 crop','boxLTRB':[0,3981,4096,4096]})
state=p.read(ROOT/'evidence/boundary-state.json');state['north']={'source':str(dest),'sha256':p.sha(dest),'anchor':str(anchor),'anchorSha256':p.sha(anchor),'stable':True,'confirmation':'fabric_repairs locked internal-v3 bottom115; local exact combination with root-reviewed west joint mask; pending parent corner QA'};p.write(ROOT/'evidence/boundary-state.json',state)
guides();print(p.sha(anchor))
