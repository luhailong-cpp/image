"""Bounded color-only magenta despill prototype. Never change alpha or geometry."""
from pathlib import Path
import json, hashlib, math
import numpy as np
from PIL import Image, ImageDraw

def shifted(a, dy, dx, fill=0):
    out=np.full_like(a,fill)
    h,w=a.shape[:2]
    ty=slice(max(0,-dy),min(h,h-dy));tx=slice(max(0,-dx),min(w,w-dx))
    sy=slice(max(0,dy),min(h,h+dy));sx=slice(max(0,dx),min(w,w+dx))
    out[ty,tx]=a[sy,sx]
    return out

def despill(image, radius=2, reference_radius=6):
    """Reduce edge color contamination without changing alpha, green, or geometry."""
    if not isinstance(radius, int) or radius < 1:
        raise ValueError("despill radius must be a positive integer")
    if not isinstance(reference_radius, int) or reference_radius < radius:
        raise ValueError("clean reference radius must be an integer >= edge radius")
    a=np.array(image.convert('RGBA'));rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3]
    fg=alpha>8
    distance_sq=np.full(alpha.shape,999,dtype=np.int16)
    offsets=sorted((dx*dx+dy*dy,dy,dx) for dy in range(-radius,radius+1) for dx in range(-radius,radius+1) if dx*dx+dy*dy<=radius*radius)
    for dd,dy,dx in offsets:
        near=shifted(~fg,dy,dx,True)
        distance_sq[near]=np.minimum(distance_sq[near],dd)
    band=fg & (distance_sq<=radius*radius)
    rr,gg,bb=(rgb[:,:,i] for i in range(3))
    magenta=(rr-gg>=12)&(bb-gg>=12)&(bb*5>=rr*4)
    red_protected=(rr-gg>=30)&(rr*10>bb*13)
    candidate=band&magenta&~red_protected
    clean=(alpha>=224)&((rr-gg<=4)|(bb-gg<=4))
    pending=candidate.copy();reference=np.zeros_like(rgb);ref_distance=np.zeros(alpha.shape,dtype=np.int16)
    offsets=sorted((dx*dx+dy*dy,dy,dx) for dy in range(-reference_radius,reference_radius+1) for dx in range(-reference_radius,reference_radius+1) if 0<dx*dx+dy*dy<=reference_radius*reference_radius)
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
    stats={'radius_px':radius,'reference_radius_px':reference_radius,'visible_pixels':int(fg.sum()),'boundary_band_pixels':int(band.sum()),'candidate_pixels':int(candidate.sum()),'changed_pixels':int(changed.sum()),'changed_visible_fraction':float(changed.sum()/fg.sum()),'maximum_distance_to_alpha_le_8_px':float(math.sqrt(distance_sq[changed].max())) if len(y) else 0,'maximum_clean_reference_distance_px':float(math.sqrt(ref_distance[changed].max())) if len(y) else 0,'no_clean_reference_candidates_unchanged':int(pending.sum()),'changed_bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(y) else None,'alpha_sha256_before':hashlib.sha256(alpha.tobytes()).hexdigest(),'alpha_sha256_after':hashlib.sha256(out[:,:,3].tobytes()).hexdigest(),'alpha_equal':True,'green_equal':True,'geometry_equal':True,'outside_band_changes':0,'protected_red_changes':0,'protected_red_pixels':int(red_protected.sum()),'remaining_magenta_inside_band':int((remaining&band).sum()),'remaining_magenta_outside_band_untouched':int((remaining&~band).sum()),'maximum_channel_reduction':int((rgb-out[:,:,:3].astype(int))[changed].max()) if len(y) else 0}
    return Image.fromarray(out),stats
