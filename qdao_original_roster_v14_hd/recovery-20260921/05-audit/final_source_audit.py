"""Read-only source audit; writes only its own final audit JSON and Markdown."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
from PIL import Image
import numpy as np
A=Path(__file__).resolve().parent;R=A.parents[2];P=R/'qdao_original_roster_v14_hd';G=A.parent/'05-generation'
S=A.parent/'05-delivery-preview/revisions/complete-review-v1';CHAR='05_celestial_musician_girl'
DIRS=['N','NE','E','SE','S','SW','W','NW']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def info(p):
 p=Path(p);d={'path':str(p),'exists':p.is_file()}
 if d['exists']:d['sha256']=sha(p)
 return d
def binding(p,expected):
 d=info(p);d['expectedSha256']=expected;d['shaMatches']=d.get('sha256')==expected
 if d['exists'] and not d['shaMatches']:
  b=Path(p).read_bytes();lf=b.replace(b'\r\n',b'\n');d['historicalLineEndingOnly']=expected in {hashlib.sha256(lf).hexdigest(),hashlib.sha256(lf.replace(b'\n',b'\r\n')).hexdigest()}
 return d
def require(test,issues,name):
 if not test:issues.append(name)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def reconstruct(row):
 candidate=Path(row['candidate']);parts=row['path'].split('/');d,n=parts[1],int(Path(parts[2]).stem)
 historical=row['classification']=='retained_hd_ne'
 stage=A/'evidence-shadow' if historical else candidate.parent.parent
 verifier=module('audit_verify_'+d+str(n),P/'tools/verify.py');verifier.ROOT=stage
 verifier.mod=lambda name:module('audit_vendor_'+d+str(n)+name,P/'tools/vendor'/f'{name}.py')
 try:result=verifier.verify(CHAR,d,False,n)
 except Exception as e:result={'status':'failed','error':str(e)}
 result['usedExistingHistoricalShadow']=historical;result['sourceStage']=str(stage)
 return row['path'],result
manifest=read(S/'manifest.json');before=sha(S/'manifest.json');rows=[];global_issues=[];warnings=[]
expected={*[f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)],*[f'idle/{d}.png' for d in DIRS]}
require(len(manifest['files'])==136 and {x['path'] for x in manifest['files']}==expected,global_issues,'manifest_inventory_not_128_walk_8_idle')
require({str(p.relative_to(S/'runtime')).replace('\\','/') for p in (S/'runtime').rglob('*.png')}==expected,global_issues,'runtime_inventory_differs')
for f in manifest['files']:
 key=f['path'];source=Path(f['source']);candidate=Path(f['source_record_file']).parent.parent;rec=f['source_record'];issues=[];advisories=[]
 fresh=source.is_relative_to(G);classification='new_recovery' if fresh else 'preserved_v13' if f['preserved_v13'] else 'retained_hd_ne'
 out=S/'runtime'/key
 with Image.open(out) as im:
  image=im.convert('RGBA');actual={'format':im.format,'mode':im.mode,'size':list(im.size),'sha256':sha(out),'pixelSha256':hashlib.sha256(image.tobytes()).hexdigest(),'alphaExtrema':list(image.getchannel('A').getextrema())}
 require(actual['format']=='PNG' and actual['mode']=='RGBA',issues,'output_not_rgba_png')
 require(actual['size']==f['size']==([512,512] if f['preserved_v13'] else [1024,1024]),issues,'output_size_mismatch')
 require(actual['sha256']==f['sha256']==sha(source)==rec['output_sha256'],issues,'final_sha_mismatch')
 require(actual['pixelSha256']==f['pixel_sha256'],issues,'final_pixel_sha_mismatch')
 require(actual['alphaExtrema']==[0,255],issues,'output_alpha_range')
 map_binding=binding(f['source_record_file'],f['source_record_file_sha256']);require(map_binding['shaMatches'],issues,'manifest_source_mapping_file_mismatch')
 require(read(f['source_record_file']).get(key)==rec,issues,'embedded_source_record_differs')
 b={label:binding(candidate/value['path'],value['sha256']) for label,value in [('raw',rec['source']),('prompt',rec['prompt']),('receipt',rec['generation']['receipt'])]}
 for label,value in b.items():
  if not value['exists']:issues.append(label+'_missing')
  elif not value['shaMatches']:
   if classification!='new_recovery' and value.get('historicalLineEndingOnly'):advisories.append(label+'_historical_LF_CRLF_hash_difference')
   else:issues.append(label+'_sha_mismatch')
 stages={name:binding(candidate/value['path'],value['sha256']) for name,value in rec.get('stages',{}).items()}
 require(len(stages)==5 and all(x['shaMatches'] for x in stages.values()),issues,'processing_stages_missing_or_changed')
 rawpath=Path(b['raw']['path']);rawinfo={}
 if rawpath.is_file():
  with Image.open(rawpath) as raw:rawinfo={'size':list(raw.size),'mode':raw.mode,'format':raw.format}
  require(rawinfo['size']==rec['source']['native_size'],issues,'raw_native_dimensions_changed')
  if not f['preserved_v13']:require(min(rawinfo['size'])>=1024 and rec['source']['grid']==[1,1],issues,'HD_not_native_complete_single_frame')
 receipt=read(b['receipt']['path']) if b['receipt']['exists'] else {};request=receipt.get('actual_request',{})
 prompt_exact=Path(b['prompt']['path']).read_bytes()==request.get('prompt','').encode('utf-8') if b['prompt']['exists'] else False
 archive_info={}
 if fresh:
  archive=source.parents[5];archive_info={'path':str(archive),'selectedRevisionLabel':f['selected_revision'],'actualArchiveName':archive.name}
  if f['selected_revision']!=archive.name:advisories.append('known_selected_revision_display_label_staging')
  required=['raw.png','prompt.txt','request.json','generation-receipt.json','tool-result.json','provenance.json','raw.png.generation.json']
  archive_info['files']={name:info(archive/name) for name in required}
  require(all(x['exists'] for x in archive_info['files'].values()),issues,'archive_evidence_missing')
  require(sha(archive/'raw.png')==b['raw'].get('sha256'),issues,'archive_raw_differs_from_import')
  require(sha(archive/'prompt.txt')==b['prompt'].get('sha256'),issues,'archive_prompt_differs_from_import')
  require(sha(archive/'generation-receipt.json')==b['receipt'].get('sha256'),issues,'archive_receipt_differs_from_import')
  require(prompt_exact,issues,'exact_prompt_does_not_match_actual_request')
  meta=read(archive/'raw.png.generation.json');req=read(archive/'request.json');tool=read(archive/'tool-result.json')
  require(req.get('actual_request',{}).get('prompt')==request.get('prompt') and req['actual_request'].get('referenced_image_paths')==request.get('referenced_image_paths'),issues,'request_receipt_disagree')
  require(meta['sha256']==b['raw'].get('sha256') and [meta['width'],meta['height']]==rawinfo['size'],issues,'raw_generation_metadata_mismatch')
  require(bool(meta.get('generatedAt')) and bool(meta.get('configSnapshot')),issues,'time_or_config_snapshot_missing')
  require(meta.get('submittedParameters')=={'model':None,'quality':None} and meta.get('actualModel') is None and meta.get('actualQuality') is None and bool(meta.get('unverifiedReason')),issues,'unverified_model_quality_not_explicit')
  require(receipt.get('output_hint')==tool.get('output_hint') and receipt.get('original_generated_file') in tool.get('output_hint',''),issues,'tool_result_receipt_binding_bad')
  require(meta.get('paidApiCalls')==0 and receipt.get('paid_api_calls')==0,issues,'paid_api_not_zero_recorded')
  archive_info['metadataSummary']={k:meta.get(k) for k in ['generatedAt','generatedAtBasis','configSnapshotEvidence','submittedParameters','actualModel','actualQuality','unverifiedReason','generationCalls','paidApiCalls']}
  archive_info['referenceBindings']=[binding(x['path'],x['sha256']) for x in meta.get('references',[]) if 'sha256' in x]
  require(archive_info['referenceBindings'] and all(x['shaMatches'] for x in archive_info['referenceBindings']),issues,'reference_images_missing_or_changed_before_cleanup')
  validation=candidate/f'review/validation-{rec["direction"]}-{rec["frame"]:02d}.json';archive_info['priorReconstruction']=info(validation)
  if validation.is_file():
   v=read(validation);archive_info['priorReconstruction']['record']=v
   require(v.get('reconstructed_frames')==1 and v.get('synthetic_frames_created')==0 and not v.get('missing_generation_receipts') and v.get('native_resolution',{}).get('upscaled_frames')==0,issues,'prior_reconstruction_failed_or_incomplete')
   require(v.get('manifest_sha256')==sha(candidate/'manifest.json') and v.get('qc_sha256')==sha(candidate/'qc.json'),issues,'prior_reconstruction_binding_changed')
  else:issues.append('prior_reconstruction_record_missing')
 row={'path':key,'classification':classification,'candidate':str(candidate),'final':actual,'manifestSha256':f['sha256'],'sourceMappingFile':map_binding,'sourceBindings':b,'rawNative':rawinfo,'sourceCell':rec['source'],'promptExactRequestBytes':prompt_exact,'processingStages':stages,'archive':archive_info,'issues':issues,'advisories':advisories}
 rows.append(row)
print('File/source binding inspection complete',len(rows),flush=True)
newrows=[r for r in rows if r['classification']!='preserved_v13']
with ThreadPoolExecutor(max_workers=4) as pool:
 jobs={pool.submit(reconstruct,r):r for r in newrows}
 for i,fut in enumerate(as_completed(jobs),1):
  key,result=fut.result();row=jobs[fut];row['freshReadOnlyReconstruction']=result
  if result.get('reconstructed_frames')!=1 or result.get('status')!='partial_sources_pending_visual':row['issues'].append('fresh_independent_reconstruction_failed')
  if i%8==0 or i==len(jobs):print('Reconstructed',i,'/',len(jobs),key,result['status'],flush=True)
walk=[r for r in rows if r['path'].startswith('walk/')];idle=[r for r in rows if r['path'].startswith('idle/')]
idle_results=[]
for r in idle:
 cell=(r['sourceCell']['sha256'],tuple(r['sourceCell']['cell_xyxy']))
 v={'path':r['path'],'uniqueFromEveryWalkPixel':r['final']['pixelSha256'] not in {w['final']['pixelSha256'] for w in walk},'sourceCellNotReusedByWalk':cell not in {(w['sourceCell']['sha256'],tuple(w['sourceCell']['cell_xyxy'])) for w in walk}}
 require(all(v[k] for k in ['uniqueFromEveryWalkPixel','sourceCellNotReusedByWalk']),global_issues,'idle_reuses_walk:'+r['path']);idle_results.append(v)
require(len({r['final']['pixelSha256'] for r in idle})==8,global_issues,'idle_pixels_not_eight_unique')
direction_results={d:{'count':sum(r['path'].split('/')[1]==d for r in walk),'uniquePixels':len({r['final']['pixelSha256'] for r in walk if r['path'].split('/')[1]==d})} for d in DIRS}
require(all(v=={'count':16,'uniquePixels':16} for v in direction_results.values()),global_issues,'direction_count_or_unique_frame_failure')
fresh=[r for r in rows if r['classification']=='new_recovery'];require(len({r['sourceCell']['sha256'] for r in fresh})==len(fresh)==67,global_issues,'new_sources_not_67_distinct_raws')
gifs=[]
for p in sorted((S/'preview').glob('*.gif')):
 with Image.open(p) as gif:
  durations=[]
  for i in range(gif.n_frames):gif.seek(i);durations.append(gif.info.get('duration'))
  record={'path':str(p),'sha256':sha(p),'frameCount':gif.n_frames,'durationsMs':durations,'cycleMs':sum(durations),'loop':gif.info.get('loop')}
 require(record['frameCount']==16 and record['durationsMs']==[30]*16 and record['cycleMs']==480 and record['loop']==0,global_issues,'gif_timing_failure:'+p.name);gifs.append(record)
require(len(gifs)==16,global_issues,'gif_count_not_16')
require(sha(S/'manifest.json')==before,global_issues,'snapshot_manifest_changed_during_audit')
issues=[{'path':r['path'],'issues':r['issues']} for r in rows if r['issues']]
summary={'runtimeFrames':len(rows),'walk':len(walk),'idle':len(idle),'dimensions':dict(Counter('x'.join(map(str,r['final']['size'])) for r in rows)),'classification':dict(Counter(r['classification'] for r in rows)),'selectedNewRawDistinct':len({r['sourceCell']['sha256'] for r in fresh}),'freshIndependentReconstructionsPassed':sum(r.get('freshReadOnlyReconstruction',{}).get('reconstructed_frames')==1 for r in rows),'gifCount':len(gifs),'gifFrameMs':30,'gifCycleMs':480,'knownStagingLabelCount':sum('known_selected_revision_display_label_staging' in r['advisories'] for r in rows),'historicalNewlineAdvisoryRows':sum(any('LF_CRLF' in a for a in r['advisories']) for r in rows),'rowIssueCount':len(issues),'globalIssueCount':len(global_issues)}
report={'schema':1,'character':CHAR,'auditedAt':now(),'auditScope':'Read-only file/source/prompt/receipt/model-evidence/reconstruction/timing audit before requested source cleanup','snapshot':str(S),'snapshotManifestSha256':before,'status':'passed_source_and_timing_only' if not issues and not global_issues else 'issues_found','summary':summary,'sourceCompletenessIssues':issues,'globalIssues':global_issues,'directions':direction_results,'independentIdle':idle_results,'gifs':gifs,'files':rows,'historicalShadowEvidence':info(A/'NE-independent-reconstruction-shadow.json'),'limitations':['Does not approve art or claim animation was viewed.','Does not claim Unity, formal release, or client integration.','Actual model and quality of new built-in outputs remain host-managed/unverified.','Source files were read before cleanup; this report retains hashes, not the removed image pixels.','Known selected_revision staging labels in v1 are presentation metadata; exact source paths and hashes were audited independently.'],'sourceFilesModified':False,'imagesDeleted':False}
(A/'FINAL-SOURCE-AUDIT-20260923.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 05 天音少女最终来源与时长独立审计','',f'审计快照：`{S}`。',f'快照 manifest SHA256：`{before}`。',f'审计时间：{report["auditedAt"]}。','',f'结果：**{report["status"]}**；仅代表文件、来源与时长检查，不代表视觉通过或客户端通过。','',f'- 成品：{len(walk)} 张行走 + {len(idle)} 张独立站立；136 个最终文件逐个核对文件 SHA、像素 SHA 与选用来源。',f'- 尺寸：{summary["dimensions"]}；旧 512 未放大成高清。',f'- 来源分组：{summary["classification"]}；67 个新选用稿的独立 raw、prompt、request、tool-result、receipt、元数据与重建记录逐个核对。',f'- 76 张高清帧重新只读像素重建，通过 {summary["freshIndependentReconstructionsPassed"]} 张；保留的 9 张旧 NE 使用既有 evidence-shadow，不改历史 LF/CRLF。',f'- 8 张 idle 像素互异，且均不复用任何行走图的像素或原始格子。',f'- 16 个 GIF 均逐帧核对：每个 16 帧，每帧 30ms，每圈 480ms，无限循环。','', '## 缺证与差异','',f'- 文件/来源问题行数：{len(issues)}；全局问题数：{len(global_issues)}。',f'- v1 的 `selected_revision=staging` 标签共 {summary["knownStagingLabelCount"]} 条；已按真实路径和 SHA 核验，不将标签误写视为来源造假。',f'- 历史 LF/CRLF 提示涉及 {summary["historicalNewlineAdvisoryRows"]} 行；字节原样保留，细项见 JSON。','- 实际模型/质量由宿主管理且未披露；新图均保留目标配置、实际未提供的参数与未确认原因，不能据此宣称锁定指定型号或 max。']
for item in issues:lines.append(f'- `{item["path"]}`：'+', '.join(item['issues']))
for item in global_issues:lines.append('- '+item)
lines+=['','## 边界','','未修改来源、选用配置或历史换行，未删除图片；未执行视觉批准、Unity 或正式客户端验收。此为删源前的当前字节核验，删源后仅能追溯文字与哈希记录。','', '[完整逐帧证据](FINAL-SOURCE-AUDIT-20260923.json)']
(A/'FINAL-SOURCE-AUDIT-20260923.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'summary':summary,'issues':issues,'globalIssues':global_issues},ensure_ascii=False),flush=True)
