"""Read reviewed RGBA artwork and make deterministic, contract-sized UI pieces."""
from pathlib import Path
import json
from functools import lru_cache
from PIL import Image

PACK = Path(__file__).resolve().parents[1]
REPO = PACK.parent
ARTWORK = PACK / 'artwork'
LANCZOS = Image.Resampling.LANCZOS


def save(image, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, compress_level=9)


def _entry(name):
    index = json.loads((ARTWORK/'index.json').read_text(encoding='utf-8-sig'))
    return index['assets'][name]


def _read(relative):
    path = (ARTWORK/relative).resolve()
    if not path.is_relative_to(ARTWORK.resolve()):
        raise ValueError(f'Unsafe artwork path: {relative}')
    with Image.open(path) as image:
        return image.convert('RGBA')


def load_art(name):
    """The complete crop, including separately managed hanging ornaments."""
    return _read(_entry(name)['file'])


def _fit(image, width, height, pad=0):
    width, height, pad = int(width), int(height), int(pad)
    if width <= 2*pad or height <= 2*pad:
        raise ValueError((width, height, pad))
    ratio = min((width-2*pad)/image.width, (height-2*pad)/image.height)
    item = image.resize((max(1,round(image.width*ratio)), max(1,round(image.height*ratio))), LANCZOS)
    result = Image.new('RGBA', (width,height))
    result.alpha_composite(item, ((width-item.width)//2, (height-item.height)//2))
    return result


def fit_art(name, w, h, pad=0):
    return _fit(load_art(name), w, h, pad)


def _composite_clipped(target, image, x, y):
    x, y = int(round(x)), int(round(y))
    left, top = max(0,x), max(0,y)
    right, bottom = min(target.width,x+image.width), min(target.height,y+image.height)
    if right > left and bottom > top:
        target.alpha_composite(image.crop((left-x,top-y,right-x,bottom-y)), (left,top))


def _horizontal_caps(entry, width, height, borders, pad):
    """Uniform complete painted endcaps; stretch only the unornamented middle.

    These plate contracts permit horizontal resizing only. Keeping each full cap
    as a single object also preserves dangling tassels and round cloud scrolls.
    """
    source = _read(entry['file'])
    sl, sr = entry['nine_slice']['left'], entry['nine_slice']['right']
    dl, dt, dr, db = borders
    scale = min((height-2*pad)/source.height, (dl-pad)/sl, (dr-pad)/sr)
    dh = max(1,round(source.height*scale))
    lw,rw = max(1,round(sl*scale)),max(1,round(sr*scale))
    y = (height-dh)//2
    result = Image.new('RGBA',(width,height))
    result.alpha_composite(source.crop((0,0,sl,source.height)).resize((lw,dh),LANCZOS),(pad,y))
    result.alpha_composite(source.crop((source.width-sr,0,source.width,source.height)).resize((rw,dh),LANCZOS),(width-pad-rw,y))
    center = source.crop(entry.get('horizontal_center_sample',[sl,0,source.width-sr,source.height]))
    result.alpha_composite(center.resize((width-2*pad-lw-rw,dh),LANCZOS),(pad+lw,y))
    if entry.get('horizontal_center_sample'):
        for stamp in entry.get('fixed_stamps',[]):
            item = _read(stamp['file'])
            item = item.resize((max(1,round(item.width*scale)),max(1,round(item.height*scale))),LANCZOS)
            box = stamp['source_box_xyxy']
            _composite_clipped(result,item,(width-item.width)/2,y+box[1]*scale)
    return result


def nine_slice(name, w, h, dest_borders, pad=0):
    """Explicit fixed source borders; optional sampled rails and uniform ornaments.

    Destination borders always retain the caller's existing left/top/right/bottom
    contract. Hanging ornaments reserve space within the destination bottom border.
    Source border amounts are reviewed pixels recorded per artwork, never inferred
    from a shared percentage. Round badges should use fit_art instead.
    """
    width, height, pad = int(w), int(h), int(pad)
    entry = _entry(name)
    if entry.get('resize_mode') == 'horizontal_caps':
        return _horizontal_caps(entry,width,height,tuple(int(round(value)) for value in dest_borders),pad)
    source = _read(entry.get('body_file',entry['file']))
    borders = entry.get('nine_slice')
    if borders is None:
        raise ValueError(f'{name} has no reviewed source nine-slice borders')
    sl,st,sr,sb = [int(borders[side]) for side in ('left','top','right','bottom')]
    dl,dt,dr,db = [int(round(value)) for value in dest_borders]
    if not (0<sl<source.width-sr<source.width and 0<st<source.height-sb<source.height):
        raise ValueError(f'{name}: invalid source borders {borders} for {source.size}')
    if not (pad<dl<width-dr<width-pad and pad<dt<height-db<height-pad):
        raise ValueError(f'{name}: invalid destination borders {(dl,dt,dr,db)} for {(width,height,pad)}')
    hanging = entry.get('hanging_overlays', [])
    extension = max((part['source_box_xyxy'][3]-source.height for part in hanging),default=0)
    ornament_scale = min((dl-pad)/sl,(dr-pad)/sr,(dt-pad)/st,(db-pad)/(sb+max(0,extension)))
    reserve = 0 if entry.get('hanging_inside_canvas') else min(max(0,round(extension*ornament_scale)),db-pad-1)
    xs,ys = [0,sl,source.width-sr,source.width],[0,st,source.height-sb,source.height]
    dx,dy = [pad,dl,width-dr,width-pad],[pad,dt,height-db,height-pad-reserve]
    result = Image.new('RGBA',(width,height))
    edge_names = {(0,1):'top',(2,1):'bottom',(1,0):'left',(1,2):'right'}
    for row in range(3):
        for col in range(3):
            rect = entry.get('edge_samples',{}).get(edge_names.get((row,col)),
                    [xs[col],ys[row],xs[col+1],ys[row+1]])
            tile = source.crop(rect['box']).rotate(rect.get('rotate',0),expand=True) if isinstance(rect,dict) else source.crop(rect)
            tw,th=dx[col+1]-dx[col],dy[row+1]-dy[row]
            if entry.get('fixed_side_edge_ornaments') and row==1 and col in (0,2):
                uniform_h=max(1,min(th,round(tile.height*tw/tile.width)))
                core=tile.resize((tw,uniform_h),LANCZOS)
                before=(th-uniform_h)//2;after=th-uniform_h-before
                column=Image.new('RGBA',(tw,th))
                if before:
                    column.alpha_composite(tile.crop((0,0,tile.width,2)).resize((tw,before),LANCZOS),(0,0))
                column.alpha_composite(core,(0,before))
                if after:
                    column.alpha_composite(tile.crop((0,tile.height-2,tile.width,tile.height)).resize((tw,after),LANCZOS),(0,before+uniform_h))
                tile=column
            else:
                tile=tile.resize((tw,th),LANCZOS)
            result.alpha_composite(tile,(dx[col],dy[row]))
    for part in hanging:
        item = _read(part['file'])
        box = part['source_box_xyxy']
        item = item.resize((max(1,round(item.width*ornament_scale)),max(1,round(item.height*ornament_scale))),LANCZOS)
        x = (pad+box[0]*ornament_scale if part['anchor']=='bottom-left'
             else width-pad-(source.width-box[2])*ornament_scale-item.width)
        y = height-pad-item.height if entry.get('hanging_inside_canvas') else dy[-1]+(box[1]-source.height)*ornament_scale
        _composite_clipped(result,item,x,y)
    for stamp in entry.get('fixed_stamps',[]):
        item = _read(stamp['file'])
        box = stamp['source_box_xyxy']
        horizontal,vertical = stamp['anchor'].split('-')
        scale = min((dl-pad)/sl,(dr-pad)/sr)
        if vertical == 'top': scale=min(scale,(dt-pad)/st)
        elif vertical == 'bottom': scale=min(scale,(db-pad-reserve)/sb)
        else: scale=min(scale,(height-2*pad-reserve)/source.height)
        item = item.resize((max(1,round(item.width*scale)),max(1,round(item.height*scale))),LANCZOS)
        x = ((width-item.width)/2 if horizontal=='center' else pad+box[0]*scale
             if horizontal=='left' else width-pad-(source.width-box[2])*scale-item.width)
        y = (pad+box[1]*scale if vertical=='top' else dy[-1]-(source.height-box[3])*scale-item.height
             if vertical=='bottom' else (pad+dy[-1]-item.height)/2)
        _composite_clipped(result,item,x,y)
    return result


def stretch_divider(w, h, vertical=False, pad=0):
    """Preserve painted end-scrolls and center crescent; stretch straight rails."""
    width,height=(int(h),int(w)) if vertical else (int(w),int(h))
    entry=_entry('divider')
    source=_read(entry['file'])
    parts=entry['fixed_horizontal_segments']
    fixed_width=sum(parts[key][2]-parts[key][0] for key in ('left_end','center','right_end'))
    scale=min((height-2*pad)/source.height,(width-2*pad-2)/fixed_width)
    scaled={}
    for key in ('left_end','center','right_end'):
        tile=source.crop(parts[key])
        scaled[key]=tile.resize((max(1,round(tile.width*scale)),max(1,round(source.height*scale))),LANCZOS)
    dh=scaled['center'].height
    free=width-2*pad-sum(tile.width for tile in scaled.values())
    if free<2:
        return _fit(source.rotate(90,expand=True) if vertical else source,w,h,pad)
    rail_widths=(free//2,free-free//2)
    result=Image.new('RGBA',(width,height))
    x=pad;y=(height-dh)//2
    for key,dw in (('left_end',0),('left_rail',rail_widths[0]),('center',0),('right_rail',rail_widths[1]),('right_end',0)):
        item=scaled[key] if key in scaled else source.crop(parts[key]).resize((dw,dh),LANCZOS)
        result.alpha_composite(item,(x,y));x+=item.width
    return result.rotate(90,expand=True) if vertical else result
