"""Stage RGB-only removal of residual magenta from existing pet/item cutouts."""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
import repair_edges as base

def repair(im,kind):
    a=np.asarray(im.convert('RGBA')).copy();out=a.copy()
    r,g,b=a[:,:,:3].astype(np.int16).transpose(2,0,1);alpha=a[:,:,3]
    distance_band=np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)))>0
    core=np.asarray(Image.fromarray(((alpha>=224)*255).astype('uint8')).filter(ImageFilter.MinFilter(7)))>0
    if kind=='fox':
        mask=(np.minimum(r,b)-g>42)&(r>=b-8)&(alpha>0)&distance_band
        clean=((b>r+10)|(np.minimum(r,b)-g<24))&core
    else:
        pink=(b>g-15)&(b>r*.42)&(r>g+15)
        mask=pink&(alpha>0)&distance_band
        clean=(~pink)&core
    changed=[];skipped=[];h,w=alpha.shape
    for y,x in zip(*np.nonzero(mask)):
        donor=None
        for radius in (5,9,14):
            x0=max(0,x-radius);x1=min(w,x+radius+1);y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(clean[y0:y1,x0:x1]);yy+=y0;xx+=x0
            if len(xx):
                k=np.argmin((xx-x)**2+(yy-y)**2);donor=a[yy[k],xx[k],:3];break
        if donor is None:skipped.append([int(x),int(y)]);continue
        out[y,x,:3]=donor;changed.append([int(x),int(y)])
    assert np.array_equal(a[:,:,3],out[:,:,3])
    assert np.array_equal(a[~mask],out[~mask])
    assert len(changed)<w*h*.02
    return Image.fromarray(out),dict(candidate_pixels=int(mask.sum()),changed_rgb_pixels=len(changed),unresolved_pixels=skipped,alpha_changed_pixels=0,other_pixels_changed=0,changed_coordinates=changed)

if __name__=='__main__':
    records=[]
    for r in base.load(base.PACK/'review.json')['records'][32:]:
        src=base.ROOT/r['path'];before=base.sha(src)
        im=Image.open(src).convert('RGBA');out,stats=repair(im,r['kind'])
        dest=base.PACK/'support-v2'/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,optimize=True)
        assert before==base.sha(src)
        records.append(dict(path=r['path'],kind=r['kind'],source_sha256=before,output_sha256=base.sha(dest),size=list(im.size),alpha_bbox=list(im.getchannel('A').getbbox()),**stats))
    # Evidence renderer expects a staged directory. Use a separate evidence pack.
    actual=base.PACK;base.PACK=actual/'support-review';base.PACK.mkdir(exist_ok=True)
    for r in records:
        dest=base.PACK/'staged'/r['path'];dest.parent.mkdir(parents=True,exist_ok=True)
        base.shutil.copy2(actual/'support-v2'/r['path'],dest)
    pages=base.evidence(records,'support-v2')
    base.dump(actual/'support-v2.json',dict(status='needs_visual_review',records=records,evidence=pages))
    print([(Path(r['path']).name,r['changed_rgb_pixels'],len(r['unresolved_pixels'])) for r in records])
