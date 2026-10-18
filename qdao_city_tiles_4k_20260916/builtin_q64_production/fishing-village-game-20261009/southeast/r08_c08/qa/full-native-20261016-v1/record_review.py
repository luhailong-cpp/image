from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent; T=Q.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=json.loads((Q/'manifest.json').read_text()); s=json.loads((T/'selected-patches.json').read_text(encoding='utf-8-sig'))
im=np.array(Image.open(m['candidate']).convert('RGB')); assert im.shape==(4096,4096,3)
proof=[]
for a in m['sources']:
 p=Path(a['file']); assert sha(p)==a['sha256'] and str(p)==str(T/s['patches'][a['patch']])
 x,y=a['destination']; core=np.array(Image.open(p).convert('RGB'))[115:1139,115:1139]
 assert np.array_equal(core,im[y:y+1024,x:x+1024]); proof.append({'patch':a['patch'],'sha256':a['sha256'],'exactNativeCoreReplay':True})
issues={
 'p12--p13':'Visible vertical change in gray medallion stone grain density.',
 'p12--p22':'Visible horizontal change from fine gray grain to broad pale stone patches.',
 'p13--p23':'Stone grain/brightness transition across the medallion and ring.',
 'p21--p22':'Stone density transition across the pale ring.',
 'p22--p23':'Warm/cool and grain-density change across pale ring and gray medallion.',
 'p31--p32':'Paving grain density and sharpness change at the vertical boundary.',
 'p32--p33':'Visible local slab-edge notch/endpoint mismatch near central blue slab; texture transition.',
 'p34--p44':'Paving below boundary becomes softer and paler.',
 'p41--p42':'Local bevel/stone endpoint kink on vertical boundary and density change.',
 'p42--p43':'Local bevel/stone endpoint kink on vertical boundary and density change.',
 'p43--p44':'Paving softness and fine-grain change; local slab edge needs further joint review.',
 'cross-r1-c1':'Pale stone and gray medallion grain transition.',
 'cross-r1-c2':'Clearly visible quadrant grain-density transition on gray medallion.',
 'cross-r1-c3':'Fine/coarse grain change across ring junction.',
 'cross-r2-c1':'Stone sharpness and density transition across lower ring.',
 'cross-r2-c2':'Pale ring and paving material transition.',
 'cross-r2-c3':'Paving fine/coarse grain transition.',
 'cross-r3-c1':'Minor endpoint/sharpness discontinuity around paving cross.',
 'cross-r3-c2':'Minor endpoint/sharpness discontinuity around paving cross.',
 'cross-r3-c3':'Paving softness/density transition toward p44.'}
reviews=[]
for e in m['evidence']:
 p=Path(e['file']); assert sha(p)==e['sha256']; name=p.stem
 box=e['globalBox']; box=[box[0]-28672,box[1]-28672,box[2]-28672,box[3]-28672]
 assert np.array_equal(np.array(Image.open(p)),im[box[1]:box[3],box[0]:box[2]])
 reviews.append({'evidence':str(p),'sha256':e['sha256'],'viewedAtNativeScale':True,'status':'pending_local_repair' if name in issues else 'usable_local_join','note':issues.get(name,'No new visible object discontinuity in this evidence crop. Does not imply whole-tile acceptance.')})
r={'tile':'r08_c08','createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':m['candidate'],'candidateSha256':sha(m['candidate']),'dimensions':[4096,4096],'nativeCoreCount':16,'exactCoreReplay':proof,'all16PixelExact':True,'all33EvidencePixelExact':True,'newlyViewedEvidenceCount':33,'reusedVisualPassCount':0,'reuseNote':'Existing quick QA metadata remained pending; no completed pass was inferred.','reviews':reviews,'internalReady':False,'formalAccepted':False,'materialPending':True,'geometryPending':True,'externalQA':'not assessed in this batch','resamplingAppliedToArtwork':False,'layoutPixelsUsed':False,'completionScope':'Native core production and full internal QA complete; local material and bevel issues remain pending.'}
write(Q/'independent-replay-and-review.json',r)
(Q/'selected-patches-snapshot.json').write_bytes((T/'selected-patches.json').read_bytes())
s.update({'candidate':m['candidate'],'candidateSha256':r['candidateSha256'],'status':'native_complete_internal_material_and_local_joint_pending','internalReady':False,'formalAccepted':False,'materialPending':True,'geometryPending':True,'review':str(Q/'independent-replay-and-review.json')})
write(T/'selected-patches.json',s)
print(json.dumps({'candidate':m['candidate'],'sha256':r['candidateSha256'],'nativeCoreCount':16,'evidenceCount':33,'internalReady':False}))
