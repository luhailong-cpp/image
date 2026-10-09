"""Exact source-pixel overlap diagnostics; no assembly, scaling or acceptance."""
from pathlib import Path
import hashlib,json
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def source(c):
    p=T/'native'/f'r01_c{c:02}.png'; r=read(str(p)+'.generation.json')
    assert sha(p)==r['sha256']
    im=Image.open(p).convert('RGB'); assert im.size==(1254,1254)
    return p,im
def save(name,specs,size,kind):
    canvas=Image.new('RGB',size); refs=[]
    for p,im,box,origin in specs:
        canvas.paste(im.crop(box),origin)
        refs.append({'file':str(p),'sha256':sha(p),'cropXYXY':list(box),'pasteXY':list(origin)})
    p=T/'qa/row1-native-overlaps'/name; p.parent.mkdir(parents=True,exist_ok=True);canvas.save(p)
    rec={'file':str(p),'sha256':sha(p),'pixels':list(size),'operation':kind,'derivedFrom':refs,'resized':False,'pixelScale':1,'finalArt':False}
    Path(str(p)+'.generation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8');return rec
def main():
    items=[]
    for c in range(1,4):
        pa,a=source(c);pb,b=source(c+1)
        items.append(save(f'c{c:02}-c{c+1:02}-same-global-overlap.png',[(pa,a,(1024,0,1254,1254),(0,0)),(pb,b,(0,0,230,1254),(230,0))],(460,1254),'complete 230px same-coordinate native overlap; left earlier native, right incoming native; no assembly'))
    contract=read(T/'source-contract.json');ref=contract['paletteAuthority'];np=Path(ref['file']);assert sha(np)==ref['sha256']
    north=Image.open(np).convert('RGB');assert north.size==(4096,4096)
    for c in range(1,5):
        p,im=source(c);x=-115+(c-1)*1024;lo=max(x,0);hi=min(x+1254,4096);w=hi-lo
        items.append(save(f'north-final-c{c:02}-same-global-115px-overlap.png',[(np,north,(lo,3981,hi,4096),(0,0)),(p,im,(lo-x,0,hi-x,115),(0,115))],(w,230),'external north final bottom115 and same-global target-native top115; only spatial intersection is compared; external pixels never pasted into guide'))
    out=T/'qa/row1-native-overlaps/manifest.json';out.write_text(json.dumps({'scope':'all3 full same-row overlaps and all4 intersections with pinned external north final; external common-edge acceptance pending','sheets':items},indent=2),encoding='utf-8')
    print(json.dumps({'sheets':[x['file']for x in items]}))
if __name__=='__main__':main()
