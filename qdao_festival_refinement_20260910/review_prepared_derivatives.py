"""Read-only derivative consistency review; writes only this task's JSON report."""
import ast,hashlib,json,sys
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qdao_festival_refinement_20260910/prepared-derivative-review.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LANCZOS=Image.Resampling.LANCZOS
ns={'Image':Image,'LANCZOS':LANCZOS}
tree=ast.parse((ROOT/'client_ui_refresh_20260908/sync_assets.py').read_text(encoding='utf-8-sig'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='nine_slice')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<existing-nine-slice-function>','exec'),ns)
inv=read(ROOT/'qdao_festival_refinement_20260910/inventory.json')
rows=[r for r in inv['records'] if r['path'].startswith('client_ui_refresh_20260908/') and 'pending' in r['role']]
manifest=read(ROOT/'client_ui_refresh_20260908/assets_manifest.json')
by={'client_ui_refresh_20260908/'+r['staged']:r for r in manifest['records'] if r.get('staged')}
components={a['id']:a for a in read(ROOT/'qdao_ui_redesign_v5/components/manifest.json')['assets']}
scene_plan=read(ROOT/'qdao_festival_refinement_20260910/legacy-scene-sync-plan.json')
scene_targets={t['path']:g['copy_source'] for g in scene_plan['copy_groups'] for t in g['targets']}
hero='qdao_chibi_game_pack_v4/hero-transparent_1024.png'
records=[];errors=[]
for r in rows:
 rel=r['path'];p=ROOT/rel
 if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError(rel)
 stat=p.stat();rec={'path':rel,'current_sha256':sha(p),'current_bytes':stat.st_size,'inventory_role':r['role']}
 with Image.open(p) as im:
  im.load();actual=im.convert('RGBA');rec.update(size=list(im.size),mode=im.mode,rgba_sha256=hashlib.sha256(actual.tobytes()).hexdigest(),alpha_sha256=hashlib.sha256(actual.getchannel('A').tobytes()).hexdigest())
 original=by.get(rel)
 if not original:
  if rel.endswith('additional/login_background.raw.png'):
   rec.update(decision='historical_native_reference_preserve',evidence='legacy-scene-sync-plan.json protected_original_sources; original generation record retained')
  elif rel in scene_targets:
   rec.update(decision='pending_scene_sync',planned_source=scene_targets[rel])
  elif rel.endswith('prepared/UI/Ugui/RefreshV8/title_logo.png'):
   original={'source':'client_ui_refresh_20260908/additional/title_logo.png','method':'byte_copy','size':rec['size'],'category':'additional_art'}
  else:rec.update(decision='standalone_current_source_needs_separate_visual_review',evidence='additional/title_logo.png is optional authored source in sync_assets.py; no higher source in assets_manifest')
 if original:
  src=ROOT/original['source']
  if not src.resolve().is_relative_to(ROOT.resolve()):raise ValueError(original['source'])
  rec.update(source=original['source'],source_sha256=sha(src),category=original.get('category'),method=original.get('method'),authority='client_ui_refresh_20260908/sync_assets.py + current component contracts and source files')
  target=tuple(rec['size'])
  with Image.open(src) as sim:
   sim.load();rec['source_size']=list(sim.size)
   if sim.size==target: expected=sim.convert('RGBA');method='byte_copy'
   else:
    expected=sim.convert('RGBA');cc=original.get('component_contract');component=components.get((cc or {}).get('id'));edge=(component or {}).get('nine_slice')
    if cc:rec['component_contract_matches_current']={k:component.get(k) for k in cc}==cc
    if edge:
     if component.get('resize_axes')=='horizontal' and expected.height!=target[1]:
      ratio=target[1]/expected.height;expected=expected.resize((round(expected.width*ratio),target[1]),LANCZOS);edge={k:round(edge[k]*ratio) for k in ('left','top','right','bottom')};method='proportional_height_then_horizontal_nine_slice'
     else:method='manifest_nine_slice'
     expected=ns['nine_slice'](expected,target,edge)
    else:expected=expected.resize(target,LANCZOS);method='LANCZOS_resample'
  exact=actual.tobytes()==expected.tobytes();rec.update(derived_method=method,exact_source_file_bytes=rec['current_sha256']==rec['source_sha256'],expected_rgba_sha256=hashlib.sha256(expected.tobytes()).hexdigest(),matches_current_expected_rgba=exact,alpha_matches_expected=actual.getchannel('A').tobytes()==expected.getchannel('A').tobytes())
  rec['decision']='retain_current_consistent_derivative' if exact else 'update_from_current_authoritative_source'
  if not exact:
   diff=ImageChops.difference(actual,expected);rec['rgba_difference_bbox']=diff.convert('RGB').getbbox();rec['changed_pixel_count']=sum(1 for q in diff.getdata() if any(q))
  if rel in scene_targets:rec.update(decision='pending_scene_sync',planned_source=scene_targets[rel])
  elif original['source']==hero or rel.endswith('Native/screen_art_headband.png'):rec.update(decision='pending_final_hero_source_refresh',note='Current consistency recorded separately; parent authorized same new hero RGB correction to flow into actor/server previews.')
  if sha(src)!=rec['source_sha256']:errors.append('Source changed during review: '+original['source'])
 if p.stat().st_mtime_ns!=stat.st_mtime_ns or sha(p)!=rec['current_sha256']:errors.append('Target changed during review: '+rel)
 records.append(rec)
report={'schema':'qdao.prepared-derivative-review.v1','checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Exactly 220 inventory pending client_ui_refresh entries; excludes 22 accepted v9 profession copies and client filesystem','images_modified':0,'client_read_or_written':False,'summary':{'count':len(records),'decisions':dict(Counter(r['decision'] for r in records)),'derived_comparisons':sum('matches_current_expected_rgba'in r for r in records),'rgba_consistent':sum(r.get('matches_current_expected_rgba',False) for r in records),'byte_identical_to_current_source':sum(r.get('exact_source_file_bytes',False) for r in records),'categories':dict(Counter(r.get('category','standalone') for r in records))},'records':records,'attribute_exports':{'historical':['designs/attribute-panels/01-character_2560x1080.png','designs/attribute-panels/02-pet_2560x1080.png','designs/attribute-panels/index.html','designs/attribute-panels/assets/','designs/attribute-panels/v2-painted/01-character-ui.png','designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','designs/attribute-panels/v2-painted/02-pet-ui.png','designs/attribute-panels/v2-painted/index.html'],'current':['designs/attribute-panels/v2-painted/unity-slices/ 31 formal sprites','designs/attribute-panels/v10-preview/assets/ 22 byte copies','designs/attribute-panels/v10-preview/01-character_2560x1080.png','designs/attribute-panels/v10-preview/02-pet_2560x1080.png','designs/attribute-panels/v10-preview/mobile-character.png','designs/attribute-panels/v10-preview/mobile-pet.png','designs/attribute-panels/v10-preview/index.html'],'evidence':['designs/attribute-panels/README.md first paragraph explicitly preserves old root HTML and whole-screen drafts as history','designs/attribute-panels/v2-painted/README.md calls baked words/numbers historical art effect drafts and old static/interactive previews unsynchronized v10','designs/attribute-panels/v10-preview/README.md current interactive entry and browser screenshots; do not paint screenshots'],'action':'Keep old drafts/reference assets unchanged. Current formal sprites propagate to v10-preview copies then rerender browser evidence when sources change.'},'old_hero_frames_note':'No old movement frame rows exist among these 220 inventory pending entries. Client-only animation strips in assets_manifest preserved_reason are historical/client inventory, not repository prepared images; no client was inspected.','errors':errors,'limitations':['This review tests source-derived pixel consistency, not independent visual approval of every item or logo.','Snapshots may be superseded by concurrently authorized hero RGB repair; pending_final_hero_source_refresh records require rebuilding after final source publication.','Existing client statuses, failures and client hashes were only read as mapping context; no new client acceptance claimed.']}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'summary':report['summary'],'errors':errors},ensure_ascii=False))
