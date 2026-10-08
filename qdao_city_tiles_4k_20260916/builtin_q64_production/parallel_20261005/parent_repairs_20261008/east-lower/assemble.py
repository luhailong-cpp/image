from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,numpy as np

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
now=lambda:datetime.now(timezone.utc).isoformat()
host=Path('C:/Users/luyua/.codex/generated_images/01a10997-f575-7002-8029-c9cdf6a0e32a/exec-1e7ec14f-ce97-48c8-8cdc-397687800e7b.png')
native=R/'native.png';shutil.copy2(host,native)
src=json.loads((R/'context.png.generation.json').read_text(encoding='utf-8'))
receipt=json.loads((R/'tool-response.json').read_text(encoding='utf-8'))
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
with Image.open(native) as im:
    assert im.size==(1254,1254); out=np.asarray(im.convert('RGB'))
with Image.open(R/'context.png') as im: original=np.asarray(im.convert('RGB'))
save(R/'native.png.generation.json',dict(file=str(native),sha256=sha(native),generatedAt=receipt['ended']['current_time'],
    generationTimeEvidence='Completion time observed from clock immediately after tool return; exact server timestamp undisclosed.',
    generationWindow={'start':receipt['started'],'end':receipt['ended']},width=1254,height=1254,format='PNG',
    tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((R/'config.snapshot.json').read_text(encoding='utf-8')),
    submittedParameters={'model':None,'quality':None,'size':None,'transparent_background':False},actualModel=None,actualQuality=None,
    evidence={'toolResponse':str(R/'tool-response.json'),'hostSavedOriginal':str(host),'copyByteIdentical':sha(host)==sha(native)},
    unverifiedReason='Host-managed builtin; tool does not disclose actual model or quality.',prompt=str(R/'prompt.txt'),
    references=[{'file':str(R/'context.png'),'sha256':src['sha256'],'role':'exact edit target','generationRecord':str(R/'context.png.generation.json')},
    {'file':str(style),'sha256':sha(style),'role':'approved painterly style only'}]))

# Native local repair with measured subpixel highlight mismatch and a longer right return.
# No geometric registration, resizing or image blur. Core covers the old vertical mark.
x0,y0,x1,y1=558,565,800,735
core=[582,593,650,706]
y,x=np.mgrid[0:1254,0:1254]
edge=np.minimum.reduce([(x-x0)/(core[0]-x0),(x1-1-x)/(x1-1-core[2]),(y-y0)/(core[1]-y0),(y1-1-y)/(y1-1-core[3])])
t=np.clip(edge,0,1);mask=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
joined=((original.astype(np.uint32)*(255-mask[:,:,None])+out.astype(np.uint32)*mask[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(mask).save(R/'mask.png')
Image.fromarray(joined).save(R/'composite.png')
O=R/'coupled';O.mkdir(exist_ok=True)
outputs=[]
for part in src['parts']:
    source=part['source'];assert sha(source['path'])==source['sha256']
    with Image.open(source['path']) as im:arr=np.array(im.convert('RGB'))
    cx0,cy0,cx1,cy1=part['cropLTRB'];dx,dy=part['pasteXY'];w,h=cx1-cx0,cy1-cy0
    before=arr.copy();arr[cy0:cy1,cx0:cx1]=joined[dy:dy+h,dx:dx+w]
    p=O/(part['tile']+'.png');Image.fromarray(arr).save(p)
    changed=np.any(before!=arr,axis=2);yy,xx=np.where(changed)
    entry=dict(tileId=part['tile'],path=str(p),sha256=sha(p),width=4096,height=4096,
        source=source,changedPixels=int(changed.sum()),changedBBoxLTRB=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
        generationRecord=str(p)+'.generation.json')
    save(str(p)+'.generation.json',dict(file=str(p),sha256=entry['sha256'],createdAt=now(),
        operation='Native-scale local AI repair composited with asymmetric smoothstep return; 149px right return, 24px left, 28px top/bottom; no resize, warp, translation, tone matching or blur.',
        derivedFrom=[source,{'file':str(native),'sha256':sha(native),'generationRecord':str(R/'native.png.generation.json')}],
        placement=part,mask={'file':str(R/'mask.png'),'sha256':sha(R/'mask.png'),'roiLTRB':[x0,y0,x1,y1],'coreLTRB':core},formalAccepted=False))
    outputs.append(entry)
Q=R/'qa';Q.mkdir(exist_ok=True)
boards=[]
for name,box in [('center',(490,535,850,775)),('north',(520,525,840,625)),('south',(520,675,840,775)),('west',(508,535,622,765)),('east',(630,535,850,765))]:
    p=Q/(name+'.png');Image.fromarray(joined).crop(box).save(p)
    boards.append(dict(name=name,file=str(p),sha256=sha(p),contextLTRB=box,nativeScale=1))
save(R/'bindings.json',dict(createdAt=now(),status='parent_patch_pending_visual_review_and_integration',
    contextSource=src,outputs=outputs,qaBoards=boards,mask=str(R/'mask.png'),native=str(native),
    integrationRule='Recheck source SHA; do not overwrite active city task source or selection.',formalAccepted=False,wholeCityComplete=False))
print(json.dumps({'outputs':outputs,'qa':boards},ensure_ascii=True))
