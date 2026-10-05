from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
from PIL import Image
ROOT=Path(__file__).resolve().parent
TASK=ROOT.parent.parent
REPO=Path('D:/work/image')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(pid,original,start,finish):
    src=Path(original); out=ROOT/(pid+'.png')
    assert not out.exists(),out
    shutil.copy2(src,out)
    im=Image.open(out); im.load()
    assert im.size==(1254,1254),im.size
    guide=TASK/'guides'/(pid+'.png')
    target=ROOT/(pid+'-target.png')
    if not target.exists(): target=guide
    refs=[dict(file=str(target),sha256=sha(target),role='exact layout edit target with native left neighbor context when target exists'),dict(file=str(REPO/'designs/gameplay-ui/04-guild.png'),sha256=sha(REPO/'designs/gameplay-ui/04-guild.png'),role='primary approved art style; no UI content')]
    d=dict(file=str(out),sha256=sha(out),generatedAt=finish,startedAt=start,width=im.width,height=im.height,format=im.format,tool='image_gen.imagegen',route='builtin',originalToolOutputPath=str(src),configSnapshot=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[r['file'] for r in refs],prompt=(ROOT/(pid+'.prompt.txt')).read_text(encoding='utf-8').strip()),actualModel=None,actualQuality=None,evidence=dict(toolResultFile=str(ROOT/(pid+'.tool-result.json')),officialBatchVerification=str(TASK/'evidence/model-verification.json')),unverifiedReason='宿主管理，工具未开放型号/质量选择器，返回值未披露型号/质量；配置目标不等于实际版本。',prompt=str(ROOT/(pid+'.prompt.txt')),references=refs,nativePixels=True,resized=False,coreRectLTRB=[115,115,1139,1139],corePixels=[1024,1024],haloPixels=115,formalTile=False,formalAccepted=False)
    write(str(out)+'.generation.json',d)
    write(ROOT/(pid+'.tool-result.json'),dict(tool='image_gen.imagegen',returnedKeys=['image_url','output_hint'],image_url='data:image/png;base64 payload omitted; identical bytes preserved at originalToolOutputPath and file',originalToolOutputPath=str(src),originalToolOutputSha256=sha(src),file=str(out),sha256=sha(out),startedAt=start,finishedAt=finish,actualModel=None,actualQuality=None))
    print(json.dumps(dict(file=str(out),sha256=sha(out),size=im.size)))
def target(pid,left):
    guide=TASK/'guides'/(pid+'.png'); left=ROOT/(left+'.png'); out=ROOT/(pid+'-target.png')
    im=Image.open(guide).convert('RGB'); li=Image.open(left)
    assert im.size==li.size==(1254,1254)
    im.paste(li.crop((1024,0,1254,1254)),(0,0)); im.save(out)
    write(str(out)+'.generation.json',dict(file=str(out),sha256=sha(out),createdAt=now(),width=1254,height=1254,format='PNG',derivedFrom=[dict(file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json') for p in [guide,left]],operation=dict(kind='authorized native context paste into layout-only guide',guide='1254 square enlarged layout reference; not production pixels',sourceCropLTRB=[1024,0,1254,1254],destinationXY=[0,0],scale=1,resampling=None,productionPixels=False),productionPixels=False))
    print(str(out))
if __name__=='__main__':
    if sys.argv[1]=='record': record(*sys.argv[2:])
    elif sys.argv[1]=='target': target(*sys.argv[2:])
