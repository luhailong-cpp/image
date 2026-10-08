"""Complete independent QA and explicit placement manifest for a reviewed patch.

Writes only this patch directory. Does not publish the root checkpoint.
"""
from pathlib import Path
import hashlib,json,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
D=P.parent
T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
checkpoint=read(T/'source-checkpoint.json')
prior=checkpoint['fragment']
assert sha(prior['file'])==prior['sha256']
assert sha(D/'native.png')=='e7a836aded791a782ab7cb14af412cd8d34b11ae61172192854a27cedc50a888'
assert sha(P/'joined.png')=='6a1242f81db6af2e08942edec09b3391d84b80e44a062faf9e9e5814271f5cae'
a=np.array(Image.open(prior['file']).convert('RGBA'))
c=np.array(Image.open(D/'context.png').convert('RGBA'))
n=np.array(Image.open(D/'native.png').convert('RGB'))
j=np.array(Image.open(P/'joined.png').convert('RGB'))
assert prior['tileLocalLTRB']==[0,0,4096,4096]
assert np.all(a[0:1139,909:1933,3]==0)
assert np.array_equal(a[0:1139,1933:2163],c[115:,1024:])
assert np.array_equal(j[:,1104:],c[:,1104:,:3])
assert np.array_equal(j[:,:620],n[:,:620])
flow=np.load(P/'flow.npy');tone=np.load(P/'tone.npy')
assert np.abs(flow[:,:,0]).max()<=8 and np.abs(flow[:,:,1]).max()<=5
assert np.abs(tone).max()<=12
assembly=read(P/'assembly.json')
for r in assembly['source']+assembly['fields']+[assembly['script'],assembly['output']]:
 assert sha(r['file'])==r['sha256'],r
verified={
 'createdAtUtc':now,'checkpoint':ref(T/'source-checkpoint.json'),'checkpointVersion':checkpoint['version'],
 'priorSource':prior,'contextSource':ref(D/'context.png'),
 'newRegionTileLocalLTRB':[909,0,1933,1139],
 'allNewRegionPixelsMissing':True,'newNativePixels':1024*1139,
 'returnContextTileLocalLTRB':[1933,0,2163,1139],
 'rightContextMatchesLatestCheckpoint':True,
 'unchangedKnownColumnFrom':1104,'exactKnownPixelsPreserved':150*1254,
 'nativeUnchangedColumns':[0,620],'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),
 'actualMaxToneRGB':np.abs(tone).max(axis=(0,1)).tolist(),
 'actualMaxAdjacentFieldChangeAcrossX':np.abs(np.diff(flow,axis=1)).max(axis=(0,1)).tolist(),
 'actualMaxAdjacentFieldChangeAcrossY':np.abs(np.diff(flow,axis=0)).max(axis=(0,1)).tolist(),
 'nativeScale':1,'noUpscale':True,'noLayoutReferencePixels':True,
 'newModelCalls':0,'writtenOnlyInsidePatch':True
}
write(P/'independent-source-validation.json',verified)
qa=[ref(P/f) for f in ['right-return-474x1254.png','upper-return.png','lower-rim-return.png','lower-joint-return.png','bottom-return.png','corner-independent-review.png']]
review={
 'reviewedAtUtc':now,'image':ref(P/'joined.png'),
 'reviewMethod':'Viewed full native and joined image, complete right return at native pixel size, upper paving joint, center rounded joint, lower rim and bottom return; independent corner comparison reviewed at 1:1.',
 'inspectedImages':qa,'sourceValidation':ref(P/'independent-source-validation.json'),
 'registrationAssembly':ref(P/'assembly.json'),
 'findings':[
  'Existing registration-v1 uses complete corresponding native structures, inverse shifts <=8px x / <=5px y over a 404px smooth approach; no missing geometry was mechanically invented.',
  'The visible wave in the older automatic join is absent in the reviewed registration-v1. The long beveled rim, rounded central paving intersection and narrow grooves continue without a visible double edge or abrupt slope change.',
  'The complete right return remains continuous in shape and warm ivory material; known context from x1104 remains pixel-exact.',
  'The older one-dimensional minimum test reports a 17px residual at x1065 because its search window selects a different branch of the rounded junction. This is not a reliable corresponding contour measurement; acceptance uses the viewed two-dimensional junction and the source-preservation proof.',
  'The new region and 80px changed known return must be committed together. Top115px is preserved as same-world context in joined.png but is outside the active tile and is not exported to an unowned neighbor.'
 ],
 'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,
 'limitations':['This review accepts only this native patch and its changed right return. Whole 4K tile, exterior neighbors, whole-city navigation and runtime remain outside this review.'],
 'actualModel':None,'actualQuality':None,'newModelCalls':0
}
write(P/'visual-review.json',review)
patches=[]
for name,crop,dest,required in [
 ('new-placement.png',[0,115,1024,1254],[909,0,1933,1139],None),
 ('right-return-placement.png',[1024,115,1104,1254],[1933,0,2013,1139],prior),
]:
 image=Image.fromarray(j).crop(crop);image.save(P/name)
 write(P/(name+'.generation.json'),{'file':str(P/name),'sha256':sha(P/name),'derivedAtUtc':now,'derivedFrom':[ref(P/'joined.png')],'operation':'Exact native 1:1 crop; no resize','cropFromJoinedLTRB':crop,'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1})
 patches.append({'asset':ref(P/name),'cropFromJoinedLTRB':crop,'destinationTile':'r08_c10','destinationTileLTRB':dest,'requiredPriorSource':required,'nativeScale':1,'mustApplyTogether':True})
manifest={
 'createdAtUtc':now,'joined':ref(P/'joined.png'),'windowTileLocalLTRB':[909,-115,2163,1139],
 'windowGlobalLTRB':[37773,28557,39027,29811],'patches':patches,
 'visualReview':ref(P/'visual-review.json'),'sourceValidation':ref(P/'independent-source-validation.json'),
 'localVisualAccepted':True,'formalAccepted':False,'nativeScale':1,
 'excludedUnchangedColumns':[1104,1254],
 'uncommittedTopHalo':{'joinedLTRB':[0,0,1254,115],'reason':'Outside active tile; retained only as original same-world context, no unowned neighbor is overwritten.'}
}
write(P/'manifest.json',manifest)
write(P/'corner-independent-review.png.generation.json',{'file':str(P/'corner-independent-review.png'),'sha256':sha(P/'corner-independent-review.png'),'derivedFrom':[ref(D/'native.png'),ref(D/'context.png'),ref(P/'joined.png')],'operation':'Native/context/joined comparison of crop [940,570,1180,810], each pasted 1:1','newModelCalls':0,'actualModel':None,'actualQuality':None})
print(json.dumps({'manifest':ref(P/'manifest.json'),'joined':ref(P/'joined.png'),'sourceValidation':ref(P/'independent-source-validation.json'),'newPixels':verified['newNativePixels'],'review':ref(P/'visual-review.json')},ensure_ascii=False))
