from pathlib import Path
import importlib.util,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
HERE=Path(__file__).resolve().parent
STAGE=HERE/'work-S-second-final'
OUT=STAGE/'candidate/06_thunder_caster_boy'
REVIEW=OUT/'review/s09-16'
REVIEW.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
verifier=module('s_second_verify',HERE/'alpha_verify.py')
verifier.ROOT=STAGE
verifier.mod=lambda name:module('s_second_vendor_'+name,HERE.parents[1]/'tools/vendor'/f'{name}.py')
records=load(OUT/'processing/frame-sources.json')
rows=[]
for frame in range(9,17):
 key=f'walk/S/{frame:02d}.png';batch=f'S{frame:02d}-edge-final-v1'
 p=OUT/key;im=Image.open(p).convert('RGBA');a=np.array(im)
 opaque=a[:,:,3]>8;y,x=np.where(opaque)
 edge=opaque & (np.asarray(Image.fromarray((opaque*255).astype('uint8')).filter(ImageFilter.MinFilter(7)))==0)
 c=a[:,:,:3].astype('int16');magenta=edge&(c[:,:,0]>c[:,:,1]+35)&(c[:,:,2]>c[:,:,1]+25)&(c[:,:,0]>80)&(c[:,:,2]>80)
 archive=HERE.parent/'06-generation'/batch;job=load(archive/'job.json');legacy=Path(job['references'][0]['path'])
 assert sha(legacy)==job['references'][0]['sha256']
 verification=verifier.verify('06_thunder_caster_boy','S',False,frame)
 (OUT/'review'/f'validation-S-{frame:02d}.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 crops=[('hair',(330,max(0,int(y.min())-12),842,max(0,int(y.min())-12)+256)),('staff and hands',(120,300,632,556)),('robe hems',(128,622,640,878)),('boots',(290,738,802,994))]
 zoom=Image.new('RGB',(2048,2048),(0,0,0))
 d=ImageDraw.Draw(zoom)
 for i,(label,box) in enumerate(crops):
  for j,(bg,color) in enumerate((('dark',(30,38,46)),('light',(240,238,228)))):
   tile=Image.new('RGBA',(512,256),color+(255,));tile.alpha_composite(im.crop(box));tile=tile.convert('RGB').resize((1024,512),Image.Resampling.NEAREST);zoom.paste(tile,(j*1024,i*512));d.text((j*1024+10,i*512+6),f'S{frame:02d} {label} {bg} 200%',fill=(255,255,255) if j==0 else (0,0,0))
 zp=REVIEW/f'S{frame:02d}-edge-200.png';zoom.save(zp)
 rows.append({'frame':key,'batch':batch,'sha256':sha(p),'raw_sha256':records[key]['source']['sha256'],'native_size':records[key]['source']['native_size'],'final_size':list(im.size),'subject_bbox_alpha_gt_8':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],'subject_height':int(y.max()-y.min()+1),'foot_y':int(y.max()),'common_scale':records[key]['common_scale'],'whole_cell_scale':records[key]['whole_cell_scale'],'strict_magenta_edge_pixels':int(magenta.sum()),'old_file_sha256':sha(legacy),'old_original_unchanged_vs_generation_request':True,'independent_reconstruction':verification,'edge_zoom':str(zp),'visual_review':'pending'})
summary={'scope':'S09-S16 only','checked_at':datetime.now(timezone.utc).isoformat(),'status':'numeric_passed_visual_pending','unique_final_sha256':len({r['sha256'] for r in rows}),'unique_raw_sha256':len({r['raw_sha256'] for r in rows}),'rows':rows}
(REVIEW/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(rows),'unique':summary['unique_final_sha256'],'height':[r['subject_height'] for r in rows],'magenta_edge':[r['strict_magenta_edge_pixels'] for r in rows]},ensure_ascii=False))
