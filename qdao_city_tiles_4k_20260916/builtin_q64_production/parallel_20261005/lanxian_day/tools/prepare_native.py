"""Create guide-only square with exact existing north/west overlaps."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import argparse,json,hashlib

ROOT=Path(__file__).resolve().parents[1]; TILE=ROOT/'r08_c09'
REPO=Path('D:/work/image')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(row,col):
    assert 1<=row<=4 and 1<=col<=4
    cell=f'r{row:02d}_c{col:02d}'
    assert not (TILE/'native'/f'{cell}.png').exists(),cell
    neighbors=[]
    for r,c,side in [(row,col-1,'west'),(row-1,col,'north')]:
        if r and c:
            p=TILE/'native'/f'r{r:02d}_c{c:02d}.png'
            if not p.exists() or not Path(str(p)+'.generation.json').exists():raise SystemExit(f'WAIT: {side} neighbor {p}')
            neighbors.append((side,p))
    region=TILE/'regional/regional-v2.png'
    master=Image.open(region).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
    x,y=(col-1)*1024,(row-1)*1024
    guide=master.crop((x,y,x+1254,y+1254))
    constraints=[]
    for side,p in neighbors:
        im=Image.open(p).convert('RGB')
        if side=='west':guide.paste(im.crop((1024,0,1254,1254)),(0,0));box=[0,0,230,1254]
        else:guide.paste(im.crop((0,1024,1254,1254)),(0,0));box=[0,0,1254,230]
        constraints.append({'side':side,'file':str(p),'sha256':sha(p),'targetBox':box})
    if col==1:
        h=read(ROOT/'handoff.json');west=next(t for t in h['baselineCandidates'] if t['tile']=='r08_c08')
        im=Image.open(west['file']).convert('RGB')
        for gy in range(1254):
            sy=min(4095,max(0,y+gy-115))
            guide.paste(im.crop((3981,sy,4096,sy+1)),(0,gy))
        constraints.append({'side':'external_west','file':west['file'],'sha256':west['sha256'],'targetBox':[0,0,115,1254],'unavailableExterior':'guide-only edge padding at map-local y<0 or >=4096'})
    target=TILE/'guides'/f'{cell}.layout-only.png';guide.save(target)
    sides=[]
    if col>1:sides.append('the first230px on the left')
    else:sides.append('the first115px on the left')
    if row>1:sides.append('the first230px at the top')
    prompt=(f'Use case: precise-object-edit. Make one opaque full-bleed square native game-map DETAIL in exactly Image 1 framing. This is cell {cell} within an already planned town-plaza tile, not a new overall scene. Image 1 is a layout guide with true native neighbor pixels in '+ ' and '.join(sides)+'. These edge strips are exact geometry and material constraints: preserve their coordinates, colors and scale and smoothly connect every visible groove, bevel, ring, leaf outline and shadow. Reconstruct the soft remaining interior into crisp real detail at the same mapped size. Do not shift, magnify, rotate, crop, add symbols or redesign the composition. Image 2 is the user-confirmed PRIMARY style reference: clean bright rounded full-bodied Daoist chibi fantasy, polished hand-painted materials, restrained surface variation and clear contour, not photographic. Copy no UI or text. Keep all ivory stone platform edges and shallow warm-brown risers, cream trim widths, gray radial paving, warm planter, tree footprint and existing shadows where present. Quiet clean stone, crisp joints and rounded bevels, no gritty noise, cracks, speckles, excessive marbling, blur or sharpening halos. No new circles, medallions, stairs, buildings, objects, characters, frame, labels or watermark. Return the single target square only, preserving the native1254-square context framing; highest available visual fidelity.')
    pf=TILE/'prompts'/f'{cell}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
    refs=[{'path':str(target),'role':'Target layout only with exact existing neighbor bands; every constrained coordinate is invariant'}, {'path':str(REPO/'designs/gameplay-ui/04-guild.png'),'role':'User-confirmed primary painting/material style; no UI copied'}]
    job={'tileDir':str(TILE),'cell':cell,'promptFile':str(pf),'references':refs,'configSnapshot':read(REPO/'config/image-generation.json'),'generatedAt':datetime.now(timezone.utc).isoformat(),'constraints':constraints,'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['path'] for r in refs]},'guideDerivation':{'regional':str(region),'regionalSha256':sha(region),'regionalResampling':'BICUBIC4326 only for guide; forbidden in final pixels','guide':str(target),'guideSha256':sha(target),'guideOnly':True,'cropInExtended':[x,y,x+1254,y+1254]}}
    jf=TILE/'jobs'/f'{cell}.json';write(jf,job)
    print(json.dumps({'job':str(jf),'promptFile':str(pf),'references':refs,'constraints':[x['side'] for x in constraints]}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('row',type=int);p.add_argument('col',type=int);a=p.parse_args();prepare(a.row,a.col)
