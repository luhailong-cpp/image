import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent
pre='west-corner-r08r09c04c05-v3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def png(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
source=read(Q/'west-corner-r08r09c04c05-v1-source-trace.json')
mt=read(Q/(pre+'-mask-trace.json'));box=source['globalContextBox'];patch=rgb(mt['after']['path'])
result={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pending_native_visual_qa','sourceTrace':ref(Q/'west-corner-r08r09c04c05-v1-source-trace.json'),'repairMaskTrace':ref(Q/(pre+'-mask-trace.json')),'repairGeneration':ref(Z/'native/r08_c05_repair_t_westcorner_v2.png.generation.json'),'baseAudits':[ref(Q/'block2x2-r08r09c05c06-v7-art-audit.json')],'method':'Native AI repaired pixels selected with recorded closed hard mask, then integer global-coordinate copy to each affected image. Outside repair, core pixels remain original; halo uses actual adjacent selected core pixels. No resampling/feathering/colour edits.','globalContextBox':box,'tiles':[],'partials':[],'qa':[],'validation':{'nativePixelsResampled':False,'sourcePixelIdentity':True}}
arrays={}
for s in source['sources']:
 tile=s['tile'];src=Path(s['source']['path']);assert ref(src)==s['source'];base=rgb(src);out=base.copy();b=s['sourceGlobalBox']
 g=[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]
 target=[g[0]-b[0],g[1]-b[1],g[2]-b[0],g[3]-b[1]];crop=[g[0]-box[0],g[1]-box[1],g[2]-box[0],g[3]-box[1]]
 l,t,r,bt=target;cl,ct,cr,cb=crop;out[t:bt,l:r]=patch[ct:cb,cl:cr];arrays[tile]=out
 diff=np.any(out!=base,axis=2);ys,xs=np.where(diff)
 rec={'tile':tile,'base':s['source'],'sourceGlobalBox':b,'appliedGlobalBox':g,'targetBox':target,'patchCropBox':crop,'changedPixelCount':int(diff.sum()),'changedBoundingBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'context':png(Q/(pre+'-'+tile+'-context-native.png'),out)}
 if out.shape[:2]==(4326,4326):
  rec['candidate']=png(Q/(pre+'-'+tile+'-candidate-4096.png'),out[115:4211,115:4211]);result['tiles'].append(rec)
 else:rec['patch']='p04_04';rec['candidateStatus']='partial_tile_only';result['partials'].append(rec)
# Native direct export crop across south row boundary (x345).
a=arrays['r09_c04'];b=arrays['r09_c05']
result['qa'].append(dict(role='r09_c04/r09_c05 direct export top corner, boundary x345',**png(Q/(pre+'-south-west-direct-100pct.png'),np.concatenate([a[115:1015,3866:4211],b[115:1015,115:460]],axis=1))))
a=arrays['r08_c05'];b=arrays['r09_c05']
result['qa'].append(dict(role='r08_c05/r09_c05 left horizontal export joint, boundary y345',**png(Q/(pre+'-c05-horizontal-left-100pct.png'),np.concatenate([a[3866:4211,115:1015],b[115:460,115:1015]],axis=0))))
# Full 1254 native source-mask junction for partial c04 continuing later.
result['qa'].append(dict(role='partial c04 corner; upper-left joint still pending full tile composition',**mt['after']))
# Existing c05 shared overlap identity unaffected by common patch.
assert np.array_equal(arrays['r08_c05'][4096:4326],arrays['r09_c05'][:230])
# direct export corner overlapping halos exact across this repaired local region
assert np.array_equal(arrays['r09_c04'][:742,4096:4326],arrays['r09_c05'][:742,:230])
result['validation']['c05HorizontalHaloExact']=True
result['validation']['southWestTop742RowsHaloExact']=True
# Existing c05 internal seam coordinates (1024,2048,3072) are outside changed local x/y corner.
result['reuseUnchangedAudits']='v7 all internal/native seam views except west shared edge part5; new c05 horizontal-left view replaces that affected edge scope; other shared edges and all internal patch seams unchanged.'
out=Q/(pre+'-export-trace.json');assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'trace':ref(out),'tiles':result['tiles'],'partials':result['partials'],'qa':result['qa']}))

