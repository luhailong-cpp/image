from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;D=N/'full-review-native-v1';read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'file':str(p),'sha256':sha(p)}
root=read(T/'source-checkpoint.json');i=read(D/'native-crop-index.json');checks=[]
for key,tile,box in [('fragment','r07_c09',[0,0,4096,4096]),('prospectiveRight','r07_c10',[0,0,256,4096]),('prospectiveBottom','r08_c09',[0,0,4096,256])]:
 a=i['sources'][key];b=next(v for v in root['candidateSet'] if v['tile']==tile)
 for v in [a,b]:assert sha(v['file'])==v['sha256']
 A=np.array(Image.open(a['file']).convert('RGBA').crop(box));B=np.array(Image.open(b['file']).convert('RGBA').crop(box));eq=bool(np.array_equal(A,B));assert eq,(tile,int(np.any(A!=B,axis=2).sum()));checks.append({'tile':tile,'reviewedSource':a,'rootSource':b,'roi':box,'pixelExact':eq,'differentPixels':0})
source=next(v for v in root['candidateSet'] if v['tile']=='r07_c09')
r={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c09','fullyPaintedNativeTileReviewed':True,'source':source,'fullNativeCoveragePixels':16777216,'nativeScale':1,'visualReview':ref(D/'visual-review.json'),'rootCheckpoint':ref(T/'source-checkpoint.json'),'exactRootPixelChecks':checks,'openInternalFindings':[],'formalAccepted':False,'pendingExternalChecks':[{'neighbor':'r06_c09','edge':'north','status':'await actual native neighbor'},{'neighbor':'r07_c08','edge':'west','status':'await actual native neighbor'},{'scope':'complete city256 tiles and nearest-camera runtime','status':'not part of this local image review'}],'eastActualRootBoundaryReviewed':True,'southActualRootBoundaryReviewed':True,'method':'All15 frozen native crops visually inspected. Root complete4096-square pixels plus eastern and southern256px strips subsequently proved exact to the reviewed frozen sources; no regeneration/review substitution by metrics.','rootStateModified':False}
p=D/'root-reviewed-v017.json';p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'report':ref(p),'checks':[{'tile':c['tile'],'exact':c['pixelExact']} for c in checks]}))
