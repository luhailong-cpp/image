from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=lambda:datetime.now(timezone.utc).isoformat()
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'));src=cp['fragment'];win=[1933,1933,3187,3187]
ctx=np.array(Image.open(src['file']).convert('RGBA').crop(win));j=np.array(Image.open(O/'joined.png').convert('RGBA'))
assert j.shape==(1254,1254,4) and np.all(j[:,:,3]==255)
specs=[('new-core',[230,0,1024,1024],False),('left-return',[180,880,230,1226],True),('bottom-return',[230,1024,1024,1226],True),('right-return',[1024,0,1226,1226],True)]
patches=[];mask=np.zeros((1254,1254),bool)
for name,b,prior in specs:
 l,t,r,bt=b
 if prior:assert np.all(ctx[t:bt,l:r,3]==255)
 else:assert np.all(ctx[t:bt,l:r,3]==0)
 path=O/(name+'.png');Image.fromarray(j[t:bt,l:r]).save(path)
 patches.append({'name':name,'asset':info(path),'cropFromJoinedLTRB':b,'destinationTile':'r08_c10','destinationTileLTRB':[b[0]+1933,b[1]+1933,b[2]+1933,b[3]+1933],'requiredPriorSource':src if prior else None,'nativeScale':1,'mustApplyTogether':True})
 mask[t:bt,l:r]=True
outside=(ctx[:,:,3]==255)&~mask
assert np.array_equal(j[outside],ctx[outside])
write(O/'source-checkpoint-input.json',cp)
derived=[info(P/'upper-repair-v4/joined.png'),info(P/'registration-v3/aligned-native.png'),src]
review={'reviewedAtUtc':now(),'reviewer':'Codex finish_mid_patch','image':info(O/'joined.png'),'localVisualAccepted':True,'localAccepted':True,'integrationReady':True,'formalAccepted':False,'complete4KTile':False,
 'viewedAtNativePixelScale':[{**info(p),'nativeScale':1} for p in sorted((O/'qa').glob('*.png'))],
 'observations':['Crossband bevels restored by the existing actual AI repair; <=3px correspondence correction and bounded face matching removed rectangular returns.','Top-left latestc02 bevel repaired with actual built-in generation upper-repair-v4. Top upright slab separators retained. The new gray-inset vertical return aligned by max6.5px horizontal, max2px vertical, then joined on matched surfaces.','Old bottom ownership cut left a visible tonalstep despite geometric correspondence. An explicit202px coupled return now carries its matched stone faces continuously back to currentpixels; secondary alignment is <=0.533px.','Right cloud relief color rectangle cleared with explicit202px coupled return after <=2px residual registration. Cloud contours and carved shadows are continuous in native pixel crops.','Full1254, left strip, upperleft, crossband, bottom strip, lowergray/channel, right strip and lowercorners were visually inspected. No visible abrupt contour step, doubled edge or material rectangle remains in these inspected local returns.'],
 'limits':['Only this1254x1254 native window and declared three currentreturns inspected. No complete4K tile or city acceptance.','Upper edge continues into a still-missing neighboring field and needs review when that field is generated.','Inherited graystone fine veins are unchanged outside local repair; not used as new style reference.']}
write(O/'visual-review.json',review)
ass={'createdAtUtc':now(),'image':info(O/'joined.png'),'nativeScale':1,'windowTileLocalLTRB':win,'derivedFrom':derived,'newAICallsInThisStage':3,'adoptedNewAICallsInThisStage':1,
 'adoptedAIRecord':info(P/'upper-repair-v4/native.png.generation.json'),'priorCrossbandAIRecord':info(P/'r03_c03-repair-v1/native.png.generation.json'),'initialNativeRecord':info(P/'native.png.generation.json'),
 'operation':'Native1:1 source stitching; actualAI for missingbevelstructure, bounded correspondence fields and surface RGB matching, explicitreturn ownership. No enlargement.',
 'fieldLimits':{'inheritedMainRegistrationHorizontalMaxPx':20,'inheritedLeftCrossbandVerticalMaxPx':10,'crossbandRepairHorizontalMaxPx':1,'crossbandRepairVerticalMaxPx':3,'topBaseRegistrationVerticalMaxPx':11,'adoptedTopRepairHorizontalMaxPx':6.5,'adoptedTopRepairVerticalMaxPx':2,'finalBottomResidualHorizontalActualMaxPx':float(abs(np.load(O/'flow.npy')).max()),'finalRightResidualActualXYMaxPx':abs(np.load(O/'right-flow.npy')).max((0,1)).tolist(),'toneMaxPerStageRGB':12,'resampling':'OpenCV INTER_CUBIC remap; nativecanvas1254 retained'},
 'sourceOwnership':{'prior':src,'newROI':[230,0,1024,1024],'returns':[b for _,b,r in specs if r],'outsideReturnsKnownPixelIdentical':True,'outsideReturnsKnownPixelCount':int(outside.sum()),'newMissingPixels':794*1024},
 'scripts':[info(O/'finish.py'),info(P/'upper-repair-v4/join.py'),info(P/'final-registration-v1/register.py')],
 'fields':[info(p) for p in [O/'flow.npy',O/'tone.npy',O/'mask.png',O/'right-flow.npy',O/'right-tone.npy',O/'right-mask.png',P/'upper-repair-v4/field.npy',P/'upper-repair-v4/tone.npy',P/'upper-repair-v4/mask.png',P/'final-registration-v1/repair-field.npy',P/'final-registration-v1/top-field.npy',P/'final-registration-v1/repair-tone.npy',P/'final-registration-v1/left-tone.npy',P/'final-registration-v1/repair-mask.png']],
 'visualReview':info(O/'visual-review.json'),'localAccepted':True,'formalAccepted':False}
write(O/'assembly.json',ass)
manifest={'createdAtUtc':now(),'appearance':'tianyong_festival','tile':'r08_c10','nativeScale':1,'windowTileLocalLTRB':win,'joined':info(O/'joined.png'),'visualReview':info(O/'visual-review.json'),'assembly':info(O/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':info(O/'source-checkpoint-input.json'),'note':'Allthree returns andnewcore must be applied together againstROI-verified current sources. Rootcommit only.'}
write(O/'manifest.json',manifest)
for p in O.rglob('*.png'):
 rec={'file':str(p),'sha256':sha(p),'generatedAt':None,'derivedAtUtc':now(),'derivedFrom':derived if p.name in ['joined.png','context.png'] else [info(O/'joined.png')],'actualModel':None,'actualQuality':None,'newModelCalls':0,'operation':'Native-scale crop/composition/QA from cited sources; no generation','assembly':info(O/'assembly.json'),'nativeScale':1,'formalAccepted':False}
 if p.name.endswith('mask.png'):rec['operation']='Mechanicalpixelownershipmask derivedfromscript, not artwork'
 write(Path(str(p)+'.generation.json'),rec)
# Fill derived-chain links on adopted intermediates without changing existing
# native-generation records.
for folder,sources,assembly in [(P/'final-registration-v1',[info(P/'registration-v3/joined.png'),info(P/'r03_c03-repair-v1/native.png'),src],P/'final-registration-v1/assembly.json'),(P/'upper-repair-v4',[info(P/'upper-repair-v4/native.png'),info(P/'final-registration-v1/joined.png')],O/'assembly.json')]:
 for p in folder.rglob('*.png'):
  recp=Path(str(p)+'.generation.json')
  if recp.exists():continue
  write(recp,{'file':str(p),'sha256':sha(p),'generatedAt':None,'derivedAtUtc':now(),'derivedFrom':sources,'actualModel':None,'actualQuality':None,'newModelCalls':0,'nativeScale':1,'operation':'Nativecrop/registration/stitching orQA mask; seeassemblyscript','assembly':info(assembly),'formalAccepted':False})
write(O/'qa/manifest.json',[{**info(p),'nativeScale':1} for p in sorted((O/'qa').glob('*.png'))])
print(json.dumps({'manifest':info(O/'manifest.json'),'joined':info(O/'joined.png'),'checkpointVersion':cp['version'],'checkpointSha256':sha(T/'source-checkpoint.json'),'newPixels':794*1024,'knownOutsideExact':True}))

