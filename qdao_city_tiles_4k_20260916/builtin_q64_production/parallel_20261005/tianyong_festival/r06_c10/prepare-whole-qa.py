from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).parent;cp=json.loads((B/'local-source-checkpoint.json').read_text(encoding='utf-8-sig'));Q=B/'full-tile-qa';im=Image.open(cp['fragment']['file']).convert('RGB');south=Image.open(cp['coupledBottom']['file']).convert('RGB');refs=[];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for r,y in enumerate([0,1280,2560],1):
 for c,x in enumerate([0,1280,2560],1):
  p=Q/f'overlap-r{r}-c{c}-1536.png';im.crop((x,y,x+1536,y+1536)).save(p);refs.append({'file':str(p),'sha256':sha(p),'tileLocalLTRB':[x,y,x+1536,y+1536],'nativeScale':1})
edge=Image.new('RGB',(4096,640));edge.paste(im.crop((0,3776,4096,4096)),(0,0));edge.paste(south.crop((0,0,4096,320)),(0,320));edge.save(Q/'south-full-native.png');srefs=[]
for i,x in enumerate([0,1280,2560],1):
 p=Q/f'south-overlap-{i}-native.png';edge.crop((x,0,x+1536,640)).save(p);srefs.append({'file':str(p),'sha256':sha(p),'globalLTRB':[36864+x,24256,36864+x+1536,24896],'nativeScale':1})
(Q/'inspection-index.json').write_text(json.dumps({'source':cp['fragment'],'southSource':cp['coupledBottom'],'wholeTilePanels':refs,'southPanels':srefs,'wholeTileEveryPixelCovered':True,'internalSeamsCovered':[1024,2048,3072],'nineIntersectionsCovered':True,'resamplingApplied':False},indent=2),encoding='utf8');print(json.dumps({'panels':9,'southPanels':3}))
