"""Private 05-only source auditing and deterministic packaging. No AI pose synthesis."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib, json, argparse, shutil
BASE=Path(__file__).resolve().parents[1]
WORKSPACE=BASE.parents[3]
CLIENT=WORKSPACE.parent/'mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14/05_celestial_musician_girl'
SOURCE=WORKSPACE/'qdao_original_roster_v14_hd/recovery-20260921/05-delivery-preview/final/runtime'
DIRECTIONS=['N','NE','E','SE','S','SW','W','NW']
def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def out(p):
    p=(BASE/p).resolve()
    if not p.is_relative_to(BASE): raise ValueError('Output outside 05')
    p.parent.mkdir(parents=True,exist_ok=True)
    return p
def write(p,data): out(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def describe(p):
    with Image.open(p) as im:
        mode=im.mode
        a=im.convert('RGBA').getchannel('A')
        return {'file':str(p),'sha256':sha(p),'width':im.width,'height':im.height,'format':im.format,'mode':mode,'alphaExtrema':a.getextrema(),'bboxAlphaGt8':a.point(lambda x:255 if x>8 else 0).getbbox(),'pixelSha256':hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()}
def baseline():
    records=[]
    for d in DIRECTIONS:
        for n in range(1,17):
            rel=Path('walk')/d/f'{n:02}.png'
            c=describe(CLIENT/rel); s=describe(SOURCE/rel)
            records.append({'relativePath':rel.as_posix(),'client':c,'imageSource':s,'sameFileSha256':c['sha256']==s['sha256']})
    write('baseline-source.json',{'auditedAt':stamp(),'scope':'05 walk only; read-only client and source','currentClient':str(CLIENT),'source':str(SOURCE),'all128Match':all(x['sameFileSha256'] for x in records),'records':records,'appearance':json.loads((CLIENT/'appearance.json').read_text(encoding='utf-8')),'appearanceSha256':sha(CLIENT/'appearance.json')})
    print(json.dumps({'baselineFrames':len(records),'matches':sum(x['sameFileSha256'] for x in records),'dimensions':sorted(set((x['client']['width'],x['client']['height']) for x in records))}))
def import_image(direction,frame,version,source,receipt):
    key=f'generation/{direction}/{frame:02}-v{version}'
    req=json.loads((BASE/(key+'.request.json')).read_text(encoding='utf-8'))
    dest=out(key+'.png')
    if dest.exists(): raise ValueError('Refusing source overwrite')
    shutil.copyfile(source,dest)
    info=describe(dest)
    config=json.loads((WORKSPACE/'config/image-generation.json').read_text(encoding='utf-8'))
    rec={**info,'generatedAt':stamp(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{**req,'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露模型/质量；提示词尺寸不等于工具尺寸参数','evidence':{'receipt':receipt,'hostOutputPath':source},'prompt':key+'.prompt.txt','references':[{'file':r,'sha256':sha(r),'role':('exact character identity/camera' if i==0 else 'same character details' if i==1 else 'approved painted style or continuity reference')} for i,r in enumerate(req['referenced_image_paths'])],'nativeFrameCount':1,'nativePerFrame':[info['width'],info['height']],'status':'pending_visual_review'}
    write(key+'.png.generation.json',rec)
    print(json.dumps({'imported':str(dest),'width':info['width'],'height':info['height'],'mode':info['mode'],'sha256':info['sha256']}))
def export(direction,frame,version):
    key=f'generation/{direction}/{frame:02}-v{version}'
    src=BASE/(key+'.png')
    info=describe(src)
    if min(info['width'],info['height'])<1024 or info['width']!=info['height']: raise ValueError('Native frame is not square >=1024')
    if info['mode']!='RGBA' or info['alphaExtrema']!=(0,255): raise ValueError('True RGBA required')
    dst=out(f'candidate/walk/{direction}/{frame:02}.png')
    with Image.open(src) as im:
        # One global canvas transform; no bbox fitting or per-frame floor alignment.
        im.resize((1024,1024),Image.Resampling.LANCZOS).save(dst)
    rec={'file':str(dst),'sha256':sha(dst),'derivedFrom':{'file':str(src),'sha256':info['sha256'],'generationRecord':key+'.png.generation.json'},'operation':'uniform full-canvas downsample to 1024; no per-frame alignment; no pose synthesis','nativePerFrame':[info['width'],info['height']],'exportDimensions':[1024,1024],'root':{'x':512,'groundY':942.08,'pivot':[0.5,0.08],'pixelsPerUnit':104},'createdAt':stamp()}
    write(f'candidate/walk/{direction}/{frame:02}.png.generation.json',rec)
    print(json.dumps(describe(dst)))
p=argparse.ArgumentParser()
sp=p.add_subparsers(dest='cmd',required=True)
sp.add_parser('baseline')
s=sp.add_parser('import'); s.add_argument('direction');s.add_argument('frame',type=int);s.add_argument('version',type=int);s.add_argument('source');s.add_argument('receipt')
s=sp.add_parser('export');s.add_argument('direction');s.add_argument('frame',type=int);s.add_argument('version',type=int)
if __name__=='__main__':
    a=p.parse_args()
    if a.cmd=='baseline':baseline()
    elif a.cmd=='import':import_image(a.direction,a.frame,a.version,a.source,a.receipt)
    elif a.cmd=='export':export(a.direction,a.frame,a.version)

