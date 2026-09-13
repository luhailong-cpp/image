"""Bounded color-only magenta despill prototype. Never change alpha or geometry."""
from pathlib import Path
import json, hashlib, math
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent

def shifted(a, dy, dx, fill=0):
    out=np.full_like(a,fill)
    h,w=a.shape[:2]
    ty=slice(max(0,-dy),min(h,h-dy));tx=slice(max(0,-dx),min(w,w-dx))
    sy=slice(max(0,dy),min(h,h+dy));sx=slice(max(0,dx),min(w,w+dx))
    out[ty,tx]=a[sy,sx]
    return out

def despill(image):
    a=np.array(image.convert('RGBA'));rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3]
    fg=alpha>8
    distance_sq=np.full(alpha.shape,999,dtype=np.int16)
    offsets=sorted((dx*dx+dy*dy,dy,dx) for dy in range(-2,3) for dx in range(-2,3) if dx*dx+dy*dy<=4)
    for dd,dy,dx in offsets:
        near=shifted(~fg,dy,dx,True)
        distance_sq[near]=np.minimum(distance_sq[near],dd)
    band=fg & (distance_sq<=4)
    rr,gg,bb=(rgb[:,:,i] for i in range(3))
    magenta=(rr-gg>=12)&(bb-gg>=12)&(bb*5>=rr*4)
    red_protected=(rr-gg>=30)&(rr*10>bb*13)
    candidate=band&magenta&~red_protected
    clean=(alpha>=224)&((rr-gg<=4)|(bb-gg<=4))
    pending=candidate.copy();reference=np.zeros_like(rgb);ref_distance=np.zeros(alpha.shape,dtype=np.int16)
    offsets=sorted((dx*dx+dy*dy,dy,dx) for dy in range(-6,7) for dx in range(-6,7) if 0<dx*dx+dy*dy<=36)
    for dd,dy,dx in offsets:
        use=pending&shifted(clean,dy,dx,False)
        if np.any(use):
            reference[use]=shifted(rgb,dy,dx,0)[use]
            ref_distance[use]=dd
            pending[use]=False
        if not np.any(pending):break
    eligible=candidate&~pending
    out=a.copy()
    for channel in (0,2):
        target=np.clip(gg+reference[:,:,channel]-reference[:,:,1],0,255)
        out[:,:,channel][eligible]=np.minimum(rgb[:,:,channel],target)[eligible].astype(np.uint8)
    changed=np.any(out[:,:,:3]!=a[:,:,:3],axis=2)
    assert np.array_equal(out[:,:,3],alpha)
    assert np.array_equal(out[:,:,1],a[:,:,1])
    assert not np.any(changed&~band)
    assert not np.any(changed&red_protected)
    assert np.array_equal(out[~changed],a[~changed])
    y,x=np.where(changed)
    remaining=(out[:,:,0].astype(int)-out[:,:,1]>=12)&(out[:,:,2].astype(int)-out[:,:,1]>=12)&(out[:,:,2].astype(int)*5>=out[:,:,0].astype(int)*4)&fg
    stats={'visible_pixels':int(fg.sum()),'boundary_band_pixels':int(band.sum()),'candidate_pixels':int(candidate.sum()),'changed_pixels':int(changed.sum()),'changed_visible_fraction':float(changed.sum()/fg.sum()),'maximum_distance_to_alpha_le_8_px':float(math.sqrt(distance_sq[changed].max())) if len(y) else 0,'maximum_clean_reference_distance_px':float(math.sqrt(ref_distance[changed].max())) if len(y) else 0,'no_clean_reference_candidates_unchanged':int(pending.sum()),'changed_bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(y) else None,'alpha_sha256_before':hashlib.sha256(alpha.tobytes()).hexdigest(),'alpha_sha256_after':hashlib.sha256(out[:,:,3].tobytes()).hexdigest(),'alpha_equal':True,'green_equal':True,'geometry_equal':True,'outside_band_changes':0,'protected_red_changes':0,'protected_red_pixels':int(red_protected.sum()),'remaining_magenta_inside_band':int((remaining&band).sum()),'remaining_magenta_outside_band_untouched':int((remaining&~band).sum()),'maximum_channel_reduction':int((rgb-out[:,:,:3].astype(int))[changed].max()) if len(y) else 0}
    return Image.fromarray(out),stats

def main():
    dest=ROOT/'despill-prototype';(dest/'fixed'/'idle').mkdir(parents=True,exist_ok=True)
    report={'operation':'local prototype; no production files changed','policy':{'boundary_radius_px':2,'boundary_metric':'Euclidean; nearest alpha <=8','alpha_unchanged':True,'green_channel_unchanged':True,'geometry_unchanged':True,'minimum_red_minus_green':12,'minimum_blue_minus_green':12,'minimum_blue_red_ratio':0.8,'clean_reference_radius_px':6,'no_reference_action':'leave unchanged','method':'Reduce R/B only to preserve nearest clean opaque pixel chroma relative to unchanged G','red_guard':'R-G>=30 and R/B>1.3 always unchanged'},'files':{}}
    all_pairs=[]
    for d in ['N','S','NW']:
        path=ROOT/'idle'/f'{d}.png';before=Image.open(path).convert('RGBA');after,stats=despill(before)
        after_path=dest/'fixed'/'idle'/f'{d}.png';after.save(after_path)
        stats.update(source_path=str(path),source_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),prototype_path=str(after_path),prototype_file_sha256=hashlib.sha256(after_path.read_bytes()).hexdigest());report['files'][d]=stats;all_pairs.append((d,before,after))
    for detail in ['full','head']:
        crop=(100,38,390,270) if detail=='head' else (0,0,512,512)
        width,height=crop[2]-crop[0],crop[3]-crop[1];header=28
        canvas=Image.new('RGB',(width*4,(height+header)*3),(232,233,231));draw=ImageDraw.Draw(canvas)
        for row,(d,before,after) in enumerate(all_pairs):
            for col,(im,bg,label) in enumerate([(before,(26,34,31),'before dark'),(after,(26,34,31),'after dark'),(before,(245,246,241),'before light'),(after,(245,246,241),'after light')]):
                tile=Image.new('RGBA',im.size,(*bg,255));tile.alpha_composite(im);tile=tile.convert('RGB').crop(crop)
                x=col*width;y=row*(height+header);canvas.paste(tile,(x,y+header));draw.text((x+5,y+4),f'{d} {label}',fill=(18,32,22),font_size=17)
        canvas.save(dest/f'comparison-{detail}.png')
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    unchanged=all(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'] for item in manifest['files'])
    assert unchanged
    report['all_89_production_media_match_manifest']=unchanged
    (dest/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
