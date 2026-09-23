"""08-only cleanup PLAN. Read images/receipts; write candidates JSON/MD. Never delete."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import json,hashlib,re

ROOT=Path(__file__).resolve().parent.parent
GEN=ROOT/'08-generation'; PREVIEW=ROOT/'08-delivery-preview'; TOOLS=ROOT/'08-tools'
ALLOWED=[p.resolve() for p in (GEN,PREVIEW,TOOLS)]
HOST=Path('C:/Users/Administrator/.codex/generated_images').resolve()
EXT={'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.avif'}
START=datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def under(p,roots):
    return any(p.resolve().is_relative_to(r) for r in roots)
def fileinfo(p):
    a=p.stat(); digest=sha(p); b=p.stat()
    return {'path':str(p.resolve()),'exists':True,'bytes':b.st_size,'sha256':digest,'modifiedAt':datetime.fromtimestamp(b.st_mtime,timezone.utc).isoformat(),'stableDuringRead':a.st_size==b.st_size and a.st_mtime_ns==b.st_mtime_ns}
def direction(attempt):
    m=re.match(r'(?:walk|idle)-(N|NE|E|SE|S|SW|W|NW)-',attempt)
    return m.group(1) if m else None
def hold_reason(d):return 'active_N_NE_production_wait_final_lock' if d in ('N','NE') else 'wait_approved_136_runtime_and_final_preview_lock'

repo=[]; excluded=[]; text_counts=Counter(); dirs=defaultdict(lambda:{'imageCount':0,'imageBytes':0,'kinds':Counter()})
for allowed in ALLOWED:
    for p in sorted(allowed.rglob('*')):
        if not p.is_file():continue
        if p.suffix.lower() not in EXT:
            text_counts[allowed.name]+=1;continue
        if p.is_symlink() or not under(p,ALLOWED):
            excluded.append({'path':str(p),'reason':'symlink_or_resolved_outside_08_scope'});continue
        row=fileinfo(p);rel=p.relative_to(allowed);attempt=None;d=None
        if allowed==GEN:
            attempt=rel.parts[0] if len(rel.parts)>1 else None;d=direction(attempt or '')
            kind='temporary_reference_copy' if attempt=='references' else 'repository_generated_raw_or_attempt_image'
            disposition='remove_image_after_generation_and_reference_lock'
        elif allowed==PREVIEW and rel.parts[0]=='processed':
            attempt=rel.parts[1] if len(rel.parts)>2 else None;d=direction(attempt or '')
            kind='processed_runtime_copy' if p.name=='frame.png' else 'processed_intermediate_or_QA_image'
            disposition='remove_after_exact_final_runtime_copy_verified' if p.name=='frame.png' else 'remove_image_after_final_lock'
        elif allowed==PREVIEW and rel.parts[0]=='revisions':
            if 'runtime' in rel.parts:
                kind='revision_runtime_copy';disposition='conditional_remove_only_if_not_in_locked_final_136'
                ix=rel.parts.index('runtime'); tail=rel.parts[ix+1:];d=tail[1] if len(tail)>1 else None
            else:
                kind='revision_preview_image';disposition='conditional_remove_only_if_not_in_locked_final_preview_design'
                m=re.match(r'(N|NE|E|SE|S|SW|W|NW)-',p.name);d=m.group(1) if m else None
        else:
            kind='temporary_review_or_work_image';disposition='conditional_remove_after_final_preview_selection'
            if 'n-ne-work' in rel.parts:d='N' if p.name.startswith('N-') else 'NE'
            else:
                m=re.match(r'(N|NE|E|SE|S|SW|W|NW)[-_]',p.name);d=m.group(1) if m else None
        row.update({'kind':kind,'attempt':attempt,'direction':d,'proposedDisposition':disposition,'hold':hold_reason(d),'deleteAllowedNow':False,'scopeValidated':True})
        repo.append(row);g=dirs[str(p.parent.resolve())];g['imageCount']+=1;g['imageBytes']+=row['bytes'];g['kinds'][kind]+=1

receipts=[];host_map=defaultdict(list);receipt_errors=[];interrupted=[]
for attempt in sorted(GEN.iterdir()):
    if not attempt.is_dir() or attempt.name=='references':continue
    files=sorted(attempt.glob('*receipt*.json'))
    if not files:
        interrupted.append({'attempt':attempt.name,'direction':direction(attempt.name),'rawExists':(attempt/'raw.png').exists(),'requestExists':(attempt/'request.json').exists(),'state':'no_receipt_no_host_file_claimed'})
    for receipt in files:
        try:r=read(receipt)
        except Exception as e:receipt_errors.append({'receipt':str(receipt),'error':str(e)});continue
        hint=r.get('output_hint','')
        parsed=re.findall(r'\bas\s+((?:[A-Za-z]:[\\/])[^\r\n]+?\.(?:png|jpe?g|webp))\s+by default',hint,re.I)
        row={'receipt':str(receipt.resolve()),'receiptSHA256':sha(receipt),'attempt':attempt.name,'direction':direction(attempt.name),'parsedHintPaths':parsed,'sourcePathField':r.get('sourcePath'),'rawPath':str((attempt/'raw.png').resolve()),'rawExists':(attempt/'raw.png').exists(),'mappingStatus':'pending'}
        if len(parsed)!=1:
            row['mappingStatus']='unverified_hint_not_exactly_one_file';receipts.append(row);continue
        host=Path(parsed[0]).resolve()
        if not under(host,[HOST]) or host.suffix.lower() not in EXT:
            row['mappingStatus']='excluded_outside_designated_host_generated_images';receipts.append(row);continue
        if r.get('sourcePath') and Path(r['sourcePath']).resolve()!=host:
            row['mappingStatus']='sourcePath_and_output_hint_disagree';receipts.append(row);continue
        row['mappingStatus']='exact_output_hint_file_mapping';row['mappedHostPath']=str(host)
        if host.is_file() and not host.is_symlink():
            hi=fileinfo(host);row['hostExists']=True;row['hostSHA256']=hi['sha256'];row['hostBytes']=hi['bytes']
            if row['rawExists']:
                row['rawSHA256']=sha(attempt/'raw.png');row['matchesRepositoryRaw']=row['rawSHA256']==hi['sha256']
            else:row['matchesRepositoryRaw']=None
        else:
            row['hostExists']=False;row['matchesRepositoryRaw']=None
        receipts.append(row);host_map[str(host)].append(row)

hosts=[]
for path,mappings in sorted(host_map.items()):
    exists=all(x.get('hostExists') for x in mappings)
    matched=exists and all(x.get('matchesRepositoryRaw') is True for x in mappings)
    ds=sorted({x['direction'] for x in mappings if x['direction']})
    hosts.append({'path':path,'exists':exists,'bytes':mappings[0].get('hostBytes'),'sha256':mappings[0].get('hostSHA256'),'scopeValidatedBy':'exact08receipt.output_hint_and_generated_images_root','receiptMappings':[{'receipt':x['receipt'],'attempt':x['attempt'],'matchesRepositoryRaw':x.get('matchesRepositoryRaw')} for x in mappings],'directions':ds,'allMappedRawHashesMatch':matched,'proposedDisposition':'remove_exact_host_file_after_final_lock' if matched else 'hold_unverified_or_missing_host_file','hold':'active_N_NE_production_wait_final_lock' if any(d in ('N','NE') for d in ds) else 'wait_approved_136_runtime_and_final_preview_lock','deleteAllowedNow':False,'neverDeleteParentDirectory':True})

manifests=[]
for p in sorted((PREVIEW/'revisions').glob('*/manifest.json')):
    try:
        m=read(p);manifests.append({'path':str(p.resolve()),'sha256':sha(p),'revision':m.get('revision'),'walk':m.get('actual_walk'),'idle':m.get('actual_idle'),'visualApproval':m.get('visual_approval'),'is136Inventory':m.get('actual_walk')==128 and m.get('actual_idle')==8,'selectionIsNotInferredFromName':True})
    except Exception as e:receipt_errors.append({'manifest':str(p),'error':str(e)})

summary={'repositoryImageFiles':len(repo),'repositoryImageBytes':sum(x['bytes'] for x in repo),'repositoryImagesByKind':dict(Counter(x['kind'] for x in repo)),'repoImagesOnNNEHold':sum(x['hold'].startswith('active_') for x in repo),'receiptsInspected':len(receipts),'exactMappedHostFiles':len(hosts),'existingHostFiles':sum(x['exists'] for x in hosts),'allRawMatchedHostFiles':sum(x['allMappedRawHashesMatch'] for x in hosts),'hostFileBytes':sum(x.get('bytes') or 0 for x in hosts),'hostFilesOnNNEHold':sum(x['hold'].startswith('active_') for x in hosts),'unverifiedReceiptMappings':sum(x['mappingStatus']!='exact_output_hint_file_mapping' for x in receipts),'attemptsWithoutReceipt':len(interrupted),'excludedScopeEntries':len(excluded),'errors':len(receipt_errors),'deletedFiles':0}
plan={'schema':'qdao08-cleanup-plan-v1','createdAt':START,'completedAt':datetime.now(timezone.utc).isoformat(),'mode':'PLAN_ONLY_NO_DELETION','deleteExecutionAllowed':False,'recursiveDirectoryDeletionAllowed':False,'scope':{'repositoryRoots':[str(p) for p in ALLOWED],'hostRoot':str(HOST),'hostScope':'Only exact files mapped by real receipts inside08-generation; no host directory scan or unknown outputs claimed.'},'protectedClasses':['Final approved 128 walk plus8 idle runtime PNGs, exact file list to be locked by root','Final selected preview/design images and HTML, exact list to be locked by root','All prompt/request/receipt/generation/review/source/manifest/selection/config provenance text and helper code','Shared identity4096 original and designs style originals outside08scope are excluded entirely','Active N/NE unique working sources and derived frames until final selection'], 'executionGates':['Root locks exactly136 approved game PNGs and final preview/design list; protected destinations may not overlap deletion paths.','N/NE production completes and all directions are accepted; unique in-progress sources must remain.','Verify final PNGs and current references; retain complete per-image model/quality/prompt/receipt/SHA evidence, record original image removal explicitly.','Reinventory after final build; additions and concurrently changed files are not covered by this snapshot.','At execution resolve every path within approved08roots, or exact receipt-mapped host file under generated_images; recheck exact SHA and no symlink.','Delete individual image files only; preserve all textual evidence; never recursively delete attempt/revision/host directories from this plan.'],'summary':summary,'repositoryImageCandidates':repo,'mappedHostImageCandidates':hosts,'receiptMappingAudit':receipts,'attemptsWithoutReceipt':interrupted,'reviewDirectorySummaries':[{'directory':d,**v,'kinds':dict(v['kinds']),'deleteDirectory':False,'preserveTextFiles':True} for d,v in sorted(dirs.items())],'revisionManifestInventory':manifests,'preservedNonImageFileCounts':dict(text_counts),'scopeExclusions':excluded,'errors':receipt_errors}
(TOOLS/'cleanup-candidates.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=f'''# 08 清理候选清单（只计划）

快照时间：{START}。未删除、移动或改写任何图片。详细逐文件路径、字节数、SHA、作用范围和回执映射见 [cleanup-candidates.json](cleanup-candidates.json)。计划脚本 [cleanup_inventory.py](cleanup_inventory.py) 只读取文件并更新此计划，不含删除逻辑。

- 仓库候选图片 {summary['repositoryImageFiles']} 个，{summary['repositoryImageBytes']:,} 字节；只来自 08-generation、08-delivery-preview、08-tools 三个专属根目录。
- 检查真实回执 {summary['receiptsInspected']} 份，精确映射宿主图片 {summary['exactMappedHostFiles']} 个，其中存在 {summary['existingHostFiles']} 个、与仓库 raw SHA 一致 {summary['allRawMatchedHostFiles']} 个。未扫描宿主输出目录，也未认领无回执的图片。
- N/NE 在制保护：仓库图片 {summary['repoImagesOnNNEHold']} 个、宿主映射 {summary['hostFilesOnNNEHold']} 个；都标记等待最终锁定。
- 未核实回执映射 {summary['unverifiedReceiptMappings']} 项；无回执 attempt {summary['attemptsWithoutReceipt']} 项。这些项目不构成宿主原图删除授权。

候选不是立即删除清单：所有条目 deleteAllowedNow=false。runtime 副本和 revision 预览必须等 root 锁定最终 136 张游戏 PNG、最终预览设计名单后再逐文件排除保留项。N/NE 正在制作的唯一稿仍应保留；其他方向也等待最终成品与引用审计。后续新增文件不在本次快照内，执行前重新核对。

可在上述前提满足后移除：仓库 raw、拒稿图、清边/缩放加工图、被正式包替代的 frame 副本、未选用的旧 revision/临时 review 图片，以及回执精确映射且 SHA 匹配的宿主原图。08-generation/references 内的 identity1024/style1280 只是本角色临时输入副本，须待全部生成结束后再移除；共享原始4096身份设计、designs 风格原件未进入候选。

逐图 prompt/request/receipt、模型与质量记录、SHA/来源链、选用和拒稿文字证据全部保留。只能据精确路径移除图片，不递归删除 attempt、revision 或宿主目录。此清单没有执行任何清理。
'''
(TOOLS/'cleanup-candidates.md').write_text(md,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
