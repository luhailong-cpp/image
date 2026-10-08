"""Independently rebuild the adopted canopy from native sources and saved fields."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent.parent;T=R/'r09_c08';V=T/'canopy-repair/candidate-v5'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def pixels(p):return np.array(Image.open(p).convert('RGB'))
m=read(V/'manifest.json');source={}
for k,e in m['sourceNativeImages'].items():
 p=Path(e['file']);assert sha(p)==e['sha256'];source[k]=pixels(p)
b=source['baseRejectedAttempt04'];p=source['newBridgeBuiltin'];n=source['authenticNorthCore'];e=source['authenticEastNative']
mask=np.array(Image.open(V/'replacement-mask.png'))>0
with np.load(V/'rgb-fields.npz',allow_pickle=False) as f:
 dx=f['geometry_source_dx'];dy=f['geometry_source_dy'];requested=f['requested_delta_rgb'];delta=f['actual_delta_rgb'];limits=f['per_pixel_rgb_limit']
 assert dx.shape==dy.shape==(1254,1254) and requested.shape==delta.shape==limits.shape==(1254,1254,3)
 assert dx.min()>=0 and dx.max()<=1 and dy.min()>=-4 and dy.max()<=2
 assert np.all(np.abs(requested)<=np.ceil(limits))
 s=b.copy();s[115:350]=p[627:862]
 yy,xx=np.where((dx!=0)|(dy!=0));sy=yy+512+dy[yy,xx];sx=xx+dx[yy,xx]
 assert np.all((sy>=0)&(sy<1254)&(sx>=0)&(sx<1254))
 s[yy,xx]=p[sy,sx]
 corrected=np.clip(s.astype(np.int16)+requested,0,255).astype(np.uint8)
 assert np.array_equal(corrected.astype(np.int16)-s.astype(np.int16),delta)
 rebuilt=b.copy();rebuilt[mask]=corrected[mask]
 rebuilt[115:,1139:]=e[115:,115:230];rebuilt[:115]=n[3981:4096,1933:3187]
candidate=V/'candidate1254.png';native=T/'native/r01_c03.png'
assert np.array_equal(rebuilt,pixels(candidate)) and np.array_equal(rebuilt,pixels(native))
assert sha(candidate)==sha(native)=='a8e8ece5cf8ea2a958536b2674e588451781b62129129750937abb55ec12a6fc'
out={'verifiedAtUtc':datetime.now(timezone.utc).isoformat(),'readOnlyArtVerification':True,
 'native':ref(native),'candidate':ref(candidate),'manifest':ref(V/'manifest.json'),
 'mask':ref(V/'replacement-mask.png'),'fields':ref(V/'rgb-fields.npz'),
 'nativeRebuiltExactlyFromActualRawSourcesAndSavedCoordinatesAndRgbDeltas':True,
 'sourceCoordinateLimitsVerified':{'dx':[0,1],'dy':[-4,2]},'requestedRgbPerPixelLimitsVerified':True,
 'actualRgbDeltaExactlyMatchesClippedRequestedDelta':True,
 'trueNorthAndEastExact':True,'imageBlurApplied':False,'imageUpscalingApplied':False,
 'scope':'Pixel derivation proof only; does not grant visual or complete-tile acceptance.'}
dest=T/'canopy-repair/pixel-reconstruction-proof.json';assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ref(dest)))
