from pathlib import Path
from PIL import Image
import json,hashlib,shutil
N=Path(__file__).parent;Q=N/'review-bottom-row-v1';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
cp=read(N/'local-source-checkpoint.json');src={k:cp[k] for k in ['fragment','prospectiveBottom','prospectiveRight']};im={}
for k,v in src.items():
 assert sha(v['file'])==v['sha256'];p=Q/('frozen-'+k+'.png');shutil.copy2(v['file'],p);im[k]=Image.open(p).convert('RGBA');src[k]=dict(ref(p),originalSource=v)
C=Image.new('RGBA',(4096,1536));C.paste(im['fragment'].crop((0,2957,4096,4096)),(0,0));C.paste(im['prospectiveBottom'].crop((0,0,4096,397)),(0,1139));crops=[]
for i,x in enumerate([0,1280,2560]):
 p=Q/f'native-complete-bottom-{i+1}.png';C.crop((x,0,x+1536,1536)).save(p);crops.append(dict(ref(p),ownLocalLTRB=[x,2957,x+1536,4096],bottomLocalLTRB=[x,0,x+1536,397]))
R=Image.new('RGBA',(512,1139));R.paste(im['fragment'].crop((3840,2957,4096,4096)),(0,0));R.paste(im['prospectiveRight'].crop((0,2957,256,4096)),(256,0));p=Q/'native-east-bottom.png';R.save(p);crops.append(dict(ref(p),ownLocalLTRB=[3840,2957,4096,4096],rightLocalLTRB=[0,2957,256,4096]))
(Q/'inspection-index.json').write_text(json.dumps({'frozenSources':src,'localCheckpointAtFreeze':cp,'nativeScale':1,'prospectiveExternalContext':True,'inspectionCrops':crops},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'qa':str(Q),'cropCount':len(crops)}))
