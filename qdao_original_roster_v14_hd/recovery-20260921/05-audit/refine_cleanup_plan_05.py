"""Normalize previously audited receipt paths and add conservative shared-consumer holds; no deletion."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime,timezone
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=HERE/'CLEANUP-PLAN-20260923.json';doc=json.loads(p.read_text())
old_by_path={r['path'].replace('\\','/').lower():r for r in doc['externalOriginals']}
merged={}
for row in doc['externalOriginals']:
 found=re.findall(r'[A-Za-z]:[\\/][^:\r\n"<>]+?\.png',row['path'])
 assert len(found)==1,(row['path'],found)
 value=found[0];key=value.replace('\\','/').lower()
 if key not in merged:merged[key]={'path':str(Path(value)),'receiptFiles':set(),'boundRawFiles':set(),'expectedRawHashes':set()}
 for name in ('receiptFiles','boundRawFiles','expectedRawHashes'):merged[key][name].update(row[name])
results=[]
for key,row in sorted(merged.items()):
 target=Path(row['path']);exists=target.is_file();previous=old_by_path.get(key)
 if exists and previous and previous['existsNow']:digest=previous['sha256'];size=previous['bytes']
 elif exists:
  with target.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  size=target.stat().st_size
 else:digest=None;size=None
 match=digest in row['expectedRawHashes'] if exists else None
 disposition='EXTERNAL_PERMISSION_REQUIRED_AFTER_FINAL_ACCEPTANCE' if exists and match else ('HOLD_EXTERNAL_HASH_BINDING' if exists else 'HISTORICAL_PATH_MISSING_DO_NOT_GUESS_REMAP')
 results.append({**{k:sorted(v) if isinstance(v,set) else v for k,v in row.items()},'workspaceContained':target.resolve().is_relative_to(ROOT.resolve()),'existsNow':exists,'sha256':digest,'bytes':size,'matchesBoundRaw':match,'proposedDisposition':disposition,'deleteScope':'this_exact_file_only_never_parent_directory'})
doc['externalOriginals']=results;doc['externalSummary']={'count':len(results),'existsNow':sum(x['existsNow'] for x in results),'missingHistoricalPaths':sum(not x['existsNow'] for x in results),'existingHashMismatchOrUnbound':sum(x['existsNow'] and not x['matchesBoundRaw'] for x in results)}
counts=Counter();sizes=Counter()
for row in doc['workspaceFiles']:
 if row['proposedDisposition'].startswith('DELETE_') and any(x['kind'] in {'tool_or_code_reference_requires_inspection','older_preview_or_html_reference'} for x in row['otherCharacterOrSharedReferences']):
  row['proposedDisposition']='HOLD_SHARED_CONSUMER_REVIEW';row['reason']='shared_code_or_html_image_reference_requires_rebinding_first'
 counts[row['proposedDisposition']]+=1;sizes[row['proposedDisposition']]+=row['bytes']
doc['counts']=dict(counts);doc['bytesByDisposition']=dict(sizes);doc['refinedAt']=datetime.now(timezone.utc).isoformat();doc['externalPathParsingNote']='Only concrete image filename paths are extracted; a parent directory preceding "as C:/...png" in output_hint is not part of the path.'
doc['preconditions'].append('Resolve HOLD_SHARED_CONSUMER_REVIEW and HOLD_EXTERNAL_HASH_BINDING rows before deleting those files.')
p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 05 天音少女清理计划（只规划，未删除）','',f'核对：{doc["createdAt"]}；清单修订：{doc["refinedAt"]}。当前 `05-delivery-preview/revisions/complete-review-v1` 的128walk+8idle已逐张SHA验证；最终命名与离线美术验收由主代理完成。','',f'05独占图片共{doc["ownedImageCount"]}个。逐文件绝对路径、SHA、当前引用和外部原图见 [JSON](CLEANUP-PLAN-20260923.json)。来源文字记录保留。','','| 处置 | 图片数 | MiB |','|---|---:|---:|']
for k,n in counts.items():lines.append(f'| {k} | {n} | {sizes[k]/1024**2:.2f} |')
lines+=['','当前预览仅实际读取自身runtime的136张PNG；selected-overrides及方向selection仍指向staging，删除当前选用导出前先重新绑定最终包，或明确标为历史。原图路径和SHA应追加已删除标记；删除后不再承诺来源像素重建。','',f'宿主generated_images具体图路径{len(results)}个：现存{doc["externalSummary"]["existsNow"]}、历史缺失{doc["externalSummary"]["missingHistoricalPaths"]}、现存SHA绑定异常{doc["externalSummary"]["existingHashMismatchOrUnbound"]}。现存文件均逐个列出，工作区外操作需对应权限；不得删除整个宿主目录，不猜测旧用户名路径。','','保护：当前4096肖像、全部designs风格图、V13现正式52walk+8idle及其他角色。另有基线肖像、V13候选portrait和N/E/S三个strip列为HOLD；共享代码/HTML仍用到的图另列HOLD，不当作无引用图片。','','执行前先完成最终验收、定名、136张SHA与当前引用复核；仅按具体图片路径删除，绝不递归删除目录或删除JSON/MD/txt等记录；每项重新核对SHA和工作区包含关系。正式客户端或Unity未由本计划验收。']
(HERE/'CLEANUP-PLAN-20260923.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'counts':doc['counts'],'externalSummary':doc['externalSummary'],'planBytes':p.stat().st_size},ensure_ascii=False))
