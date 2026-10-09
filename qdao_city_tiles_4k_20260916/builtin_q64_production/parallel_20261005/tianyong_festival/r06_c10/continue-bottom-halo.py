from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).parent;ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
h=Image.open(B/'r07-top-native-halo.png').convert('RGBA');j=Image.open(B/'r04_c04-v1/final-v7/joined.png').convert('RGBA');h.paste(j.crop((0,1024,1639,1139)),(2457,0));h.save(B/'r07-top-native-halo-after-c04.png')
(B/'r07-top-native-halo-after-c04.png.generation.json').write_text(json.dumps({'output':ref(B/'r07-top-native-halo-after-c04.png'),'sources':[ref(B/'r07-top-native-halo.png'),ref(B/'r04_c04-v1/final-v7/joined.png')],'operation':'Native generated continuation context for r06 bottom115; external halo does not increase committed r06 coverage','nativeScale':1,'newModelCalls':0,'updatedX':[2457,4096],'newSourceCropLTRB':[0,1024,1639,1139]}),encoding='utf8')
cp=read(B/'local-source-checkpoint.json');cp['bottomNativeHalo']=ref(B/'r07-top-native-halo-after-c04.png');(B/'local-source-checkpoint.json').write_text(json.dumps(cp,indent=2),encoding='utf8')
