import json, hashlib, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
BASE=Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters')
OUT=Path(__file__).parent
CONFIG=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def refs(n):
    return [dict(path=str(p),role=role,sha256=sha(p)) for p,role in [
        (BASE/'07_moon_shadow_assassin_girl'/f'frames/cast/W/{n:02}.png','edit_target_original_Moon_Shadow_frame'),
        (BASE/'09_bamboo_archer_girl'/f'runtime/cast/W/{n:02}.png','same_heading_foot_axis_perspective_only'),
        (Path('D:/work/image/designs/jubaozhai-ui/02-characters.png'),'approved_primary_painted_style_reference')]]
mode=sys.argv[1]
if mode=='init':
    write(OUT/'original-reference-snapshot.json',dict(capturedAt=datetime.now(timezone.utc).isoformat(),configSnapshot=CONFIG,frames={f'{n:02}':refs(n) for n in range(1,17)}))
    print('Original references for all 16 cast W frames frozen.')
elif mode=='prepare':
    stem=sys.argv[2]
    data=json.loads((OUT/f'{stem}.args.json').read_text(encoding='utf-8-sig'))
    n=int(stem[:2]); rs=refs(n)
    write(OUT/f'{stem}.request.json',dict(requestedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',parameters=data,configSnapshot=CONFIG,references=rs,editSource=dict(path=rs[0]['path'],sha256=rs[0]['sha256'],generationRecord=rs[0]['path']+'.generation.json')))
    print(stem+' request captured before image generation')
elif mode=='save':
    stem,source,note=sys.argv[2:5]
    dst=OUT/f'{stem}.png'; shutil.copyfile(source,dst)
    im=Image.open(dst)
    if im.size!=(1254,1254) or im.mode!='RGBA': raise ValueError((im.size,im.mode))
    req=json.loads((OUT/f'{stem}.request.json').read_text(encoding='utf-8-sig'))
    write(OUT/f'{stem}.png.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=datetime.now(timezone.utc).isoformat(),width=im.width,height=im.height,mode=im.mode,format='PNG',tool='image_gen.imagegen',route='builtin_host_managed',configSnapshot=req['configSnapshot'],submittedParameters=dict(model=None,quality=None,transparent_background=True),actualModel=None,actualQuality=None,unverifiedReason='Host managed; tool exposes no model/quality selectors and returned no verified model/quality.',evidence=dict(receipt=f'{stem}.receipt.json',source=source,request=f'{stem}.request.json'),prompt=f'{stem}.request.json#/parameters/prompt',references=req['references'],editSource=req['editSource'],visualReview=dict(status='recommend_for_parent_review',notes=note),timing=dict(frameDurationMs=45,frameCount=16,cycleDurationMs=720)))
    print(stem+' saved native RGBA 1254; '+sha(dst))
