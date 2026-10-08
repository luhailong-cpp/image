from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, copy

B = Path('D:/work/image/qdao_city_tiles_4k_20260916')
P = B / 'builtin_q64_production/parallel_20261005'
A = P / 'parent_audit_20261008'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path': Path(p).as_posix(), 'sha256': sha(p)}
def dump(p, d): Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
ip = A / 'verified-current-index.json'
dp = A / 'live-refresh-20261008-source-audit.json'
I, D, S = read(ip), read(dp), read(B/'status.json')
before = sha(ip)
assert I['summary']['completePixelCandidateCount'] == 45
assert D['baseIndex']['sha256'] == before
assert D['proposedTotal'] == 48 and D['baselineAllFilesMatch']
repairs_before = {e['tileId']: copy.deepcopy(e['parentRepairCandidate']) for a in I['appearances'] for e in a['entries'] if 'parentRepairCandidate' in e}
assert len(repairs_before) == 5
proof_checks = []
for n in D['selectedAdditions']:
    assert n['eligibleCompletePixelCandidate'] and n['allNative1254SourcesVerified'] and n['sourceCount']==16
    # The previous read-only audit binds native sources and QA. Recheck the selected
    # pixels and manifest bytes so a later in-place write cannot inherit that proof.
    for k in ['core','manifest']:
        r=n[k]; actual=sha(r['path']); assert actual==r['sha256'], ('changed audited addition',k,r)
        proof_checks.append(dict(**ref(r['path']), expectedShaMatches=True, role=k))
    a=next(a for a in I['appearances'] if a['appearance']==n['appearance'])
    assert not any(e['tileId']==n['tileId'] for e in a['entries'])
    e={'tileId':n['tileId'],'path':n['core']['path'],'sha256':n['core']['sha256'],
       'width':4096,'height':4096,'fullPixelCandidate':True,'formalAccepted':False,
       'selectionSource':n['selectionSource'],'selectionSnapshot':n['selectedEntry'],
       'generationRecord':n['manifest'],'auditSource':ref(dp),
       'auditEntryPointer':'/selectedAdditions/'+str(D['selectedAdditions'].index(n)),
       'qaEvidence':n.get('qaBindings',[n['qaBinding']] if 'qaBinding' in n else []),
       'qaStatus':n.get('qaStatus','限定水面修复范围检查通过；外部邻边及正式验收待完成'),
       'remainingLimitations':n['remaining'],'observedAt':D['completedAt'],
       'sourceCount':16,'nativeSourceAndQABindingAudit':ref(dp)}
    if 'qaScope' in n: e['qaScope']=n['qaScope']
    a['entries'].append(e)
for a in I['appearances']:
    a['entries'].sort(key=lambda e:e['tileId'])
    a['completePixelCandidateCount']=len(a['entries'])
    a['missingOf256']=256-len(a['entries'])
    assert len(a['entries'])==D['proposedCounts'][a['appearance']]
I.setdefault('historicalAggregateSummaries',[]).append({'summary':copy.deepcopy(I['summary']),'indexSha256':before,'supersededAt':now,'scope':'45-coordinate snapshot before three audited selected additions'})
I['summary']['completePixelCandidateCount']=48
I['summary']['missingFullPixelCoordinates']=1744
I['snapshotScope']='七任务权威选择和绑定来源的 48 坐标快照，另附 5 个同坐标 parentRepairCandidate。完整像素候选不等于正式游戏成品，父修补引用不替换子任务选择。'
I['observedAt'],I['updatedAt']=D['completedAt'],now
I.setdefault('priorDeltaAudits',[]).append(I['latestDeltaAudit'])
I['latestDeltaAudit']=I['latestLiveDelta']=ref(dp)
I.setdefault('historicalIncompleteWorkSnapshots',[]).append(I['activeIncompleteWork'])
I['activeIncompleteWork']={'observedAt':D['observedAt'],'excludedFromAdditionalCount':D['excluded'],'registryObservationsSource':ref(dp)}
I['currentRegistryObservations']={'otherRegistries':D['otherRegistries'],'lanternRegistrySnapshot':D['lanternRegistrySnapshot'],'snapshotSource':ref(dp)}
if I.get('excludedAssembliesPendingRebuild'):
    I.setdefault('historicalExcludedAssemblies',[]).append({'snapshot':I['excludedAssembliesPendingRebuild'],'resolvedAt':now,'resolution':'Replacement sources, rebuilt current assembly, selected progress and bound water QA verified by current audit. Historical rejected assembly remains excluded.','evidence':ref(dp)})
    I['excludedAssembliesPendingRebuild']=[]
I['parentIndexValidation']['scope']='Historical parent repair integration check; current candidate count and additions are bound by latestLiveDelta and liveAggregationValidation.'

# Mechanical, proportion-preserving thumbnail display only. No production pixels altered.
W,H=1808,1920
im=Image.new('RGB',(W,H),'#eef2f7'); dr=ImageDraw.Draw(im)
def font(size,bold=False): return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
dr.text((28,20),'七套主城 · 现有区域缩略预览',font=font(32,True),fill='#1d2d44')
dr.text((28,70),'完整像素候选 48 / 1792  |  7 套均未完成  |  灰格为缺块  |  仅展示当前已选区域，不是整城图',font=font(20),fill='#4d5c70')
sources,groups=[],[]
for j,a in enumerate(I['appearances']):
    x,y=28+(j%2)*888,116+(j//2)*450
    dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='white',outline='#d9e1eb',width=2)
    dr.text((x+18,y+16),f"{j+1:02d}  {a['title']}",font=font(24,True),fill='#1d2d44')
    dr.text((x+694,y+18),f"{len(a['entries'])} / 256 块",font=font(21),fill='#476483')
    coords={(int(e['tileId'][1:3]),int(e['tileId'][5:7])):e for e in a['entries']}
    r0,r1=min(p[0] for p in coords),max(p[0] for p in coords)
    c0,c1=min(p[1] for p in coords),max(p[1] for p in coords)
    dr.text((x+18,y+48),f'范围 r{r0:02d}–r{r1:02d} / c{c0:02d}–c{c1:02d} · 相同比例缩小，非原尺寸验收',font=font(14),fill='#778392')
    gx,gy=x+(864-(c1-c0+1)*112)//2,y+71+(336-(r1-r0+1)*112)//2
    missing=[]
    for r in range(r0,r1+1):
        for c in range(c0,c1+1):
            px,py=gx+(c-c0)*112,gy+(r-r0)*112
            tid=f'r{r:02d}_c{c:02d}';e=coords.get((r,c))
            if e:
                raw=Path(e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'],('changed source',e['path'])
                with Image.open(BytesIO(raw)) as src:
                    assert src.size==(4096,4096)
                    assert 'A' not in src.getbands() or src.getchannel('A').getextrema()==(255,255)
                    im.paste(src.convert('RGB').resize((112,112),Image.Resampling.LANCZOS),(px,py))
                sources.append({'appearance':a['appearance'],'tileId':tid,'path':e['path'],'sha256':e['sha256'],'expectedShaMatches':True,'observedAt':now,'sourcePixels':[4096,4096],'previewPixels':[112,112],'scaleX':112/4096,'scaleY':112/4096,'resampling':'LANCZOS downsampling','stretch':False,'destinationRectXYWH':[px,py,112,112]})
            else:
                missing.append(tid);dr.rectangle((px,py,px+111,py+111),fill='#5d697a');dr.line((px+14,py+96,px+96,py+14),fill='#697486');dr.text((px+36,py+45),'缺块',font=font(20),fill='#dce1e9')
            dr.rectangle((px,py,px+111,py+111),outline='#edf0f4');dr.rectangle((px+2,py+2,px+73,py+18),fill='#1d2d44');dr.text((px+4,py+2),tid,font=font(11),fill='white')
    groups.append({'appearance':a['appearance'],'bboxTileRowsInclusive':[r0,r1],'bboxTileColumnsInclusive':[c0,c1],'tilePreviewPixels':[112,112],'missingCoordinatesInsideBBox':missing})
x,y=916,1466
dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='#1d2d44')
dr.text((x+28,y+30),'当前候选总数',font=font(25,True),fill='#dce5ef')
dr.text((x+28,y+82),'48 / 1792',font=font(58,True),fill='white')
dr.text((x+28,y+164),'尚缺完整像素图块 1744 块',font=font(24,True),fill='#f5c963')
for n,t in enumerate(['正式验收：0 块    整套完成：0 / 7','按真实行列缩小；灰格与细网格是预览标记。','父修补 5 个同坐标备选单独索引，不重复计数。','新增：小镇日景 r09_c09、春节 r09_c11。','渔村日景 r08_c14 已重建并核验当前来源。']):
    dr.text((x+28,y+224+n*33),t,font=font(19),fill='#dce5ef')
assert len(sources)==48 and sha(ip)==before
for s in sources: assert sha(s['path'])==s['sha256'],('late source change',s['path'])
repairs_after={e['tileId']:e['parentRepairCandidate'] for a in I['appearances'] for e in a['entries'] if 'parentRepairCandidate' in e}
assert repairs_before==repairs_after
preview=A/'overview.jpg';im.save(preview,quality=94,subsampling=0)
I['preview']={'path':preview.as_posix(),'sha256':sha(preview),'pixels':[W,H],'createdAt':now,'kind':'mechanical-downsample-contact-sheet-only','notGameAsset':True,'notWholeCity':True,'sourcePixelsGenerated':False,'sourcePixelsModified':False,'sources':sources,'groups':groups,'visualReview':{'status':'pending_layout_review'}}
I['liveAggregationValidation']={'checkedAt':now,'sourceCount':48,'uniqueCoordinateCount':48,'allSourceHashesMatchedBeforePreviewWrite':True,'allSourcesDecoded4096':True,'allSourcesFullyOpaque':True,'sameCoordinateUpdates':0,'newCoordinates':3,'formalAcceptedCount':0,'wholeCityCompleteCount':0,'fiveParentRepairAlternativesPreserved':True,'source':ref(dp),'addedCoreAndManifestRechecks':proof_checks}
dump(ip,I)
for key in ['generated4KCandidateCount','currentSelectedCandidateCoordinateCountAllAppearances']:S[key]=48
S['updatedAtUtc']=now;S['scope']=S['scope'].replace('45 unique','48 unique').replace('1747 missing','1744 missing')
S['currentBatchSha256']=sha(ip);S['candidateFiles']=[Path(e['path']).relative_to(B).as_posix() for a in I['appearances'] for e in a['entries']]
S['candidatePreviewSha256']=sha(preview);S['candidatePreviewMeaning']='48-coordinate selected snapshot; five parent repair alternatives remain separate.'
S['scopeDecision'].update(currentCompletePixelCandidateCount=48,remainingFullPixelCoordinates=1744)
S['activeProductionRun'].update(updatedAtUtc=now,currentCompletePixelCandidateCount=48,remainingFullPixelCoordinates=1744)
S['activeProductionRun']['countMeaning']=S['activeProductionRun']['countMeaning'].replace('45 unique','48 unique')
S['latestContinuation'].update(currentWorkingCoordinates=48,updatedAtUtc=now,latestLiveDelta=ref(dp));S['latestContinuation']['checkpoint']['sha256']=sha(ip)
S['counterMeaning']=S['counterMeaning'].replace('45 counts','48 counts');S['baselineSelectionCountMeaning']=S['baselineSelectionCountMeaning'].replace('45-coordinate','48-coordinate')
dump(B/'status.json',S)
for p in [A/'README.md',P/'README.md']:
    t=p.read_text(encoding='utf-8-sig')
    for old,new in [('45 / 1792','48 / 1792'),('45/1792','48/1792'),('当前 45 块','当前 48 块'),('1747','1744'),('总数仍为 45','总数仍为 48'),('展示 45 坐标','展示 48 坐标'),('| 小镇日景地图 | 6 | 250 | 0 |','| 小镇日景地图 | 7 | 249 | 0 |'),('| 小镇春节地图 | 6 | 250 | 0 |','| 小镇春节地图 | 7 | 249 | 0 |'),('| 渔村日景地图 | 6 | 250 | 0 |','| 渔村日景地图 | 7 | 249 | 0 |'),('小镇日景/春节各 6，渔村日景 6','小镇日景/春节各 7，渔村日景 7')]:t=t.replace(old,new)
    if p==A/'README.md':
        lines=t.splitlines()
        for n,line in enumerate(lines):
            if line.startswith('快照来源观察：'):lines[n]=f'快照来源观察：{D["completedAt"]}（UTC）；最新汇总生成：{now}（UTC）。'
            elif line.startswith('本轮可靠新增'):lines[n]='本轮可靠新增小镇日景 r09_c09、小镇春节 r09_c11、渔村日景 r08_c14，三块均核验当前选择、16 片原生来源、完整像素覆盖及限定范围 QA；渔村 r08_c14 已使用替换水面来源重建。完整像素仅表示当前唯一坐标有完整 4096×4096 候选，限定范围 QA 不等于整块、整城、寻路或客户端验收。'
            elif line.startswith('- 渔村日景 r08_c13'):lines[n]='- 渔村日景 r08_c14 已用替换水面来源重建，当前像素 SHA 与 assembly manifest、限定水面修复 QA 绑定并正式选为完整像素候选；旧拒稿源合图只留历史排除记录。外部邻边和整城仍待验收。'
            elif line.startswith('- 渔村元宵 r08_c11'):lines[n]=line+' r08_c13 新候选未由权威索引选定，原尺寸检查仍为 pending，暂不计数。'
            elif line.startswith('最新增量观察：'):lines[n]=f'最新增量观察：{D["completedAt"]}（UTC）。[本轮 3 块来源与限定 QA 审计](live-refresh-20261008-source-audit.json)。渔村日景 c12/c13 当前集成稿仍需完成所属任务接缝 QA，未继承旧稿验收结论。'
        t='\n'.join(lines)+'\n'
        t=t.replace('[本轮增量审计](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/parent_audit_20261008/delta-latest.json)','[本轮增量审计](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/parent_audit_20261008/live-refresh-20261008-source-audit.json)')
    p.write_text(t,encoding='utf-8')
p=B/'README.md';t=p.read_text(encoding='utf-8');first,rest=t.split('\n\n',1);first=first.replace('45/1792','48/1792').replace('1747','1744');p.write_text(first+'\n\n'+rest,encoding='utf-8')
print(json.dumps({'result':'48_published_pending_preview_layout_view','count':48,'preview':preview.as_posix(),'indexSha':sha(ip)},ensure_ascii=False))
