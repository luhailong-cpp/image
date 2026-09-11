"""Postprocess five reviewed matte-contaminated regions in existing v9 art.

Staging only. Does not alter source files, canvas, alpha, or nonselected pixels.
Donor chroma comes from the same local foreground; luminance detail is retained.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED = {
    4: 'bc1069d476055dd851b16acddc915897f1aee2300e6be1cc5f4982dee1f123f3',
    14: '05a243a00f7cef9f9548b31454c87746b3cb69d8f10ea1491bfc135ff5675972',
}
REGIONS = {
    4: [[1233, 2488, 1373, 2628]],
    14: [[2290, 303, 2382, 394], [2760, 763, 2850, 983],
         [2970, 1189, 3060, 1279], [1020, 1207, 1110, 1297]],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def evidence(source, output, number, regions):
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    pages = []
    for i, region in enumerate(regions):
        x0,y0,x1,y1 = region
        # Include a 24 px surrounding boundary for inspecting unmodified lines.
        box = [x0-24,y0-24,x1+24,y1+24]
        crops = [im.crop(box).resize(((x1-x0+48)*2,(y1-y0+48)*2), Image.Resampling.NEAREST) for im in (source, output)]
        w,h = crops[0].size
        page = Image.new('RGB', (w*2+30,h*2+110), '#e8e3d8')
        d = ImageDraw.Draw(page)
        d.text((10,5),f'{number:02d} region {i+1} | 2x | {region}',font=font,fill='#153a30')
        for row,bg in enumerate(('#f9f1de','#182a25')):
            for col,crop in enumerate(crops):
                tile = Image.new('RGBA',crop.size,bg); tile.alpha_composite(crop)
                px,py=10+col*(w+10),45+row*(h+40)
                page.paste(tile.convert('RGB'),(px,py))
                d.text((px,py-23),'BEFORE' if col==0 else 'AFTER',font=font,fill='#153a30')
        name=f'review-{number:02d}-region-{i+1}.png'
        page.save(HERE/name)
        pages.append(name)
    return pages

def main():
    records=[]
    for number,regions in REGIONS.items():
        source=next((ROOT/'q_daoist_character_pack_4096').glob(f'{number:02d}_*.png'))
        before_sha=sha(source)
        assert before_sha==EXPECTED[number], 'Source changed; must re-review current art'
        image=Image.open(source).convert('RGBA')
        a=np.asarray(image).copy();out=a.copy()
        rgb=a[:,:,:3].astype(np.float32);alpha=a[:,:,3]
        r,g,b=rgb.transpose(2,0,1);dom=np.minimum(r,b)-g
        in_regions=np.zeros(alpha.shape,dtype=bool)
        for x0,y0,x1,y1 in regions:in_regions[y0:y1,x0:x1]=True
        # Region-only desaturation: intentional purple clothing remains outside.
        if number == 4:
            selected=in_regions&(r>g+6)&(b>g+3)&(alpha>0)
            clean=(b<=g)&(r>=g)&(alpha>=230)
        else:
            selected=in_regions&(dom>12)&(alpha>0)
            clean=(dom<7)&(alpha>=230)
        weights=np.array([0.2126,0.7152,0.0722],dtype=np.float32)
        changed=[];donor_coordinates=[];unresolved=[]
        for y,x in zip(*np.nonzero(selected)):
            donor=None
            for radius in (5,10,20,36,60):
                x0,x1=max(0,x-radius),min(alpha.shape[1],x+radius+1)
                y0,y1=max(0,y-radius),min(alpha.shape[0],y+radius+1)
                yy,xx=np.nonzero(clean[y0:y1,x0:x1]);yy+=y0;xx+=x0
                if len(xx):
                    # Favor close colors of comparable luminance to retain outline depth.
                    distance=(xx-x)**2+(yy-y)**2
                    k=int(np.argmin(distance))
                    donor=rgb[yy[k],xx[k]];donor_xy=[int(xx[k]),int(yy[k])]
                    break
            if donor is None:unresolved.append([int(x),int(y)]);continue
            # Chroma transfer preserves source luminance, including dark fine lines.
            value=donor + float(rgb[y,x]@weights-donor@weights)
            out[y,x,:3]=np.clip(np.rint(value),0,255).astype(np.uint8)
            if not np.array_equal(out[y,x,:3],a[y,x,:3]):
                changed.append([int(x),int(y)]);donor_coordinates.append(donor_xy)
        assert not unresolved
        assert np.array_equal(a[:,:,3],out[:,:,3])
        assert np.array_equal(a[~selected],out[~selected])
        assert len(changed)<a.shape[0]*a.shape[1]*0.002
        relative=source.relative_to(ROOT).as_posix()
        dest=HERE/'staged'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        result=Image.fromarray(out);result.save(dest,optimize=True)
        assert sha(source)==before_sha
        pages=evidence(image,result,number,regions)
        records.append({'path':relative,'staged_path':dest.relative_to(ROOT).as_posix(),
            'source_sha256':before_sha,'output_sha256':sha(dest),'size':list(image.size),
            'alpha_bbox':list(image.getchannel('A').getbbox()),'regions':regions,
            'candidate_pixels':int(selected.sum()),'changed_rgb_pixels':len(changed),
            'changed_coordinates':changed,'donor_coordinates':donor_coordinates,
            'alpha_changed_pixels':0,'unselected_pixels_changed':0,
            'outside_regions_changed':0,'unresolved_pixels':unresolved,'evidence':pages})
    report={'status':'staged_needs_visual_review','created_utc':datetime.now(timezone.utc).isoformat(),
        'method':'Same-image nearest clean foreground chroma transfer with original luminance retained; five manually reviewed regions only',
        'source_origin':'Existing generated v9 character portraits; deterministic edge decontamination only',
        'processor':'qdao_cutout_edge_repair_20260911/v9/stage_local_edges.py',
        'processor_sha256':sha(Path(__file__)),'records':records}
    dump(HERE/'review.json',report)
    print(json.dumps({'files':len(records),'changed_rgb_pixels':[r['changed_rgb_pixels'] for r in records],'evidence':[r['evidence'] for r in records]}))

if __name__=='__main__':main()
