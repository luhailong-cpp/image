from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'join-v1';N=D.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(D/'request.json');prep=read(D/'preparation.json');J=Image.open(O/'joined.png').convert('RGBA')
assembly=read(O/'assembly.json');assembly.update(visualReviewPending=False,localVisualAccepted=True);save(O/'assembly.json',assembly)
gen=read(O/'joined.png.generation.json');gen['assembly']=ref(O/'assembly.json');save(O/'joined.png.generation.json',gen)
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'image':ref(O/'joined.png'),'reviewer':'root','viewedNativeImages':[ref(D/'native.png'),ref(O/'left-seam-native-qa.png'),ref(O/'corner-native-qa.png')],'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'findings':[],'observation':'The scroll contour, rim bevels, broad stone surfaces and top horizontal joint are continuous across the left return. Bottom-left corner return is also continuous. No warp, resize or tone correction was applied.','limits':'Only this1254-square native window and explicit returns are reviewed; missing r07_c11 remainder, r08_c11, other outside neighbors and runtime remain pending.'}
save(O/'visual-review.json',review)
patches=[]
specs=[('new-core',[115,0,1254,1139],'r07_c11',[0,2957,1139,4096],None),('left-return',[54,0,115,1139],'r07_c10',[4035,2957,4096,4096],prep['sources']['r07_c10']),('bottom-left-return',[54,1139,115,1200],'r08_c10',[4035,0,4096,61],prep['sources']['r08_c10'])]
fragment=Image.new('RGBA',(4096,4096),(0,0,0,0))
for name,crop,tile,box,prior in specs:
 f=O/(name+'.png');asset=J.crop(crop);asset.save(f)
 p={'name':name,'asset':ref(f),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True};patches.append(p)
 save(O/(name+'.png.generation.json'),{'file':str(f),'sha256':sha(f),'derivedFrom':[ref(O/'joined.png')],'operation':'Exact native crop, no resizing or generation','nativeScale':1,'newModelCalls':0,'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':box,'formalAccepted':False})
 if tile=='r07_c11':fragment.paste(asset,tuple(box[:2]))
fragment.save(O/'r07_c11-fragment.png')
src={**ref(O/'r07_c11-fragment.png'),'tile':'r07_c11','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':True,'fullyPainted':False,'nativeScale':1,'formalAccepted':False,'generationRecord':str(O/'r07_c11-fragment.png.generation.json')}
save(O/'r07_c11-fragment.png.generation.json',{'file':src['file'],'sha256':src['sha256'],'derivedFrom':[patches[0]['asset']],'operation':'Exact new-core native crop placed on transparent coordinate scaffold','newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'coveredNativeTilePixels':1139*1139,'formalAccepted':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r07_c11','tileGlobalOrigin':req['tileGlobalOrigin'],'nativeScale':1,'windowTileLocalLTRB':req['tileLocalCropLTRB'],'windowGlobalLTRB':req['globalCropLTRB'],'joined':ref(O/'joined.png'),'visualReview':ref(O/'visual-review.json'),'assembly':ref(O/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'note':'Apply core and both external return ROIs together; no bottom r08_c11 source yet exists. Do not replace external tiles with an old full snapshot.'}
save(O/'manifest.json',manifest)
save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c11','fragment':src,'coveragePixels':1139*1139,'contextJoined':ref(O/'joined.png'),'manifest':ref(O/'manifest.json'),'externalReturnDependencies':patches[1:],'rootPublished':False,'formalAccepted':False})
print(json.dumps({'manifest':ref(O/'manifest.json'),'fragment':src,'coverage':1139*1139}))
