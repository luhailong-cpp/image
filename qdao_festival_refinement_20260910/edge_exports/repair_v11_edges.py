"""Rebuild already-generated v11 exports: local RGB matte cleanup; never draw or change alpha.
Derived from qdao_cutout_edge_repair_20260911/27/repair.py and the existing
30_han_xiangzi/clean_export_edges.py. Stage -> inspect -> approve -> publish.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,hashlib,json,shutil,importlib.util
from collections import deque
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageFont,ImageSequence
PACK=Path(__file__).resolve().parent
ROOT=PACK.parents[1]
ROSTER=ROOT/'qdao_chibi_roster_v11'
REVIEW=ROOT/'qdao_festival_refinement_20260910/reviews/v11-style-review.json'
SLUGS=['23_lantern_courier','24_lu_dongbin','25_lion_drum_guard','26_osmanthus_healer','28_moon_rabbit_artificer','29_he_xiangu']
DIRS=['S','SW','W','NW','N','NE','E','SE']
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def local(p):return p.relative_to(ROOT).as_posix()
def safe(p):p=p.resolve();assert p.is_relative_to(ROOT);return p

def snapshot():
    if (PACK/'before.json').exists():return load(PACK/'before.json')
    paths=[]
    for slug in SLUGS:
        base=ROSTER/slug;m=load(base/'manifest.json')
        paths += [base/f['path'] for f in m['files']]
        paths += [base/'manifest.json',base/'qc.json']
        paths += [p for p in (base/'processing').rglob('*') if p.is_file() and p.suffix in ['.json','.txt','.py','.md']]
    paths += [ROSTER/name for name in ['manifest.json','validation.json','roster-overview.jpg','movement-overview.gif','qdao-roster-v11-final.zip','download.json'] if (ROSTER/name).exists()]
    paths += [REVIEW,Path(__file__).resolve()]
    rows=[]
    for p in sorted(set(paths)):
        rel=local(p); dest=PACK/'before'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        assert sha(p)==sha(dest)
        rows.append({'path':rel,'before':local(dest),'sha256':sha(p),'bytes':p.stat().st_size})
    d={'status':'frozen_before_export_repair','created_utc':now(),'files':rows,'images_generated':False}
    dump(PACK/'before.json',d);return d

def clean(im,slug):
    a=np.asarray(im.convert('RGBA')).copy(); out=a.copy()
    r,g,b=a[:,:,:3].astype(np.int16).transpose(2,0,1); alpha=a[:,:,3]
    dom=np.minimum(r,b)-g
    near=np.asarray(Image.fromarray(((alpha<16)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17)))>0
    inner=np.asarray(Image.fromarray(((alpha<16)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))==0
    protected=slug.startswith(('28_','29_'))
    if protected:
        yy=np.nonzero(alpha>8)[0];cut=float(yy.min()+.40*(yy.max()-yy.min()))
        head=np.arange(a.shape[0])[:,None]<=cut
        # The portrait/frame palette includes intentional lilac or pink below
        # the head. There only accept a strongly saturated key signature.
        strong=(dom>35)&(g<np.minimum(r,b)*.55)&(np.minimum(r,b)>45)
        mask=(alpha>0)&((near&((head&(dom>10))|strong))|(head&strong))
        hair_extension=np.zeros_like(mask)
        if slug.startswith('29_'):
            neutral_dark=(alpha>=128)&(np.max(a[:,:,:3],axis=2)<110)&(np.max(a[:,:,:3],axis=2).astype(int)-np.min(a[:,:,:3],axis=2).astype(int)<35)
            # Limit dark donors to neutral-black components connected to the
            # upper head; shaded pink sleeves and the lower garment are not seeds.
            connected_dark=neutral_dark&head
            queue=deque(zip(*np.nonzero(connected_dark)))
            while queue:
                cy,cx=queue.popleft()
                for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<a.shape[0] and 0<=nx<a.shape[1] and neutral_dark[ny,nx] and not connected_dark[ny,nx]:
                        connected_dark[ny,nx]=True;queue.append((ny,nx))
            near_dark=np.asarray(Image.fromarray((connected_dark*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0
            hair_extension=(alpha>0)&near&near_dark&(dom>10)&(np.arange(a.shape[0])[:,None]<(yy.min()+.62*(yy.max()-yy.min())))
            mask|=hair_extension
        # Intentional purple is permitted as a donor for purple cloth, but
        # not for the upper black-hair zone.
        donor=(alpha>=240)&inner&(~strong)
    else:
        cut=None;head=None
        strong=(dom>40)&(r>100)&(b>100)
        mask=(alpha>0)&(near|strong)&(dom>10)
        donor=(alpha>=240)&inner&(dom<5)
    head_donor=donor&(dom<5)
    hair_donor=(donor&connected_dark&(dom<5)) if slug.startswith('29_') else donor
    h,w=alpha.shape;unresolved=[];distances=[];selected=int(mask.sum())
    for y,x in zip(*np.nonzero(mask)):
        available=donor
        if protected and head[y,0]:available=head_donor
        elif protected and slug.startswith('29_') and hair_extension[y,x]:
            available=hair_donor
        best=None
        for radius in [8,16,32]:
            x0=max(0,x-radius);x1=min(w,x+radius+1);y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(available[y0:y1,x0:x1]);yy+=y0;xx+=x0
            if len(xx):
                dd=(xx-x)**2+(yy-y)**2
                colors=a[yy,xx,:3].astype(np.float32);observed=a[y,x,:3].astype(np.float32)
                key=np.array([255.,0.,255.],dtype=np.float32);v=key-colors
                fraction=np.clip(np.sum((observed-colors)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1),0,.99)
                error=np.sum((colors+v*fraction[:,None]-observed)**2,axis=1)
                k=int(np.argmin(error+dd*3.0));best=(int(yy[k]),int(xx[k]));distances.append(float(np.sqrt(dd[k])));break
        if best is None:unresolved.append([int(x),int(y),int(alpha[y,x])]);continue
        out[y,x,:3]=a[best[0],best[1],:3]
    changed=np.any(out[:,:,:3]!=a[:,:,:3],axis=2)
    assert np.array_equal(a[:,:,3],out[:,:,3])
    assert np.array_equal(a[~mask],out[~mask])
    assert np.array_equal(a[alpha==0],out[alpha==0])
    assert changed.sum()<a.shape[0]*a.shape[1]*.04,'Unexpected broad pixel change'
    maskim=Image.fromarray((changed*255).astype(np.uint8))
    before_diag=(r>g+40)&(b>g+40)&(r>100)&(b>100)&(alpha>=32)
    nr,ng,nb=out[:,:,:3].astype(np.int16).transpose(2,0,1)
    after_diag=(nr>ng+40)&(nb>ng+40)&(nr>100)&(nb>100)&(alpha>=32)
    return Image.fromarray(out),maskim,{'selected_pixels':selected,'changed_rgb_pixels':int(changed.sum()),'alpha_changed_pixels':0,'unselected_rgb_changed_pixels':0,'transparent_pixels_changed':0,'unresolved':unresolved,'max_donor_distance':max(distances or [0]),'mean_donor_distance':float(np.mean(distances)) if distances else 0,'before_strong_magenta':int(before_diag.sum()),'after_strong_magenta_diagnostic':int(after_diag.sum()),'protected_lilac_or_pink_palette':protected,'head_cut_y':cut,'alpha_sha256':ah(alpha),'before_rgba_sha256':ah(a),'after_rgba_sha256':ah(out)}

def evidence(rows,tag):
    outdir=PACK/'evidence'/tag;outdir.mkdir(parents=True,exist_ok=True);paths=[]
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    for start in range(0,len(rows),4):
        group=rows[start:start+4];page=Image.new('RGB',(2048,552*len(group)),'#e9e3d6');draw=ImageDraw.Draw(page)
        for ri,row in enumerate(group):
            old=Image.open(ROOT/row['before']);new=Image.open(ROOT/row['staged'])
            for col,(im,bg,label) in enumerate([(old,'#f2eddf','BEFORE LIGHT'),(old,'#172c26','BEFORE DARK'),(new,'#f2eddf','AFTER LIGHT'),(new,'#172c26','AFTER DARK')]):
                im=im.convert('RGBA');im.thumbnail((512,512),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(512,512),bg);tile.alpha_composite(im,((512-im.width)//2,(512-im.height)//2))
                page.paste(tile.convert('RGB'),(col*512,ri*552+40));draw.text((col*512+5,ri*552+6),row['slug'][:2]+' '+row['relative']+' '+label,fill='#17382d',font=font)
        dest=outdir/f'{start//4+1:02}.jpg';page.save(dest,quality=97);paths.append({'path':local(dest),'sha256':sha(dest)})
    return paths

def stage(trial,only=None):
    snapshot();review=load(REVIEW); rows=[]
    if only and not trial and (PACK/'stage.json').exists():
        rows=[r for r in load(PACK/'stage.json')['files'] if not r['slug'].startswith(only)]
    flagged={r['path'] for r in review['files'] if r['status']=='needs_edit'}
    for slug in SLUGS:
        if only and not slug.startswith(only):continue
        base=ROSTER/slug
        candidates=[base/'portrait.png']+[base/'walk'/d/f'{i:02d}.png' for d in DIRS for i in range(1,5)]
        if trial:candidates=[base/'portrait.png',base/'walk/S/01.png']
        for p in candidates:
            rel=local(p);old=PACK/'before'/rel
            dest=PACK/'staged'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            im=Image.open(old).convert('RGBA')
            if rel in flagged:
                result,mask,stats=clean(im,slug);result.save(dest,optimize=True)
                mp=PACK/'masks'/slug/p.relative_to(base);mp.parent.mkdir(parents=True,exist_ok=True);mask.save(mp)
            else:
                shutil.copy2(old,dest);a=np.asarray(im);stats={'changed_rgb_pixels':0,'alpha_changed_pixels':0,'unselected_rgb_changed_pixels':0,'transparent_pixels_changed':0,'unresolved':[],'alpha_sha256':ah(a[:,:,3]),'before_rgba_sha256':ah(a),'after_rgba_sha256':ah(a),'retained_reason':'portrait passed current style/edge review'};mp=None
            assert sha(p)==sha(old),'Upstream changed current source during staging'
            assert im.size==Image.open(dest).size
            if p.parent.name in DIRS:assert np.nonzero(np.asarray(im)[:,:,3]>8)[0].max()==471
            rows.append({'path':rel,'slug':slug,'relative':p.relative_to(base).as_posix(),'before':local(old),'staged':local(dest),'mask':local(mp) if mp else None,'source_sha256':sha(old),'output_sha256':sha(dest),'size':list(im.size),**stats})
    pages=evidence(rows,'trial' if trial else 'all')
    d={'schema':'qdao.festival.edge-export-stage.v1','status':'trial_needs_visual_review' if trial else 'staged_needs_visual_review','created_utc':now(),'source':'Accepted AI-generated existing portrait/32 frames; local matte RGB decontamination only','processor':local(Path(__file__).resolve()),'processor_sha256':sha(Path(__file__)),'reference_processors':[{'path':p,'sha256':sha(ROOT/p)} for p in ['qdao_cutout_edge_repair_20260911/27/repair.py','qdao_chibi_roster_v11/30_han_xiangzi/clean_export_edges.py']],'files':rows,'evidence':pages,'summary':{'base_images':len(rows),'changed':sum(x['changed_rgb_pixels']>0 for x in rows),'changed_rgb_pixels':sum(x['changed_rgb_pixels'] for x in rows),'unresolved':sum(len(x['unresolved']) for x in rows),'alpha_changes':0}}
    dump(PACK/('trial.json' if trial else 'stage.json'),d)
    print(json.dumps(d['summary']),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trial',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--only');a=p.parse_args()
    if a.trial or a.stage:stage(a.trial,a.only)
    else:p.print_help()
