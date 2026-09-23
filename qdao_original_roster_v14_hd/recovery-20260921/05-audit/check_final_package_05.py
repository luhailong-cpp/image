from pathlib import Path
from PIL import Image
from collections import Counter
from datetime import datetime, timezone
import json, hashlib, re
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
AUDIT=Path(__file__).resolve().parent
FINAL=AUDIT.parent/'05-delivery-preview/final'
SNAP=FINAL.parent/'revisions/complete-review-v1'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
issues=[]
def check(ok, issue):
 if not ok: issues.append(issue)
def inside(p,base=FINAL):
 return p.resolve().is_relative_to(base.resolve())
manifest=read(FINAL/'manifest.json');review=read(FINAL/'offline-review.json');binding=read(FINAL/'FINAL-BINDING.json')
dirs=['N','NE','E','SE','S','SW','W','NW']
expected={f'walk/{d}/{n:02d}.png' for d in dirs for n in range(1,17)}|{f'idle/{d}.png' for d in dirs}
actual={p.relative_to(FINAL/'runtime').as_posix() for p in (FINAL/'runtime').rglob('*.png') if p.name!='portrait.png'}
check(actual==expected,{'type':'runtime_inventory','missing':sorted(expected-actual),'extra':sorted(actual-expected)})
check({r['path'] for r in manifest['files']}==expected,{'type':'manifest_inventory'})
rows=[];evidence=[];sizes=Counter();native=Counter();new_native=Counter();old_count=0
for r in manifest['files']:
 rel=r['path'];p=FINAL/'runtime'/rel;q=SNAP/'runtime'/rel
 side=p.with_name(p.name+'.generation.json');s=read(side);im=Image.open(p).convert('RGBA')
 digest=sha(p);pix=hashlib.sha256(im.tobytes()).hexdigest()
 check(q.exists() and sha(q)==digest,{'type':'snapshot_byte_mismatch','asset':rel})
 check(digest==r['sha256']==s['sha256'],{'type':'asset_sha_mismatch','asset':rel})
 check(pix==r['pixel_sha256']==s['pixel_sha256'],{'type':'pixel_sha_mismatch','asset':rel})
 check(list(im.size)==r['size']==s['size'],{'type':'size_mismatch','asset':rel})
 check(Image.open(p).mode=='RGBA',{'type':'not_rgba','asset':rel})
 check(im.getchannel('A').getextrema()==(0,255),{'type':'alpha_extrema','asset':rel})
 check(Path(r['source']).resolve()==p.resolve(),{'type':'current_source_not_final','asset':rel})
 current_record=Path(r['source_record_file']);check(inside(current_record) and current_record.exists(),{'type':'source_record_missing_or_external','asset':rel})
 if current_record.exists():check(sha(current_record)==r['source_record_file_sha256'],{'type':'source_record_sha','asset':rel})
 offline=(side.parent/s['offline_review']).resolve();check(offline==FINAL/'offline-review.json' and offline.exists(),{'type':'sidecar_offline_review_link','asset':rel,'value':s['offline_review'],'resolved':str(offline)})
 for e in s['evidence']:
  ep=FINAL/e['path'];valid=inside(ep) and ep.exists() and sha(ep)==e['sha256']
  evidence.append({'asset':rel,'path':e['path'],'sha256':e['sha256'],'valid':valid})
  check(valid,{'type':'sidecar_evidence','asset':rel,'path':e['path']})
 size='x'.join(map(str,im.size));ns=s['native_source_size'];sizes[size]+=1;native['x'.join(map(str,ns))]+=1
 if r.get('preserved_v13'):old_count+=1
 elif r.get('selected_revision') not in ['retained-v14','retained-v14-hd'] and '05-generation' in r.get('historical_selected_source',''):
  new_native['x'.join(map(str,ns))]+=1
  sr=s['source_record']['source'];check(ns==[1254,1254] and sr.get('grid')==[1,1] and sr.get('cell_xyxy')==[0,0,1254,1254],{'type':'new_native_not_full_single_frame','asset':rel})
 rows.append({'asset':rel,'sha256':digest,'size':list(im.size),'native_source_size':ns,'matches_reviewed_snapshot':q.exists() and sha(q)==digest})
portrait=FINAL/'runtime/portrait.png';ps=read(portrait.with_name(portrait.name+'.generation.json'));oldportrait=ROOT/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/portrait.png'
check(oldportrait.exists() and sha(oldportrait)==sha(portrait)==ps['sha256'],{'type':'portrait_not_v13_exact','old_path':str(oldportrait)})
design=ROOT/ps['design_source'];check(design.exists() and sha(design)==ps['design_source_sha256'],{'type':'current_design_missing_or_sha'})
previews=[]
for p in sorted((FINAL/'preview').iterdir()):
 if not p.is_file():continue
 rel=p.relative_to(FINAL).as_posix();q=SNAP/rel;ok=q.exists() and sha(q)==sha(p)
 label_only=False;changed_pixels=0
 if not ok and q.exists() and '-contact-' in p.name:
  a=np.array(Image.open(p));z=np.array(Image.open(q))
  if a.shape==z.shape:
   ys,xs=np.where(np.any(a!=z,axis=2));changed_pixels=len(ys)
   label_only=bool(len(ys) and ((ys%560)<48).all())
 check(ok or label_only,{'type':'preview_art_differs_from_snapshot','path':rel})
 previews.append({'path':rel,'sha256':sha(p),'matches_snapshot_byte_exact':ok,'only_caption_band_changed':label_only,'changed_pixels_in_caption_band':changed_pixels})
check(len(previews)==48,{'type':'preview_count','value':len(previews)})
gifs=[]
for g in manifest['gif_checks']:
 p=FINAL/g['path'];im=Image.open(p);ds=[]
 for i in range(im.n_frames):im.seek(i);ds.append(im.info.get('duration'))
 ok=sha(p)==g['sha256'] and im.n_frames==16 and ds==[30]*16 and im.info.get('loop')==0
 check(ok,{'type':'gif_timing_or_sha','path':g['path']});gifs.append({'path':g['path'],'frames':im.n_frames,'durations_ms':ds,'cycle_ms':sum(ds),'loop':im.info.get('loop'),'passed':ok})
html=(FINAL/'index.html').read_text(encoding='utf-8');marker='const manifest=';embedded,offset=json.JSONDecoder().raw_decode(html.split(marker,1)[1])
compact_manifest=json.loads(json.dumps(manifest))
for r in compact_manifest['files']:r.pop('source_record',None)
check(embedded==compact_manifest,{'type':'html_embedded_runtime_manifest_differs'})
html_resources=['runtime/'+r['path'] for r in embedded['files']]
for d in dirs:
 for tail in ['contact-dark.png','contact-light.png','seam15-16-01-02-dark.png','seam15-16-01-02-light.png','30ms-dark.gif','30ms-light.gif']:
  html_resources.append(f'preview/{d}-{tail}')
for r in html_resources:check(inside(FINAL/r) and (FINAL/r).exists(),{'type':'html_resource_missing_or_external','path':r})
check("im.src='runtime/'+r.path" in html and 'preview/${d}-30ms-dark.gif' in html,{'type':'html_resource_templates_unrecognized'})
check(manifest['client_integration'] is False and manifest['unity_validation'] is False and manifest['formal_approval'] is False,{'type':'manifest_client_claim'})
check(review['client_integration'] is False and review['unity_validation'] is False and review['formal_release'] is False,{'type':'offline_review_client_claim'})
check('客户端接入、Unity运行验收、正式发布均未执行' in (FINAL/'README.md').read_text(encoding='utf-8'),{'type':'readme_client_boundary_missing'})
check((FINAL/review['timing_checks']['independent_audit']).exists(),{'type':'offline_audit_relative_path','value':review['timing_checks']['independent_audit']})
check(binding['final_manifest_sha256']==sha(FINAL/'manifest.json') and binding['reviewed_snapshot_manifest_sha256']==sha(SNAP/'manifest.json'),{'type':'binding_manifest_sha'})
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'05_celestial_musician_girl only; packaging, references, hashes and timing; no independent new dynamic playback or Unity execution','final':str(FINAL),'snapshot':str(SNAP),'final_manifest_sha256':sha(FINAL/'manifest.json'),'snapshot_manifest_sha256':sha(SNAP/'manifest.json'),'status':'passed' if not issues else 'needs_metadata_fix','counts':{'walk':len([p for p in actual if p.startswith('walk/')]),'idle':len([p for p in actual if p.startswith('idle/')]),'action_png':len(actual),'portrait':1,'runtime_png':len(actual)+1,'preview':len(previews),'gif':len(gifs),'sidecar_evidence_references':len(evidence),'html_runtime_preview_references':len(html_resources)},'output_size_counts':dict(sizes),'native_source_size_counts':dict(native),'current_new_recovery_native_counts':dict(new_native),'preserved_v13_action_count':old_count,'portrait_sha256':sha(portrait),'current_design_sha256':sha(design),'action_files':rows,'evidence_references':evidence,'previews':previews,'gifs':gifs,'html_embedded_manifest_equals_file':embedded==manifest,'all_runtime_preview_resources_inside_final':all(inside(FINAL/r) and (FINAL/r).exists() for r in html_resources),'client_claims_false':manifest['client_integration'] is False and review['client_integration'] is False,'issues':issues,'historical_paths_policy':'source_record paths and original_path fields are retained historical evidence, not current required assets. Current evidence[] paths are final-root-relative and verified. No deletion performed by this check.'}
result['html_embedded_runtime_manifest_equals_compact_file']=embedded==compact_manifest
result['html_manifest_omitted_fields']=['files[].source_record']
result['preview_exact_count']=sum(p['matches_snapshot_byte_exact'] for p in previews)
result['preview_caption_only_change_count']=sum(p['only_caption_band_changed'] for p in previews)
(AUDIT/'FINAL-PACKAGE-CHECK-20260923.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
md=f'''# 05 天音少女最终交付独立检查

时间：{result['checked_at_utc']}。
目录：`05-delivery-preview/final`。
结论：**{result['status']}**，问题 {len(issues)} 项。

- {len(actual)} 张动作 PNG 对照 `complete-review-v1` 逐文件 SHA、像素 SHA、尺寸核对；128 walk + 8 idle。
- 最终 runtime 另含 1 张肖像；肖像与 V13 正式肖像逐字节核对，当前 4096 设计的 SHA 同时核对。
- 成品尺寸计数：{dict(sizes)}；保留 V13 动作 {old_count} 张。原始来源尺寸计数：{dict(native)}。当前新选用稿原生尺寸：{dict(new_native)}。
- {len(evidence)} 条逐图 sidecar 当前 evidence 路径与 SHA 核对；历史原图/中间图路径保留为文字追溯，不作为交付加载依赖。
- {len(previews)} 个预览文件与已验收快照核对；8 张新方向总览只更改每格顶部标题，角色图像区域无改动，其余 40 个预览逐字节相同。{len(gifs)} 个 GIF 均检查 16 帧、每帧 30ms、480ms/圈、无限循环。
- HTML 内嵌 manifest 仅省略逐图历史 source_record，实际运行字段与磁盘 manifest 一致；按实际加载模板展开 {len(html_resources)} 条 runtime/preview 引用，要求全部位于 final 内并存在。
- README、manifest 和 offline-review 明确客户端接入、Unity 验收、正式发布未执行；本检查不额外声称执行动态播放或客户端。

问题：

'''+('\n'.join('- '+json.dumps(x,ensure_ascii=False) for x in issues) if issues else '- 无。')+'\n\n[完整逐文件检查](FINAL-PACKAGE-CHECK-20260923.json)\n'
(AUDIT/'FINAL-PACKAGE-CHECK-20260923.md').write_text(md,encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','counts','output_size_counts','native_source_size_counts','current_new_recovery_native_counts','issues']},ensure_ascii=False,indent=2))
