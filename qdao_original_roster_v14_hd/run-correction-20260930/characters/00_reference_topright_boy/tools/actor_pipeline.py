"""Private 00-only provenance/preview/export helpers. Never modifies other actors or client."""
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[3]
DIRECTIONS=['N','NE','E','SE','S','SW','W','NW']
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    p=Path(p).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('Write outside actor root')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
    with Image.open(p) as im:
        rgba=im.convert('RGBA'); a=rgba.getchannel('A'); hist=a.histogram()
        return dict(width=im.width,height=im.height,mode=im.mode,format=im.format,sha256=sha(p),
                    alpha_bbox=a.getbbox(),alpha_zero_pixels=hist[0],alpha_opaque_pixels=hist[255],
                    decoded_pixel_sha256=hashlib.sha256(rgba.tobytes()).hexdigest())
def snapshot():
    base=PROJECT.parent/'mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV13/00_reference_topright_boy'
    files=[]
    for d in DIRECTIONS:
        for n in range(1,17):
            p=base/'walk'/d/f'{n:02d}.png'
            files.append(dict(path=str(p),direction=d,frame=n,modifiedAt=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),**info(p)))
    save(ROOT/'baseline.json',dict(capturedAt=now(),readOnly=True,clientRoot=str(base),frames=files))
    print(json.dumps(dict(baselineFrames=len(files),output=str(ROOT/'baseline.json'))))
def register(request_path,source):
    req=json.loads(Path(request_path).read_text(encoding='utf-8'))
    target=ROOT/req['destination']
    if target.exists(): raise ValueError('Never overwrite native output')
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    dimensions=info(target)
    rec=dict(schema_version=1,file=target.name,generatedAt=now(),generatedAtBasis='local archive completion time; provider completion not disclosed',
             requestedAt=req['requestedAt'],tool='image_gen.imagegen',route='builtin',
             configSnapshot=json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8')),
             officialRecheckedAt='2026-09-30',
             officialEvidence=dict(url='https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst',finding='most capable image model, supports max; verified in this turn'),
             submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=req['references']),
             actualModel=None,actualQuality=None,
             unverifiedReason='宿主管理，工具未披露实际模型与质量；配置与提示词不作为返回证据。',
             prompt=req['prompt'],references=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][i]) for i,p in enumerate(req['references'])],
             evidence=dict(toolOutputFile=str(source),toolOutputHint=req['outputHint']),
             state='unreviewed_native_candidate',**dimensions)
    save(str(target)+'.generation.json',rec)
    print(json.dumps(dict(file=str(target),**dimensions)))
def export(source,direction,frame):
    source=Path(source).resolve()
    if not source.is_relative_to(ROOT/'generation'): raise ValueError('native source must belong to actor')
    rec=json.loads(Path(str(source)+'.generation.json').read_text(encoding='utf-8'))
    with Image.open(source) as im:
        if im.width!=im.height or im.width<1024 or im.mode!='RGBA': raise ValueError('Native square RGBA >=1024 required')
        if info(source)['alpha_zero_pixels']==0: raise ValueError('No true transparency')
        # Whole-canvas fixed scaling, not per-frame alpha bounds. No pose interpolation.
        out=im.resize((1024,1024),Image.Resampling.LANCZOS)
        target=ROOT/'candidate/walk'/direction/f'{frame:02d}.png'
        target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
    save(str(target)+'.generation.json',dict(file=target.name,exportedAt=now(),**info(target),
         derivedFrom=dict(path=str(source),sha256=sha(source),generationRecord=str(source)+'.generation.json'),
         operation='Uniform whole-square downsample to 1024; no bbox normalization, translation, mirroring or interpolation between poses',
         virtualGroundPx=942,rootPx=[512,942],spritePivotBottomLeft=[0.5,80/1024],
         actualModel=rec['actualModel'],actualQuality=rec['actualQuality'],visualApproval='pending'))
    print(json.dumps(dict(exported=str(target),sha256=sha(target))))
def preview():
    entries=[]
    for d in DIRECTIONS:
        files=sorted((ROOT/'candidate/walk'/d).glob('*.png'))
        if not files: continue
        contact=Image.new('RGB',(1024,1088),(45,53,57)); draw=ImageDraw.Draw(contact)
        for k,p in enumerate(files):
            with Image.open(p) as im:
                tile=im.convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
                x=(k%4)*256;y=(k//4)*272
                contact.paste(tile,(x,y),tile)
                draw.line((x,y+235,x+255,y+235),fill=(85,102,108))
                draw.text((x+8,y+254),p.stem,fill='white')
            entries.append(dict(direction=d,frame=int(p.stem),path='../candidate/walk/'+d+'/'+p.name,**info(p)))
        p=ROOT/'preview'/f'{d}-contact.jpg';p.parent.mkdir(parents=True,exist_ok=True);contact.save(p,quality=94)
        save(str(p)+'.derivation.json',dict(operation='4x4 contact sheet with uniform preview downsampling',sourceFrames=[dict(path=str(x),sha256=sha(x)) for x in files]))
    save(ROOT/'preview/frames.json',dict(frames=entries))
    save(ROOT/'candidate-inventory.json',dict(timestamp=now(),present=len(entries),expected=128,frames=entries,visualAcceptance='not_implied_by_inventory'))
    print(json.dumps(dict(candidateFrames=len(entries),preview=str(ROOT/'preview/index.html'))))
p=argparse.ArgumentParser();p.add_argument('command',choices=['snapshot','register','export','preview']);p.add_argument('args',nargs='*');a=p.parse_args()
if a.command=='snapshot':snapshot()
elif a.command=='register':register(*a.args)
elif a.command=='export':export(a.args[0],a.args[1],int(a.args[2]))
else:preview()

