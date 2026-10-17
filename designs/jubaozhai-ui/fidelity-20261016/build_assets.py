"""Native artwork extraction from approved Jubaozhai pages; never calls a model or modifies the client."""
from pathlib import Path
from PIL import Image, ImageOps
from collections import deque
import json, hashlib, uuid
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
CLIENT=Path('E:/work/mmorpg-client')
OUT=ROOT/'staged/Assets/Resources/UI/Ugui/JubaozhaiFidelity20261016'
OUT.mkdir(parents=True,exist_ok=True)
images={n:Image.open(SOURCE/(n+'.png')).convert('RGB') for n in ('01-empty','02-characters','04-weapons')}
rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
template_path=ROOT/'sprite-meta-template.txt'
if not template_path.exists():
    template_path.write_text((SOURCE.parents[0]/'gameplay-ui/fidelity-20261016/staged/Assets/Resources/UI/Ugui/GameplayFidelity20261016/inventory-frame.png.meta').read_text(encoding='utf-8'),encoding='utf-8')
template=template_path.read_text(encoding='utf-8')
def sprite(name,im,source,rect=None,operation='native crop'):
    path=OUT/(name+'.png'); im.save(path)
    meta=template
    import re
    meta=re.sub(r'(?m)^guid: .*$', 'guid: '+uuid.uuid5(uuid.NAMESPACE_URL,'jubaozhai-fidelity-20261016/'+name).hex,meta)
    meta=re.sub(r'(?m)^    spriteID: .*$', '    spriteID: '+uuid.uuid5(uuid.NAMESPACE_DNS,'jubaozhai-'+name).hex,meta)
    meta=meta.replace('Gameplay fidelity native crop 20261016','Jubaozhai fidelity native crop 20261016')
    Path(str(path)+'.meta').write_text(meta,encoding='utf-8')
    rows.append(dict(name=name,source='../'+source+'.png',source_sha256=sha(SOURCE/(source+'.png')),native_source_size=list(images[source].size),source_rect=rect,operation=operation,output=str(path.relative_to(ROOT)).replace('\\','/'),size=list(im.size),sha256=sha(path),generation='no new generation; derives from original source lineage in ../manifest.json'))
def crop(name,source,rect):sprite(name,images[source].crop(rect),source,list(rect))
def fill(im,area,tile):
    x0,y0,x1,y1=area;w,h=tile.size
    for y in range(y0,y1,h):
        for x in range(x0,x1,w):
            piece=tile
            if (x-x0)//w%2:piece=ImageOps.mirror(piece)
            if (y-y0)//h%2:piece=ImageOps.flip(piece)
            im.paste(piece.crop((0,0,min(w,x1-x),min(h,y1-y))),(x,y))

# The exterior, original frame, static carved title, two hanging shop signs,
# jade beads, red tassels and flowered mountain city remain exact source pixels.
base=images['01-empty'].copy()
paper=images['01-empty'].crop((1620,264,1684,328))
for area in ((198,197,468,735),(498,135,1729,773)):
    fill(base,area,paper)
sprite('native-frame',base,'01-empty',operation='same-source mirrored paper tiles remove only dynamic interior; approved exterior/frame/static title/tassels untouched; no resize')

header=images['01-empty'].crop((500,198,1726,249))
header_paper=images['01-empty'].crop((1030,207,1070,239))
for area in ((236,8,364,43),(631,8,722,43),(1000,8,1166,43)):fill(header,area,header_paper)
sprite('table-header',header,'01-empty',[500,198,1726,249],'native header border crop; fixed labels removed for native sort/header controls')

for name,rect,fill_global in (
    ('section-selected',(1737,188,1830,347),(222,141,263,180)),
    ('section-normal',(1737,351,1830,511),(1763,376,1773,386))):
    panel=images['01-empty'].crop(rect)
    fill(panel,(19,23,74,panel.height-22),images['01-empty'].crop(fill_global))
    sprite(name,panel,'01-empty',list(rect),'native vertical hanging plate crop with only central label cleared')
    if name=='section-selected':
        short=Image.new('RGB',(panel.width,147));short.paste(panel.crop((0,0,panel.width,74)),(0,0));short.paste(panel.crop((0,86,panel.width,panel.height)),(0,74))
        sprite('section-selected-short',short,'01-empty',list(rect),'native selected plate crop; remove twelve central blank rows to match shorter third hanging plate; edges remain unscaled')
short=images['01-empty'].crop((1737,512,1830,659))
fill(short,(19,20,74,127),images['01-empty'].crop((1763,376,1773,386)))
sprite('section-normal-short',short,'01-empty',[1737,512,1830,659],'native third hanging plate with only central label cleared; preserves red tassel below')

# Existing top tabs already have clean, text-free jade/ivory skins. Reuse all
# 36 existing Sprite resources, and add the missing native-position ornaments.
crop('search-button','02-characters',(819,707,897,770))
crop('page-previous','02-characters',(986,718,1032,766))
crop('page-next','02-characters',(1134,718,1181,766))

bubble=images['01-empty'].crop((1005,375,1456,525))
fill(bubble,(77,28,392,124),images['01-empty'].crop((1062,410,1083,431)))
sprite('empty-bubble',bubble,'01-empty',[1005,375,1456,525],'native speech bubble crop; only interior copy cleared for live empty/error messages')

def icon(name,rect):
    im=images['01-empty'].crop(rect).convert('RGBA');pix=im.load();w,h=im.size;seen=set();q=deque()
    for x in range(w):q.extend(((x,0),(x,h-1)))
    for y in range(h):q.extend(((0,y),(w-1,y)))
    while q:
        x,y=q.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y));r,g,b,a=pix[x,y]
        if not (r>171 and g>157 and b>128 and max(r,g,b)-min(r,g,b)<85):continue
        pix[x,y]=(0,0,0,0);q.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    sprite(name,im,'01-empty',list(rect),'native decorative category glyph; boundary-connected paper alpha extraction')
for name,rect in (
    ('category-character',(218,303,255,344)),('category-pet',(215,357,257,397)),
    ('category-weapon',(216,409,257,453)),('category-armor',(215,463,257,507)),
    ('category-set',(216,517,257,561)),('category-treasure',(216,573,257,617)),
    ('category-jewelry',(218,627,257,668)),('category-summoningorder',(215,682,257,726)),
    ('category-search',(217,202,256,242)),('category-favorite',(215,253,257,296))):icon(name,rect)

existing=json.loads((SOURCE/'unity-slices/manifest.json').read_text(encoding='utf-8-sig'))
reused=[]
for item in existing['sprites']:
    p=CLIENT/item['output']
    reused.append(dict(name=item['name'],client_path=item['output'],sha256=sha(p),original_slice_sha256=item.get('outputSha256'),lineage='../unity-slices/manifest.json',size=list(Image.open(p).size)))
(ROOT/'asset-manifest.json').write_text(json.dumps(dict(schema='qdao.jubaozhai.fidelity.native.v1',native_canvas=[1932,814],new_assets=rows,reused_existing_sprites=reused,new_ai_generation_calls=0,importer='Sprite Single FullRect 100PPU Uncompressed mipmaps=false max4096',postprocessor_added=False),ensure_ascii=False,indent=2),encoding='utf-8')
for suffix in ('.png','.png.meta'):
    stale=(OUT/('eagle-heading'+suffix)).resolve()
    if stale.parent==OUT.resolve() and stale.exists():stale.unlink()
print(f'{len(rows)} native derived assets; {len(reused)} current Sprite resources reused')
