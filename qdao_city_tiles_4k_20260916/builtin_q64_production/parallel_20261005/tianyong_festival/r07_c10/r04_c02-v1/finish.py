from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v1'
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
prep=read(D/'preparation.json');J=Image.open(F/'joined.png').convert('RGB')
save(F/'visual-review.json',{'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'image':ref(F/'joined.png'),'reviewMethod':'Full native image, complete right and bottom return strips, and bottom right corner viewed at original pixel size.','inspectedImages':[ref(p) for p in (F/'qa').glob('*.png')],'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['Canonical broad paving and diagonal ivory/slate channel meet existing lower and right geometry.','Latest c01 upper halo replaces the obsolete c02 halo where6224 pixels differ; both current lower overlaps verified exact.','No extra strip at transparency edges, no doubled outlines or material/color step seen in return strips.','No resizing, registration, tone adjustment or blur was applied; only known native overlap compositing.','New core and both returns must be applied together after preceding c03 manifest.'],'actualModel':None,'actualQuality':None})
prior={**prep['northPriorFragment'],'tile':'r07_c10','tileLocalLTRB':[0,0,4096,4096],'nativeScale':1}
patches=[]
for name,crop,tile,dest,src in [('new-core',[0,0,1024,1139],'r07_c10',[909,2957,1933,4096],None),('right-return',[1024,0,1200,1139],'r07_c10',[1933,2957,2109,4096],prior),('bottom-return',[0,1139,1200,1200],'r08_c10',[909,0,2109,61],prep['sourceTile'])]:
 p=F/(name+'.png');J.crop(crop).save(p);patches.append({'name':name,'asset':ref(p),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':src,'nativeScale':1,'mustApplyTogether':True})
m={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r07_c10','tileGlobalOrigin':[36864,24576],'nativeScale':1,'windowTileLocalLTRB':[909,2957,2163,4211],'windowGlobalLTRB':[37773,27533,39027,28787],'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['savedCheckpoint'],'requiresPriorManifest':prep['requiresPriorManifest'],'note':'Root review and ROI validation before publication. Current root source plus previous manifest return overlays is the required prior.'}
save(F/'manifest.json',m)
save(F/'joined.png.generation.json',{'operation':'native-preserving composite','sources':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(F/'assembly.json'),'output':ref(F/'joined.png'),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'formalAccepted':False})
fragment=Image.open(prior['file']).convert('RGBA');fragment.paste(J.crop((0,0,1200,1139)).convert('RGBA'),(909,2957));fragment.save(F/'r07_c10-fragment.png')
coverage=int(np.count_nonzero(np.array(fragment)[:,:,3]==255));assert coverage==3629993
save(D.parent/'local-source-checkpoint.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r07_c10','fragment':ref(F/'r07_c10-fragment.png'),'nativeScale':1,'coveragePixels':coverage,'formalAccepted':False,'rootPublished':False,'manifest':ref(F/'manifest.json'),'previousManifest':prep['requiresPriorManifest'],'contextJoined':ref(F/'joined.png'),'bottomReturn':patches[2]})
print(json.dumps({'manifest':ref(F/'manifest.json'),'joined':ref(F/'joined.png'),'localCoveragePixels':coverage}))
