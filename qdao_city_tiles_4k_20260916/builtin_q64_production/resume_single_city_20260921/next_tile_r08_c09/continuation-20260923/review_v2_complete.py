"""Read-only source verification and exact-pixel QA crops for the second repair."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
V=HERE/'versions/bottom-material-v2-20260923T094331634966Z'
OUT=V/('complete-review-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p): return {'file':str(p),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(e):
    assert Path(e['file']).is_file(), e
    assert sha(e['file'])==e['sha256'],e
    return e
r=read(V/'repair.json')
for k in ['candidate','sourceCandidate','sourceRecord','neighbor','mask','script','helper']: verify(r[k])
for s in r['sources']:
    for k in ['prepared','native','generationRecord','mask']: verify(s[k])
    prep=read(s['prepared']['file'])
    for k in ['context','mask','request','prompt']: verify(prep[k])
    for e in prep['references']: verify(e)
    gen=read(s['generationRecord']['file'])
    assert gen['sha256']==s['native']['sha256']
    assert gen['actualModel'] is None and gen['actualQuality'] is None
a=np.asarray(Image.open(r['candidate']['file']).convert('RGB'))
b=np.asarray(Image.open(r['sourceCandidate']['file']).convert('RGB'))
m=np.asarray(Image.open(r['mask']['file']))
assert a.shape==(4096,4096,3)
changed=np.any(a!=b,axis=2)
assert not np.any(changed & (m==0))
assert changed.sum()==r['changedPixels']
OUT.mkdir();items=[]
def save(name,im,scope):
    p=OUT/(name+'.png');im.save(p);items.append({'id':name,**info(p),'scope':scope,'pixelScale':'1:1','resampled':False})
im=Image.fromarray(a)
for axis in ['v','h']:
    for n in [1,2,3]:
        pos=1024*n
        board=Image.new('RGB',(1024,2048))
        parts=[]
        for j in range(4):
            box=[pos-256,1024*j,pos+256,1024*(j+1)] if axis=='v' else [1024*j,pos-256,1024*(j+1),pos+256]
            c=im.crop(box)
            if axis=='v': c=c.transpose(Image.Transpose.ROTATE_90)
            board.paste(c,(0,j*512));parts.append(box)
        save(f'full-{axis}-{n:02}',board,{'axis':axis,'coordinate':pos,'segmentsLTRB':parts,'verticalBoardsRotated90':axis=='v'})
jboard=Image.new('RGB',(1536,1536));coords=[]
for yi,y in enumerate([1024,2048,3072]):
    for xi,x in enumerate([1024,2048,3072]):
        box=[x-256,y-256,x+256,y+256]
        jboard.paste(im.crop(box),(xi*512,yi*512));coords.append(box)
save('nine-junctions',jboard,{'boxesLTRB':coords,'order':'row-major'})
overview=im.resize((1024,1024),Image.Resampling.LANCZOS);overview.save(OUT/'overview-reference-only.png')
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':info(V/'r08_c09.png'),'repair':info(V/'repair.json'),'neighbor':r['neighbor'],'sourceIntegrityChecked':True,'outsideAllowedMaskPixelsUnchanged':True,'changedPixels':int(changed.sum()),'evidence':items,'overviewRole':'downsampled context only, never acceptance evidence','script':info(Path(__file__))}
(OUT/'verification-and-crops.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(OUT),'candidate':out['candidate'],'repair':out['repair']}))
