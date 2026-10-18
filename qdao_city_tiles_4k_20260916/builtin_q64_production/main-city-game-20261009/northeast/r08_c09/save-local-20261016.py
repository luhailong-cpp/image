from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil,datetime
T=Path(__file__).parent;name=sys.argv[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=T/'receipts'/(name+'.receipt.json');rec=json.loads(r.read_text(encoding='utf8'));src=Path(rec['sourceOutputPath']);dst=T/'native/repairs'/(name+'.png');dst.parent.mkdir(exist_ok=True)
assert not dst.exists();im=Image.open(src);assert im.size==(1254,1254) and im.format=='PNG';shutil.copyfile(src,dst);assert sha(src)==sha(dst)
req=T/'prompts'/(name+'.request.json');args=json.loads(req.read_text(encoding='utf8'))
record={'route':'builtin','tool':'image_gen','actualModel':None,'actualQuality':None,'sourceOutputPath':str(src),'file':str(dst),'sha256':sha(dst),'nativeSize':[1254,1254],'receipt':str(r),'request':str(req),'requestSha256':sha(req),'references':[{'file':p,'sha256':sha(Path(p))} for p in args['referenced_image_paths']],'savedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan':str(T/'qa/local-repair-20261016/plan-v1.json')}
Path(str(dst)+'.generation.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record))
