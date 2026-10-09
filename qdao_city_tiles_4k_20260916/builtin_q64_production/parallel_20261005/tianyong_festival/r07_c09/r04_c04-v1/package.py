from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent;N=D.parent;T=N.parent;F=D/'final-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
prep=read(D/'preparation.json');req=read(D/'request.json');J=Image.open(F/'joined.png').convert('RGB')
assert sha(F/'joined.png')=='c170700708189af6077121ffd49b0d72d4201fa7b8afb35faa56466beecb5cc7'
now=datetime.now(timezone.utc).isoformat();assembly=read(F/'assembly.json');assembly['visualReviewPending']=False;assembly['localVisualAccepted']=True;save(F/'assembly.json',assembly)
review={'reviewedAtUtc':now,'image':ref(F/'joined.png'),'nativePixelInspection':True,'reviewMethod':'Viewed full1254 native image and complete right354x1254 and bottom1254x254 strips after AI geometry/material repairs and bounded registration.','inspectedImages':[ref(F/'qa'/f) for f in ('full.png','right.png','bottom.png')],'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['Single slate-gray lower-left inset now extends continuously to its real ivory frame. Invented horizontal joint removed by actual AI edit.','Right rail and beige inset contours remain continuous; bottom slate bevel, dark channel and ivory rail have no remaining visible diagonal step or double line in native inspection.','No enlarged guide pixels used. Generated-native pixels remain at1254 scale; bounded local registration uses recorded cubic resampling with maxDx15/maxDy24 and gradual fades.','Material veining remains compatible with inherited surrounding stone; no new object or physical seam introduced.'],'limitations':['Partial r07_c09 patch only; whole tile, all external neighbours, geometry/navigation and runtime acceptance pending.'],'modelDisclosure':'Actual model and quality unconfirmed; built-in host has no selectors or returned identifiers.'}
save(F/'visual-review.json',review)
specs=[('new-core',[0,0,1139,1139],'r07_c09',[2957,2957,4096,4096],None),('right-return',[1139,0,1200,1139],'r07_c10',[0,2957,61,4096],prep['sources']['r07_c10']),('bottom-return',[0,1139,1139,1200],'r08_c09',[2957,0,4096,61],prep['sources']['r08_c09']),('bottom-right-return',[1139,1139,1200,1200],'r08_c10',[0,0,61,61],prep['sources']['r08_c10'])]
patches=[];root=read(T/'source-checkpoint.json');latest={v['tile']:v for v in root['candidateSet']}
for name,crop,tile,dest,prior in specs:
 p=F/(name+'.png');J.crop(crop).save(p)
 if prior:
  assert sha(prior['file'])==prior['sha256'];assert sha(latest[tile]['file'])==latest[tile]['sha256']
  assert Image.open(prior['file']).convert('RGBA').crop(dest).tobytes()==Image.open(latest[tile]['file']).convert('RGBA').crop(dest).tobytes(),('latest required ROI changed',tile,dest)
  prior=dict(prior,tileLocalLTRB=[0,0,4096,4096],nativeScale=1)
 patches.append({'name':name,'asset':ref(p),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 save(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'1:1 exact crop from registered native composite','derivedFrom':[dict(ref(F/'joined.png'),generationRecord=str(F/'joined.png.generation.json'))],'cropLTRB':crop,'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None})
m={'createdAtUtc':now,'appearance':'tianyong_festival','tile':'r07_c09','tileGlobalOrigin':[32768,24576],'nativeScale':1,'windowTileLocalLTRB':[2957,2957,4211,4211],'windowGlobalLTRB':[35725,27533,36979,28787],'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['sourceCheckpoint'],'lastRootRoiCheck':{'file':str(T/'source-checkpoint.json'),'sha256':sha(T/'source-checkpoint.json'),'allRequiredExternalROIsExact':True},'note':'Apply new r07_c09 core and all three external returns together; only explicit ROI patches, never overwrite external full tiles with old snapshots.'}
save(F/'manifest.json',m)
save(F/'joined.png.generation.json',{'file':str(F/'joined.png'),'sha256':sha(F/'joined.png'),'operation':'AI-redrawn native image plus bounded local registration and exact native source return','derivedFrom':[dict(ref(D/'repair-v2/native.png'),generationRecord=str(D/'repair-v2/native.png.generation.json')),dict(ref(D/'context.png'),generationRecord=str(D/'context.png.generation.json'))],'assembly':ref(F/'assembly.json'),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'formalAccepted':False})
fragment=Image.new('RGBA',(4096,4096));fragment.paste(J.crop((0,0,1139,1139)).convert('RGBA'),(2957,2957));fragment.save(F/'r07_c09-fragment.png')
save(F/'r07_c09-fragment.png.generation.json',{'file':str(F/'r07_c09-fragment.png'),'sha256':sha(F/'r07_c09-fragment.png'),'operation':'1:1 placement with unknown pixels left transparent','derivedFrom':[ref(F/'joined.png')],'manifest':ref(F/'manifest.json'),'nativeScale':1,'actualModel':None,'actualQuality':None,'formalAccepted':False})
prospective=Image.open(prep['sources']['r08_c09']['file']).convert('RGBA');prospective.paste(J.crop((0,1139,1139,1200)).convert('RGBA'),(2957,0));prospective.save(F/'prospective-r08_c09.png')
save(F/'prospective-r08_c09.png.generation.json',{'file':str(F/'prospective-r08_c09.png'),'sha256':sha(F/'prospective-r08_c09.png'),'operation':'Prospective native ROI overlay for next patch context only; not a root-published external tile and must never replace a current whole tile.','derivedFrom':[prep['sources']['r08_c09'],ref(F/'bottom-return.png')],'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False})
save(N/'local-source-checkpoint.json',{'createdAtUtc':now,'tile':'r07_c09','fragment':ref(F/'r07_c09-fragment.png'),'nativeScale':1,'coveragePixels':1297321,'formalAccepted':False,'rootPublished':False,'manifest':ref(F/'manifest.json'),'contextJoined':ref(F/'joined.png'),'prospectiveBottom':dict(ref(F/'prospective-r08_c09.png'),tile='r08_c09'),'externalReturnDependencies':[ref(F/'manifest.json')]})
print(json.dumps({'manifest':ref(F/'manifest.json'),'fragment':ref(F/'r07_c09-fragment.png'),'coveragePixels':1297321,'rootPublished':False}))
