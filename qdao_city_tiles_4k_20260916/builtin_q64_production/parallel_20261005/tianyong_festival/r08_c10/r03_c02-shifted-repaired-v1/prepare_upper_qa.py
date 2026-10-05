from pathlib import Path
import hashlib,json
from PIL import Image
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
context=Image.open(OUT/'context.png').convert('RGB');native=Image.open(OUT/'native.png').convert('RGB')
board=Image.new('RGB',(1254,790));board.paste(context.crop((0,0,1254,395)),(0,0));board.paste(native.crop((0,0,1254,395)),(0,395));board.save(OUT/'comparison-upper395-original-above-raw-below.png')
hard=Image.new('RGB',(1254,256));hard.paste(context.crop((0,267,1254,395)),(0,0));hard.paste(native.crop((0,395,1254,523)),(0,128));hard.save(OUT/'comparison-hard-upper-y395.png')
for name in ['comparison-upper395-original-above-raw-below.png','comparison-hard-upper-y395.png']:
    record={**info(OUT/name),'derivedFrom':[info(OUT/'native.png'),info(OUT/'context.png')],'operation':'Exact native-scale juxtaposition at retained upper source boundary; no scaling','newModelCalls':0,'reviewOnly':True}
    (OUT/(name+'.generation.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'upperQA':['comparison-upper395-original-above-raw-below.png','comparison-hard-upper-y395.png']}))
