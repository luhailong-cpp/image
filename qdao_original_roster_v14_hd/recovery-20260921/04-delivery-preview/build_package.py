"""Build byte-preserving 04 mixed action snapshots and explicitly unapproved previews."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil,re
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];IMAGE_ROOT=ROOT.parent
CHAR='04_mountain_guardian_boy';DIRS=('N','NE','E','SE','S','SW','W','NW')
V13=IMAGE_ROOT/'qdao_original_roster_v13/candidate'/CHAR;V14=ROOT/'candidate'/CHAR
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--revision',required=True);parser.add_argument('--selections',type=Path,default=HERE/'selections.json');args=parser.parse_args()
 assert re.fullmatch(r'[a-zA-Z0-9_-]+',args.revision)
 out=HERE/'revisions'/args.revision
 assert not out.exists(), 'Use a fresh revision; never overwrite a reviewed snapshot.'
 selections=read(args.selections);overrides=selections['overrides'];out.mkdir(parents=True);(out/'preview').mkdir()
 write(out/'selection-input.json',selections)
 rows=[];missing=[]
 expected=[*[f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1,17)],*[f'idle/{d}.png' for d in DIRS]]
 assert all(key in expected and key.startswith('walk/') for key in overrides)
 for key in expected:
  old=V13/key;new=V14/key;selection=overrides.get(key)
  if old.exists():
   assert selection is None,'Preserved V13 action override forbidden: '+key
   source=old;origin=V13;revision='preserved-v13';visual='preserved_existing_not_reapproved'
  elif selection:
   source=Path(selection['path']).resolve();assert source.is_relative_to((ROOT/'recovery-20260921').resolve());assert sha(source)==selection['sha256']
   origin=next(p for p in source.parents if p.name==CHAR);revision=selection['selected_revision'];visual=selection['visual_status']
   assert visual in ('pending','rejected','static_reviewed_pending_dynamic','root_selected_unapproved')
  elif new.exists():source=new;origin=V14;revision='canonical-v14-candidate';visual='pending'
  else:missing.append(key);continue
  source_hash=sha(source)
  binding=selections.get('expected_sources',{}).get(key)
  if binding:assert source.resolve()==Path(binding['path']).resolve() and source_hash==binding['sha256'],'Selected source differs from reviewed path/SHA: '+key
  dest=out/'runtime'/key;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);assert sha(dest)==source_hash
  im=Image.open(source);assert im.mode=='RGBA' and im.format=='PNG';size=list(im.size);assert size in ([512,512],[1024,1024]);arr=np.asarray(im)[:,:,3];ys,xs=np.where(arr>8);top=int(ys.min());h=int(ys.max()-ys.min()+1);axis=float(np.median(xs[ys<top+max(1,int((h-1)*.42))]))
  records_file=origin/'processing/frame-sources.json';records=read(records_file) if records_file.exists() else {};record=records.get(key)
  row={'path':key,'sha256':source_hash,'size':size,'pixels_per_unit':52 if size==[512,512] else 104,'source':str(source.resolve()),'selected_revision':revision,'visual_status':visual,'copied_byte_exact':True,'source_record_file':str(records_file) if records_file.exists() else None,'source_record_file_sha256':sha(records_file) if records_file.exists() else None,'source_record':record,'native_source_size':record.get('source',{}).get('native_size') if record else None,'anchor_native_px':[axis,int(ys.max())],'subject_height_native_px':h,'body_scale':float(np.sqrt(np.count_nonzero(arr[:,size[0]//4:3*size[0]//4])/(size[0]*size[1])))}
  row['review_note']=selections.get('review_notes',{}).get(key,'')
  rows.append(row)
 assert len({row['sha256'] for row in rows})==len(rows),'Duplicate PNG bytes across action slots'
 bykey={row['path']:row for row in rows};gifs=[];directions={}
 for direction in DIRS:
  keys=[f'walk/{direction}/{n:02d}.png' for n in range(1,17)];present=[key for key in keys if key in bykey];complete=len(present)==16
  directions[direction]={'available_walk':len(present),'complete_inventory':complete,'idle_present':f'idle/{direction}.png' in bykey,'visual_approval':False,'body_scale_cv':float(np.std([bykey[k]['body_scale'] for k in present])/np.mean([bykey[k]['body_scale'] for k in present])) if present else None}
  for mode,color in [('dark',(30,38,46)),('light',(240,238,228))]:
   text='white' if mode=='dark' else 'black';contact=Image.new('RGB',(2048,2240),color);draw=ImageDraw.Draw(contact);displays=[]
   for n,key in enumerate(keys):
    display=Image.new('RGB',(512,512),color)
    if key in bykey:
     im=Image.open(out/'runtime'/key).convert('RGBA');small=im if im.size==(512,512) else im.resize((512,512),Image.Resampling.LANCZOS);display.paste(small,(0,0),small)
    else:ImageDraw.Draw(display).text((160,250),'MISSING - NO SUBSTITUTE',fill=text)
    x=n%4*512;y=n//4*560;contact.paste(display,(x,y+32));draw.text((x+10,y+8),f'{direction}{n+1:02d} / '+(f'{bykey[key]["size"][0]}px {bykey[key]["selected_revision"]}' if key in bykey else 'MISSING'),fill=text);displays.append(display)
   contact.save(out/f'preview/{direction}-contact-{mode}.png')
   seam=Image.new('RGB',(2048,570),color);sd=ImageDraw.Draw(seam)
   for col,n in enumerate((14,15,0,1)):seam.paste(displays[n],(col*512,48));sd.text((col*512+15,15),f'{direction}{n+1:02d}',fill=text)
   seam.save(out/f'preview/{direction}-seam15-16-01-02-{mode}.png')
   if complete:
    gif=out/f'preview/{direction}-30ms-{mode}.gif';displays[0].save(gif,save_all=True,append_images=displays[1:],duration=[30]*16,loop=0,optimize=False,disposal=2)
    check=Image.open(gif);duration=[]
    for n in range(check.n_frames):check.seek(n);duration.append(check.info['duration'])
    assert check.n_frames==16 and duration==[30]*16
    gifs.append({'path':str(gif.relative_to(out)).replace('\\','/'),'sha256':sha(gif),'frames':16,'duration_ms':duration,'cycle_ms':480,'interpolation':False})
 manifest={'schema':'qdao-mixed-review-only-v1','created_at_utc':datetime.now(timezone.utc).isoformat(),'revision':args.revision,'character_id':CHAR,'status':'inventory_complete_visual_pending' if not missing else 'inventory_incomplete_visual_pending','target_walk':128,'target_idle':8,'actual_walk':sum(r['path'].startswith('walk/') for r in rows),'actual_idle':sum(r['path'].startswith('idle/') for r in rows),'missing':missing,'directions':directions,'frame_duration_ms':30,'cycle_duration_ms':480,'files':rows,'gif_checks':gifs,'source_png_bytes_unchanged':True,'old512_not_upscaled_on_disk':True,'new1024_not_downscaled_on_disk':True,'preview_only_equal_world_display':True,'formal_approval':False,'client_integration':False,'browser_dynamic_review':{'performed':False,'reason':'Not performed by package-building agent; root will review this pinned snapshot in its browser.'},'selection_input_sha256':sha(out/'selection-input.json')}
 manifest['known_rework_slots']=selections.get('known_rework_slots',[])
 manifest['review_notes']=selections.get('review_notes',{})
 write(out/'manifest.json',manifest)
 compact={**manifest,'files':[{k:v for k,v in row.items() if k!='source_record'} for row in rows]}
 template=(HERE/'preview-template.html').read_text(encoding='utf-8');(out/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(compact,ensure_ascii=False)),encoding='utf-8')
 (HERE/'index.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>04 山岳守卫素材预览</title><style>body{{font:20px system-ui;margin:40px;background:#eee9dc;color:#173833}}a{{color:#175d57}}</style><h1>04 山岳守卫 · 八方向混合素材预览</h1><p>当前快照：{args.revision}。{manifest["actual_walk"]}/128 行走，{manifest["actual_idle"]}/8 独立站立。未正式批准，未接入客户端。</p><p><a href="revisions/{args.revision}/index.html">打开八方向逐帧／30ms循环预览</a></p><p><a href="revisions/{args.revision}/manifest.json">查看逐文件来源、尺寸与SHA</a></p></html>',encoding='utf-8')
 print(json.dumps({'revision':args.revision,'walk':manifest['actual_walk'],'idle':manifest['actual_idle'],'missing':missing,'gif_count':len(gifs),'approved':False},ensure_ascii=False))
if __name__=='__main__':main()
