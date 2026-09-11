"""Mechanical matte-color decontamination of existing ImageGen cutouts.

Does not generate art, move silhouettes, rescale frames, or alter alpha. Paint
colors are borrowed only from nearby clean foreground inside the same cutout.
Run stage first, inspect before/after evidence, then publish explicitly.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
import numpy as np

PACK=Path(__file__).resolve().parent
ROOT=PACK.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def candidates(a,kind):
    rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3]
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    dom=np.minimum(r,b)-g
    near=np.asarray(Image.fromarray(((alpha<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)))>0
    if kind=='hero':
        mask=(dom>28)&(r>g+28)&(b>g+28)&(alpha>0)&near
        rows=np.flatnonzero((alpha>0).any(axis=1))
        mask[rows[0]+round((rows[-1]-rows[0])*.42):]=False
        clean=(dom<18)
    elif kind=='fox':
        mask=(dom>75)&(r>b+6)&(alpha>0)&((alpha<160)|near)
        clean=~((dom>50)&(r>b+3))
    else:
        mask=(dom>42)&(r>b+6)&(alpha>0)&near
        clean=~((dom>25)&(r>b+3))
    return mask,clean&(alpha>=224)

def repair(im,kind):
    a=np.asarray(im.convert('RGBA')).copy();out=a.copy();mask,donors=candidates(a,kind)
    h,w=a.shape[:2]; changed=[];skipped=[]
    for y,x in zip(*np.nonzero(mask)):
        best=None
        for radius in (3,6,10):
            x0=max(0,x-radius);x1=min(w,x+radius+1);y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(donors[y0:y1,x0:x1]);yy+=y0;xx+=x0
            if len(xx):
                dist=(xx-x)**2+(yy-y)**2
                k=int(np.argmin(dist));best=a[yy[k],xx[k],:3];break
        if best is None:skipped.append([int(x),int(y)]);continue
        out[y,x,:3]=best
        changed.append([int(x),int(y)])
    assert np.array_equal(a[:,:,3],out[:,:,3])
    assert np.array_equal(a[~mask],out[~mask])
    assert len(changed)<w*h*.02,'Unexpected affected area; manual review required'
    return Image.fromarray(out),dict(candidate_pixels=int(mask.sum()),changed_rgb_pixels=len(changed),
        unresolved_pixels=skipped,alpha_changed_pixels=0,other_pixels_changed=0,changed_coordinates=changed)

def inputs(trial):
    if trial:return [('character_move_8dir/east_frame_01.png','hero'),('character_move_8dir/south_frame_01.png','hero')]
    rows=[(p.relative_to(ROOT).as_posix(),'hero') for p in sorted((ROOT/'character_move_8dir').glob('*_frame_*.png'))]
    rows += [(p.relative_to(ROOT).as_posix(),'pet') for p in sorted((ROOT/'qdao_chibi_pets_v1').glob('*-transparent_1254.png'))]
    rows += [('qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png','fox')]
    icons=load(ROOT/'docs/style-audit-20260910/continuation/icons/review.json')
    rows += [(r['path'],'item') for r in icons['records'] if r['verdict']=='style_compatible_edge_cleanup']
    return rows

def evidence(records,tag):
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    reviews=load(ROOT/'docs/style-audit-20260910/continuation/edges/review.json')['records']
    rois={r['path']:next((e.get('crop_xyxy') for e in r['evidence'] if e.get('crop_xyxy')),None) for r in reviews}
    pages=[]
    for start in range(0,len(records),8):
        page=Image.new('RGB',(1320,980),'#eee7da');d=ImageDraw.Draw(page)
        for i,r in enumerate(records[start:start+8]):
            p=r['path']; old=Image.open(ROOT/p).convert('RGBA');new=Image.open(PACK/'staged'/p).convert('RGBA')
            roi=rois.get(p)
            if not roi:
                pts=r['changed_coordinates']
                if pts: x,y=pts[len(pts)//2];roi=[max(0,x-40),max(0,y-40),min(old.width,x+40),min(old.height,y+40)]
                else:roi=[0,0,min(80,old.width),min(80,old.height)]
            x0=i%2*660;y0=i//2*245
            d.text((x0+8,y0+5),Path(p).name+' | OLD / NEW',font=font,fill='#163b2f')
            for j,im in enumerate((old,new)):
                crop=im.crop(roi);crop.thumbnail((150,90));crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST)
                for k,bg in enumerate(('#f1eedf','#172a25')):
                    tile=Image.new('RGBA',crop.size,bg);tile.alpha_composite(crop)
                    page.paste(tile.convert('RGB'),(x0+j*320+8+k*155,y0+35))
            d.text((x0+8,y0+214),f'RGB fixed: {r["changed_rgb_pixels"]}; alpha unchanged; crop {roi}',font=font,fill='#163b2f')
        name=f'{tag}-{start//8+1:02}.jpg';page.save(PACK/name,quality=95);pages.append(name)
    return pages

def stage(trial):
    records=[]
    for rel,kind in inputs(trial):
        path=(ROOT/rel).resolve();assert path.is_relative_to(ROOT)
        before=sha(path);im=Image.open(path).convert('RGBA');out,stats=repair(im,kind)
        dest=PACK/'staged'/rel;dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest,optimize=True)
        assert sha(path)==before,'Source changed during processing'
        assert im.getchannel('A').getbbox()==out.getchannel('A').getbbox()
        row=dict(path=rel,kind=kind,source_sha256=before,output_sha256=sha(dest),size=list(im.size),
            alpha_bbox=list(im.getchannel('A').getbbox()),**stats)
        if kind=='hero':assert row['alpha_bbox'][3]==1179
        records.append(row)
    tag='trial' if trial else 'review'
    pages=evidence(records,tag)
    result=dict(status='staged_needs_visual_review',created_utc=datetime.now(timezone.utc).isoformat(),
        source_origin='Existing built-in ImageGen artwork; deterministic matte-edge RGB repair only',
        counts=dict(files=len(records),changed=sum(r['changed_rgb_pixels']>0 for r in records),
            pixels=sum(r['changed_rgb_pixels'] for r in records),unresolved=sum(len(r['unresolved_pixels']) for r in records)),
        invariants=['canvas','all alpha bytes','silhouette','frame anchor','unselected RGB'],evidence=pages,records=records)
    dump(PACK/f'{tag}.json',result);print(json.dumps(result['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trial',action='store_true');args=p.parse_args();stage(args.trial)
