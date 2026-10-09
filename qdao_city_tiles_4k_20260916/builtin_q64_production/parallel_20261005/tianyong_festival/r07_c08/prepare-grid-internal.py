from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib,shutil,sys
N=Path(__file__).parent;T=N.parent;ROOT=next(p for p in N.parents if (p/'config/image-generation.json').exists());name=sys.argv[1];x0=int(sys.argv[2]);y0=int(sys.argv[3]);D=N/name;D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
cp=read(N/'local-source-checkpoint.json');own=dict(cp['fragment'],tile='r07_c08',tileLocalLTRB=[0,0,4096,4096],nativeScale=1);assert sha(own['file'])==own['sha256'];A=Image.open(own['file']).convert('RGBA');local=[x0,y0,x0+1254,y0+1254];origin=[28672,24576];world=[origin[i%2]+local[i] for i in range(4)];assert x0>=0 and x0+1254<=4096
C=A.crop(local);arr=np.array(C);kx=int(np.flatnonzero(arr[0,:,3]==255)[0]);ky=int(np.flatnonzero(arr[:,0,3]==255)[0]);assert kx>0 and ky>0
assert not arr[:ky,:kx,3].any() and np.all(arr[ky:,:,3]==255) and np.all(arr[:,kx:,3]==255)
C.save(D/'context.png');master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
G=Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world));G.save(D/'layout-reference-only.png');G=G.convert('RGBA');G.alpha_composite(C);G.convert('RGB').save(D/'coarse-layout-with-native-anchors-reference-only.png')
refs=[D/'coarse-layout-with-native-anchors-reference-only.png',D/'context.png',ROOT/'designs/gameplay-ui/04-guild.png']
save(D/'source-checkpoint-input.json',cp)
prep={'sources':{'r07_c08':own},'knownStartX':kx,'knownStartY':ky,'sourceCheckpoint':ref(D/'source-checkpoint-input.json'),'previousManifest':cp['manifest'],'externalReturnDependencies':cp['externalReturnDependencies'],'master':ref(master),'references':[dict(ref(p),role=role) for p,role in zip(refs,['coarse canonical input guide with exact native anchors; no guide output pixels','exact native bottom and right context','approved actual art style'])],'knownRegions':[{'source':own,'sourceLTRB':[x0+kx,y0,x0+1254,y0+1254],'contextXY':[kx,0]},{'source':own,'sourceLTRB':[x0,y0+ky,x0+kx,y0+1254],'contextXY':[0,ky]}],'nativeScale':1,'guidePixelsAllowedInFinal':False}
save(D/'preparation.json',prep);save(D/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c08','patch':name,'tileGlobalOrigin':origin,'tileLocalCropLTRB':local,'globalCropLTRB':world,'configSnapshot':read(ROOT/'config/image-generation.json'),'knownPixels':int((arr[:,:,3]==255).sum()),'missingPixels':int((arr[:,:,3]==0).sum()),'submittedParameters':{'model':None,'quality':None,'size':None}})
for fn,inputs,op in [('context.png',[own],'Exact native crop, no resize'),('layout-reference-only.png',[ref(master)],'Coarse canonical layout input only; no final production pixels'),('coarse-layout-with-native-anchors-reference-only.png',[ref(D/'layout-reference-only.png'),ref(D/'context.png')],'INPUT ONLY composite: authentic current native anchors over rough guide; actual AI redraw required')]:save(D/(fn+'.generation.json'),{'file':str(D/fn),'sha256':sha(D/fn),'operation':op,'derivedFrom':inputs,'newModelCalls':0,'actualModel':None,'actualQuality':None})
shutil.copy2(N/'r04_c04-v1/ingest.py',D/'ingest.py')
print(json.dumps({'directory':str(D),'window':local,'knownStartX':kx,'knownStartY':ky}))
