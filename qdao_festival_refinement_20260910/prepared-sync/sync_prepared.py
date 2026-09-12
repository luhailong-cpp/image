"""Rebuild only 198 repository prepared derivatives from current reviewed art.
Uses existing resize algorithms; never reads or writes the client project.
"""
from pathlib import Path
import json,hashlib,shutil,ast,argparse,datetime,collections
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;ROOT=B.parents[1];LANCZOS=Image.Resampling.LANCZOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Copy the established pure in-memory nine_slice function without executing module IO.
tree=ast.parse((ROOT/'client_ui_refresh_20260908/sync_assets.py').read_text(encoding='utf-8'))
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='nine_slice')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'existing_nine_slice','exec'))
def build():
 review=json.loads((B.parent/'prepared-derivative-review.json').read_text(encoding='utf-8'))
 jobs=[x for x in review['records'] if x['decision']=='update_from_current_authoritative_source']
 components=json.loads((ROOT/'qdao_ui_redesign_v5/components/manifest.json').read_text(encoding='utf-8'))['assets']
 cm={'qdao_ui_redesign_v5/components/'+x['png']:x for x in components}
 rows=[]
 for e in jobs:
  src=ROOT/e['source'];dst=ROOT/e['path'];stage=B/'staged'/e['path'];stage.parent.mkdir(parents=True,exist_ok=True)
  assert sha(src)==e['source_sha256'],str(src)+' changed source'
  before=sha(dst);size=tuple(e['size']);method=e['derived_method'];im=Image.open(src).convert('RGBA')
  if method=='byte_copy':shutil.copyfile(src,stage)
  else:
   if method in ('manifest_nine_slice','proportional_height_then_horizontal_nine_slice'):
    comp=cm[e['source']];edge=comp['nine_slice']
    if method=='proportional_height_then_horizontal_nine_slice':
     ratio=size[1]/im.height;im=im.resize((round(im.width*ratio),size[1]),LANCZOS)
     edge={k:round(edge[k]*ratio) for k in ('left','top','right','bottom')}
    im=nine_slice(im,size,edge)
   elif method=='LANCZOS_resample':im=im.resize(size,LANCZOS)
   else:raise ValueError(method)
   im.save(stage,optimize=True)
  out=Image.open(stage);out.load();old=Image.open(dst).convert('RGBA')
  assert out.size==size and out.mode==e['mode'],e['path']
  rgba=out.convert('RGBA');rgba_sha=hashlib.sha256(rgba.tobytes()).hexdigest()
  assert rgba_sha==e['expected_rgba_sha256'],e['path']+' unexpected resize pixels'
  rows.append({'path':e['path'],'source':e['source'],'source_sha256':sha(src),'before_sha256':before,'after_sha256':sha(stage),'size':list(size),'mode':out.mode,'category':e['category'],'method':method,'rgba_matches_current_source_recipe':True,'alpha_identical_to_previous_prepared':rgba.getchannel('A').tobytes()==old.getchannel('A').tobytes(),'note':'Retain target canvas and RGBA channel; obsolete UI silhouette follows already-reviewed current v10 source and its existing border recipe. No canonical source pixels changed.','stage':stage.relative_to(ROOT).as_posix()})
 dump(B/'staged-validation.json',{'status':'staged_verified','files':rows,'count':len(rows),'alpha_identical_count':sum(x['alpha_identical_to_previous_prepared'] for x in rows),'errors':[],'client_read_or_written':False})
 # Comparison evidence: all four sizing methods and distinctive legacy controls.
 selected=[]
 for method in ['manifest_nine_slice','proportional_height_then_horizontal_nine_slice','LANCZOS_resample','byte_copy']:
  selected.append(next(x for x in rows if x['method']==method))
 selected += [next(x for x in rows if x['path'].endswith('/round_badge_taiji.png')),next(x for x in rows if x['path'].endswith('/tab_normal.png'))]
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);sheet=Image.new('RGB',(1024,768),'#ded8ce');d=ImageDraw.Draw(sheet)
 for n,e in enumerate(selected):
  y=n*128;d.text((8,y+2),Path(e['path']).name+' | before / current-source export',fill='#17392c',font=font)
  for col,p in enumerate([ROOT/e['path'],ROOT/e['stage']]):
   im=Image.open(p).convert('RGBA');im.thumbnail((492,100),LANCZOS);sheet.paste(im,(col*512+(512-im.width)//2,y+25),im)
 sheet.save(B/'prepared-before-after.jpg',quality=95)
 return rows
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--publish',action='store_true');a=ap.parse_args()
 if not a.publish:rows=build();print(json.dumps({'staged':len(rows),'errors':[]}))
 else:
  v=json.loads((B/'staged-validation.json').read_text(encoding='utf-8'));approval=json.loads((B/'visual-approval.json').read_text(encoding='utf-8'));assert approval['status']=='passed'
  assert approval['validation_sha256']==sha(B/'staged-validation.json')
  for e in v['files']:
   src=ROOT/e['source'];dst=ROOT/e['path'];stage=ROOT/e['stage'];backup=B/'before'/e['path']
   assert sha(src)==e['source_sha256'] and sha(stage)==e['after_sha256'] and sha(dst)==e['before_sha256'],'Concurrent modification'
   backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,backup);shutil.copyfile(stage,dst)
   assert sha(dst)==e['after_sha256'];e['backup']=backup.relative_to(ROOT).as_posix();e['status']='published';e['decision']='updated_derived'
  report={'status':'published','published_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':v['files'],'count':len(v['files']),'alpha_identical_count':v['alpha_identical_count'],'errors':[],'client_read_or_written':False,'visual_review':'visual-approval.json','recipe':'sync_prepared.py'}
  dump(B/'publication.json',report)
  # Separate repository publication pointer; no rewriting historical client hashes/status.
  dump(ROOT/'client_ui_refresh_20260908/prepared-festival-current.json',{'status':'repository_prepared_updated_not_client_synced','publication':'../qdao_festival_refinement_20260910/prepared-sync/publication.json','files':v['files'],'client_synced':False})
  print(json.dumps({'published':len(v['files']),'errors':[]}))
