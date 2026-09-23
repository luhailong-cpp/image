"""Create the byte-bound final 05 delivery after explicit offline review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3]
C=R/'qdao_original_roster_v14_hd/recovery-20260921'
P=C/'05-delivery-preview'
S=P/'revisions/complete-review-v1'
F=P/'final'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not F.exists(),'Final already exists'
m=read(S/'manifest.json')
review=read(C/'05-audit/OFFLINE-REVIEW-20260923.json')
assert review['all_walk_and_idle_accepted'] and not review['blocking_issues']
assert sha(S/'manifest.json')==review['reviewed_manifest_sha256']
sel=read(P/'selected-overrides.json')
for row in m['files']:
 key=row['path']; source=S/'runtime'/key; dest=F/'runtime'/key
 assert sha(source)==row['sha256']
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 if key in sel['overrides']: row['selected_revision']=sel['overrides'][key]['selected_revision']
 historical=row['source']; row['historical_selected_source']=historical
 row['source']=str(dest);row['visual_status']='offline_accepted_with_nonblocking_notes'
 row['source_provenance_status']='verified_before_raw_cleanup'
 lineage=F/'lineage'/key.removesuffix('.png')
 lineage.mkdir(parents=True,exist_ok=True)
 evidence=[]
 records_file=Path(row['source_record_file']) if row.get('source_record_file') else None
 if records_file and records_file.exists():
  target=lineage/'frame-sources.json';shutil.copy2(records_file,target)
  evidence.append({'path':target.relative_to(F).as_posix(),'sha256':sha(target),'original_path':str(records_file)})
  row['historical_source_record_file']=str(records_file);row['source_record_file']=str(target)
 record=row.get('source_record') or {}
 candidates=[]
 if records_file and record.get('source',{}).get('path'):
  rawparent=records_file.parent.parent/Path(record['source']['path']).parent
  if rawparent.exists(): candidates.extend(p for p in rawparent.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.txt','.md'))
 hp=Path(historical)
 archive=next((p for p in hp.parents if (p/'raw.png.generation.json').exists()),None)
 if archive: candidates.extend(p for p in archive.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.txt','.md'))
 seen=set()
 for source_text in candidates:
  if source_text.name in seen: continue
  seen.add(source_text.name); target=lineage/source_text.name;shutil.copy2(source_text,target)
  evidence.append({'path':target.relative_to(F).as_posix(),'sha256':sha(target),'original_path':str(source_text)})
 sidecar={'schema':'qdao-final-png-lineage-v1','asset':key,'sha256':row['sha256'],'pixel_sha256':row['pixel_sha256'],'size':row['size'],'native_source_size':row.get('native_source_size'),'selected_revision':row['selected_revision'],'source_record':record,'historical_selected_source':historical,'evidence':evidence,'actual_model':'legacy_as_recorded' if row['preserved_v13'] else 'host-managed-unverified','actual_quality':'legacy_as_recorded' if row['preserved_v13'] else 'host-managed-unverified','operations':'byte_exact_copy_only','source_verified_before_cleanup':True,'raw_retention':'removed_after_final_reference_verification_by_user_request','offline_review':'../../../offline-review.json'}
 write(dest.with_suffix('.png.generation.json'),sidecar)
 assert sha(dest)==row['sha256']
portrait=R/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/portrait.png'
shutil.copy2(portrait,F/'runtime/portrait.png')
write(F/'runtime/portrait.png.generation.json',{'schema':'qdao-final-portrait-lineage-v1','sha256':sha(portrait),'size':[1024,1024],'operations':'byte_exact_copy_of_existing_official_portrait','historical_source':str(portrait),'design_source':'q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png','design_source_sha256':'f8cd360988a1d5d9b6aebb81d9868b5d4692aa520d7fcae1af9d525bf70e12f8','derivation':'Existing1024portrait verified exact LANCZOS resize of current4096 design; no newAI call','actual_model':'historical_unverified','actual_quality':'historical_unverified'})
spec=importlib.util.spec_from_file_location('preview05',P/'build_preview.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
(F/'preview').mkdir()
directions,gifs=mod.build_images(F,m['files'])
for d in directions.values(): d['visual_approval']=True
m.update({'schema':'qdao-05-final-delivery-v1','created_at_utc':datetime.now(timezone.utc).isoformat(),'revision':'final-20260923','status':'offline_accepted_with_nonblocking_notes','offline_accepted':True,'formal_approval':False,'client_integration':False,'unity_validation':False,'directions':directions,'gif_checks':gifs,'browser_dynamic_review':review['browser_dynamic_review'],'known_rework_slots':[],'review_notes':{'inspection':'素材及离线预览通过；保留旧512清晰度及轻微步态起伏说明，详见offline-review.json。'},'reviewed_prior_manifest_sha256':review['reviewed_manifest_sha256'],'portrait':{'path':'runtime/portrait.png','sha256':sha(F/'runtime/portrait.png')},'current_runtime_asset_count_including_portrait':137})
write(F/'manifest.json',m);write(F/'offline-review.json',review)
for name in ['FINAL-SOURCE-AUDIT-20260923.json','FINAL-SOURCE-AUDIT-20260923.md','FINAL-STATIC-NEIGHBOR-REVIEW.md']:
 shutil.copy2(C/'05-audit'/name,F/name)
html=mod.HTML
html=html.replace('此快照待验收，不代表美术批准或客户端验收。','素材与离线预览已通过（含非阻塞观察记录）；客户端接入及Unity验收未执行。')
html=html.replace(' · 待验收 · 浏览器动态验收未记录',' · 离线验收通过 · 客户端未接入')
compact={**m,'files':[{k:v for k,v in r.items() if k!='source_record'} for r in m['files']]}
html=html.replace('__MANIFEST__',json.dumps(compact,ensure_ascii=False).replace('<','\\u003c'))
(F/'index.html').write_text(html,encoding='utf-8')
(P/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=final/index.html"><a href="final/index.html">05 天音少女最终素材与八方向预览</a>',encoding='utf-8')
readme="""# 05 天音少女最终交付

动作成品在 runtime/walk 和 runtime/idle；128张行走、8张独立站立，另runtime/portrait.png为正式1024肖像。index.html可离线打开，提供八方向30ms循环、逐帧、深浅底与512/1024显示。preview含各方向深浅底GIF、16帧总览和15→16→01→02接缝图。

素材与离线验收通过，非阻塞观察见offline-review.json；客户端接入、Unity运行验收、正式发布均未执行。manifest.json为当前路径和SHA权威清单。不要把frame数量或source审计单独当作视觉验收。

方向顺序：N/NE/E/SE/S/SW/W/NW。每方向walk/01.png–16.png，30毫秒每帧、480毫秒一圈。idle每方向独立一张，禁止拿walk代替。

60张既有512PNG保持原字节；76张高清PNG为1024透明RGBA，67本轮新选用加9既有NE。新动作均来自1254原生完整单帧，不包含镜像、插值或复制补帧。显示同世界尺寸时512的PPU=52、1024的PPU=104。alpha>8最后可见脚底行：旧512为471、新1024为942，身体轴分别256/512；逐图实测anchor以manifest为准。不要把旧512保存成1024冒充高清。

逐图png.generation.json和lineage保留模型/质量/请求/提示词/回执/来源SHA文字证据。实际内置工具没有披露型号或质量，不能声称锁定配置目标。收费API调用0。历史来源路径只用于追溯；原图、拒稿、回退和处理图在最终核验后按用户要求删除，删源前76张HD独立像素重建全部通过。

当前4096角色设计保留在仓库q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png。本目录不含其他角色。
"""
(F/'README.md').write_text(readme,encoding='utf-8')
write(F/'FINAL-BINDING.json',{'reviewed_snapshot_manifest_sha256':review['reviewed_manifest_sha256'],'final_manifest_sha256':sha(F/'manifest.json'),'matched_action_files':len(m['files']),'all_action_pngs_byte_exact':all(sha(F/'runtime'/r['path'])==r['sha256'] for r in m['files']),'portrait_sha256':sha(F/'runtime/portrait.png'),'gif_count':len(gifs)})
print(json.dumps({'final':str(F),'walk':128,'idle':8,'portrait':1,'gif':len(gifs),'binding':read(F/'FINAL-BINDING.json')},ensure_ascii=False))
