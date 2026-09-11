"""Conservative RGB-only matte repair for the existing brown-haired hero.

Trial output only by default; production originals are never written. Retains
the original alpha exactly. The brown-hair refinement uses nearby interior
colors of this image and rejects red spill as a color donor.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, hashlib, argparse
import numpy as np
from repair_edges import repair

PACK = Path(__file__).resolve().parent
ROOT = PACK.parent

def hash_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# These small hair-only regions were visually inspected at 3x. They cover
# narrow spikes with no clean donor inside 14px, and one brighter hair tuft.
MANUAL_HAIR_ROIS = {
 'southwest_frame_01.png': [(350,90,480,220)],
 'northeast_frame_01.png': [(797,98,889,180)],
 'northeast_frame_02.png': [(718,64,744,93),(800,97,870,147),(899,225,927,252)],
 'northeast_frame_03.png': [(810,132,835,164),(870,240,896,269)],
 'northeast_frame_04.png': [(718,73,744,98),(870,151,895,181)],
 'southeast_frame_01.png': [(834,142,862,173)],
 'south_frame_03.png': [(330,378,347,401)],
 'northwest_frame_01.png': [(518,114,538,134)],
 'northwest_frame_03.png': [(761,123,786,143)],
}

def refine(original, frame_name=None):
    a = np.asarray(original.convert('RGBA')).copy()
    base, base_stats = repair(original, 'hero')
    out = np.asarray(base).copy()
    rgb = a[:,:,:3].astype(np.int16)
    r,g,b = rgb.transpose(2,0,1)
    alpha = a[:,:,3]
    ys = np.flatnonzero((alpha>0).any(axis=1))
    cutoff = int(ys[0]+round((ys[-1]-ys[0])*.42))
    near = np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(17)))>0
    inner = np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))==0
    # Magenta spill raises blue above the green-dominant brown hair. Existing
    # red tassels (well below cutoff), warm skin, and gold retain their colors.
    mask = (alpha>0)&near&((b>=g-8)|((r-g)>1.9*(g-b)))&(r>g+12)
    mask[cutoff:]=False
    # Allow gold and skin as competing donors so a nearby ribbon/ear never
    # borrows a more distant hair color merely because hair exists nearby.
    any_clean = (alpha>=240)&inner&(b<g-7)&(r-g<140)&(g>10)&((r>=g)|(g>=70))&(((g-b)>.7*(r-g))|((r>=170)&((g-b)>.3*(r-g))))
    hair_clean = any_clean&(r<170)&(g<120)&(r-g<72)&(r>=g)&((g-b)>.7*(r-g))
    manual_rois=MANUAL_HAIR_ROIS.get(frame_name,[])
    local_hair=(alpha>=224)&inner&(r>=g)&(g>8)&(r<230)&(g<185)&((g-b)>.6*(r-g))
    manual_changed=0
    changed=[]; unresolved=[]; nonhair=[]
    h,w=alpha.shape
    for y,x in zip(*np.nonzero(mask)):
        best=None
        manual=any(x0<=x<x1 and y0<=y<y1 for x0,y0,x1,y1 in manual_rois)
        donor_pool=local_hair if manual else any_clean
        for radius in ((4,8,14,28) if manual else (4,8,14)):
            x0=max(0,x-radius);x1=min(w,x+radius+1)
            y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(donor_pool[y0:y1,x0:x1]); yy+=y0;xx+=x0
            if len(xx):
                dist=(xx-x)**2+(yy-y)**2
                k=int(np.argmin(dist))
                best=(int(yy[k]),int(xx[k]));break
        if best is None:
            unresolved.append([int(x),int(y)]);continue
        by,bx=best
        if not manual and not hair_clean[by,bx]:
            nonhair.append([int(x),int(y)]);continue
        out[y,x,:3]=a[by,bx,:3]
        manual_changed+=int(manual)
        changed.append([int(x),int(y)])
    assert np.array_equal(a[:,:,3],out[:,:,3])
    assert np.array_equal(a[cutoff:],out[cutoff:])
    actual=np.any(a[:,:,:3]!=out[:,:,:3],axis=2)
    return Image.fromarray(out),dict(head_cutoff_y=cutoff,manual_hair_refinement_pixels=manual_changed,original_to_output_rgb_pixels=int(actual.sum()),hair_refinement_pixels=len(changed),unresolved=len(unresolved),unresolved_coordinates=unresolved,unresolved_alpha_max=max([int(alpha[y,x]) for x,y in unresolved] or [0]),competing_nonhair=len(nonhair),alpha_changed_pixels=0,body_changed_pixels=0,base_pixels=base_stats['changed_rgb_pixels'])

def main(all_frames=False):
    records=[]; inputs=sorted((ROOT/'character_move_8dir').glob('*_frame_*.png')) if all_frames else [ROOT/'character_move_8dir'/f'{d}_frame_01.png' for d in ['east','south']]
    tag='review-v2' if all_frames else 'trial-v2'
    for path in inputs:
        before=hash_file(path);src=Image.open(path).convert('RGBA');out,stats=refine(src,path.name)
        dest=PACK/'staged-v2'/'character_move_8dir'/path.name;dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,optimize=True)
        assert hash_file(path)==before
        records.append(dict(path=path.relative_to(ROOT).as_posix(),output=dest.relative_to(ROOT).as_posix(),source_sha256=before,output_sha256=hash_file(dest),size=list(src.size),alpha_bbox=list(src.getchannel('A').getbbox()),**stats))
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    evidence=[]
    for start in range(0,len(records),4):
        page=Image.new('RGB',(1536,480*min(4,len(records)-start)),'#eee7da');draw=ImageDraw.Draw(page)
        for row,record in enumerate(records[start:start+4]):
            a=Image.open(ROOT/record['path']).convert('RGBA'); b=Image.open(ROOT/record['output']).convert('RGBA')
            roi=(455,97,535,177) if 'east_frame_01' in record['path'] else ((696,126,776,206) if 'south_frame_01' in record['path'] else None)
            if roi is None:
                arr=np.asarray(a); dif=np.any(arr[:,:,:3]!=np.asarray(b)[:,:,:3],axis=2); yy,xx=np.nonzero(dif); x=int(np.median(xx));y=int(np.percentile(yy,25));roi=(max(0,x-40),max(0,y-40),x+40,y+40)
            for col,im in enumerate((a,b)):
                for bgidx,bg in enumerate(('#f1eedf','#172a25')):
                    x=col*768+bgidx*384;y=row*480
                    draw.text((x+8,y+5),Path(record['path']).name+(' OLD' if col==0 else ' V2'),fill='#17372f',font=font)
                    full=im.copy();full.thumbnail((330,330));tile=Image.new('RGBA',(384,430),bg);tile.alpha_composite(full,(27,0));crop=im.crop(roi).resize((100,100),Image.Resampling.NEAREST);tile.alpha_composite(crop,(140,326));page.paste(tile.convert('RGB'),(x,y+35))
        output=PACK/f'{tag}-{start//4+1:02}.jpg';page.save(output,quality=98);evidence.append(output.name)
    result=dict(status='trial_needs_visual_review',records=records,evidence=evidence)
    (PACK/f'{tag}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(records),rgb_pixels=sum(r['original_to_output_rgb_pixels'] for r in records),refined_pixels=sum(r['hair_refinement_pixels'] for r in records),unresolved=sum(r['unresolved'] for r in records),evidence=evidence)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');args=p.parse_args();main(args.all)
