"""Supplement only moon-rabbit portrait black-hair tips; RGB sampling, no alpha edits."""
from pathlib import Path
from collections import deque
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
B=Path(__file__).resolve().parent;ROOT=B.parents[2];ROSTER=ROOT/'qdao_chibi_roster_v11';REL='28_moon_rabbit_artificer/portrait.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def snapshot():
    if (B/'before.json').exists():return
    paths=[ROSTER/x for x in [REL,'28_moon_rabbit_artificer/manifest.json','28_moon_rabbit_artificer/qc.json','28_moon_rabbit_artificer/processing/festival-edge-approval.json','manifest.json','validation.json','roster-overview.jpg','movement-overview.gif','qdao-roster-v11-final.zip','download.json']]
    paths += [B.parent/x for x in ['final-verification.json','README.md']]
    rows=[]
    for p in paths:
        rel=p.relative_to(ROOT);dst=B/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert sha(p)==sha(dst);rows.append({'path':rel.as_posix(),'before':dst.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    dump(B/'before.json',{'status':'frozen_prior_303_export_revision','utc':datetime.now(timezone.utc).isoformat(),'files':rows})
def clean(im):
    a=np.array(im.convert('RGBA'));out=a.copy();rgb=a[:,:,:3].astype(np.int16);al=a[:,:,3];ygrid=np.arange(a.shape[0])[:,None]
    dom=np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]
    neutral=(al>=128)&(rgb.max(axis=2)<110)&((rgb.max(axis=2)-rgb.min(axis=2))<35)
    connected=neutral&(ygrid<370);q=deque(zip(*np.where(connected)))
    while q:
        y,x=q.popleft()
        for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            ny,nx=y+dy,x+dx
            if 0<=ny<a.shape[0] and 0<=nx<a.shape[1] and neutral[ny,nx] and not connected[ny,nx]:connected[ny,nx]=True;q.append((ny,nx))
    near=np.array(Image.fromarray(((al<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(17)))>0
    inner=np.array(Image.fromarray(((al<16)*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))==0
    near_hair=np.array(Image.fromarray((connected*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)))>0
    mask=near_hair&near&(al>0)&(dom>10)&(ygrid>=330)&(ygrid<=450)
    donor=connected&(al>=240)&inner&(dom<5)
    distances=[];unresolved=[]
    for y,x in zip(*np.where(mask)):
        best=None
        for radius in [8,16,32]:
            x0=max(0,x-radius);x1=min(a.shape[1],x+radius+1);y0=max(0,y-radius);y1=min(a.shape[0],y+radius+1)
            yy,xx=np.where(donor[y0:y1,x0:x1]);yy+=y0;xx+=x0
            if len(xx):
                dd=(xx-x)**2+(yy-y)**2;c=rgb[yy,xx].astype('float32');o=rgb[y,x].astype('float32');v=np.array([255.,0.,255.])-c;f=np.clip(np.sum((o-c)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1),0,.99);err=np.sum((c+v*f[:,None]-o)**2,axis=1);k=np.argmin(err+dd*3);best=(yy[k],xx[k]);distances.append(float(np.sqrt(dd[k])));break
        if best is None:unresolved.append([int(x),int(y)]);continue
        out[y,x,:3]=a[best[0],best[1],:3]
    changed=np.any(a[:,:,:3]!=out[:,:,:3],axis=2)
    assert not unresolved;assert np.array_equal(a[:,:,3],out[:,:,3]);assert np.array_equal(a[~mask],out[~mask]);assert np.array_equal(a[al==0],out[al==0])
    assert np.array_equal(a[451:],out[451:]);assert np.array_equal(a[425,454],out[425,454]);assert changed.sum()<1500
    return Image.fromarray(out),Image.fromarray((changed*255).astype('uint8')),{'changed_rgb_pixels':int(changed.sum()),'alpha_changed_pixels':0,'alpha0_rgba_changed_pixels':0,'unselected_rgba_changed_pixels':0,'source_cloth_sample_454_425_retained':True,'all_pixels_y_ge_451_identical':True,'unresolved':unresolved,'max_donor_distance':max(distances),'mean_donor_distance':float(np.mean(distances)),'alpha_sha256':hashlib.sha256(al.tobytes()).hexdigest(),'changed_bbox':list(Image.fromarray((changed*255).astype('uint8')).getbbox())}
def main():
    snapshot();old=B/'before/qdao_chibi_roster_v11'/REL;im=Image.open(old).convert('RGBA');result,mask,stats=clean(im);dest=B/'staged/portrait.png';dest.parent.mkdir(parents=True,exist_ok=True);result.save(dest,optimize=True);mask.save(B/'changed-mask.png')
    page=Image.new('RGB',(1040,960),'#b9ad98');d=ImageDraw.Draw(page)
    for j,bg in enumerate(['#172c26','#f2eddf']):
        for i,img in enumerate([im,result]):
            tile=Image.new('RGBA',img.size,bg);tile.alpha_composite(img);crop=tile.crop((270,285,760,505));page.paste(crop.convert('RGB'),(i*520,j*480+25));d.text((i*520+6,j*480+4),('BEFORE' if i==0 else 'AFTER')+' native crop '+bg,fill='black')
            mini=tile.resize((230,230),Image.Resampling.LANCZOS);page.paste(mini.convert('RGB'),(i*520+145,j*480+246))
    page.save(B/'trial.png');dump(B/'trial.json',{'status':'numeric_passed_pending_visual','created_utc':datetime.now(timezone.utc).isoformat(),'path':'qdao_chibi_roster_v11/'+REL,'before_sha256':sha(old),'staged_sha256':sha(dest),'processor_sha256':sha(Path(__file__)),'mask_sha256':sha(B/'changed-mask.png'),'evidence':{'path':'trial.png','sha256':sha(B/'trial.png')},'stats':stats});print(json.dumps(stats))
if __name__=='__main__':main()
