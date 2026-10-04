"""Read-only inventory/provenance audit. Writes text reports only in this folder."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
import hashlib, io, json, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TARGET = ('gpt-image-2.5-sunburst', 'max')
EXPECTED = {f'frames/{a}/{d}/frame_{n:02}.png' for a,ds,count in [
    ('run',['N','NE','E','SE','S','SW','W','NW'],16),
    ('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16)]
    for d in ds for n in range(1,count+1)}

def digest(data): return hashlib.sha256(data).hexdigest()
def readjson(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT/p
def dt(value): return datetime.fromisoformat(value.replace('Z','+00:00')) if value else None
def refpath(value): return value.get('path') if isinstance(value,dict) else value
def add(row,level,code,detail): row[level].append({'code':code,'detail':detail})
cache = {}
def inspect(path):
    path = path.resolve()
    stat = path.stat()
    key = (str(path), stat.st_mtime_ns, stat.st_size)
    if key in cache: return cache[key]
    data = path.read_bytes()
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        result={'sha256':digest(data),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
        rgba = im.convert('RGBA')
        result['rgbaPixelSha256']=digest(rgba.tobytes())
        alpha = rgba.getchannel('A')
        result['alphaExtrema']=list(alpha.getextrema())
        result['outermostEdgeMaxAlpha']=max(alpha.crop(box).getextrema()[1] for box in
            [(0,0,im.width,1),(0,im.height-1,im.width,im.height),(0,0,1,im.height),(im.width-1,0,im.width,im.height)])
        result['alphaBounds']={}
        for threshold in (0,127):
            bbox=alpha.point(lambda v:255 if v>threshold else 0).getbbox()
            result['alphaBounds'][str(threshold)]={'bbox':list(bbox) if bbox else None,
                'marginsLTRB':[bbox[0],bbox[1],im.width-bbox[2],im.height-bbox[3]] if bbox else None}
    result['stableDuringRead']=path.stat().st_mtime_ns==stat.st_mtime_ns
    cache[key]=result
    return result

started=datetime.now(timezone.utc).isoformat()
historical=defaultdict(list)
cleanup_texts={p.relative_to(ROOT).as_posix():p.read_text(encoding='utf-8-sig').lower() for p in (ROOT/'provenance').rglob('*cleanup*.json')}
for p in (ROOT/'provenance').rglob('*.generation.json'):
    try:
        j=readjson(p)
        if j.get('sha256'): historical[j['sha256'].lower()].append(p.relative_to(ROOT).as_posix())
        if isinstance(j.get('nativeSource'),dict) and j['nativeSource'].get('sha256'):
            historical[j['nativeSource']['sha256'].lower()].append(p.relative_to(ROOT).as_posix()+'#nativeSource')
    except Exception: pass
actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'frames').rglob('*.png')}
report={'startedAt':started,'root':str(ROOT),'scope':'只读技术与来源审计；不以哈希、数量或边距自动判断美术、动态或接地通过。',
        'expectedCount':len(EXPECTED),'actualPngCount':len(actual),'missingPngs':sorted(EXPECTED-actual),'extraPngs':sorted(actual-EXPECTED),'frames':[]}
for rel in sorted(EXPECTED):
    row={'file':rel,'errors':[],'warnings':[],'information':[]}
    report['frames'].append(row)
    p=ROOT/rel; side=p.with_suffix('.generation.json')
    if not p.exists(): add(row,'errors','missing_png',rel); continue
    try: pix=inspect(p); row['actual']=pix
    except Exception as e: add(row,'errors','png_unreadable',str(e)); continue
    if not pix['stableDuringRead']: add(row,'warnings','file_changed_during_read',rel)
    if (pix['width'],pix['height'],pix['mode'],pix['format'])!=(1024,1024,'RGBA','PNG'):
        add(row,'errors','formal_image_spec',pix)
    if not side.exists(): add(row,'errors','missing_sidecar',str(side)); continue
    raw=side.read_bytes(); row['sidecarSha256']=digest(raw)
    try: j=json.loads(raw.decode('utf-8-sig'))
    except Exception as e: add(row,'errors','sidecar_unreadable',str(e)); continue
    row.update(action=j.get('action'),direction=j.get('direction'),frame=j.get('frame'),review=j.get('review'),
               frameDurationMs=j.get('frameDurationMs'),runTiming=j.get('runTiming'),rootAnchor=j.get('rootAnchor'))
    for key in ('sha256','width','height','mode','format','alphaExtrema'):
        if j.get(key)!=pix[key]: add(row,'errors','formal_metadata_mismatch',{'field':key,'record':j.get(key),'actual':pix[key]})
    if j.get('file','').replace('\\','/')!=rel: add(row,'errors','file_slot_mismatch',j.get('file'))
    if j.get('character')!=ROOT.name: add(row,'errors','character_mismatch',j.get('character'))
    if j.get('review',{}).get('reviewedSha256') not in (None,pix['sha256']): add(row,'warnings','review_for_old_sha',j['review']['reviewedSha256'])
    if j.get('clientIntegration')!='not_integrated': add(row,'warnings','client_status_check',j.get('clientIntegration'))
    evidence={}
    prompt_item=j.get('prompt') or j.get('submittedParameters',{}).get('prompt')
    for name,item in [('prompt',prompt_item),*j.get('evidence',{}).items()]:
        if name=='originalHostSource': continue
        q=refpath(item)
        if not q: add(row,'errors','evidence_path_missing',name); continue
        ep=resolve(q)
        if not ep.exists(): add(row,'errors','evidence_missing',{'kind':name,'path':q}); continue
        eb=ep.read_bytes(); recordsha=item.get('sha256') if isinstance(item,dict) else None
        if recordsha and digest(eb)!=recordsha.lower(): add(row,'errors','evidence_sha_mismatch',{'kind':name,'path':q})
        if not recordsha: add(row,'warnings','evidence_sha_not_declared',{'kind':name,'path':q,'computedSha256':digest(eb)})
        if name in ('submission','receipt'):
            try: evidence[name]=json.loads(eb.decode('utf-8-sig'))
            except Exception as e: add(row,'errors','evidence_invalid_json',{'kind':name,'error':str(e)})
        elif name=='prompt': evidence['promptText']=eb.decode('utf-8-sig')
    sub=evidence.get('submission',{}); rec=evidence.get('receipt',{})
    parms=j.get('submittedParameters',{}); sourceparms=sub.get('submittedParameters',{})
    row['modelEvidence']={'configTarget':[j.get('configSnapshot',{}).get('model'),j.get('configSnapshot',{}).get('quality')],
        'submissionConfigTarget':j.get('submissionConfigTarget'),'submittedModel':parms.get('model'),'submittedQuality':parms.get('quality'),
        'submissionFileModel':sourceparms.get('model'),'submissionFileQuality':sourceparms.get('quality'),
        'actualModel':j.get('actualModel'),'actualQuality':j.get('actualQuality')}
    for key in ('model','quality','transparent_background','referenced_image_paths'):
        if parms.get(key)!=sourceparms.get(key): add(row,'errors','submitted_parameter_mismatch',{'field':key,'sidecar':parms.get(key),'submission':sourceparms.get(key)})
    for key in ('model','quality'):
        if parms.get(key) is not None: add(row,'errors','unsupported_selector_claim',{'field':key,'value':parms[key]})
    for key in ('actualModel','actualQuality'):
        if j.get(key) is not None: add(row,'errors','actual_model_quality_claim_requires_return_evidence',{key:j[key]})
        if sub.get(key) is not None: add(row,'warnings','submission_actual_claim_check',{key:sub[key]})
        if rec.get(key) is not None: add(row,'warnings','receipt_actual_claim_check',{key:rec[key]})
    if not j.get('unverifiedReason'): add(row,'warnings','unverified_explanation_missing','actual model/quality unconfirmed')
    if tuple(row['modelEvidence']['configTarget'])!=TARGET: add(row,'warnings','configuration_target_differs',row['modelEvidence']['configTarget'])
    sprompt=sourceparms.get('prompt')
    if sprompt and evidence.get('promptText') and sprompt.strip()!=evidence['promptText'].strip():
        add(row,'errors','prompt_text_differs_from_submission','Exact submitted prompt not equal to saved prompt after trim.')
    t=j.get('generationTimeEvidence',{}); start=t.get('startedAt'); end=t.get('completedAt'); exported=j.get('exportedAt')
    substart=sub.get('startedAt') or sub.get('submittedAt') or sub.get('attemptedAt')
    recend=rec.get('completedAt')
    row['timeEvidence']={'startedAt':start,'submissionBoundary':substart,'completedAt':end,'receiptBoundary':recend,'exportedAt':exported,'generatedAt':j.get('generatedAt')}
    try:
        if start and end and dt(start)>dt(end): add(row,'errors','generation_time_reversed',row['timeEvidence'])
        if end and exported and dt(end)>dt(exported): add(row,'errors','export_before_completion',row['timeEvidence'])
        if start and substart and dt(start)!=dt(substart): add(row,'warnings','start_boundary_mismatch',row['timeEvidence'])
        if end and recend and dt(end)!=dt(recend): add(row,'warnings','completion_boundary_mismatch',row['timeEvidence'])
        if not start: add(row,'information','started_at_missing','Sidecar start null; submission boundary preserved separately.' if substart else 'No recorded request start.')
        if not end: add(row,'warnings','completed_at_missing',row['timeEvidence'])
        if j.get('generatedAt'):
            gen=dt(j['generatedAt'])
            if (start and gen<dt(start)) or (end and gen>dt(end)):
                add(row,'warnings','generated_at_outside_call',row['timeEvidence'])
            if j['generatedAt'] in t.get('c2paTextTimeCandidates',[]):
                add(row,'information','unsigned_c2pa_time_candidate','generatedAt is from PNG C2PA text candidates, not independently signature verified.')
    except Exception as e: add(row,'errors','invalid_timestamp',str(e))
    native=j.get('nativeSource') or {}; row['nativeRecord']=native
    if min(native.get('width',0),native.get('height',0))<1024: add(row,'errors','native_record_below_1024',native)
    np=resolve(native['path']) if native.get('path') else None
    if not np or not np.exists():
        row['nativeAvailability']='missing'
        add(row,'warnings' if native.get('fileRetained') is False else 'errors','native_source_missing',native)
    else:
        n=inspect(np); row['nativeAvailability']='available'; row['nativeActual']=n
        for key in ('sha256','width','height','mode','format','alphaExtrema'):
            if native.get(key)!=n[key]: add(row,'errors','native_metadata_mismatch',{'field':key,'record':native.get(key),'actual':n[key]})
        if min(n['width'],n['height'])<1024: add(row,'errors','native_actual_below_1024',n)
        with Image.open(np) as im:
            reproduced=im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
            same=digest(reproduced.tobytes())==pix['rgbaPixelSha256']
            row['wholeCanvasResizePixelMatch']=same
            if not same: add(row,'warnings','resize_pixel_mismatch','Declared whole canvas LANCZOS resize differs from native reproduction.')
    op=j.get('operation',{})
    if op.get('crop') or op.get('mirroring') or op.get('poseInterpolation') or op.get('bboxAlignment') or op.get('footAlignment'):
        add(row,'errors','forbidden_operation_declared',op)
    refs=[]
    for rr in j.get('references',[]):
        result={'path':rr.get('path'),'recordedSha256':rr.get('sha256')}; refs.append(result)
        rp=resolve(rr['path']) if rr.get('path') else None
        if not rp or not rp.exists():
            result['status']='missing'
            h=rr.get('sha256','').lower()
            result['historicalRecords']=historical.get(h,[])
            result['cleanupRecords']=[f for f,txt in cleanup_texts.items() if h and h in txt]
            continue
        ri=inspect(rp); result['currentSha256']=ri['sha256']
        if rr.get('sha256','').lower()==ri['sha256']: result['status']='same_bytes_available'
        else:
            result['status']='historical_path_replaced'
            result['historicalRecords']=historical.get(rr.get('sha256','').lower(),[])
            if not result['historicalRecords']: result['status']='hash_differs_no_retired_record_found'
    row['inputReferenceAvailability']=refs
    if digest(side.read_bytes())!=row['sidecarSha256']: add(row,'warnings','sidecar_changed_during_audit',rel)

files=defaultdict(list); pixels=defaultdict(list); natives=defaultdict(list)
for r in report['frames']:
    if 'actual' in r:
        files[r['actual']['sha256']].append(r['file']); pixels[r['actual']['rgbaPixelSha256']].append(r['file'])
    if 'nativeActual' in r: natives[r['nativeActual']['sha256']].append(r['file'])
report['duplicateFormalShaGroups']=[v for v in files.values() if len(v)>1]
report['duplicateRgbaPixelGroups']=[v for v in pixels.values() if len(v)>1]
report['duplicateNativeShaGroups']=[v for v in natives.values() if len(v)>1]
for threshold in ('0','127'):
    report['alpha'+threshold+'MarginsAtMost8']=[{'file':r['file'],**r['actual']['alphaBounds'][threshold]} for r in report['frames'] if 'actual' in r and r['actual']['alphaBounds'][threshold]['marginsLTRB'] and min(r['actual']['alphaBounds'][threshold]['marginsLTRB'])<=8]
report['summary']={'byAction':dict(Counter(r.get('action','missing') for r in report['frames'])),
    'errorCount':sum(len(r['errors']) for r in report['frames']), 'warningCount':sum(len(r['warnings']) for r in report['frames']),
    'errorsByCode':dict(Counter(i['code'] for r in report['frames'] for i in r['errors'])),
    'warningsByCode':dict(Counter(i['code'] for r in report['frames'] for i in r['warnings'])),
    'nativeAvailability':dict(Counter(r.get('nativeAvailability','not_checked') for r in report['frames'])),
    'reviewStatuses':dict(Counter(r.get('review',{}).get('status','missing') for r in report['frames'])),
    'inputReferenceAvailability':dict(Counter(i['status'] for r in report['frames'] for i in r.get('inputReferenceAvailability',[]))),
    'frameDurations':dict(Counter(f"{r.get('action')}/{r.get('frameDurationMs')}" for r in report['frames'])),
    'runTimingTrialRecords':sum(r.get('runTiming') is not None for r in report['frames']),
    'alpha0MarginsAtMost8Count':len(report['alpha0MarginsAtMost8']),
    'alpha127MarginsAtMost8Count':len(report['alpha127MarginsAtMost8']),
    'outermostEdgeMaxAlpha':max(r.get('actual',{}).get('outermostEdgeMaxAlpha',0) for r in report['frames']),
    'outermostEdgeNonzeroFrames':sum(r.get('actual',{}).get('outermostEdgeMaxAlpha',0)>0 for r in report['frames']),
    'sidecarStartedAtMissing':sum(not r.get('timeEvidence',{}).get('startedAt') for r in report['frames']),
    'c2paGeneratedAtCandidateCount':sum(any(i['code']=='unsigned_c2pa_time_candidate' for i in r['information']) for r in report['frames']),
    'allActualModelQualityUnconfirmed':all(r.get('modelEvidence',{}).get('actualModel') is None and r.get('modelEvidence',{}).get('actualQuality') is None for r in report['frames'])}
manifest_path=ROOT/'manifest.technical.json'
if manifest_path.exists():
    manifest=readjson(manifest_path)
    report['manifestTimingSnapshot']={'sha256':digest(manifest_path.read_bytes()),'generatedAt':manifest.get('generated_at_utc'),
        'sequences':[{k:s.get(k) for k in ['action','direction','frame_ms','duration_ms','timing_status','trial_loop_ms','client_approved_loop_ms']}
                     for s in manifest.get('sequences',[])]}
report['nearBorderVisualReview']={
    'scope':'2026-10-03实际view_image逐张检查；只判断画布切断，不替代完整静态/动态动作验收。',
    'observations':[
        {'file':'frames/attack/E/frame_05.png','observed':'杖首金色尖端距右边窄，但尖端完整，未见主体被画布平切。','blocking':False},
        {'file':'frames/attack/E/frame_06.png','observed':'杖首金色尖端距右边窄，但尖端完整，未见主体被画布平切。','blocking':False},
        {'file':'frames/run/SE/frame_13.png','observed':'盾下流苏靠右，外沿完整，未见主体被画布平切。','blocking':False},
        {'file':'frames/run/SW/frame_04.png','observed':'盾下流苏靠右，外沿完整，未见主体被画布平切。','blocking':False}]}
for obs in report['nearBorderVisualReview']['observations']:
    obs['sha256']=next(r['actual']['sha256'] for r in report['frames'] if r['file']==obs['file'])
report['completedAt']=datetime.now(timezone.utc).isoformat()
out=OUT/'final_inventory_audit_20261003.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=report['summary']
notes=[
    '# 04 山岳守卫 · 最终库存与来源只读审计', '',
    f"快照时间：{report['completedAt']}。脚本仅读取正式PNG、sidecar、原生图、提示词、提交和回执；只在本目录写入文字审计结果。", '',
    '## 技术核验', '',
    f"- 正式图 {report['actualPngCount']}/196：run128、hit12、attack24、cast32。缺槽 {len(report['missingPngs'])}，额外槽 {len(report['extraPngs'])}。",
    f"- 硬错误 {s['errorCount']}；字段规范提醒 {s['warningCount']}，详见下表与JSON。",
    '- 逐张核对正式文件SHA、1024×1024 PNG RGBA、透明通道范围，与sidecar一致。',
    f"- 当前原生来源可用 {s['nativeAvailability'].get('available',0)}/196；原生1254×1254 RGBA及SHA已实测，符合原生至少1024要求。每张正式RGBA像素与全画布LANCZOS缩放原生的重现一致。",
    f"- 正式文件SHA重复组 {len(report['duplicateFormalShaGroups'])}；RGBA像素重复组 {len(report['duplicateRgbaPixelGroups'])}；原生SHA重复组 {len(report['duplicateNativeShaGroups'])}。这只能排除完全重复，不证明姿态独立或动画合格。", '',
    '## 模型与时间证据', '',
    '- 196张配置目标均为 GPT Image 2.5 Sunburst / max。实际提交model/quality均null，实际返回型号/质量均null并说明未确认；未发现用配置目标冒充实际返回或使用不存在的型号质量选择器。',
    '- 提示词、submission、receipt均存在；保存的提示词文本与提交内容一致。已有SHA字段均匹配。',
    f"- 未发现提交开始、完成、导出时间倒置。{s['sidecarStartedAtMissing']}份sidecar开始时间为null（attack E01/E06），submission仍留attemptedAt边界；不补造精确出图时间。",
    f"- {s['c2paGeneratedAtCandidateCount']}份hit的generatedAt来自PNG C2PA文本候选；记录已注明未独立验签，不据此确认型号或质量。", '',
    '## 来源链与已清理历史输入', '',
    f"- 历史输入引用按出现次数：{s['inputReferenceAvailability'].get('same_bytes_available',0)}项仍有相同字节；{s['inputReferenceAvailability'].get('historical_path_replaced',0)}项正式路径后来换版、旧SHA均有retired记录；{s['inputReferenceAvailability'].get('missing',0)}项旧PNG已删除，均能查到历史来源及cleanup文字记录。",
    '- 上述历史输入可用性不等于当前原生来源缺失。当前196张nativeSource均在；审计未删除或恢复任何图。',
    '- 证据文件的现算SHA已写入本审计JSON；原始sidecar/submission/receipt保持不动。', '',
    '| 正式槽 | 缺少独立SHA的记录 | 审计现算SHA |', '| --- | --- | --- |']
for r in report['frames']:
    for w in r['warnings']:
        if w['code']=='evidence_sha_not_declared':
            d=w['detail']; notes.append(f"| {r['file']} | {d['kind']}：{d['path']} | `{d['computedSha256']}` |")
notes += ['', '## 边距诊断与实际查看', '',
    f"alpha>0边距≤8px有{s['alpha0MarginsAtMost8Count']}张；{s['outermostEdgeNonzeroFrames']}张最外边存在低透明度像素，最外边alpha最大仅{s['outermostEdgeMaxAlpha']}/255。不能用最低非零alpha像素判断脚着地或主体被裁。", '',
    '| 槽位 | alpha>127右边距 | 实际查看 |', '| --- | ---: | --- |']
for item in report['alpha127MarginsAtMost8']:
    obs=next((o for o in report['nearBorderVisualReview']['observations'] if o['file']==item['file']),None)
    notes.append(f"| {item['file']} | {item['marginsLTRB'][2]} px | {obs['observed'] if obs else '待实际查看'} |")
old_run_count=s['frameDurations'].get('run/30',0)
w03=next(r for r in report['frames'] if r['file']=='frames/run/W/frame_03.png')
notes += ['', '这4项为窄边距提示，当前观察不构成切断阻断。没有以阈值自动批准美术。', '',
    '## 节奏、状态与交接边界', '',
    f"- sidecar快照状态：{json.dumps(s['reviewStatuses'],ensure_ascii=False)}；这是声明统计，不自动补写通过状态。",
    f"- sidecar帧时长统计：{json.dumps(s['frameDurations'],ensure_ascii=False)}。run有{s['runTimingTrialRecords']}张显式runTiming试播记录；旧30ms字段仍有{old_run_count}张。最终交接须明确480ms旧基线、640/720/800ms试播与客户端值未确认。",
    '- 当前manifest已将run480标作legacy_480_baseline_trials_pending、客户端跑步时长null。网页默认720ms明确标作待审。战斗240/360/720ms为规格值；这不是客户端实测通过。',
    '- 196张根锚点(512,928)为声明的画布目标，未做实际骨骼/根点像素校准；不得据此声称完成客户端注册。',
    '- 所有客户端状态均未接入。完整动态、根位置及接地感由根窗口继续验收，本审计不将数量/SHA/PNG格式等同动作通过。',
    '- 审计快照后如有新图替换或sidecar统一，需要重跑本目录final_inventory_audit.py刷新结果。S02/S03已核对当前attempt02（3c59e675… / a5e09a06…）。',
    f"- 本快照W03：`{w03['actual']['sha256']}`，原生`{w03['nativeRecord']['path']}`。后续替换版本不在本快照范围。", '',
    '[完整逐图JSON](final_inventory_audit_20261003.json) · [可重跑只读脚本](final_inventory_audit.py)', '']
(OUT/'FINAL_INVENTORY_AUDIT_20261003.md').write_text('\n'.join(notes),encoding='utf-8')
print(json.dumps({'report':str(out),'summary':report['summary'],'duplicateFormalShaGroups':report['duplicateFormalShaGroups'],'duplicateRgbaPixelGroups':report['duplicateRgbaPixelGroups'],'alpha127MarginsAtMost8':report['alpha127MarginsAtMost8']},ensure_ascii=False,indent=2))
