"""Read-only Donghai candidate and provenance validation; no artwork mutation."""
from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'builtin_q64_production'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ledger=read(HERE/'ledger-update.json');records=[]
for app in ['donghai_day','donghai_lantern']:
 for tile in ['r08_c08','r08_c09']:records.extend(sorted((P/app/tile/'native').glob('r*.record.json')))
base_count=len(records);records.extend(ROOT/p for p in ledger['repairRecords']);hashes=[];failed=0
for rf in records:
 r=read(rf);f=Path(r['outputPath']);src=Path(r['sourceOutputPath'])
 assert sha(f)==r['outputSha256']==sha(src)==r['sourceOutputSha256'],rf
 im=Image.open(f);assert im.size==(1254,1254),rf
 assert r.get('route') in ['builtin_image_gen','builtin'] and r.get('backendModelVerified') is False,rf
 assert r.get('finalArtUpscaled') is False and r.get('resizedAfterGeneration') is False,rf
 for k,h in [('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:assert sha(r[k])==r[h],(rf,k)
 for a in r.get('actualInputReferences',[]):assert sha(a['path'])==a['sha256'],rf
 for a in r.get('additionalSubmittedReferences',[]):assert sha(a['path'])==a['sha256'],rf
 if r.get('selected') is False:failed+=1
 else:assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255),rf
 hashes.append(r['outputSha256'])
assert len(hashes)==len(set(hashes))
assert base_count==64 and len(records)==93 and failed==4,(base_count,len(records),failed)
assert len(ledger['candidates'])==len({(c['appearance'],c['tile']) for c in ledger['candidates']})==4
assemblies=set()
for c in ledger['candidates']:
 f=ROOT/c['file'];assert Image.open(f).size==(4096,4096) and sha(f)==c['sha256']
 assert not c['accepted'] and not c['runtimePublished']
 col=int(c['tile'][-2:]);assert c['finalPixelRectXYWH']==[(col-1)*4096,28672,4096,4096]
 assert c['worldRect']==dict(x=50+(col-1)*18.75,z=150,width=18.75,height=18.75)
 assemblies.add(ROOT/c['assembly']);qa=read(ROOT/c['qa']);assert not qa['accepted'] and not qa['runtimePublished']
 for e in qa['files']:assert sha(e['file'])==e['sha256'] and e['viewed']
qa_count=0
for af in assemblies:
 a=read(af);folder=af.parent
 extended=Image.open(folder/'extended-context-pair.png');assert extended.size==(8422,4326)
 core=Image.open(folder/'paired-core8192x4096.png');assert core.size==(8192,4096)
 left=np.array(Image.open(folder/'r08_c08.png'));right=np.array(Image.open(folder/'r08_c09.png'))
 assert np.array_equal(np.concatenate([left,right],axis=1),np.array(core))
 for e in a['outputs']:
  assert sha(e['file'])==e['sha256'];im=Image.open(e['file']);assert list(im.size)==e['pixels']
  if e.get('cropXYXY'):assert np.array_equal(np.array(im),np.array(extended.crop(e['cropXYXY'])))
 for e in a['sources']:assert sha(e['path'])==e['sha256']
 for e in a.get('nativeRepairRecords',[]):assert sha(e['file'])==e['sha256']
 for e in a['qa']:
  assert sha(e['file'])==e['sha256'];im=Image.open(e['file']);assert list(im.size)==e['pixels'];qa_count+=1
  if e.get('cropXYXY'):
   src=extended if e.get('coordinateSpace')=='extended_pair' else core
   assert np.array_equal(np.array(im),np.array(src.crop(e['cropXYXY'])))
 if a.get('registeredRepairs'):
  for x in a['registeredRepairs']:
   t=x['mechanical'];assert t['maximumAllowedShiftPixels']<=8 and max(t['actualMaxShiftXY'])<=8.00001
   assert max(t['maxLocalColorCorrectionRGB'])<=18.00001 and t['nativeInteriorPixelsUnchanged'] and t['zeroMaskPixelsUnchanged']
  assert sha(a['mechanicalHelper']['file'])==a['mechanicalHelper']['sha256']
  assert sha(HERE/'apply_registered_repairs.py')==a['scriptSha256']
history=read(HERE/'cross_seam_repair/plan.json');assert sha(history['retainedSourcePath'])==history['sourceSha256']
hist=Image.open(history['retainedSourcePath'])
for e in history['patches']:assert np.array_equal(np.array(Image.open(e['guidePath'])),np.array(hist.crop(e['boxXYXY'])))
print(json.dumps(dict(passed=True,uniqueCoordinateCandidates=4,newCoordinateCandidates=2,baseNativeSources=base_count,additionalNativeRecords=len(records)-base_count,totalRetainedNativeSources=len(records),rejectedNativeSources=failed,pairedQACropsVerified=qa_count,nativePixels=[1254,1254],deliveryPixels=[4096,4096],byteIdentityAndReferenceHashesVerified=True,accepted=0,runtimePublished=False),indent=2))

