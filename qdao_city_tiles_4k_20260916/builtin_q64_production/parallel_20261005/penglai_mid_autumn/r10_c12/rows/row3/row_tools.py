from pathlib import Path
import json, hashlib, shutil, sys
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent
TASK=ROOT.parent.parent
REPO=Path('D:/work/image')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stamp(): return datetime.now(timezone.utc).isoformat()
def ref(p,role): return {'file':str(p),'sha256':sha(p),'role':role}
def accept(patch,source,target):
    src=Path(source); dst=ROOT/(patch+'.png')
    assert src.exists() and not dst.exists()
    shutil.copy2(src,dst)
    im=Image.open(dst); im.load()
    refs=[ref(Path(target),'edit target; exact shared geometry and neighboring native-pixel context where recorded'),ref(REPO/'designs/gameplay-ui/04-guild.png','main approved painting style only')]
    toolresult=ROOT/(patch+'.tool-result.txt')
    write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'generatedAt':stamp(),'width':im.width,'height':im.height,'format':im.format,'nativePixels':[im.width,im.height],'tool':'image_gen.imagegen','route':'builtin','toolResultPath':str(src),'toolResultSha256':sha(src),'toolResultEvidence':str(toolresult),'configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[v['file'] for v in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin. Tool exposes no model/quality selectors and returns neither model nor quality metadata. Configuration and prompt are targets only.','prompt':str(ROOT/(patch+'.prompt.txt')),'references':refs,'core':[115,115,1139,1139],'corePixels':[1024,1024],'haloPixels':115,'formalAccepted':False,'productionStage':'native detail fragment; not a complete 4K tile'})
    print(str(dst),im.size,sha(dst))
def target(previous,current):
    left=ROOT/(previous+'.png'); guide=TASK/'guides'/(current+'.png'); dst=ROOT/(current+'.edit-target.png')
    a=Image.open(guide).convert('RGB'); b=Image.open(left).convert('RGB')
    assert a.size==b.size==(1254,1254)
    a.paste(b.crop((1024,0,1254,1254)),(0,0)); a.save(dst)
    write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'createdAt':stamp(),'width':1254,'height':1254,'format':'PNG','derivedFrom':[ref(guide,'layout-only guide'),ref(left,'left neighbor native original-pixel context')],'operation':{'kind':'pixel_crop_paste_edit_target','scale':1,'cropLTRB':[1024,0,1254,1254],'pasteXY':[0,0],'overlap':230,'nonContextPixels':'layout guide only; must be AI redrawn'},'productionPixels':False})
    print(str(dst))
def context(current):
    col=int(current[-1]); guide=TASK/'guides'/(current+'.png'); dst=ROOT/(current+'.edit-target.png')
    a=Image.open(guide).convert('RGB'); sources=[ref(guide,'layout guide only')]; ops=[]
    upper=TASK/'rows/row2'/('p2'+str(col)+'.png')
    if upper.exists():
        b=Image.open(upper).convert('RGB'); assert b.size==(1254,1254)
        a.paste(b.crop((0,1024,1254,1254)),(0,0)); sources.append(ref(upper,'native upper adjacent bottom230px')); ops.append({'source':str(upper),'cropLTRB':[0,1024,1254,1254],'pasteXY':[0,0]})
    left=ROOT/('p3'+str(col-1)+'.png')
    if col>1 and left.exists():
        b=Image.open(left).convert('RGB'); assert b.size==(1254,1254)
        a.paste(b.crop((1024,0,1254,1254)),(0,0)); sources.append(ref(left,'native left adjacent right230px, takes precedence at corner')); ops.append({'source':str(left),'cropLTRB':[1024,0,1254,1254],'pasteXY':[0,0]})
    a.save(dst); write(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'createdAt':stamp(),'width':1254,'height':1254,'format':'PNG','derivedFrom':sources,'operation':{'kind':'native_pixel_context_crop_paste','scale':1,'steps':ops,'notProductionArt':True},'productionPixels':False})
    print(str(dst)); print(json.dumps(ops))
def enrich(current):
    p=ROOT/(current+'.png.generation.json'); v=json.loads(p.read_text()); col=int(current[-1]); v['tile']='r10_c12'; v['globalPatchXYWH']=[44941+(col-1)*1024,38797,1254,1254];v['globalCoreXYWH']=[45056+(col-1)*1024,38912,1024,1024]
    v['submittedParameters']['prompt']=(ROOT/(current+'.prompt.txt')).read_text();v['promptSha256']=sha(ROOT/(current+'.prompt.txt'));write(p,v);write(ROOT/(current+'.call.json'),v['submittedParameters'])
if __name__=='__main__':
    if sys.argv[1]=='accept': accept(*sys.argv[2:])
    elif sys.argv[1]=='target': target(*sys.argv[2:])
    elif sys.argv[1]=='context': context(*sys.argv[2:])
    elif sys.argv[1]=='enrich': enrich(*sys.argv[2:])
