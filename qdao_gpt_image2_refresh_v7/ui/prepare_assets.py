"""Derive fixed-contract UI exports from two NEW built-in image_gen artworks.

No image API calls. Local work is alpha cleanup, cropping, nine-slice layout,
resampling and functional status placement. AI painting remains in source/*.png.
"""
from pathlib import Path
import json, hashlib, argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from PIL import ImageFilter
from collections import deque

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / 'derived'
LANCZOS = Image.Resampling.LANCZOS

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(im, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p, compress_level=9)
def fit(im, w, h, pad=3):
    out = Image.new('RGBA', (w,h))
    scale = min((w-pad*2)/im.width, (h-pad*2)/im.height)
    obj = im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))), LANCZOS)
    out.alpha_composite(obj, ((w-obj.width)//2,(h-obj.height)//2))
    return out

crop_records=[]
def split(filename, names, n):
    src=Image.open(ROOT/'source'/filename).convert('RGBA')
    result={}
    for i,name in enumerate(names):
        x,y=i%n,i//n
        rect=(round(src.width*x/n),round(src.height*y/n),round(src.width*(x+1)/n),round(src.height*(y+1)/n))
        im=src.crop(rect); a=np.array(im)
        # Preserve real generated alpha. Remove only isolated outside remnants.
        if a[:,:,3].min()==255:
            magenta=(a[:,:,0]>150)&(a[:,:,2]>130)&(a[:,:,1]<100)
            a[magenta,3]=0
        pending=a[:,:,3]>20; best=[]; hh,ww=pending.shape
        for yy,xx in zip(*np.nonzero(pending)):
            if not pending[yy,xx]:continue
            queue=[(int(yy),int(xx))]; pending[yy,xx]=False; points=[]
            while queue:
                py,px=queue.pop();points.append((py,px))
                for ny,nx in ((py-1,px),(py+1,px),(py,px-1),(py,px+1)):
                    if 0<=ny<hh and 0<=nx<ww and pending[ny,nx]:
                        pending[ny,nx]=False;queue.append((ny,nx))
            if len(points)>len(best):best=points
        if not best:raise ValueError(f'Empty generated cell {name}')
        keep=np.zeros((hh,ww),dtype=np.uint8)
        by,bx=zip(*best);keep[by,bx]=255
        near=np.array(Image.fromarray(keep).filter(ImageFilter.MaxFilter(5)))>0
        a[~near,3]=0
        # Vivid pink antialias remnants cannot belong to these jade/gold assets.
        fringe=(a[:,:,0]>180)&(a[:,:,2]>140)&(a[:,:,1]<80)
        a[fringe,3]=0
        # Generated opaque paint sometimes carries alpha 250-254. Normalize its solid core.
        a[a[:,:,3]>=250,3]=255
        im=Image.fromarray(a); bbox=im.getbbox()
        if not bbox: raise ValueError(name)
        im=im.crop(bbox); save(im,OUT/'crops'/f'{name}.png'); result[name]=im
        crop_records.append({'id':name,'source':'source/'+filename,'native_size':list(src.size),'cell_xyxy':list(rect),'tight_crop_in_cell':list(bbox),'crop_size':list(im.size),'alpha_cleanup':'largest connected component with 2px antialias support; magenta fringe removed; near-opaque core alpha >=250 normalized to255'})
    return result

def patch(im,w,h,dest_borders,pad=3):
    """Resample nine rectangles; ornament stays inside target fixed borders."""
    dl,dt,dr,db=dest_borders
    is_panel=im.height/im.width>.40
    sl=round(im.width*(.235 if is_panel else .235))
    sr=sl
    st=round(im.height*(.30 if is_panel else .36)); sb=st
    xs=[0,sl,im.width-sr,im.width]; ys=[0,st,im.height-sb,im.height]
    dx=[pad,dl,w-dr,w-pad]; dy=[pad,dt,h-db,h-pad]
    if min(np.diff(dx))<=0 or min(np.diff(dy))<=0: raise ValueError((w,h,dest_borders))
    out=Image.new('RGBA',(w,h))
    for row in range(3):
        for col in range(3):
            tile=im.crop((xs[col],ys[row],xs[col+1],ys[row+1])).resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),LANCZOS)
            out.alpha_composite(tile,(dx[col],dy[row]))
    return out

def compose_glyph(out,im,x,y,size):
    out.alpha_composite(fit(im,size,size,0),(round(x),round(y)))

def magnifier(out,x,y,size,color):
    # Fixed semantic search glyph; this geometry is not claimed as AI artwork.
    overlay=Image.new('RGBA',(out.width*3,out.height*3)); d=ImageDraw.Draw(overlay)
    x*=3; y*=3; r=size*.29*3; sw=max(2,round(size*.1*3))
    d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=sw)
    d.line((x+r*.65,y+r*.65,x+r*1.7,y+r*1.7),fill=color,width=sw)
    out.alpha_composite(overlay.resize(out.size,LANCZOS))

def main():
    skins=split('ui-skins-native.png',['jade','ivory','muted','frame','panel','recommend','flower','corner','divider'],3)
    symbols=['taiji','pagoda','furnace','mountain','lotus','sword','water','compass','peach_spirit','flame','check','lock','status_red','status_green','status_orange','status_gray']
    icons=split('ui-emblems-native.png',symbols,4)
    cm=json.loads((REPO/'qdao_ui_redesign_v5/components/manifest.json').read_text('utf-8'))
    source_map={}
    for a in cm['assets']:
        ident=a['id']; w,h=a['width'],a['height']; category=a['category']; state=a.get('state','normal')
        if a.get('nine_slice'):
            key='frame' if category=='main_frame' else 'panel' if category=='content_panel' else 'muted' if state=='disabled' else 'jade' if state=='selected' or category=='primary_button' else 'ivory'
            n=a['nine_slice']; borders=[n[k] for k in ['left','top','right','bottom']]
            if category=='summary_bar': borders[0]=29
            im=patch(skins[key],w,h,borders)
            if state in ['selected','disabled']:
                g='check' if state=='selected' else 'lock'; gx=w-49 if category=='search' else 30
                compose_glyph(im,icons[g],gx,(h-40)/2-2,32)
                if state=='selected':
                    d=ImageDraw.Draw(im); d.line((20,h/2-13,20,h/2+13),fill='#F5DE92',width=4)
                    d.polygon([(38,h-12),(62,h-12),(50,h-18)],fill='#EDD48B')
            if category=='search': magnifier(im,39,h/2-5,32,'#FFF7DE' if state=='selected' else '#795638')
            used=[key]+([g] if state in ['selected','disabled'] else [])
        elif category=='round_badge':
            key=a['symbol']; im=fit(icons[key],w,h,5); used=[key]
        elif category=='status_dot':
            key='status_'+state; im=fit(icons[key],w,h,2); used=[key]
        else:
            key={'gold_flower':'flower','cloud_corner':'corner','recommend_badge':'recommend'}.get(category,category)
            im=fit(icons.get(key,skins.get(key)),w,h,2); used=[key]
        save(im,OUT/'components'/f'{ident}.png'); source_map[ident]=used
    lm=json.loads((REPO/'exact_qdao_slices/manifest_native_q5.json').read_text('utf-8'))
    for a in lm['assets']:
        name=Path(a['png']).name; w,h=a['width'],a['height']; role=a['role']
        if role in ['tab','list_row','search','summary_bar','server_card_base','control_base']:
            logical=a.get('legacy_import',{}).get('target_size',[w,h]); tw,th=logical
            grid=a.get('legacy_import',{}).get('scale9grid_center_xywh') or a['nine_slice']['center_xywh']
            l,t,cw,ch=grid; key='jade' if a.get('state')=='selected' else 'ivory'
            im=patch(skins[key],tw,th,[l,t,tw-l-cw,th-t-ch])
            if role=='search':magnifier(im,min(32,l/2),th/2-4,26,'#795638')
            if im.size!=(w,h): im=im.resize((w,h),LANCZOS)
            used=[key]
        elif role in ['round_badge','legacy_alias']:
            key=a['symbol']; im=fit(icons[key],w,h,5 if w==420 else 2); used=[key]
        elif role=='status_dot': im=fit(icons['status_red'],w,h,3); used=['status_red']
        elif role=='ornament': im=fit(skins['flower'],w,h,5); used=['flower']
        elif role=='decorative_divider': im=fit(skins['divider'],w,h,2); used=['divider']
        elif role=='badge_sheet':
            im=Image.new('RGBA',(w,h))
            cells=json.loads((REPO/Path(a['png']).parent/'manifest_ai_qstyle_badges.json').read_text('utf8'))['outputs']
            for i,cell in enumerate(cells):
                x,y,cw,ch=cell['source_cell']; im.alpha_composite(fit(icons[symbols[i]],328,328,4),(round(x+(cw-328)/2),round(y+(ch-328)/2)))
            used=symbols[:10]
        else: raise ValueError(a)
        save(im,OUT/'legacy'/name); source_map[a['png']]=used
    save(fit(icons['status_red'],32,32,2),OUT/'status_red.png')
    save(fit(skins['divider'],142,35,2),OUT/'divider.png')
    (ROOT/'source-map.json').write_text(json.dumps({'tool':'built-in image_gen','requested_model':'gpt-image-2','model_parameter_exposed':False,'quality_parameter_exposed':False,'native_sources':[{'file':'source/'+n,'size':list(Image.open(ROOT/'source'/n).size),'sha256':sha(ROOT/'source'/n)} for n in ['ui-skins-native.png','ui-emblems-native.png']],'crop_records':crop_records,'derivatives':source_map,'postprocess':'preserve generated alpha, cleanup isolated fringe, crop, fixed-border nine-slice resampling, compose AI check/lock glyphs, render functional search glyph separately'},ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'component_assets':len(cm['assets']),'legacy_assets':len(lm['assets']),'native_sources':2,'crops':len(crop_records)}))

if __name__=='__main__':main()
