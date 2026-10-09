from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
import numpy as np
from PIL import Image

D = Path(__file__).resolve().parent
S = D.parent / 'west-common-edge-v1'
R = D / 'repair'
RAW = Path(r'C:/Users/luyua/.codex/generated_images/01a11b10-288e-7bc2-b56b-dc4a66076082/exec-40f6fc0a-41e2-4128-ab67-267ba00d7d5d.png')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'file': str(p), 'sha256': sha(p)}
def dump(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
def read(p): return json.loads(p.read_text('utf-8'))
def arr(p): return np.asarray(Image.open(p).convert('RGB'))
def save(p, a):
    Image.fromarray(a).save(p)
    return {**ref(p), 'pixels': [a.shape[1], a.shape[0]]}

for p in [D/'output', D/'qa']: p.mkdir(exist_ok=True)
assert not (D/'output/west-final-manifest.json').exists(), 'immutable output already exists'
prepared=read(R/'prepared.json')
for r in [prepared['basePair'], prepared['sourceContract'], prepared['request'], prepared['prompt'], *prepared['references']]:
    assert sha(r['file'])==r['sha256'], r
base=arr(prepared['basePair']['file'])
window=base[2842:4096,3469:4723]
assert np.array_equal(window,arr(R/'current-window.png'))
native=arr(RAW); assert native.shape==(1254,1254,3)
shutil.copyfile(RAW,R/'native.png')
request=read(R/'request.json')
record={**ref(R/'native.png'),'pixels':[1254,1254],'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(S/'native/s4.png.generation.json')['configSnapshot'],
 'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,
 'unverifiedReason':'Host-managed builtin exposes no model/quality selectors or return metadata.',
 'request':prepared['request'],'prompt':prepared['prompt'],'references':prepared['references'],
 'rawToolOutput':ref(RAW),'nativeSourceUnscaled':True,'actualFullNativeViewed':True,
 'windowPairRectXYXY':[3469,2842,4723,4096],'geometryChangesAllowed':False,'DAYWritten':False}
dump(R/'native.png.generation.json',record)

# A small inward feather on the lower wooden surface, not a whole-image filter.
# The diagonal half-plane excludes the rail outline and adjacent water.
yy,xx=np.mgrid[:1254,:1254]
a=np.minimum.reduce([np.clip((xx-500)/48,0,1),np.clip((769-xx)/48,0,1),np.clip((yy-740)/48,0,1),np.clip((yy-xx-130)/16,0,1)])
mask=np.rint(a*255).astype(np.uint8)
delta=np.clip(native.astype(np.int16)-window.astype(np.int16),-24,24)
paint=np.clip(window.astype(np.int16)+delta,0,255).astype(np.uint8)
patched=((window.astype(np.int32)*(255-mask[:,:,None])+paint.astype(np.int32)*mask[:,:,None]+127)//255).astype(np.uint8)
assert np.array_equal(window[mask==0],patched[mask==0])
Image.fromarray(mask,'L').save(R/'mask.png')
save(R/'bounded-native-color.png',paint)
save(R/'patched-window.png',patched)
np.savez_compressed(R/'applied-color-delta.npz',delta=(patched.astype(np.int16)-window.astype(np.int16)),mask=mask)
final=base.copy();final[2842:4096,3469:4723]=patched
full_mask=np.zeros(base.shape[:2],dtype=np.uint8);full_mask[2842:4096,3469:4723]=mask
assert np.array_equal(final[full_mask==0],base[full_mask==0])

sources=read(S/'source-contract.json')['sources']
for q in sources: assert sha(q['snapshot']['file'])==q['snapshot']['sha256']
old14=arr(next(q['snapshot']['file'] for q in sources if q['id']=='festival-c14'))
old15=arr(next(q['snapshot']['file'] for q in sources if q['id']=='festival-c15'))
assert np.array_equal(final[:,:3469],old14[:,:3469])
assert np.array_equal(final[:,4723:],old15[:,627:])

out=[]
for name,data in [('pair-r08_c14-c15',final),('r08_c14',final[:,:4096]),('r08_c15',final[:,4096:])]:
    out.append({'id':name,**save(D/'output'/f'{name}.png',data)})
qa=[]
old_manifest=read(S/'output/west-final-manifest.json')
for q in old_manifest['qa']:
    x0,y0,x1,y1=q['pairRectXYXY'];crop=final[y0:y1,x0:x1]
    same=np.array_equal(crop,arr(q['file']))
    qa.append({'id':q['id'],**save(D/'qa'/f"{q['id']}.png",crop),'pairRectXYXY':q['pairRectXYXY'],'pixelsUnchangedFromV1':same,'v1QA':q})

localqa=[]
for name,rect in [('full1254',[3469,2842,4723,4096]),('return-left',[3860,3500,4069,4096]),('return-right',[4139,3500,4350,4096]),('return-top',[3860,3460,4350,3700]),('return-bottom-map-edge',[3860,3936,4350,4096])]:
    x0,y0,x1,y1=rect
    localqa.append({'id':name,**save(D/'qa'/f'local-{name}.png',final[y0:y1,x0:x1]),'pairRectXYXY':rect,'nativeScale':1})

manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'stage':'final lower-dock local color correction',
 'baseManifest':ref(S/'output/west-final-manifest.json'),'basePair':prepared['basePair'],
 'sourceContract':prepared['sourceContract'],'geometrySyncPending':ref(S/'geometry-sync-pending.json'),
 'native':ref(R/'native.png'),'nativeRecord':ref(R/'native.png.generation.json'),'request':prepared['request'],
 'repair':{'pairWindowXYXY':[3469,2842,4723,4096],'localROI':[500,740,770,1254],
  'pairMaximumROI':[3969,3582,4239,4096],'inwardFeather':48,'diagonalRailProtected':True,
  'bottomFeather':'none at y4096 map edge','mask':ref(R/'mask.png'),'appliedDelta':ref(R/'applied-color-delta.npz'),
  'maximumChannelColorChange':int(np.abs(patched.astype(np.int16)-window.astype(np.int16)).max()),
  'changedPixels':int(np.any(patched!=window,axis=2).sum()),'outsideMaskExactSame':True,
  'nativeArtResampled':False,'artBlurred':False,'geometryWarped':False},
 'authorizedPairRectXYXY':[3469,0,4723,4096],'c14OutsideEast627ExactlyPreserved':True,
 'c15OutsideWest627ExactlyPreserved':True,'outputs':out,'qa':qa,'localQA':localqa,
 'qaSameCount':sum(q['pixelsUnchangedFromV1'] for q in qa),'qaChangedCount':sum(not q['pixelsUnchangedFromV1'] for q in qa),
 'DAYWritten':False,'globalRegistryModified':False,'formalAccepted':False,'status':'immutable candidate, changed visual QA pending','script':ref(Path(__file__))}
dump(D/'output/west-final-manifest.json',manifest)
print(json.dumps({'outputs':out,'manifest':ref(D/'output/west-final-manifest.json'),'qaSameCount':manifest['qaSameCount'],'changedQA':[q['id'] for q in qa if not q['pixelsUnchangedFromV1']],'repair':manifest['repair']},ensure_ascii=False))
