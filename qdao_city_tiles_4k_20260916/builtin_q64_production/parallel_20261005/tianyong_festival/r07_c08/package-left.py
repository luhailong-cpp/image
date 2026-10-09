from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
from PIL import Image
import numpy as np
N=Path(__file__).parent;T=N.parent;D=N/sys.argv[1];F=D/sys.argv[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
prep=read(D/'preparation.json');req=read(D/'request.json');previous=read(D/'source-checkpoint-input.json')
local=req['tileLocalCropLTRB'];world=req['globalCropLTRB'];x0,y0,x1,y1=local;k=prep['knownStartX'];end=k+176;assert end<=1254 and y0==2957 and x0>=0 and x0+end<=4096
J=Image.open(F/'joined.png').convert('RGB')
for source in prep['sources'].values():assert sha(source['file'])==source['sha256']
now=datetime.now(timezone.utc).isoformat();assembly=read(F/'assembly.json');assembly.update(visualReviewPending=False,localVisualAccepted=True);save(F/'assembly.json',assembly)
review={'reviewedAtUtc':now,'image':ref(F/'joined.png'),'nativePixelInspection':True,'reviewMethod':'Actual visual inspection of full1254 native composite, full vertical boundary strip, bottom strip, and any detail crops. Registration is recorded in assembly.','inspectedImages':[ref(F/'qa'/f) for f in ('full.png','right.png','bottom.png','relief.png') if (F/'qa'/f).exists()],'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['Canonical panel layout and bevel endpoints preserved. Main ivory rail now joins existing native geometry without repeated/doubled edge or step.','Lower cloud-knot relief is newly AI rendered sharp native detail; no guide pixels are included in final. Quiet rounded warm stone and slate remain consistent.','Right and bottom edge channels visually continuous; fixed exterior pixels restored exactly by recorded mask.'],'limitations':['Partial r07_c08 tile only; whole tile and outside neighbours remain pending.'],'modelDisclosure':'Actual model and quality unconfirmed; built-in host exposes no selectors/identifiers.'}
review.update(read(F/'review-notes.json')) if (F/'review-notes.json').exists() else None
save(F/'visual-review.json',review)
specs=[('new-core',[0,0,k,1139],'r07_c08',[x0,2957,x0+k,4096],None),('right-return',[k,0,end,1139],'r07_c08',[x0+k,2957,x0+end,4096],prep['sources']['r07_c08']),('bottom-return',[0,1139,end,1200],'r08_c08',[x0,0,x0+end,61],prep['sources']['r08_c08'])]
patches=[];root=read(T/'source-checkpoint.json');latest={v['tile']:v for v in root['candidateSet']};checks=[]
for key,source in prep['sources'].items():
 if key not in latest:latest[key]=source
for name,crop,tile,dest,prior in specs:
 p=F/(name+'.png');J.crop(crop).save(p)
 if prior:
  assert sha(latest[tile]['file'])==latest[tile]['sha256']
  actual=Image.open(latest[tile]['file']).convert('RGBA').crop(dest).tobytes();expected=Image.open(prior['file']).convert('RGBA').crop(dest).tobytes()
  checks.append({'tile':tile,'roi':dest,'latestSource':latest[tile],'exact':actual==expected})
 patches.append({'name':name,'asset':ref(p),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 save(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'1:1 exact crop of native-scale registered composite','derivedFrom':[dict(ref(F/'joined.png'),generationRecord=str(F/'joined.png.generation.json'))],'cropLTRB':crop,'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None})
m={'createdAtUtc':now,'appearance':'tianyong_festival','tile':'r07_c08','tileGlobalOrigin':[28672,24576],'nativeScale':1,'windowTileLocalLTRB':local,'windowGlobalLTRB':world,'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['sourceCheckpoint'],'previousManifest':prep['previousManifest'],'externalReturnDependencies':prep['externalReturnDependencies'],'lastRootRoiCheck':{'file':str(T/'source-checkpoint.json'),'sha256':sha(T/'source-checkpoint.json'),'allRequiredExternalROIsExact':all(c['exact'] for c in checks),'checks':checks},'note':'Sequential application after previous manifest, all explicit ROI patches together. Prospective source is frozen chain context, never whole-tile replacement. Root must exact-check required prior ROI.'}
save(F/'manifest.json',m)
save(F/'joined.png.generation.json',{'file':str(F/'joined.png'),'sha256':sha(F/'joined.png'),'operation':'AI-redrawn native image plus exact native source blend; any registration explicitly recorded in assembly','derivedFrom':[dict(ref(Path(assembly['native']['file'])),generationRecord=assembly['native']['file']+'.generation.json'),dict(ref(D/'context.png'),generationRecord=str(D/'context.png.generation.json'))],'assembly':ref(F/'assembly.json'),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'formalAccepted':False})
fragment=Image.open(prep['sources']['r07_c08']['file']).convert('RGBA');assert not np.array(fragment)[2957:4096,x0:x0+k,3].any()
fragment.paste(J.crop((0,0,end,1139)).convert('RGBA'),(x0,2957));fragment.save(F/'r07_c08-fragment.png')
coverage=int((np.array(fragment)[:,:,3]==255).sum())
save(F/'r07_c08-fragment.png.generation.json',{'file':str(F/'r07_c08-fragment.png'),'sha256':sha(F/'r07_c08-fragment.png'),'operation':'1:1 explicit local ROI placement retaining current fragment outside patches; unknown pixels transparent','derivedFrom':[prep['sources']['r07_c08'],ref(F/'joined.png')],'manifest':ref(F/'manifest.json'),'nativeScale':1,'actualModel':None,'actualQuality':None,'formalAccepted':False})
prospective=Image.open(prep['sources']['r08_c08']['file']).convert('RGBA');prospective.paste(J.crop((0,1139,end,1200)).convert('RGBA'),(x0,0));prospective.save(F/'prospective-r08_c08.png')
save(F/'prospective-r08_c08.png.generation.json',{'file':str(F/'prospective-r08_c08.png'),'sha256':sha(F/'prospective-r08_c08.png'),'operation':'Prospective native ROI overlay for next context only; never replace a root-published whole tile with this snapshot.','derivedFrom':[prep['sources']['r08_c08'],ref(F/'bottom-return.png')],'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False})
save(N/'local-source-checkpoint.json',{'createdAtUtc':now,'tile':'r07_c08','fragment':ref(F/'r07_c08-fragment.png'),'nativeScale':1,'coveragePixels':coverage,'formalAccepted':False,'rootPublished':False,'manifest':ref(F/'manifest.json'),'contextJoined':ref(F/'joined.png'),'prospectiveBottom':dict(ref(F/'prospective-r08_c08.png'),tile='r08_c08'),'externalReturnDependencies':prep['externalReturnDependencies']+[ref(F/'manifest.json')],**({'prospectiveRight':previous['prospectiveRight']} if 'prospectiveRight' in previous else {})})
print(json.dumps({'manifest':ref(F/'manifest.json'),'fragment':ref(F/'r07_c08-fragment.png'),'coveragePixels':coverage,'rootPriorExact':all(c['exact'] for c in checks)}))
