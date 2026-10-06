from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def png(n,a):Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
def ss(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
source=P/'corner-repair-v2/joined.png';assert sha(source)=='8b8519ad0e04df77272a33da2917aef665c37e2599a63d906519465c9ab3a2f5'
a=np.asarray(Image.open(source).convert('RGB'),np.float32);ctx=np.asarray(Image.open(P/'repaired-v1/original-context.png').convert('RGBA'));original=ctx[:,:,:3];known=ctx[:,:,3]==255
# This selected source already contains exact outer returns and the combined color cap.
a=np.rint(a).clip(0,255).astype('uint8')
assert np.array_equal(a[:,:51],original[:,:51]) and np.array_equal(a[:,1088:],original[:,1088:]) and np.array_equal(a[1235:],original[1235:])
png('r04_c01-joined.png',a);png('r04_c01-core1024.png',a[115:1139,115:1139])
cp=read(T/'source-checkpoint.json');fb=cp['fragment']['tileLocalLTRB'];f=np.asarray(Image.open(cp['fragment']['file']).convert('RGBA'));b=np.asarray(Image.open(cp['bottom']['file']).convert('RGB'))
assert sha(cp['fragment']['file'])==cp['fragment']['sha256'] and sha(cp['bottom']['file'])==cp['bottom']['sha256']
assert np.array_equal(f[2957-fb[1]:4096-fb[1],909-fb[0]:1139-fb[0],:3],original[:1139,1024:]) and np.array_equal(b[:115,:1139],original[1139:,115:])
sources=read(P/'preparation.json')['nativeInputs'];left=sources[1];corner=sources[3]
assert sha(left['file'])==left['sha256'] and sha(corner['file'])==corner['sha256']
spec=[('new-r08_c10.png',[115,0,1024,1139],'r08_c10',[0,2957,909,4096],None),('return-r08_c10.png',[1024,0,1088,1139],'r08_c10',[909,2957,973,4096],cp['fragment']),('return-r08_c09.png',[51,0,115,1139],'r08_c09',[4032,2957,4096,4096],left),('return-r09_c10.png',[115,1139,1088,1235],'r09_c10',[0,0,973,96],cp['bottom']),('return-r09_c09.png',[51,1139,115,1235],'r09_c09',[4032,0,4096,96],corner)]
patches=[]
for n,crop,tile,box,prior in spec:
 x0,y0,x1,y1=crop;png(n,a[y0:y1,x0:x1]);patches.append({'asset':info(O/n),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
qa=[('qa-bottom-return.png',a[1011:]),('qa-left-return.png',a[:1139,:320]),('qa-right-return.png',a[:1139,896:]),('qa-upper-overlap.png',a[384:768]),('qa-left-corner.png',a[820:1020,:300]),('qa-bottom-corners.png',np.concatenate([a[1040:1254,:320],a[1040:1254,934:]],1))]
for n,pixels in qa:png(n,pixels)
lum=lambda z:z@np.array([.2126,.7152,.0722]);al=lum(a.astype(float));cl=lum(original.astype(float));edge_points=[]
for x in range(110,115):
 orig=int(np.flatnonzero(cl[880:940,x]>=250)[-1])+880;new=int(np.flatnonzero(al[880:940,x]>=250)[-1])+880;edge_points.append({'x':x,'originalLastBrightY':orig,'joinedLastBrightY':new,'delta':new-orig})
measure=[]
for oldy in [1139,1143,1162,1187,1212,1232]:
 g=np.diff(cl[max(1139,oldy-3):oldy+4].mean(0));j=np.diff(al[max(1139,oldy-3):oldy+4].mean(0));w=650+int(np.argmax(g[650:930]));d=w-65+int(np.argmax(-g[w-65:w-25]));le=100+int(np.argmax(-g[100:260]))
 for label,x,pol in [('right-gray-to-dark',d,-1),('right-dark-to-ivory',w,1),('left-gray',le,-1)]:
  q=x-5+int(np.argmax(pol*j[x-5:x+6]));measure.append({'oldWindowY':oldy,'edge':label,'originalX':x,'joinedX':q,'delta':q-x})
write('source-checkpoint-snapshot.json',cp)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'joined':info(O/'r04_c01-joined.png'),'core':info(O/'r04_c01-core1024.png'),'windowTileLocalLTRB':[-115,2957,1139,4211],'windowGlobalLTRB':[36749,31629,38003,32883],'coreTileLocalLTRB':[0,3072,1024,4096],'coreGlobalLTRB':[36864,31744,37888,32768],'patches':patches,'sourceAssembly':info(P/'left-repair-v1/assembly.json'),'additionalOperation':'Upper overlap oldrows512..639 exact native outer return using same64px C1 side profile','nativeScale':1,'sourceCheckpoint':info(O/'source-checkpoint-snapshot.json'),'sourceROIStillMatchesCurrent':True,'joinedIntoCurrent':False,'formalAccepted':False,'geometryAndNavigationAcceptance':False,'pendingIndependentVisualReview':True,'preexistingSourceIssues':['Horizontal tone step in left c09 native strip at oldwindowy115','Horizontal tone step in c09 native strip at oldwindowy1139; inherited c08 couple WIP, not formal accepted'],'newImageModelCallsThisExport':0}
manifest['additionalOperation']='Native-sized AI micro-corner highlight repair from corner-repair-v2; exact outer returns and color cap inherited from final-v2'
manifest['microCornerRepair']=info(P/'corner-repair-v2/parameters.json')
manifest['combinedMechanicalColorLimit']=12
manifest['combinedColorCap']=read(P/'final-v2/manifest.json')['combinedColorCap']
manifest['cornerMaxAIAlignmentDx']=read(P/'corner-repair-v2/parameters.json')['maxInverseDxWithinSelectedPixels']
write('manifest.json',manifest)
write('measurements.json',{'leftWhiteHighlight':edge_points,'bottomContours':measure,'maxLeftBrightEndpointResidual':max(abs(p['delta']) for p in edge_points),'maxBottomContourResidual':max(abs(p['delta']) for p in measure),'exactNativeOuterColumns':[0,51,1088,1254],'exactNativeAfterRow':1235,'leftMaterialSeamRGBP95':np.percentile(np.abs(a[500:820,115].astype(float)-a[500:820,114]),95,axis=0).tolist(),'nativePixelChecksPerformed':True,'dimensions':[1254,1254],'sourceROIMatchesCurrent':True})
generations=[info(P/'native.png.generation.json'),info(P/'repaired-v1/native.png.generation.json'),info(P/'shifted-v1/native.png.generation.json'),info(P/'shifted-curve-v2/native.png.generation.json'),info(P/'shifted-native999-v3/native.png.generation.json'),info(P/'shifted-released-v4/native.png.generation.json'),info(P/'left-repair-v1/native.png.generation.json')]
for p in O.glob('*.png'):
 write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'generatedAt':None,'derivedAtUtc':datetime.now(timezone.utc).isoformat(),'newModelCalls':0,'actualModel':None,'actualQuality':None,'sources':generations,'operation':'Native-sized composition, exact crop or return strip; no resize/upscale','manifest':info(O/'manifest.json'),'formalAccepted':False,'pendingVisualReview':True})
write('generation-chain.json',{'count':7,'route':'builtin','records':generations,'selected':['repaired-v1 upper warm slab','shifted-curve-v2 shifted lower complete paired contours, bounded mechanical alignment','left-repair-v1 material only'], 'rejectedAsStandalone':['initial native gray middle/wide mismatch','repaired-v1 lower40px+ mismatch','shifted-v1 bevel narrowed','shifted-native999-v3 lower26px mismatch','shifted-released-v4 lower23px mismatch','left-repair-v1 geometry redrawn outside mask; only flat stone material selected'],'diagnosticCaveats':['shifted-curve-v2 and shifted-released-v4 top_retained statistics include transparent pixels and are invalid as geometric evidence','shifted-released-v4 top_warm ROI extends beyond retained island and is invalid as native-color evidence'],'actualModel':None,'actualQuality':None,'configuredTargetModel':'gpt-image-2.5-sunburst','configuredTargetQuality':'max'})
print(json.dumps({'joined':manifest['joined'],'measurements':read(O/'measurements.json'),'patchCount':len(patches)},ensure_ascii=False))
