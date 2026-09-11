"""RGB-only matte decontamination of current, existing ink-kite artwork.

No drawing, resizing or alpha editing. Sources remain untouched. Review staged
images before publishing; all donors come from this same current input image.
"""
from pathlib import Path
import argparse, hashlib, json
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACK = Path(__file__).resolve().parent
ROOT = PACK.parents[1]
SOURCE = ROOT/'qdao_chibi_roster_v11/27_ink_kite_ranger'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def clean(im, extra_mask=None):
    a=np.asarray(im.convert('RGBA')).copy(); out=a.copy()
    r,g,b=a[:,:,:3].astype('int16').transpose(2,0,1); alpha=a[:,:,3]
    dom=np.minimum(r,b)-g
    near=np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(17)))>0
    inner=np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))==0
    # The established palette is charcoal/black, jade, ivory, skin and red.
    # Magenta raising BOTH R and B over G is a key contamination signature.
    # In particular this does not select red tassels or cyan bands.
    mask=(alpha>0)&(near if extra_mask is None else (near|extra_mask))&(dom>10)
    donor=(alpha>=240)&inner&(dom<5)
    h,w=alpha.shape; unresolved=[]; distances=[]
    for y,x in zip(*np.nonzero(mask)):
        best=None
        for radius in [8,16,32]:
            x0=max(0,x-radius);x1=min(w,x+radius+1);y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(donor[y0:y1,x0:x1]); yy+=y0;xx+=x0
            if len(xx):
                dd=(xx-x)**2+(yy-y)**2
                # Compare whether the candidate donor can explain the observed
                # fringe as foreground mixed with the original magenta matte.
                # This avoids borrowing a nearby white sleeve for a jade string.
                colors=a[yy,xx,:3].astype('float32'); observed=a[y,x,:3].astype('float32')
                key=np.array([255.,0.,255.],dtype='float32'); v=key-colors
                fraction=np.clip(np.sum((observed-colors)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1),0,0.99)
                predicted=colors+v*fraction[:,None]
                error=np.sum((predicted-observed)**2,axis=1)
                score=error+dd*3.0
                k=int(np.argmin(score));best=(int(yy[k]),int(xx[k]));distances.append(float(np.sqrt(dd[k])));break
        if best is None:
            unresolved.append([int(x),int(y),int(alpha[y,x])]);continue
        out[y,x,:3]=a[best[0],best[1],:3]
    changed=np.any(a[:,:,:3]!=out[:,:,:3],axis=2)
    assert np.array_equal(a[:,:,3],out[:,:,3])
    assert np.array_equal(a[~mask],out[~mask])
    assert np.array_equal(a[alpha==0],out[alpha==0])
    remaining=(np.minimum(out[:,:,0].astype('int16'),out[:,:,2].astype('int16'))-out[:,:,1].astype('int16')>10)&(alpha>8)
    return Image.fromarray(out), dict(selected_pixels=int(mask.sum()),changed_rgb_pixels=int(changed.sum()),alpha_changed_pixels=0,unselected_pixels_changed=0,transparent_pixels_changed=0,unresolved=len(unresolved),unresolved_coordinates=unresolved,unresolved_alpha_max=max([p[2] for p in unresolved] or [0]),remaining_purple_pixels_alpha_gt_8=int(remaining.sum()),max_donor_distance=max(distances or [0]),mean_donor_distance=float(np.mean(distances)) if distances else 0)

def matte(im,bg,size):
    im=im.copy();im.thumbnail(size,Image.Resampling.LANCZOS);tile=Image.new('RGBA',size,bg);tile.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return tile.convert('RGB')

def evidence(records,tag):
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);paths=[]
    for start in range(0,len(records),4):
        group=records[start:start+4];page=Image.new('RGB',(1440,480*len(group)),'#e9e3d6');draw=ImageDraw.Draw(page)
        for row,rec in enumerate(group):
            old=Image.open(ROOT/rec['path']).convert('RGBA');new=Image.open(ROOT/rec['output']).convert('RGBA')
            for col,im in enumerate([old,new]):
                for bgidx,bg in enumerate(['#f1eddf','#152d26']):
                    x=col*720+bgidx*360;y=row*480
                    draw.text((x+8,y+6),rec['name']+(' BEFORE' if col==0 else ' AFTER'),fill='#16382f',font=font)
                    page.paste(matte(im,bg,(360,446)),(x,y+30))
        p=PACK/f'{tag}-full-{start//4+1:02}.jpg';page.save(p,quality=98);paths.append(p.relative_to(ROOT).as_posix())
    # Two detailed native pixel regions per frame; four panels give before/after
    # against both light and dark backgrounds at 2x without synthesized pixels.
    for start in range(0,len(records),4):
        group=records[start:start+4];page=Image.new('RGB',(1440,460*len(group)),'#e9e3d6');draw=ImageDraw.Draw(page)
        for row,rec in enumerate(group):
            old=Image.open(ROOT/rec['path']).convert('RGBA');new=Image.open(ROOT/rec['output']).convert('RGBA');a=np.asarray(old);delta=np.any(a[:,:,:3]!=np.asarray(new)[:,:,:3],axis=2)
            yy,xx=np.nonzero(delta&(a[:,:,3]>64)); rois=[]
            for q in [20,60]:
                cy=int(np.percentile(yy,q)); band=abs(yy-cy)<25;cx=int(np.median(xx[band]));rois.append((max(0,cx-80),max(0,cy-45),max(0,cx-80)+160,max(0,cy-45)+90))
            rec['detail_rois']=rois
            for ri,roi in enumerate(rois):
                for col,im in enumerate([old,new]):
                    for bgidx,bg in enumerate(['#f1eddf','#152d26']):
                        x=col*720+bgidx*360;y=row*460+ri*230
                        draw.text((x+6,y+3),rec['name']+(' BEFORE' if col==0 else ' AFTER')+f' ROI {ri+1}',fill='#16382f',font=font)
                        crop=im.crop(roi).resize((320,180),Image.Resampling.NEAREST);tile=Image.new('RGBA',(360,205),bg);tile.alpha_composite(crop,(20,10));page.paste(tile.convert('RGB'),(x,y+25))
        p=PACK/f'{tag}-detail-{start//4+1:02}.jpg';page.save(p,quality=98);paths.append(p.relative_to(ROOT).as_posix())
    return paths

def main(all_files=False):
    inputs=[SOURCE/'portrait.png']+sorted(SOURCE.glob('walk/*/[0-9][0-9].png')) if all_files else [SOURCE/'portrait.png',SOURCE/'walk/E/01.png']
    records=[];tag='review' if all_files else 'trial'
    for p in inputs:
        before=sha(p);im=Image.open(p).convert('RGBA');out,stats=clean(im);dest=PACK/'staged'/p.relative_to(SOURCE);dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,optimize=True);assert sha(p)==before
        rec=dict(name=p.relative_to(SOURCE).as_posix(),path=p.relative_to(ROOT).as_posix(),output=dest.relative_to(ROOT).as_posix(),source_sha256=before,output_sha256=sha(dest),size=list(im.size),alpha_bbox=list(im.getchannel('A').getbbox()),**stats);records.append(rec)
    images=evidence(records,tag)
    result=dict(status='staged_needs_visual_review',created_utc=datetime.now(timezone.utc).isoformat(),source_unchanged=True,files=len(records),changed_rgb_pixels=sum(r['changed_rgb_pixels'] for r in records),unresolved=sum(r['unresolved'] for r in records),alpha_changed_pixels=0,records=records,evidence=images)
    (PACK/f'{tag}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ['records','evidence']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');main(p.parse_args().all)
