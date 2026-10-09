from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib,shutil
N=Path(__file__).parent;T=N.parent;ROOT=next(p for p in N.parents if (p/'config/image-generation.json').exists());D=N/'r03_c04-v1';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
cp=read(N/'local-source-checkpoint.json');root=read(T/'source-checkpoint.json');right=next(v for v in root['candidateSet'] if v['tile']=='r07_c10')
for v in [cp['fragment'],right]:assert sha(v['file'])==v['sha256']
A=Image.open(cp['fragment']['file']).convert('RGBA');R=Image.open(right['file']).convert('RGBA')
local=[2957,1933,4211,3187];origin=[32768,24576];world=[origin[i%2]+local[i] for i in range(4)]
C=A.crop(local);C.paste(R.crop((0,1933,115,3187)),(1139,0));C.save(D/'context.png');arr=np.array(C)
assert np.all(arr[1024:,:,3]==255) and np.all(arr[:,1139:,3]==255) and not arr[:1024,:1139,3].any()
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
G=Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world));G.save(D/'layout-reference-only.png');G=G.convert('RGBA');G.alpha_composite(C);G.convert('RGB').save(D/'coarse-layout-with-native-anchors-reference-only.png')
refs=[D/'coarse-layout-with-native-anchors-reference-only.png',D/'context.png',ROOT/'designs/gameplay-ui/04-guild.png']
save(D/'source-checkpoint-input.json',cp);save(D/'root-checkpoint-input.json',root)
prep={'sources':{'r07_c09':dict(cp['fragment'],tile='r07_c09',tileLocalLTRB=[0,0,4096,4096],nativeScale=1),'r07_c10':right},'knownStartX':1139,'knownStartY':1024,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'rootCheckpoint':ref(D/'root-checkpoint-input.json'),'previousManifest':cp['manifest'],'externalReturnDependencies':cp['externalReturnDependencies'],'master':ref(master),'references':[dict(ref(p),role=role) for p,role in zip(refs,['coarse canonical input guide with exact native anchors; no guide output pixels','exact native bottom230 and right115','approved actual art style'])],'knownRegions':[{'source':cp['fragment'],'sourceLTRB':[2957,2957,4096,3187],'contextXY':[0,1024]},{'source':right,'sourceLTRB':[0,1933,115,3187],'contextXY':[1139,0]}],'nativeScale':1,'guidePixelsAllowedInFinal':False}
save(D/'preparation.json',prep)
save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c09','patch':'r03_c04','tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'knownPixels':int((arr[:,:,3]==255).sum()),'missingPixels':int((arr[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None}})
for name,inputs,operation in [('context.png',list(prep['sources'].values()),'Exact native crop placement; outside tile right context from latest frozen root source'),('layout-reference-only.png',[ref(master)],'Canonical broad layout enlarged solely as input reference; forbidden in final pixels'),('coarse-layout-with-native-anchors-reference-only.png',[ref(D/'layout-reference-only.png'),ref(D/'context.png')],'INPUT ONLY composite of coarse guide in unknown region and exact native known context; final must be actual AI redraw')]:save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'operation':operation,'derivedFrom':inputs,'newModelCalls':0,'actualModel':None,'actualQuality':None})
shutil.copy2(N/'r04_c03-shifted-v1/ingest.py',D/'ingest.py');shutil.copy2(N/'r04_c02-shifted-v1/set-payload.py',D/'set-payload.py')
print(json.dumps({'directory':str(D),'world':world,'rightSource':right}))
