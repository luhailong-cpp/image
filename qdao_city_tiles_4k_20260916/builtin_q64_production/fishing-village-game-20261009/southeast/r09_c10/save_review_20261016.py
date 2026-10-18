from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Q=T/'qa/full-native-20261016-v1';O=T/'processed/colorpass-finish-20261016-v1';E=T.parent/'seam-qa/r09_c10-full-native-20261016-v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=read(O/'colorpass-report.json');replay=[]
for rec in report['outputRecords']:
 p=Path(rec['file']);d=read(rec['record']);src=Path(d['derivedFrom'][0]['file']);assert sha(src)==d['derivedFrom'][0]['sha256']
 a=np.array(Image.open(src).convert('RGB'),dtype=np.float32);npz=np.load(d['correctionEvidence']['file']);g=npz['additiveGridRgb']
 pos=np.clip((np.arange(1254,dtype=np.float32)-114.5)/16,0,64);low=np.floor(pos).astype(int);high=np.minimum(low+1,64);w=pos-low
 field=(g[low[:,None],low[None,:]]*(1-w[:,None,None])*(1-w[None,:,None])+g[high[:,None],low[None,:]]*w[:,None,None]*(1-w[None,:,None])+g[low[:,None],high[None,:]]*(1-w[:,None,None])*w[None,:,None]+g[high[:,None],high[None,:]]*w[:,None,None]*w[None,:,None]).astype(np.float32)
 field*=1-npz['safetyProtectionY'][:,None,None]*(1-npz['safetyWeightX'][None,:,None])
 rebuilt=np.uint8(np.clip(np.rint(a+np.clip(field,-24,24)),0,255));actual=np.array(Image.open(p).convert('RGB'))
 # Float operation order may differ by a sub-ULP at exact .5 rounding ties.
 delta=np.abs(rebuilt.astype(int)-actual.astype(int));assert delta.max()<=1
 replay.append(dict(file=str(p),sha256=sha(p),maxIndependentReplayChannelDifference=int(delta.max()),differentChannels=int(np.count_nonzero(delta)),maxColorChange=int(np.max(np.abs(actual.astype(int)-a)))))
native=read(Q/'manifest.json');native_reviews=[]
pending_names={'p21--p31','p22--p32','p31--p32','p23--p33','p24--p34','p32--p42','p33--p43','p34--p44','p42--p43','cross-r2-c1','cross-r2-c2','cross-r3-c1','cross-r3-c2'}
for e in native['evidence']:
 p=Path(e['file']);assert sha(p)==e['sha256'];native_reviews.append(dict(file=str(p),sha256=e['sha256'],viewedAtNativeResolution=True,geometry='pending stone joint' if p.stem=='p31--p32' else 'usable',material='pending' if p.stem in pending_names else 'usable'))
color_reviews=[]
for e in report['seams']:
 p=Path(e['afterStrip']);assert sha(p)==e['sha256'];color_reviews.append(dict(file=str(p),sha256=e['sha256'],viewedAtNativeResolution=True))
for e in report['crossings']:
 p=Path(e['file']);assert sha(p)==e['sha256'];color_reviews.append(dict(file=str(p),sha256=e['sha256'],viewedAtNativeResolution=True))
external=[dict(file=str(p),sha256=sha(p),viewedAtNativeResolution=True) for p in sorted(E.glob('*-100pct.png'))]
assert len(native_reviews)==33 and len(color_reviews)==33 and len(external)==15
pending=[
 {'location':'p31/p32 vertical stone joint','nativeStatus':'geometry mismatched at local seam x1024, y~2300..2850','bestRepair':'stone-joint-v1-20261016 (native joint); geometry improved, exact 4-patch binary replacement replayed; left/top perimeter texture still visible; not adopted'},
 {'location':'p21/p31, p22/p32','status':'Stone mottling density changes across horizontal seam remain; color-only cannot certify this'},
 {'location':'p32/p42 and p42/p43','status':'Wood grain sharpness/color changes remain after bounded RGB correction; preserve pending'},
 {'location':'west-segment-3','status':'Short blue ridge/greenery transition has abrupt vertical cutoff near local seam; west stone density also changes'},
 {'location':'p13/p23 right railing post','status':'Two reddish bands exist; structure continuous, but count/proportion should be reconciled with approved post design before final acceptance'},
 {'location':'available external W/S','status':'Geometry generally connects except west short ridge above; warm-stone and south wooden tonal/density transitions remain pending'},
 {'location':'north/east external','status':'Neighbor selected cores unavailable in zone reader; not reviewed, not claimed absent globally'}]
out=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r09_c10',selectedNativeCount=16,route='builtin',actualModel=None,actualQuality=None,nativeCandidate=dict(file=str(Q/'candidate-4096.png'),sha256=sha(Q/'candidate-4096.png'),dimensions=[4096,4096]),colorCandidate=report['candidate'],colorSourceSelection=report['originalSelection'],nativeReviews=native_reviews,colorReviews=color_reviews,externalReviews=external,independentColorReplay=replay,pending=pending,canonicalSelectionUnchangedByJointOrColor=True,internalReady=False,formalAccepted=False,next='Continue independent r08_c10 from stable current r09_c10 row1 south references; return to targeted pending defects in coordinated repair batch')
write(T/'review-finish-20261016-v1.json',out)
sel=read(T/'selected-patches.json');write(T/'selected-before-status-20261016-v1.json',sel);sel.update(candidate=str(Q/'candidate-4096.png'),candidateSha256=sha(Q/'candidate-4096.png'),status='complete_native_candidate_internal_and_external_repairs_pending',internalReady=False,formalAccepted=False,materialPending=True,review=str(T/'review-finish-20261016-v1.json'));write(T/'selected-patches.json',sel)
print(json.dumps(dict(nativeCandidate=out['nativeCandidate'],colorCandidate=out['colorCandidate'],independentReplayMax=max(x['maxIndependentReplayChannelDifference'] for x in replay),internalReady=False)))
