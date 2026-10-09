from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'join-v1';N=D.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(D/'request.json');prep=read(D/'preparation.json');J=Image.open(O/'joined.png').convert('RGBA');S=prep['sources']
assembly=read(O/'assembly.json');assembly.update(visualReviewPending=False,localVisualAccepted=True);save(O/'assembly.json',assembly)
gen=read(O/'joined.png.generation.json');gen['assembly']=ref(O/'assembly.json');save(O/'joined.png.generation.json',gen)
save(O/'visual-review.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'image':ref(O/'joined.png'),'reviewer':'root','viewedNativeImages':[ref(D/'native.png'),ref(O/'top-native-qa.png'),ref(O/'left-native-qa.png')],'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'findings':[],'observation':'Entire native generated frame reviewed, followed by full top and left native cross-boundary strips. Scroll silhouettes, slab joint, bright rim and warm bevel surfaces connect through each return and top-left corner without visible gap or doubled line. No warp, resize or tone correction.','limits':'This window and its explicit returns only. Remaining r08_c11 pixels and unbuilt outside neighbors, full-grid and runtime remain pending.'})
specs=[('new-core',[115,115,1254,1254],'r08_c11',[0,0,1139,1139],None),('top-return',[115,54,1254,115],'r07_c11',[0,4035,1139,4096],S['r07_c11']),('left-return',[54,115,115,1254],'r08_c10',[4035,0,4096,1139],S['r08_c10']),('top-left-return',[54,54,115,115],'r07_c10',[4035,4035,4096,4096],S['r07_c10'])]
patches=[];fragment=Image.new('RGBA',(4096,4096),(0,0,0,0))
for name,crop,tile,box,prior in specs:
 f=O/(name+'.png');asset=J.crop(crop);asset.save(f);p={'name':name,'asset':ref(f),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True};patches.append(p)
 save(O/(name+'.png.generation.json'),{'file':str(f),'sha256':sha(f),'derivedFrom':[ref(O/'joined.png')],'operation':'Exact native crop; no resize or generation','nativeScale':1,'newModelCalls':0,'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'formalAccepted':False})
 if tile=='r08_c11':fragment.paste(asset,tuple(box[:2]))
fragment.save(O/'r08_c11-fragment.png');src={**ref(O/'r08_c11-fragment.png'),'tile':'r08_c11','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':True,'fullyPainted':False,'nativeScale':1,'formalAccepted':False,'generationRecord':str(O/'r08_c11-fragment.png.generation.json')}
save(O/'r08_c11-fragment.png.generation.json',{'file':src['file'],'sha256':src['sha256'],'derivedFrom':[patches[0]['asset']],'operation':'Exact new-core native placement on transparent coordinate scaffold','newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'coveredNativeTilePixels':1139*1139,'formalAccepted':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r08_c11','tileGlobalOrigin':req['tileGlobalOrigin'],'nativeScale':1,'windowTileLocalLTRB':req['tileLocalCropLTRB'],'windowGlobalLTRB':req['globalCropLTRB'],'joined':ref(O/'joined.png'),'visualReview':ref(O/'visual-review.json'),'assembly':ref(O/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'note':'Apply new core and all three external ROI returns together, preserving missing pixels of partially painted r07_c11. Never replace external tiles with whole prior snapshots.'}
save(O/'manifest.json',manifest);save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c11','fragment':src,'coveragePixels':1139*1139,'contextJoined':ref(O/'joined.png'),'manifest':ref(O/'manifest.json'),'externalReturnDependencies':patches[1:],'rootPublished':False,'formalAccepted':False})
print(json.dumps({'manifest':ref(O/'manifest.json'),'fragment':src,'coverage':1139*1139}))
