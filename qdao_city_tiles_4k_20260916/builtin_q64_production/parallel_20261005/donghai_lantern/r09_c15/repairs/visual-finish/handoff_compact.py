"""Freeze existing r09 evidence for the 6x6 layout migration. No generation."""
from pathlib import Path
import json, numpy as np
from PIL import Image
import repair as r
B=r.B
c=r.read(B/'contract.json');t=r.T
assert r.sha(c['baseCore']['file'])==c['baseCore']['sha256']
assert r.sha(c['baseExtended']['file'])==c['baseExtended']['sha256']
assert r.sha(c['northImmutable']['file'])==c['northImmutable']['sha256']
current=r.img(c['extendedContext']['file']);core=r.img(c['candidate']['file'])
replay=r.img(c['baseExtended']['file']);coverage=np.zeros(current.shape[:2],bool)
for op in c['operations']:
 for k in ['native','record','mask']:assert r.sha(op[k]['file'])==op[k]['sha256']
 z=np.load(op['mask']['file']);a=z['alpha'].astype(np.float32)/65535;x,y=map(int,z['origin'])
 sub=replay[y+115:y+1369,x+115:x+1369]
 sub[:]=np.rint(sub.astype(np.float32)*(1-a[...,None])+r.img(op['native']['file']).astype(np.float32)*a[...,None]).clip(0,255).astype(np.uint8)
 coverage[y+115:y+1369,x+115:x+1369]|=z['alpha']>0
assert np.array_equal(replay,current)
assert np.array_equal(current[115:4211,115:4211],core)
assert np.array_equal(current[~coverage],r.img(c['baseExtended']['file'])[~coverage])
samples=[
 ('pier-deck',[0,0,1254,1254],'木栈桥地板、立柱裁边与斜向护栏；北边旧外缝未修，不可直接作为新北边界。'),
 ('capped-pier-landmark',[1700,0,2954,1254],'蓝色套环木柱顶及栈桥外缘；辨识性最高的现有地标，可按原尺寸提取。'),
 ('pier-elbow-support',[1550,1250,2804,2504],'横梁转角、支柱与水面关系；可作为结构组合原尺寸候选，内部整合最终复核未完成。'),
 ('east-open-water',[2842,1500,4096,2754],'东侧开阔蓝水与已修横向水缝；可作水材质候选，禁止当作新河道拓扑。'),
 ('foreground-rail-water',[1650,2842,2904,4096],'前景横栏、水面与真实柱影；可作原尺寸局部组合，不能推断栏外道路。')]
out=[]
for name,box,note in samples:
 p=B/'handoff-6x6/evidence'/f'{name}.png'
 a=core[box[1]:box[3],box[0]:box[2]];r.save(p,a)
 d={**r.ref(p),'source':c['candidate'],'sourceCropXYXY':box,'sourceGlobalXYXY':[box[0]+57344,box[1]+32768,box[2]+57344,box[3]+32768],'pixels':list(Image.open(p).size),'exactSourcePixels':True,'resampled':False,'note':note,'actualView':'pending'}
 r.write(str(p)+'.json',d);out.append(d)
natives=[]
for p in sorted((t/'native').glob('*.png')):
 d=r.read(str(p)+'.generation.json');rr=int(p.stem[1:3]);cc=int(p.stem[5:7])
 natives.append({**r.ref(p),'record':r.ref(str(p)+'.generation.json'),'pixels':list(Image.open(p).size),'sourceTileRectXYXY':[(cc-1)*1024-115,(rr-1)*1024-115,(cc-1)*1024+1139,(rr-1)*1024+1139],'placementInNewLayout':None,'actualModel':d.get('actualModel'),'actualQuality':d.get('actualQuality')})
report={'createdAtUtc':r.now(),'taskStatus':'stopped at tool boundary for authorized 6x6 migration','oldGrid':[16,16],'newGrid':[6,6],'newTilePixels':[4096,4096],'newLayoutFrozen':False,'newLayoutPlacementAssigned':False,'newGenerationStarted':False,'builtinInFlight':False,'savedInternalRepairCount':len(c['operations']),'northRepairStarted':False,'northGeometrySyncPending':True,'final45AffectedWindowReviewComplete':False,'formalAccepted':False,'candidate':c['candidate'],'halo':c['extendedContext'],'baselineCore':c['baseCore'],'baselineHalo':c['baseExtended'],'immutableNorth':c['northImmutable'],'repairContract':r.ref(B/'contract.json'),'initial45Review':r.ref(t/'qa/tone-candidate-e6988dea-full45-review.json'),'sourceContract':r.ref(t/'source-contract.json'),'lockedDayLayoutPlan':r.ref(t/'source-lock/day-r09_c15-plan.json'),'oldCoordinates':{'tile':'r09_c15','coreGlobalXYWH':[57344,32768,4096,4096],'haloGlobalXYWH':[57229,32653,4326,4326],'nativePixels':[1254,1254],'nativeStride':1024,'halo':115,'overlap':230,'mapToNew6x6':None},'verification':{'exactMaskReplayEqualsSavedHalo':True,'coreEqualsHaloCrop':True,'outsideSavedMaskUnionRGBUnchanged':True,'baselineAndNorthHashesUnchanged':True,'savedRepairNativesOriginal1254':True,'mechanicalRGBFieldMax':0,'imageResampled':False,'imageBlurred':False},'reusableExactPixelSamples':out,'originalNativeInventory':natives,'repairInventory':c['operations'],'boundaryMappingEvidence':{'coordinates':'tile local pixels; approximate visual topology, not collision polygons','landmarks':[{'name':'blue-collar wooden mooring post','roi':[1900,0,2480,1580]},{'name':'gray-capped near wooden post','roi':[540,1250,1120,3360]},{'name':'outer corner long support post','roi':[2300,1300,2850,3070]}],'walkway':{'description':'northwest timber pier deck enters north and west edges; diagonal outer edge leads to central corner, front cross-beam spans left to corner','approximateDeckPolygon':[[0,0],[870,0],[2000,1230],[2340,1600],[0,2020]],'roadOutsideVisibleDeck':'not evidenced; no navmesh acceptance'},'water':{'eastBoundary':'all visible east edge is water; open-water continuity except natural faint upper broad planes','northBoundary':'west timber pier plus open water to east; known r08 north warmth/reflectance and plank gap mismatch remain','westBoundary':'upper pier/deck, mid water/supports, lower cropped foreground wood; not an uninterrupted waterway','southBoundary':'foreground timber rail spans most of edge; cannot infer passable water exit beneath/behind railing','newWaterwayTopology':'unassigned until new 6x6 layout lock'},'knownReuseLimitations':['Do not scale full old65536 layout into new24576 map. Reuse actual1254/4K pixels at1:1 in a newly frozen layout.','Old candidate is not formally accepted: internal repairs are applied and source replay verified, but final affected45-window review was cancelled by migration instruction.','North true-pair repair never started; existing external mismatch cannot be inherited as passed.','Local AI repair returns were actually viewed; completed native returns alone do not certify integrated edges.']}}
r.write(B/'handoff-6x6/reuse-evidence.json',report)
print(json.dumps({'report':r.ref(B/'handoff-6x6/reuse-evidence.json'),'candidate':c['candidate'],'halo':c['extendedContext'],'sampleFiles':[x['file']for x in out],'verified':report['verification']},ensure_ascii=False))
