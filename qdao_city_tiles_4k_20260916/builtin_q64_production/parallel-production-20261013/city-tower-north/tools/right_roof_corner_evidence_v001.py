import json, hashlib
from pathlib import Path
from PIL import Image
BASE = Path(__file__).resolve().parent.parent
root = BASE/'versions/right-r03c14-roof-corner-native-v001'
record = json.loads((root/'integration.json').read_text(encoding='utf-8'))
image = Image.open(record['candidate']['file'])
crops = {'vertical-p22-p23':[1856,1024,2240,2048], 'vertical-p32-p33':[1856,2048,2240,3072],
         'horizontal-p22-p32':[1024,1856,2048,2240], 'horizontal-p23-p33':[2048,1856,3072,2240]}
evidence=[]
for name,box in crops.items():
    path=root/(name+'-after-100pct.png')
    with path.open('xb') as stream:
        image.crop(box).save(stream,format='PNG')
    evidence.append({'name':name,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cropTilePixels':box,'resized':False})
with (BASE/'qa/right-r03c14-roof-corner-evidence-v001.json').open('x',encoding='utf-8') as stream:
    json.dump({'candidate':record['candidate'],'affectedSeamCrops':evidence},stream,ensure_ascii=False,indent=2)
print(json.dumps(evidence,ensure_ascii=False))
