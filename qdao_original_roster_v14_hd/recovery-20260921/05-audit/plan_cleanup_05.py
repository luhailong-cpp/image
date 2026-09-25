"""Read-only inventory; writes JSON/Markdown plans, never removes or moves files."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import hashlib,json,re,subprocess,os
ROOT=Path(__file__).resolve().parents[3]
REC=ROOT/'qdao_original_roster_v14_hd/recovery-20260921'
HERE=Path(__file__).resolve().parent
CHAR='05_celestial_musician_girl'
FINAL=REC/'05-delivery-preview/revisions/complete-review-v1'
V13=ROOT/'qdao_original_roster_v13/candidate'/CHAR
PORTRAIT=ROOT/'q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png'
MEDIA={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.avif'}
TEXT={'.json','.md','.txt','.py','.html','.js','.ts','.cs','.yaml','.yml','.toml'}
def norm(v):return str(v).replace('\\','/').lower()
hashcache={}
def sha(p):
 k=str(p)
 if k not in hashcache:
  with Path(p).open('rb') as f:hashcache[k]=hashlib.file_digest(f,'sha256').hexdigest()
 return hashcache[k]
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def own(p):
 r=rel(p);parts=r.split('/')
 return CHAR in r or (r.startswith('qdao_original_roster_v14_hd/recovery-20260921/') and len(parts)>2 and parts[2].startswith('05-'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[ROOT/s for s in subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','!.git/**','-g','!**/node_modules/**','-g','!**/__pycache__/**'],cwd=ROOT,text=True,encoding='utf-8').splitlines()]
print(json.dumps({'stage':'allpaths','count':len(paths)}),flush=True)
owned=[p for p in paths if own(p) and p.is_file()]
images=sorted([p for p in owned if p.suffix.lower() in MEDIA])
print(json.dumps({'stage':'owned','count':len(owned),'images':len(images)}),flush=True)
assert all(p.resolve().is_relative_to(ROOT.resolve()) for p in images)
print('workspaceContainmentChecked',flush=True)
manifest=json.loads((FINAL/'manifest.json').read_text(encoding='utf-8-sig'))
assert manifest['actual_walk']==128 and manifest['actual_idle']==8
finalrows=manifest['files'];assert len(finalrows)==136
selected=defaultdict(list);finalindex={};oldformal=set()
for r in finalrows:
 selected[norm(r['source'])].append(r['path']);p=FINAL/'runtime'/r['path'];assert p.is_file() and sha(p)==r['sha256'];finalindex[r['sha256']]=rel(p)
 if r['preserved_v13']:oldformal.add(norm(r['source']))
assert len(oldformal)==60
print('final136HashesChecked',flush=True)
imagekeys={norm(p):p for p in images}
references=defaultdict(list);external=defaultdict(lambda:{'receiptFiles':set(),'boundRawFiles':set(),'expectedRawHashes':set()})
textargs=['rg','-l','--hidden','--no-ignore','-g','!.git/**','-g','!**/node_modules/**','-g','!**/__pycache__/**']
for ext in TEXT:textargs+=['-g','*'+ext]
textargs+=['-e',CHAR,'-e','05-generation','-e','05-audit','-e','05-delivery-preview','.']
matched={ROOT/s for s in subprocess.check_output(textargs,cwd=ROOT,text=True,encoding='utf-8').splitlines()}
matched.update(p for p in owned if p.suffix.lower() in TEXT)
globaltexts=[p for p in matched if p.is_file() and p.name not in {'CLEANUP-PLAN-20260923.json','CLEANUP-PLAN-20260923.md','plan_cleanup_05.py'}]
print(json.dumps({'stage':'inventory','ownedImages':len(images),'candidateTextFiles':len(globaltexts)}),flush=True)
def refer(p,value,field):
 if len(value)>1600 or not re.search(r'\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\?|$)',value,re.I):return
 value=value.split('?')[0].strip('<>')
 if not own(p) and not any(x in value for x in (CHAR,'05-generation','05-audit','05-delivery-preview')):return
 pp=Path(value)
 targets=[Path(os.path.abspath(pp))] if pp.is_absolute() else [Path(os.path.abspath(p.parent/pp)),Path(os.path.abspath(ROOT/pp))]
 for t in targets:
  key=norm(t)
  if key in imagekeys:
   kind='historical_text_or_source_provenance'
   if p==REC/'05-delivery-preview/selected-overrides.json':kind='current_builder_selection'
   elif p.parent==REC/'05-generation' and 'selection' in p.name:kind='current_direction_selection'
   elif p==FINAL/'index.html':kind='current_snapshot_embedded_source_history'
   elif p==FINAL/'manifest.json':kind='current_snapshot_source_history'
   elif p.suffix in {'.py','.js','.ts','.cs'}:kind='tool_or_code_reference_requires_inspection'
   elif p.suffix=='.html':kind='older_preview_or_html_reference'
   references[key].append({'file':rel(p),'field':field,'kind':kind});break
def walk(p,v,field=''):
 if isinstance(v,dict):
  for k,x in v.items():walk(p,x,field+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(p,x,field+f'[{i}]')
 elif isinstance(v,str):
  refer(p,v,field)
  if own(p) and ('receipt' in p.name or 'tool-result' in p.name):
   for match in re.findall(r'[A-Za-z]:[\\/][^:\r\n"<>]+?\.png',v):
    if '/generated_images/' not in norm(match):continue
    ep=Path(match);key=norm(ep);e=external[key];e['path']=str(ep);e['receiptFiles'].add(rel(p))
    raw=p.parent/'raw.png'
    if raw.is_file():e['boundRawFiles'].add(rel(raw));e['expectedRawHashes'].add(sha(raw))
scan_count=0
for p in globaltexts:
 try:text=p.read_text(encoding='utf-8-sig')
 except (UnicodeError,OSError):continue
 if not own(p) and not any(x in text for x in (CHAR,'05-generation','05-audit','05-delivery-preview')):continue
 scan_count+=1
 if scan_count%500==0:print(json.dumps({'stage':'text_refs','scanned':scan_count}),flush=True)
 if p.suffix=='.json':
  try:walk(p,json.loads(text));continue
  except json.JSONDecodeError:pass
 for value in re.findall(r'(?:src|href)=["\']([^"\']+)["\']|\]\(([^)]+)\)|["\']([^"\'\r\n]+\.(?:png|jpg|jpeg|webp|gif))["\']',text,re.I):
  refer(p,next(x for x in value if x),'text_link_or_literal')
rows=[];groups=Counter();bytes_by_group=Counter()
for p in images:
 r=rel(p);key=norm(p);h=sha(p);refs=references[key];slots=selected.get(key,[])
 if key==norm(PORTRAIT):disposition='PROTECT';reason='current4096portrait'
 elif key in oldformal:disposition='PROTECT';reason='existing_v13_52walk_8idle'
 elif p.is_relative_to(FINAL):disposition='PROTECT_UNTIL_FINAL_NAME_BOUND';reason='current_complete136_and_companion_preview'
 elif slots:disposition='DELETE_AFTER_FINAL_REBIND';reason='current_selected_intermediate_export_byte_exact_in_complete_review'
 elif 'qdao_original_roster_v13/baseline/' in r:disposition='HOLD_REFERENCE_CONTRACT_REVIEW';reason='baseline_portrait_not_current_original_but_shared_baseline_contract'
 elif '/walk/' in r and p.name=='strip.png':disposition='HOLD_REFERENCE_CONTRACT_REVIEW';reason='v13_direction_strip_optional_integration_use_not_proven_unused'
 elif '/candidate/'+CHAR+'/walk/' in r and 'recovery-' not in r:disposition='DELETE_AFTER_FINAL_REBIND';reason='old_v14_candidate_frame_superseded_or_copied_into_complete_review'
 elif p.name=='raw.png' or '/source/' in r or '/generation/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='generation_original_or_source_copy'
 elif '/processing/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='processing_intermediate_or_reconstruction_copy'
 elif '/references/' in r or '/references-' in r or '/accepted-key-references/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='derived_generation_reference'
 elif '/05-delivery-preview/revisions/' in r:disposition='DELETE_AFTER_FINAL_REBIND';reason='superseded_ne_review_snapshot_or_preview'
 elif '/review/' in r or '/review-' in r or '-review/' in r or '/05-audit/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='old_review_preview_or_evidence_shadow'
 elif '/staging/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='unselected_attempt_export_or_review'
 elif '/05-generation/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='05_generation_work_image_not_current_selected_runtime'
 elif '/05-tools/' in r:disposition='DELETE_AFTER_FINAL_ACCEPTANCE';reason='05_tool_debug_or_work_image'
 else:disposition='HOLD_REFERENCE_CONTRACT_REVIEW';reason='purpose_requires_manual_verification'
 if r.startswith('designs/'):disposition='PROTECT';reason='current_confirmed_design'
 outside_refs=[x for x in refs if CHAR not in x['file'] and '/05-' not in x['file']]
 if disposition.startswith('DELETE_') and any(x['kind'] in {'tool_or_code_reference_requires_inspection','older_preview_or_html_reference'} for x in outside_refs):disposition='HOLD_SHARED_CONSUMER_REVIEW';reason='shared_code_or_html_image_reference_requires_rebinding_first'
 digestrefs={(x['file'],x['field'],x['kind']):x for x in refs}
 row={'path':str(p.resolve()),'relativePath':r,'sha256':h,'bytes':p.stat().st_size,'workspaceContained':True,'proposedDisposition':disposition,'reason':reason,'currentSelectedSlots':slots,'byteExactCurrentFinalCopy':finalindex.get(h),'currentConsumerReferences':[x for x in digestrefs.values() if x['kind'].startswith('current_') or x['kind']=='tool_or_code_reference_requires_inspection'],'historicalReferenceCount':sum(x['kind'].startswith('historical_') for x in digestrefs.values()),'otherCharacterOrSharedReferences':outside_refs,'referenceExamples':list(digestrefs.values())[:8]}
 rows.append(row);groups[disposition]+=1;bytes_by_group[disposition]+=row['bytes']
externalrows=[]
for key,e in sorted(external.items()):
 p=Path(e['path']);exists=p.is_file();currenthash=sha(p) if exists else None
 externalrows.append({'path':str(p),'workspaceContained':p.resolve().is_relative_to(ROOT.resolve()),'existsNow':exists,'sha256':currenthash,'expectedRawHashes':sorted(e['expectedRawHashes']),'matchesBoundRaw':currenthash in e['expectedRawHashes'] if exists else None,'bytes':p.stat().st_size if exists else None,'receiptFiles':sorted(e['receiptFiles']),'boundRawFiles':sorted(e['boundRawFiles']),'proposedDisposition':'EXTERNAL_PERMISSION_REQUIRED_AFTER_FINAL_ACCEPTANCE' if exists else 'HISTORICAL_PATH_MISSING_DO_NOT_GUESS_REMAP','deleteScope':'this_exact_file_only_never_parent_directory'})
plan={'schema':'qdao-05-cleanup-plan-v1','createdAt':datetime.now(timezone.utc).isoformat(),'mode':'PLAN_ONLY_NO_FILES_DELETED','workspace':str(ROOT),'character':CHAR,'scopeMethod':'all rg --files --hidden --no-ignore paths with exact05character identity or recovery/05-* directory; filename05.png alone never qualifies','finalSnapshot':{'path':str(FINAL),'manifestSha256':sha(FINAL/'manifest.json'),'status':manifest['status'],'walk':128,'idle':8,'finalNamePending':True,'runtimeConsumer':'index.html loads only runtime/<manifest slot>.png; provenance source fields are display/history, not runtime image loads'},'mustKeep':['all136 final game PNG plus chosen companion design/preview/integration files','all text prompts, requests, receipts, provenance, model/quality/hash records, and cleanup tombstones','current q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png','all designs confirmed style references','the60 existing V13 canonical action PNG','all other characters and all shared files'], 'preconditions':['Parent completes art/30ms-loop acceptance and assigns final package path.','Verify final136 against source SHA and preserve companion files actually linked from final HTML.','Rebind current selected-overrides/directionselection references to final files or explicitly mark them historical and superseded; never falsify original generation request/reference history.','Recheck every exact listed path andSHA immediately before deletion; do not recursively delete directories or delete text records.','For historical sources removed, retain original pathname/hash and append deletion status; mark source-dependent rebuild tools as unavailable rather than promising pixel reconstruction.','Resolve HOLD_REFERENCE_CONTRACT_REVIEW entries before including them in any deletion.','External generated_images entries require an authorized filesystem escalation per concrete file; missing historical host paths are not deletion targets.'],'counts':dict(groups),'bytesByDisposition':dict(bytes_by_group),'ownedImageCount':len(rows),'textFilesPreserved':sum(p.suffix.lower() in TEXT for p in owned),'globalTextFilesInspected':scan_count,'workspaceFiles':rows,'externalOriginals':externalrows,'externalSummary':{'count':len(externalrows),'existsNow':sum(x['existsNow'] for x in externalrows),'missingHistoricalPaths':sum(not x['existsNow'] for x in externalrows)},'deletionPerformed':False}
write(HERE/'CLEANUP-PLAN-20260923.json',plan)
lines=['# 05 天音少女清理计划（只规划，未删除）','',f'核对时间：{plan["createdAt"]}。当前保护快照 `05-delivery-preview/revisions/complete-review-v1` 已逐项SHA核对128walk+8idle；最终命名与美术验收仍由主代理完成。','',f'05独占图片共{len(rows)}个；文字记录全部保留。完整逐路径、SHA、引用与宿主原图清单见 [JSON](CLEANUP-PLAN-20260923.json)。','','| 处置 | 图片数 | MiB |','|---|---:|---:|']
for k,n in groups.items():lines.append(f'| {k} | {n} | {bytes_by_group[k]/1024**2:.2f} |')
lines+=['','当前预览仅读取自身 `runtime/` 的136张图；`selected-overrides.json`和方向selection仍引用stage，清理前要重新绑定最终包或标注历史。不能把原图删除后仍写成可重新进行像素重建。','',f'宿主generated_images回执路径共{len(externalrows)}个，其中现存{sum(x["existsNow"] for x in externalrows)}个；逐个文件单列，不授权整目录删除。旧用户/旧盘符缺失路径仅作历史记录，不猜测映射。','','明确保护：现有V13的52walk+8idle、当前4096肖像、designs风格设计及全部其他角色。旧V13方向strip与基线肖像单列HOLD，需实际接入契约核实后才能清理。','','执行前：先最终验收、定名并逐项核对136张；保留最终设计/预览/接入引用；仅删列出的图片，不删JSON/MD/txt等文字来源；逐文件重新检查绝对路径包含关系和SHA，外部宿主原图按具体路径走权限流程。']
(HERE/'CLEANUP-PLAN-20260923.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'ownedImages':len(rows),'counts':dict(groups),'externalSummary':plan['externalSummary'],'textFilesInspected':scan_count,'plan':str(HERE/'CLEANUP-PLAN-20260923.json')},ensure_ascii=False))
