from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,sys,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from processor_rgb import clean
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
REVIEW=ROOT/'qdao_festival_refinement_20260910/reviews/v9-pets-style-review.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def tile(im,bg,size=(384,420)):
 im=im.copy();im.thumbnail(size,Image.Resampling.LANCZOS);b=Image.new('RGBA',size,bg);b.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return b.convert('RGB')
def evidence(old,new,cid,delta):
 folder=HERE/'evidence';folder.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
 page=Image.new('RGB',(1536,452),'#e8e1d4');dr=ImageDraw.Draw(page)
 for col,(im,label,bg) in enumerate([(old,'BEFORE LIGHT','#f5edde'),(old,'BEFORE DARK','#19332d'),(new,'AFTER LIGHT','#f5edde'),(new,'AFTER DARK','#19332d')]):
  dr.text((col*384+8,8),cid+' '+label,font=font,fill='#243b31');page.paste(tile(im,bg),(col*384,32))
 p=folder/(cid+'-full.jpg');page.save(p,quality=95);paths=[p.relative_to(ROOT).as_posix()]
 ys,xs=np.nonzero(delta & (np.asarray(old)[:,:,3]>=64));points=[]
 if len(ys):
  for quant in [12,48,85]:
   y=int(np.percentile(ys,quant));in_band=abs(ys-y)<max(3,old.height//200);x=int(np.median(xs[in_band]));points.append((x,y))
  detail=Image.new('RGB',(1280,320*len(points)),'#e8e1d4');draw=ImageDraw.Draw(detail)
  for row,(x,y) in enumerate(points):
   box=(x-75,y-65,x+75,y+65)
   for col,(im,label,bg) in enumerate([(old,'BEFORE LIGHT','#f5edde'),(old,'BEFORE DARK','#19332d'),(new,'AFTER LIGHT','#f5edde'),(new,'AFTER DARK','#19332d')]):
    draw.text((col*320+4,row*320+4),f'{cid} {x},{y} '+label,font=font,fill='#243b31');crop=im.crop(box).resize((300,260),Image.Resampling.NEAREST);back=Image.new('RGBA',crop.size,bg);back.alpha_composite(crop);detail.paste(back.convert('RGB'),(col*320+10,row*320+40))
  q=folder/(cid+'-detail.jpg');detail.save(q,quality=97);paths.append(q.relative_to(ROOT).as_posix())
 return paths,points
def stage(ids):
 existing=HERE/'stage.json';records=json.loads(existing.read_text(encoding='utf-8'))['records'] if existing.exists() else []
 review=json.loads(REVIEW.read_text(encoding='utf-8'));items=[f for f in review['files'] if f['kind']=='v9_authoritative_static' and f['status']=='needs_edit']
 items.append({'path':'qdao_chibi_game_pack_v4/hero-transparent_1024.png','character_id':'hero1024','sha256':'b6f18732fff28c0faa8d2d0f09bf87800dbadf78c78f7cd093cbec5eae4268e4'})
 for item in items:
  cid=item['character_id'];rel=item['path']
  if ids and cid not in ids:continue
  src=ROOT/rel;assert sha(src)==item['sha256'],f'Input changed: {rel}'
  if any(x['path']==rel for x in records):continue
  before=HERE/'before'/rel;before.parent.mkdir(parents=True,exist_ok=True)
  if before.exists():assert sha(before)==item['sha256']
  else:shutil.copy2(src,before)
  dst=HERE/'staged'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  twin=next((x for x in records if x['source_sha256']==item['sha256']),None)
  if twin:
   shutil.copy2(ROOT/twin['staged_path'],dst);rec=dict(twin);rec.update(path=rel,staged_path=dst.relative_to(ROOT).as_posix(),before_path=before.relative_to(ROOT).as_posix(),byte_identical_alias_of=twin['path']);records.append(rec);dump(existing,{'status':'staged_pending_visual_review','updated_utc':datetime.now(timezone.utc).isoformat(),'processor':str((HERE/'processor_rgb.py').relative_to(ROOT)),'processor_sha256':sha(HERE/'processor_rgb.py'),'records':records});continue
  old=Image.open(src).convert('RGBA');new,stats=clean(old)
  olda=np.asarray(old);newa=np.asarray(new);delta=np.any(olda[:,:,:3]!=newa[:,:,:3],axis=2)
  assert np.array_equal(olda[:,:,3],newa[:,:,3]);assert np.array_equal(olda[olda[:,:,3]==0],newa[olda[:,:,3]==0]);assert stats['unresolved']==0,stats
  new.save(dst,optimize=True);assert sha(src)==item['sha256']
  ev,points=evidence(old,new,cid,delta)
  rec={'path':rel,'character_id':cid,'source_sha256':item['sha256'],'output_sha256':sha(dst),'before_path':before.relative_to(ROOT).as_posix(),'staged_path':dst.relative_to(ROOT).as_posix(),'processor':(HERE/'processor_rgb.py').relative_to(ROOT).as_posix(),'processor_sha256':sha(HERE/'processor_rgb.py'),'size':list(old.size),'mode':'RGBA','alpha_sha256_before':hashlib.sha256(olda[:,:,3].tobytes()).hexdigest(),'alpha_sha256_after':hashlib.sha256(newa[:,:,3].tobytes()).hexdigest(),'subject_bbox':list(old.getchannel('A').getbbox()),'rgb_changed_fraction':float(delta.mean()),'evidence':ev,'detail_points':points,**stats}
  records.append(rec);dump(existing,{'status':'staged_pending_visual_review','updated_utc':datetime.now(timezone.utc).isoformat(),'processor':str((HERE/'processor_rgb.py').relative_to(ROOT)),'processor_sha256':sha(HERE/'processor_rgb.py'),'method':'Reuse existing same-image magenta-mixture donor fitting; select only current transparent boundary pixels (8px band) with min(R,B)-G>10; donors alpha>=240, inward1px, min(R,B)-G<5; search8/16/32/64/128px; expanded only for thin native4096 contours. RGB only; no alpha, geometry, new design, global recolor or API image generation.','records':records})
  print(json.dumps({'id':cid,'path':rel,'changed_rgb_pixels':stats['changed_rgb_pixels'],'unresolved':stats['unresolved'],'alpha_changed_pixels':0}),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ids',nargs='*');args=ap.parse_args();stage(set(args.ids or []))
