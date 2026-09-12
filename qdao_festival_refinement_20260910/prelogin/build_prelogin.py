"""Deterministic composition/export of approved image_gen pre-login art.
Creative pixels come only from saved generated PNGs; original UI pixels are restored.
Run without flags to stage; --publish requires recorded visual approval.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
V5=ROOT/'qdao_ui_redesign_v5'
STEMS=['01_login','03_character_select']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p,root=ROOT):
 with Image.open(p) as im: size=list(im.size);mode=im.mode
 return {'path':p.relative_to(root).as_posix(),'size':size,'mode':mode,'bytes':p.stat().st_size,'sha256':sha(p)}
def savej(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def original(stem):
 backup=BASE/'before'/'source'/f'{stem}.png'
 return backup if backup.exists() else V5/'source'/f'{stem}.png'
def compose(stem):
 old=Image.open(original(stem)).convert('RGB'); new=Image.open(BASE/f'{stem}.generated.png').convert('RGB')
 assert old.size==new.size,(old.size,new.size)
 if stem=='01_login':
  # Original UI silhouettes are layered over AI scene. Feather stays outside UI.
  ui=Image.new('L',old.size,0); d=ImageDraw.Draw(ui)
  polygons=[[(144,209),(170,180),(348,167),(394,128),(409,93),(480,67),(528,98),(552,143),(589,172),(790,177),(824,219),(819,335),(793,373),(654,390),(580,406),(457,405),(339,399),(225,390),(174,359),(145,301)],[(183,418),(762,414),(789,429),(791,467),(767,487),(192,488),(172,472),(170,440)],[(252,509),(696,510),(716,525),(744,533),(737,566),(749,598),(722,623),(696,637),(250,636),(225,616),(206,607),(214,576),(203,556),(226,533)],[(1660,13),(1914,13),(1914,154),(1660,154)]]
  for poly in polygons:d.polygon(poly,fill=255)
  d.rectangle((408,654,571,702),fill=255)
  recover=ImageChops.lighter(ui,ui.filter(ImageFilter.GaussianBlur(5)))
  out=Image.composite(old,new,recover)
  checks=[(215,200,760,350),(228,428,753,473),(262,536,689,619),(415,662,560,695),(1690,25,1890,139)]
  spec={'method':'AI whole-scene base with original UI silhouettes','polygons':polygons,'account_box':[408,654,571,702],'outside_feather':5}
 else:
  m=Image.new('L',old.size,0);ImageDraw.Draw(m).rectangle((560,0,1450,814),fill=255);m=m.filter(ImageFilter.GaussianBlur(10))
  checks=[(0,0,554,814),(1440,0,1931,487),(1405,635,1931,814)]
  for b in checks:ImageDraw.Draw(m).rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=0)
  out=Image.composite(new,old,m)
  # Match the AI blank paper patch to unchanged blank paper below the old row.
  a=np.asarray(old).astype(np.float32); b=np.asarray(new).astype(np.float32)
  sample=(1490,570,1770,594);x0,y0,x1,y1=sample
  delta=np.median((a-b)[y0:y1,x0:x1].reshape(-1,3),axis=0)
  corrected=Image.fromarray(np.clip(np.rint(b+delta),0,255).astype(np.uint8))
  row=Image.new('L',old.size,0);ImageDraw.Draw(row).rectangle((1467,484,1795,582),fill=255);row=row.filter(ImageFilter.GaussianBlur(9))
  ImageDraw.Draw(row).rectangle((1480,505,1775,551),fill=255)
  # No generated field text or border pixels enter the original UI layer.
  rd=ImageDraw.Draw(row);rd.rectangle((0,0,1930,486),fill=0)
  out=Image.composite(corrected,out,row)
  spec={'method':'AI center scene plus restored original UI and AI blank-paper row','scene_box':[560,0,1450,814],'feather':10,'paper_delta_rgb':delta.tolist(),'paper_match_sample':sample,'row_full_opacity_box':[1480,505,1775,551]}
 tests=[{'box':b,'original_pixels_preserved':ImageChops.difference(old.crop(b),out.crop(b)).getbbox() is None} for b in checks]
 assert all(x['original_pixels_preserved'] for x in tests),tests
 dst=BASE/f'{stem}.staged.png';out.save(dst,optimize=True)
 savej(BASE/f'{stem}.composition.json',{'status':'staged_pending_visual_approval','source':record(original(stem)),'generated':record(BASE/f'{stem}.generated.png'),'staged':record(dst),'mask_spec':spec,'ui_preservation':tests,'mode':'RGB','no_native_resize':True})
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--publish',action='store_true');args=ap.parse_args()
 for stem in STEMS:compose(stem)
 if args.publish:
  approval=json.loads((BASE/'visual-approval.json').read_text(encoding='utf-8'))
  assert approval['status']=='passed'
  for stem in STEMS:assert approval['staged_sha256'][stem]==sha(BASE/f'{stem}.staged.png')
  mf=V5/'manifest.json'; j=json.loads(mf.read_text(encoding='utf-8-sig'))
  before=BASE/'before';before.mkdir(exist_ok=True)
  if not (before/'manifest.json').exists():shutil.copy2(mf,before/'manifest.json')
  changed=[]
  for stem in STEMS:
   src=V5/'source'/f'{stem}.png'; dst=V5/f'{stem}_2560x1080.png'
   for p in [src,dst]:
    back=before/p.relative_to(V5);back.parent.mkdir(parents=True,exist_ok=True)
    if not back.exists():shutil.copy2(p,back)
   baseline=json.loads((BASE/f'{stem}.composition.json').read_text(encoding='utf-8'))['source']['sha256']
   assert sha(src)==baseline or sha(src)==sha(BASE/f'{stem}.staged.png'),'Concurrent source modification'
   shutil.copyfile(BASE/f'{stem}.staged.png',src)
   with Image.open(src) as im:ImageOps.fit(im,(2560,1080),Image.Resampling.LANCZOS,centering=(.5,.5)).save(dst,optimize=True)
   e=next(e for e in j['screens'] if e['id']==stem)
   e['source']=record(src,V5);e['export']=record(dst,V5)
   e['creation_method']='built-in image_gen edit with deterministic original-UI composition'
   e['recipe']=f'../qdao_festival_refinement_20260910/prelogin/{stem}.prompt.txt'
   e['refinement_record']=f'../qdao_festival_refinement_20260910/prelogin/{stem}.composition.json'
   e['native_2560x1080_generation']=False
   changed += [record(src),record(dst)]
  j['updated']='2026-09-12';j['prelogin_refinement']='../qdao_festival_refinement_20260910/prelogin/publication.json'
  savej(mf,j)
  savej(BASE/'publication.json',{'status':'published','published_utc':datetime.now(timezone.utc).isoformat(),'files':changed,'source_count':2,'derived_count':2,'scope':'repository visual assets; no client engine writes','visual_approval':'visual-approval.json','recipe':'build_prelogin.py','generation':'built-in image_gen; model and quality parameters unavailable; project preference GPT Image 2','preserved':'native source canvases, text, layout and protected original UI pixels'})
  print(json.dumps({'published':len(changed),'errors':[]}))
 else:print('2 pre-login candidates staged; formal files unchanged')
