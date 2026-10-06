from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image

tile=Path(__file__).resolve().parent;out=tile/'early-vertical-qa';out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
canvas=Image.new('RGB',(4096,3072));sources=[]
for row in range(1,4):
    for col in range(1,5):
        p=tile/'native'/f'r{row:02d}_c{col:02d}.png';r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
        assert sha(p)==r['sha256']
        im=Image.open(p);assert im.size==(1254,1254) and im.mode=='RGB'
        canvas.paste(im.crop((115,115,1139,1139)),((col-1)*1024,(row-1)*1024))
        sources.append({'file':str(p),'sha256':sha(p),'sourceBox':[115,115,1139,1139],
                        'destinationXY':[(col-1)*1024,(row-1)*1024]})
checks=[]
def save(name,box,kind):
    p=out/(name+'.png')
    if p.exists():raise FileExistsError(p)
    canvas.crop(box).save(p)
    checks.append({'file':str(p),'sha256':sha(p),'coreBox':box,'kind':kind,'actualViewed':False,
                  'operation':'integer crop of exact native cores; no resampling'})
for row in range(3):
    for seam in range(1,4):
        x=seam*1024;y=row*1024
        save(f'vertical_c{seam}_r{row+1}',[x-128,y,x+128,y+1024],'vertical')
        x+=115
        save(f'guide_vertical_c{seam+1}_r{row+1}',[x-64,y,x+64,y+1024],'guide_vertical')
for row in range(1,3):
    for col in range(1,4):
        x=col*1024;y=row*1024
        save(f'intersection_r{row}_c{col}',[x-256,y-256,x+256,y+256],'intersection')
manifest={'writtenAtUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,
          'derivedCanvasPixels':[4096,3072],'partialOnly':True,'isComplete4KCandidate':False,
          'canvasRawRGBSha256':hashlib.sha256(canvas.tobytes()).hexdigest(),
          'formalAccepted':False,'checks':checks,'qaStatus':'pending_actual_view'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'manifest':str(out/'manifest.json')}))
