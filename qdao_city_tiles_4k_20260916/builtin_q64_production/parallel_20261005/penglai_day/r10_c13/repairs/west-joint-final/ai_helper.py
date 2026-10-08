from pathlib import Path
import json, hashlib, shutil, datetime
from PIL import Image, ImageDraw
O=Path(__file__).resolve().parent
R=O.parent.parent
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savecall(name,prompt,refs,roles):
    call={'prompt':prompt,'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'transparent_background':False}
    (O/(name+'.call.json')).write_text(json.dumps(call,ensure_ascii=False,indent=2),encoding='utf8')
    (O/(name+'.prompt.txt')).write_text(prompt,encoding='utf8')
    (O/(name+'.roles.json')).write_text(json.dumps(roles),encoding='utf8')
    return call
def ingest(name,source):
    src=Path(source);dst=O/(name+'-generated.png');shutil.copy2(src,dst)
    call=json.loads((O/(name+'.call.json')).read_text(encoding='utf8'));im=Image.open(dst)
    roles=json.loads((O/(name+'.roles.json')).read_text(encoding='utf8'))
    record={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'generatedAtEvidence':'tool output local file modification time','width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text()),'submittedParameters':dict(call,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号及质量。','evidence':{'toolResultPath':str(src),'sha256':sha(src),'displayedInToolResult':True},'prompt':str(O/(name+'.prompt.txt')),'references':[{'file':p,'sha256':sha(p),'role':roles[i]} for i,p in enumerate(call['referenced_image_paths'])],'formalAccepted':False}
    dst.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
    return dst
def derived(dst,sources,operation):
    Image.open(dst).verify()
    rec={'file':str(dst),'sha256':sha(dst),'derivedFrom':[{'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json'} for p in sources],'operation':operation,'formalAccepted':False}
    Path(str(dst)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8')
