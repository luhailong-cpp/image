from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;D=P.parent;T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();prior=read(D/'source-checkpoint-input.json');current=read(T/'source-checkpoint.json')
assert prior['version']=='v012'
j=np.array(Image.open(P/'joined.png').convert('RGB'));c=np.array(Image.open(D/'context.png').convert('RGBA'))
assert sha(P/'joined.png')=='f900a18fde0f2f7f141838aa1cc50cc5a24ccf533235a57cbd5d366fe693df99'
pf=prior['fragment'];pl=prior['coupledNeighbors']['r08_c09'];cf=current['fragment'];cl=current['coupledNeighbors']['r08_c09']
arrays=[]
for r in [pf,pl,cf,cl]:
 assert sha(r['file'])==r['sha256'];arrays.append(np.array(Image.open(r['file']).convert('RGBA')))
af,al,bf,bl=arrays
assert np.all(bf[0:1139,0:909,3]==0)
assert np.array_equal(af[0:1139,909:1139],bf[0:1139,909:1139])
assert np.array_equal(al[0:1139,3981:4096],bl[0:1139,3981:4096])
assert np.array_equal(c[115:,1024:],bf[0:1139,909:1139])
assert np.array_equal(c[115:,:115],bl[0:1139,3981:4096])
assert np.array_equal(j[:,1104:],c[:,1104:,:3])
assert np.array_equal(j[115:,:35],c[115:,:35,:3])
flow=np.load(P/'flow.npy');tone=np.load(P/'tone.npy');assert np.abs(flow).max()<=1 and np.abs(tone).max()<=12
validation={'checkedAtUtc':now,'currentCheckpoint':ref(T/'source-checkpoint.json'),'checkpointVersion':current['version'],'preparationCheckpoint':ref(D/'source-checkpoint-input.json'),'priorSourceFragment':pf,'priorLeftNeighbor':pl,'newRegionTileLocalLTRB':[0,0,909,1139],'newRegionEntirelyMissing':True,'newNativePixels':909*1139,'rightContextExactLatest':True,'leftContextExactLatest':True,'returnedSourcesHaveNoStaleROI':True,'knownPixelsPreserved':{'right':[1104,0,1254,1254],'left':[0,115,35,1254]},'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'actualMaxToneRGB':np.abs(tone).max(axis=(0,1)).tolist(),'nativeScale':1,'noLayoutReferencePixels':True,'noUpscale':True,'newModelCalls':0}
write(P/'source-validation.json',validation)
for folder,status,findings in [(D,'rejected_as_complete_patch',['The first native image invented an extra bright upper crossbar between the engraved slab and plain middle slab. Outer native pixels remain a valid compositing source for the selected final repair.']),(D/'repair-v1','rejected_as_complete_patch',['First correction recolored the unwanted upper bar but retained its separating seam; the structural repair remained incomplete.'])]:
 write(folder/'visual-review.json',{'reviewedAtUtc':now,'image':ref(folder/'native.png'),'localVisualAccepted':False,'status':status,'findings':findings,'selectedFinal':str(P/'joined.png'),'formalAccepted':False})
write(D/'repair-v2/visual-review.json',{'reviewedAtUtc':now,'image':ref(D/'repair-v2/native.png'),'localVisualAccepted':False,'status':'selected_partial_repair_source','findings':['The upper invented bar and its additional seam have been removed. The required lower bright bar remains.','The second edit subtly changed an existing middle-slab right bevel; only the requested repair area is adopted through the final source-preserving mask.'],'selectedFinal':str(P/'joined.png'),'formalAccepted':False})
qa=[ref(P/f) for f in ['left-full.png','right-full.png','left-upper.png','left-lower.png','right-upper.png','right-junction.png','right-cloud.png','repair-upper.png','top-full.png','bottom-full.png']]
review={'reviewedAtUtc':now,'image':ref(P/'joined.png'),'reviewMethod':'Viewed full native output, both AI repairs and joined output; inspected both complete edge returns, upper/lower corners, right paving junction and cloud relief at native size.','inspectedImages':qa,'sourceValidation':ref(P/'source-validation.json'),'assembly':ref(P/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['The extra upper ivory crossbar and its dividing seam were removed by AI. The upper engraved slab meets the larger plain slab at one narrow joint; the required lower crossbar remains.','Original source pixels outside the repair adoption bounds were restored before joining. The full left and right bevels, gray inset edges and carving contour remain continuous with current native context.','No visible double edge, wavy return, sudden bevel-width step or color rectangle is visible in the reviewed returns.','Only a <=1px vertical alignment was used on the left; no horizontal registration. Local tone correction is bounded by12. Right x1104 onward and left x0..35 for y115 onward are exact native context.','The new active-tile area and changed left/right returns form one indivisible patch set.'],'limitations':['Top115px and top-left corner have no committed row7 owner. They remain prospective same-world halo for future neighbor validation; this manifest does not overwrite any row7 tile.','Bottom adjacent missing region and whole4K/fullcity/runtime acceptance remain outside this local review.'],'newModelCallsForThisPatch':3,'actualModel':None,'actualQuality':None}
write(P/'visual-review.json',review)
specs=[('new-placement.png',[115,115,1024,1254],'r08_c10',[0,0,909,1139],None),('right-return-placement.png',[1024,115,1104,1254],'r08_c10',[909,0,989,1139],pf),('left-return-placement.png',[35,115,115,1254],'r08_c09',[4016,0,4096,1139],pl)]
patches=[]
for name,crop,tile,dest,required in specs:
 Image.fromarray(j).crop(crop).save(P/name)
 write(P/(name+'.generation.json'),{'file':str(P/name),'sha256':sha(P/name),'derivedAtUtc':now,'derivedFrom':[ref(P/'joined.png')],'operation':'Exact1:1 native crop, no resize','cropFromJoinedLTRB':crop,'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None})
 patches.append({'asset':ref(P/name),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':required,'nativeScale':1,'mustApplyTogether':True})
manifest={'createdAtUtc':now,'joined':ref(P/'joined.png'),'windowTileLocalLTRB':[-115,-115,1139,1139],'windowGlobalLTRB':[36749,28557,38003,29811],'patches':patches,'visualReview':ref(P/'visual-review.json'),'sourceValidation':ref(P/'source-validation.json'),'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'excludedUnchangedReturns':[{'joinedLTRB':[0,115,35,1254]},{'joinedLTRB':[1104,115,1254,1254]}],'uncommittedTopHalo':{'joinedLTRB':[0,0,1254,115],'reason':'No owned row7 baseline. Future-context-only; whole outer edge has not been validated.'}}
write(P/'manifest.json',manifest)
print(json.dumps({'manifest':ref(P/'manifest.json'),'joined':ref(P/'joined.png'),'review':ref(P/'visual-review.json'),'newPixels':909*1139,'checkpointObserved':current['version']}))
