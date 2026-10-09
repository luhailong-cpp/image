"""Unscaled source-overlap QA sheets, not assembled or approved tile pixels."""
from pathlib import Path
import hashlib, json, sys
from PIL import Image

TILE = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source(r,c):
    p=TILE/'native'/f'r{r:02}_c{c:02}.png'
    d=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
    im=Image.open(p).convert('RGB')
    assert im.size==(1254,1254) and sha(p)==d['sha256']
    return p,im
def save(out,name,specs,size):
    image=Image.new('RGB',size); origins=[]
    for r,c,rect,dest in specs:
        p,im=source(r,c); image.paste(im.crop(rect),dest)
        origins.append({'file':str(p),'sha256':sha(p),'cropXYXY':list(rect),'pasteXY':list(dest)})
    p=out/name;image.save(p)
    d={'file':str(p),'sha256':sha(p),'pixels':list(size),'operation':'two exact unscaled views of the same global230px overlap; not an assembled seam','derivedFrom':origins,'finalArt':False,'resized':False}
    Path(str(p)+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    return d
def main(row):
    out=TILE/'qa'/f'row{row}-native-overlaps';out.mkdir(parents=True,exist_ok=True);items=[]
    for c in range(1,4):
        items.append(save(out,f'c{c:02}-c{c+1:02}-same-global-overlap.png',[(row,c,(1024,0,1254,1254),(0,0)),(row,c+1,(0,0,230,1254),(230,0))],(460,1254)))
    for c in range(1,5):
        items.append(save(out,f'north-c{c:02}-same-global-overlap.png',[(row-1,c,(0,1024,1254,1254),(0,0)),(row,c,(0,0,1254,230),(0,230))],(1254,460)))
    (out/'manifest.json').write_text(json.dumps({'scope':f'row{row}: all3 same-row and4 northern native overlaps; before final repair synchronization and shared mask assembly','sheets':items},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sheets':[i['file'] for i in items]}))
if __name__=='__main__':main(int(sys.argv[1]))
