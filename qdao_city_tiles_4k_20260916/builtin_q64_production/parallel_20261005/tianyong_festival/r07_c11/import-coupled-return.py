from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
N=Path(__file__).parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mp=Path(sys.argv[1]);expected=sys.argv[2];assert sha(mp)==expected
m=read(mp);assert m['localVisualAccepted'];cp=read(N/'local-source-checkpoint.json')
D=N/('external-import-'+expected[:12]);D.mkdir(exist_ok=False);(D/'local-checkpoint-before.json').write_bytes((N/'local-source-checkpoint.json').read_bytes())
F=Image.open(cp['fragment']['file']).convert('RGBA');before=np.asarray(F).copy();mask=np.zeros((4096,4096),bool);below=Image.new('RGBA',(4096,4096));applied=[]
for p in m['patches']:
 assert sha(p['asset']['file'])==p['asset']['sha256'];im=Image.open(p['asset']['file']).convert('RGBA');box=p['destinationTileLTRB'];x1,y1,x2,y2=box
 if p['destinationTile']=='r07_c11':
  prior=p['requiredPriorSource'];assert prior and sha(prior['file'])==prior['sha256'];P=Image.open(prior['file']).convert('RGBA');assert np.array_equal(np.array(P.crop(box)),np.array(F.crop(box)))
  F.paste(im,(x1,y1));mask[y1:y2,x1:x2]=True;applied.append(p)
 elif p['destinationTile']=='r08_c11':below.paste(im,(x1,y1))
 elif p['destinationTile'] in ['r07_c10','r08_c10']:cp['externalReturnDependencies'].append(p)
after=np.asarray(F);assert np.array_equal(before[~mask],after[~mask]);assert int(np.count_nonzero(after[:,:,3]))==cp['coveragePixels']
F.save(D/'r07_c11-fragment.png');below.save(D/'r08_c11-context-fragment.png')
src={**cp['fragment'],**ref(D/'r07_c11-fragment.png'),'generationRecord':str(D/'r07_c11-fragment.png.generation.json')}
write(D/'r07_c11-fragment.png.generation.json',{'file':src['file'],'sha256':src['sha256'],'derivedFrom':[cp['fragment'],ref(mp)],'operation':'Exact native coupled-return ROI import; outside ROIs byte-identical as RGBA','nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False})
neighbor={**ref(D/'r08_c11-context-fragment.png'),'tile':'r08_c11','relativeTileLTRB':[0,4096,4096,8192],'nativeScale':1,'partialFragment':True,'formalAccepted':False}
write(D/'proof.json',{'sourceManifest':ref(mp),'priorLocalCheckpoint':ref(D/'local-checkpoint-before.json'),'result':src,'patches':applied,'outsideImportedROIsIdentical':True,'coverageUnchanged':True,'contextNeighbor':neighbor,'formalAccepted':False})
cp['fragment']=src;cp.setdefault('externalImportEvidence',[]).append(ref(D/'proof.json'));cp['contextNeighbors']=[q for q in cp.get('contextNeighbors',[]) if q['tile']!='r08_c11']+[neighbor];cp['createdAtUtc']=datetime.now(timezone.utc).isoformat();write(N/'local-source-checkpoint.json',cp)
print(json.dumps({'proof':ref(D/'proof.json'),'fragment':src,'contextNeighbor':neighbor}))
