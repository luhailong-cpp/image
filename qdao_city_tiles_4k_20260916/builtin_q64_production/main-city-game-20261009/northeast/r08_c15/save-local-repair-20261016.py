from pathlib import Path
from PIL import Image
import json,hashlib,sys,shutil
T=Path(__file__).resolve().parent;ident=sys.argv[1];source=Path(sys.argv[2]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=T/'native/repairs'/(ident+'.png');out.parent.mkdir(exist_ok=True);assert not out.exists();shutil.copy2(source,out)
assert sha(out)==sha(source)
with Image.open(out) as im:size=list(im.size);im.verify()
assert size==[1254,1254]
reqpath=T/'prompts/repairs'/(ident+'.request.json');req=json.loads(reqpath.read_text(encoding='utf-8-sig'))
record={'file':str(out),'sha256':sha(out),'nativeSize':size,'sourceOutputPath':str(source),'route':'builtin','tool':'image_gen','actualModel':None,'actualQuality':None,'request':str(reqpath),'receipt':str(T/'prompts/repairs'/(ident+'.receipt.json')),'references':[{'file':p,'sha256':sha(p)} for p in req['referenced_image_paths']],'resized':False,'status':'native-local-repair-awaiting-composition-review','attempt':req['attempt']}
Path(str(out)+'.generation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
