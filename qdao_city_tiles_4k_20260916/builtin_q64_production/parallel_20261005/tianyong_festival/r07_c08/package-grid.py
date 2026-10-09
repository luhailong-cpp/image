from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,sys,numpy as np
N=Path(__file__).parent;T=N.parent;D=N/sys.argv[1];F=D/sys.argv[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(D/'preparation.json');r=read(D/'request.json');prev=read(D/'source-checkpoint-input.json');a=read(F/'assembly.json');x0,y0,x1,y1=r['tileLocalCropLTRB'];kx=p['knownStartX'];ky=p['knownStartY'];ex=a['blendSmoothstepX'][1];ey=a['blendSmoothstepY'][1]
assert 0<=x0 and y1<4096 and x0+kx<=4096
J=Image.open(F/'joined.png').convert('RGBA')
for v in p['sources'].values():assert sha(v['file'])==v['sha256']
now=datetime.now(timezone.utc).isoformat();a.update(visualReviewPending=False,localVisualAccepted=True);save(F/'assembly.json',a)
review={'reviewedAtUtc':now,'image':ref(F/'joined.png'),'actualVisualInspection':True,'nativeScale':1,'inspectedImages':[ref(F/'qa'/f) for f in ['full.png','right.png','bottom.png','corner.png'] if (F/'qa'/f).exists()],'localVisualAccepted':True,'wholeTileAccepted':False,'formalAccepted':False,'findings':['Viewed full native image and full right/bottom seam strips. Canonical panel count and shape maintained with authentic context endpoints.','Continuous clean ivory rail and bevel contours, no visible duplicated edge or straight transparency-boundary seam.','Quiet new native stone detail matches the neighbouring finished material; guide is input-only.'],'limitations':['Partial tile; all outside neighbours and whole-tile QA remain pending.']}
if (F/'review-notes.json').exists():review.update(read(F/'review-notes.json'))
save(F/'visual-review.json',review)
own=p['sources']['r07_c08'];rightTile='r07_c09' if x0+kx==4096 else 'r07_c08';rightSource=p['sources'][rightTile];rightX=x0+kx-(4096 if rightTile=='r07_c09' else 0)
specs=[('new-core',[0,0,kx,ky],'r07_c08',[x0,y0,x0+kx,y0+ky],None),('right-return',[kx,0,ex,ky],rightTile,[rightX,y0,rightX+ex-kx,y0+ky],rightSource),('bottom-return',[0,ky,kx,ey],'r07_c08',[x0,y0+ky,x0+kx,y0+ey],own),('bottom-right-return',[kx,ky,ex,ey],rightTile,[rightX,y0+ky,rightX+ex-kx,y0+ey],rightSource)]
root=read(T/'source-checkpoint.json');latest={v['tile']:v for v in root['candidateSet']};patches=[];checks=[]
for name,crop,tile,dest,prior in specs:
 fp=F/(name+'.png');J.crop(crop).save(fp)
 if prior:
  assert sha(latest[tile]['file'])==latest[tile]['sha256']
  actual=Image.open(latest[tile]['file']).convert('RGBA').crop(dest).tobytes();expected=Image.open(prior['file']).convert('RGBA').crop(dest).tobytes()
  checks.append({'tile':tile,'roi':dest,'latestSource':latest[tile],'exact':actual==expected})
 patches.append({'name':name,'asset':ref(fp),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 save(Path(str(fp)+'.generation.json'),{'file':str(fp),'sha256':sha(fp),'operation':'1:1 exact crop of native-scale composite','derivedFrom':[dict(ref(F/'joined.png'),generationRecord=str(F/'joined.png.generation.json'))],'cropLTRB':crop,'nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None})
m={'createdAtUtc':now,'appearance':'tianyong_festival','tile':'r07_c08','tileGlobalOrigin':[28672,24576],'nativeScale':1,'windowTileLocalLTRB':r['tileLocalCropLTRB'],'windowGlobalLTRB':r['globalCropLTRB'],'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':p['sourceCheckpoint'],'previousManifest':p['previousManifest'],'externalReturnDependencies':p['externalReturnDependencies'],'lastRootRoiCheck':{'file':str(T/'source-checkpoint.json'),'sha256':sha(T/'source-checkpoint.json'),'allRequiredExternalROIsExact':all(c['exact'] for c in checks),'checks':checks},'note':'All four ROI assets must be applied together after previous manifest. Never replace a foreign full tile with a prospective context snapshot.'}
save(F/'manifest.json',m)
save(F/'joined.png.generation.json',{'file':str(F/'joined.png'),'sha256':sha(F/'joined.png'),'operation':'Native AI painting with bounded blending into exact authentic known context; registration, if any, recorded in assembly','derivedFrom':[dict(a['native'],generationRecord=a['native']['file']+'.generation.json'),dict(ref(D/'context.png'),generationRecord=str(D/'context.png.generation.json'))],'assembly':ref(F/'assembly.json'),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'formalAccepted':False})
A=Image.open(own['file']).convert('RGBA');assert not np.array(A)[y0:y0+ky,x0:x0+kx,3].any()
foreign={}
for patch in patches:
 tile=patch['destinationTile'];dest=patch['destinationTileLTRB'];asset=Image.open(patch['asset']['file']).convert('RGBA')
 if tile=='r07_c08':A.paste(asset,dest[:2])
 else:
  if tile not in foreign:foreign[tile]=Image.open(p['sources'][tile]['file']).convert('RGBA')
  foreign[tile].paste(asset,dest[:2])
A.save(F/'r07_c08-fragment.png');coverage=int((np.array(A)[:,:,3]==255).sum())
save(F/'r07_c08-fragment.png.generation.json',{'file':str(F/'r07_c08-fragment.png'),'sha256':sha(F/'r07_c08-fragment.png'),'operation':'Explicit native ROI updates to frozen prior fragment, all other pixels retained','derivedFrom':[own,ref(F/'joined.png')],'manifest':ref(F/'manifest.json'),'nativeScale':1,'actualModel':None,'actualQuality':None,'formalAccepted':False})
cp=dict(prev,createdAtUtc=now,fragment=ref(F/'r07_c08-fragment.png'),coveragePixels=coverage,manifest=ref(F/'manifest.json'),contextJoined=ref(F/'joined.png'),externalReturnDependencies=p['externalReturnDependencies']+[ref(F/'manifest.json')],rootPublished=False)
for tile,img in foreign.items():
 fp=F/('prospective-'+tile+'.png');img.save(fp)
 save(Path(str(fp)+'.generation.json'),{'file':str(fp),'sha256':sha(fp),'operation':'Prospective native explicit ROI returns for context only, never a whole-tile root replacement','derivedFrom':[p['sources'][tile],ref(F/'manifest.json')],'nativeScale':1,'actualModel':None,'actualQuality':None,'formalAccepted':False})
 if tile=='r07_c09':cp['prospectiveRight']=dict(ref(fp),tile=tile)
save(N/'local-source-checkpoint.json',cp)
print(json.dumps({'manifest':ref(F/'manifest.json'),'fragment':ref(F/'r07_c08-fragment.png'),'coveragePixels':coverage,'rootPriorExact':all(c['exact'] for c in checks)}))
