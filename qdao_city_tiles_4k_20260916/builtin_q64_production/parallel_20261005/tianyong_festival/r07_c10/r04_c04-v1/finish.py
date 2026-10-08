from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v1';T=D.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
prep=json.loads((D/'preparation.json').read_text(encoding='utf-8-sig'))
J=Image.open(F/'joined.png').convert('RGB')
review={'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'image':ref(F/'joined.png'),'reviewMethod':'Full 1254 native image and complete 1139x334 bottom seam viewed at native scale; bottom left and right junction crops reviewed.','inspectedImages':[ref(p) for p in (F/'qa').glob('*.png')],'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['Canonical inset and cloud curl geometry were newly rendered, including upper diagonal courses and partial inward curl.','Bottom outline registration is close (mostly 0–2 pixels); no warp or resizing was applied. Blend is restricted to already rendered known overlap only.','The lower existing curved relief remains continuous without a doubled groove or horizontal stripe.','Source rows y1200 and below are pixel-exact; r08_c10 return must accompany the newly filled northern tile.','Rightmost 115-pixel unknown halo is native generated context only and not committed to an unowned neighboring tile.'],'actualModel':None,'actualQuality':None,'limitations':['Only the new patch and coupled bottom return are locally accepted. Full tile, exterior neighbor and city review are still required.']}
save(F/'visual-review.json',review)
patches=[]
for name,crop,tile,dest,prior in [('new-core',[0,0,1139,1139],'r07_c10',[2957,2957,4096,4096],None),('bottom-return',[0,1139,1139,1200],'r08_c10',[2957,0,4096,61],prep['sourceTile'])]:
 p=F/(name+'.png');J.crop(crop).save(p)
 patches.append({'name':name,'asset':ref(p),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dest,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
m={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r07_c10','tileGlobalOrigin':[36864,24576],'nativeScale':1,'windowTileLocalLTRB':[2957,2957,4211,4211],'windowGlobalLTRB':[39821,27533,41075,28787],'joined':ref(F/'joined.png'),'visualReview':ref(F/'visual-review.json'),'assembly':ref(F/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':patches,'sourceCheckpoint':prep['savedCheckpoint'],'note':'Coupled new r07_c10 and bottom r08_c10 return, root review and ROI validation required before publication. Do not use old hardcoded r08_c10 commit script.'}
save(F/'manifest.json',m)
save(F/'joined.png.generation.json',{'operation':'native-preserving assembly','sources':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(F/'assembly.json'),'output':ref(F/'joined.png'),'actualModel':None,'actualQuality':None,'nativeScale':1,'noUpscale':True,'formalAccepted':False})
fragment=Image.new('RGBA',(4096,4096));fragment.paste(J.crop((0,0,1139,1139)).convert('RGBA'),(2957,2957));fragment.save(F/'r07_c10-fragment.png')
save(D.parent/'local-source-checkpoint.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r07_c10','fragment':ref(F/'r07_c10-fragment.png'),'nativeScale':1,'coveragePixels':1297321,'formalAccepted':False,'rootPublished':False,'manifest':ref(F/'manifest.json'),'contextJoined':ref(F/'joined.png'),'bottomReturn':patches[1]})
print(json.dumps({'manifest':ref(F/'manifest.json'),'joined':ref(F/'joined.png'),'rootPublished':False},indent=2))
