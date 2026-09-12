"""Read-only current-hash / pixel contract verification for published v9 edge refinement."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;V9=ROOT/'qdao_character_diversity_v9';PACK=ROOT/'q_daoist_character_pack_4096'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=read(V9/'festival_edge_refinement.json');p=read(HERE/'publication.json')
 assert r['status']==p['status']=='published' and p['count']==len(p['records'])==44
 assert sha(HERE/'publication.json')==r['publication_sha256']
 assert sha(HERE/'current-visual-review.json')==r['review_sha256']
 assert sha(V9/'visual_qa.json')==r['historical_visual_qa_unchanged_sha256']==sha(HERE/'before/qdao_character_diversity_v9/visual_qa.json')
 manifest=read(V9/'manifest.json');assert manifest==read(PACK/'manifest.json')
 vr=read(HERE/'current-visual-review.json');reviewed={x['path']:x for x in vr['records']};assert len(reviewed)==24
 changed={x['path']:x for x in p['records']}
 for row in p['records']:
  f=ROOT/row['path'];before=ROOT/row['before_path']
  assert sha(f)==row['output_sha256'] and sha(before)==row['source_sha256'],str(f)
  a=np.array(Image.open(before));b=np.array(Image.open(f))
  assert a.shape==b.shape and a.shape[2]==4
  assert np.array_equal(a[:,:,3],b[:,:,3]),'Alpha changed: '+str(f)
  hidden_changed=int(np.any(a[a[:,:,3]==0]!=b[a[:,:,3]==0],axis=1).sum())
  if row['kind']=='prepared_1024':assert hidden_changed==row['transparent_rgba_changed_pixels']
  else:assert hidden_changed==0,'Source transparent RGB changed: '+str(f)
  if row.get('processor'):assert sha(ROOT/row['processor'])==row['processor_sha256']
  if row.get('extra_mask_processor'):assert sha(ROOT/row['extra_mask_processor'])==row['extra_mask_processor_sha256']
 for row in manifest['assets']:
  f=PACK/row['path'];relative=f.relative_to(ROOT).as_posix();digest=sha(f)
  assert digest==row['sha256']==reviewed[relative]['sha256']
  im=Image.open(f);assert im.mode=='RGBA' and im.size==(4096,4096)
  assert list(im.getchannel('A').getbbox())==row['subject_bounds']
  assert list(im.getchannel('A').getextrema())==row['alpha_range']
  if 'age_direction' in row:assert read(PACK/row['record'])['sha256']==digest
  for evidence in reviewed[relative].get('evidence',[]):assert sha(ROOT/evidence['path'])==evidence['sha256']
 for row in read(V9/'compatibility_map.json')['mapping']:assert sha(ROOT/row['new_path'])==row['new_sha256']
 inv=read(ROOT/'client_ui_refresh_20260908/assets_manifest.json');by_source={x['source']:x for x in inv['records'] if x.get('category')=='profession_portrait'}
 prepared=read(V9/'prepared_sync.json');assert len(prepared['records'])==22
 for row in prepared['records']:
  s=ROOT/row['source'];out=ROOT/row['output'];desired=Image.open(s).resize((1024,1024),Image.Resampling.LANCZOS)
  assert desired.tobytes()==Image.open(out).tobytes()
  assert sha(s)==row['source_sha256']==by_source[row['source']]['source_sha256']
  assert sha(out)==row['output_sha256']==by_source[row['source']]['staged_sha256']
 hero=read(ROOT/'qdao_asset_refresh_v6/hero_compat_manifest.json')
 assert len(hero['assets'])==9 and len({sha(ROOT/x['path']) for x in hero['assets']})==1
 hero1024='qdao_chibi_game_pack_v4/hero-transparent_1024.png'
 for row in hero['assets']:assert sha(ROOT/row['path'])==row['sha256'] and sha(ROOT/hero1024)==row['source_sha256']
 v4=read(ROOT/'qdao_chibi_game_pack_v4/manifest.json')
 assert next(x for x in v4['files'] if x['path']=='hero-transparent_1024.png')['sha256']==sha(ROOT/hero1024)
 for row in p['retained_files']:assert sha(ROOT/row['path'])==row['sha256']
 assert sha(ROOT/p['overview']['path'])==p['overview']['sha256']
 for row in read(V9/'completion.json')['artifacts']:assert sha(V9/row['path'])==row['sha256']
 for row in read(V9/'followup_completion.json')['artifacts']:
  if row['path'].startswith('qdao_character_diversity_v9/'):assert sha(ROOT/row['path'])==row['sha256']
 print(json.dumps({'status':'passed','published_pngs':44,'all_alpha_pixel_exact':True,'all_source_transparent_rgb_unchanged':True,'prepared_hidden_rgb_changed_pixels':sum(x.get('transparent_rgba_changed_pixels',0) for x in p['records'] if x['kind']=='prepared_1024'),'current_v9_sources':24,'prepared_pixels_match_current_resize':22,'hero_4096_aliases':9,'retained_files_unchanged':len(p['retained_files']),'current_manifest_and_completion_hashes_match':True,'historical_visual_qa_unchanged':True,'actual_client_accessed':False}))
if __name__=='__main__':main()
