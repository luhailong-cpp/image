from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c02-v1/final-v2');T=D.parent.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((D/'source-checkpoint-input.json').read_text(encoding='utf-8'))
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'image':info(D/'joined.png'),'localAccepted':True,'formalAccepted':False,'reviewedAtNativeScale':['whole1254','top','bottom','left-full','out-left-bottom','out-top-left','out-top-right','out-bottom'],'findings':['Cloud relief and plain ivory panel continue exact upper-source geometry; separate ivory ring and right gray channel remain visible down to slate-row joint. Old lower broadpanel was replaced by actual AI structure rather than a large warp.','Top-left80x230 pixels remain exact v014. Bottom28rows remain exact v014. New source and each return use true native pixels.','Fourpixel lower-left joint offset was corrected with bounded verticalregistration and exact leftmost oldsource recovery; direct outerleft QA now joins smoothly.','Source-tone adjustment max6.624RGB, xregistration<=1, y<=4. No resizing or synthesized high-resolution claims.'],'explicitRemainingCoupledWork':[{'regionTileLocalLTRB':[2163,1933,2250,2040],'description':'Right external edge changes into neighboring r03c03 old broadpanel and its horizontal gray-top joint; root r02c03 needs actual new right230context and is already producing coupled repair. This is a working-candidate checkpoint, not a closed4K or formal acceptance.'}],'reviewer':'complete_middle','noFormalAcceptanceClaim':True}
(D/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
j=Image.open(D/'joined.png')
specs=[('new-core',[0,230,1254,1024],None),('top-return',[80,150,1254,230],cp['fragment']),('bottom-return',[0,1024,1254,1226],cp['fragment'])]
patches=[]
for name,b,prior in specs:
 out=D/f'{name}.png';j.crop(b).save(out)
 p={'name':name,'asset':info(out),'cropFromJoinedLTRB':b,'destinationTile':'r08_c10','destinationTileLTRB':[b[0]+909,b[1]+909,b[2]+909,b[3]+909],'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True}
 patches.append(p)
 (D/f'{name}.png.generation.json').write_text(json.dumps({'derivation':'exact native crop','parent':info(D/'joined.png'),'cropLTRB':b,'nativeScale':1,'file':str(out),'sha256':sha(out),'destinationTileLTRB':p['destinationTileLTRB'],'formalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r08_c10','nativeScale':1,'windowTileLocalLTRB':[909,909,2163,2163],'windowGlobalLTRB':[37773,29581,39027,30835],'joined':info(D/'joined.png'),'visualReview':info(D/'visual-review.json'),'assembly':info(D/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':info(D/'source-checkpoint-input.json'),'note':'Allthree crops must be committed together after current priorSource ROI verification. No root writes by subagent. Whole4K/formal acceptance awaits neighbor work and audit.'}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'manifest':info(D/'manifest.json'),'joined':info(D/'joined.png')}))

