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
I, D, S = read(ip), read(A/'latest-live-delta.json'), read(B/'status.json')
before = sha(ip)
assert I['summary']['completePixelCandidateCount'] == 44
assert D['expectedAggregateCount'] == 45 and not D['checkFailures']
for u in D['selectedSameCoordinateUpdates']:
    assert u['qualifiedForSameCoordinateUpdate']
    a = next(a for a in I['appearances'] if a['appearance'] == u['appearance'])
    e = next(e for e in a['entries'] if e['tileId'] == u['tileId'])
    prior = copy.deepcopy(e)
    for key in ['path','sha256','width','height','fullPixelCandidate','selectionSource','generationRecord','qaEvidence','qaStatus','observedAt']:
        e[key] = u[key]
    e['previousSelectedSnapshot'] = prior
    e['auditSource'] = ref(A/'latest-live-delta.json')
    e['auditEntryPointer'] = '/selectedSameCoordinateUpdates/'+str(D['selectedSameCoordinateUpdates'].index(u))
    if 'selectionRule' in u: e['selectionRule'] = u['selectionRule']
for n in D['newQualifiedCoordinates']:
    a = next(a for a in I['appearances'] if a['appearance'] == n['appearance'])
    assert not any(e['tileId'] == n['tileId'] for e in a['entries'])
    e = copy.deepcopy(n); e.pop('appearance')
    e['auditSource'] = ref(A/'latest-live-delta.json')
    e['auditEntryPointer'] = '/newQualifiedCoordinates/'+str(D['newQualifiedCoordinates'].index(n))
    a['entries'].append(e)
for a in I['appearances']:
    a['entries'].sort(key=lambda e:e['tileId'])
    a['completePixelCandidateCount'] = len(a['entries'])
    a['missingOf256'] = 256-len(a['entries'])
I.setdefault('historicalAggregateSummaries', []).append({'summary':copy.deepcopy(I['summary']), 'indexSha256':before, 'supersededAt':now, 'scope':'historical text snapshot before latest-live delta'})
I['summary']['completePixelCandidateCount'] = 45
I['summary']['missingFullPixelCoordinates'] = 1747
I['snapshotScope'] = '七任务权威选择和绑定来源的 45 坐标快照，另附 5 个同坐标 parentRepairCandidate。完整像素候选不等于正式游戏成品，父修补引用不替换子任务选择。'
I['observedAt'], I['updatedAt'] = D['completedAt'], now
I.setdefault('priorDeltaAudits', []).append(I['latestDeltaAudit'])
I['latestDeltaAudit'] = I['latestLiveDelta'] = ref(A/'latest-live-delta.json')
I.setdefault('historicalIncompleteWorkSnapshots', []).append(I['activeIncompleteWork'])
I['activeIncompleteWork'] = {'observedAt':D['observedAt'], 'excludedFromAdditionalCount':D['excludedFromAdditionalCount'], 'registryObservationsSource':ref(A/'latest-live-delta.json')}
I['currentRegistryObservations'] = D['registryObservations']
I['parentRepairPackage']['retirementRecord'] = ref(P/'parent_repairs_20261008/retirement.json')
I['parentIndexValidation'].update(historicalIdentityOnly=True, scope='Historical 44-coordinate parent repair integration check; latest source selections and count are bound by latestLiveDelta.')
old_alts = I['unpromotedAlternatives']
promoted = [x for x in old_alts if x['appearance']=='donghai_lantern' and x['tileId'] in ['r08_c11','r08_c12']]
I.setdefault('historicalPromotedAlternatives', []).extend([dict(x,promotedAt=now,historicalIdentityOnly=True,runtimeDependency=False) for x in promoted])
I['unpromotedAlternatives'] = [x for x in old_alts if x not in promoted]

# Only downsample and place the saved tile pixels; no artwork edits or upscaling.
W, H = 1808, 1920
im = Image.new('RGB', (W,H), '#eef2f7'); dr = ImageDraw.Draw(im)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)
dr.text((28,20), '七套主城 · 现有区域缩略预览', font=font(32,True), fill='#1d2d44')
dr.text((28,70), '完整像素候选 45 / 1792  |  7 套均未完成  |  灰格为缺块  |  仅展示当前已选区域，不是整城图', font=font(20), fill='#4d5c70')
sources, groups = [], []
for j, a in enumerate(I['appearances']):
    x, y = 28+(j%2)*888, 116+(j//2)*450
    dr.rounded_rectangle((x,y,x+864,y+426), radius=16, fill='white', outline='#d9e1eb', width=2)
    dr.text((x+18,y+16), f"{j+1:02d}  {a['title']}", font=font(24,True), fill='#1d2d44')
    dr.text((x+694,y+18), f"{len(a['entries'])} / 256 块", font=font(21), fill='#476483')
    coords = {(int(e['tileId'][1:3]),int(e['tileId'][5:7])):e for e in a['entries']}
    rs, cs = [p[0] for p in coords], [p[1] for p in coords]
    r0,r1,c0,c1 = min(rs),max(rs),min(cs),max(cs)
    dr.text((x+18,y+48),f'范围 r{r0:02d}–r{r1:02d} / c{c0:02d}–c{c1:02d} · 相同比例缩小，非原尺寸验收',font=font(14),fill='#778392')
    gx,gy = x+(864-(c1-c0+1)*112)//2, y+71+(336-(r1-r0+1)*112)//2
    missing=[]
    for r in range(r0,r1+1):
        for c in range(c0,c1+1):
            px,py = gx+(c-c0)*112,gy+(r-r0)*112
            tid=f'r{r:02d}_c{c:02d}'; e=coords.get((r,c))
            if e:
                raw=Path(e['path']).read_bytes()
                assert hashlib.sha256(raw).hexdigest()==e['sha256'], ('changed source',e['path'])
                with Image.open(BytesIO(raw)) as src:
                    assert src.size==(4096,4096)
                    im.paste(src.convert('RGB').resize((112,112),Image.Resampling.LANCZOS),(px,py))
                sources.append({'appearance':a['appearance'],'tileId':tid,'path':e['path'],'sha256':e['sha256'],'expectedShaMatches':True,'observedAt':now,'sourcePixels':[4096,4096],'previewPixels':[112,112],'scaleX':112/4096,'scaleY':112/4096,'resampling':'LANCZOS downsampling','stretch':False,'destinationRectXYWH':[px,py,112,112]})
            else:
                missing.append(tid); dr.rectangle((px,py,px+111,py+111),fill='#5d697a')
                dr.line((px+14,py+96,px+96,py+14),fill='#697486')
                dr.text((px+36,py+45),'缺块',font=font(20),fill='#dce1e9')
            dr.rectangle((px,py,px+111,py+111),outline='#edf0f4')
            dr.rectangle((px+2,py+2,px+73,py+18),fill='#1d2d44')
            dr.text((px+4,py+2),tid,font=font(11),fill='white')
    groups.append({'appearance':a['appearance'],'bboxTileRowsInclusive':[r0,r1],'bboxTileColumnsInclusive':[c0,c1],'tilePreviewPixels':[112,112],'missingCoordinatesInsideBBox':missing})
x,y=916,1466
dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='#1d2d44')
dr.text((x+28,y+30),'当前候选总数',font=font(25,True),fill='#dce5ef')
dr.text((x+28,y+82),'45 / 1792',font=font(58,True),fill='white')
dr.text((x+28,y+164),'尚缺完整像素图块 1747 块',font=font(24,True),fill='#f5c963')
for n,t in enumerate(['正式验收：0 块    整套完成：0 / 7','按真实行列缩小；灰格与细网格是预览标记。','父修补 5 个同坐标备选单独索引，不重复计数。','渔村 c14 含拒稿源旧合图待重建；未选稿不计。','新中秋 r10_c13 已核验来源与限定 QA。']):
    dr.text((x+28,y+224+n*33),t,font=font(19),fill='#dce5ef')
assert len(sources)==45 and sha(ip)==before
for s in sources: assert sha(s['path'])==s['sha256'], ('late source change',s['path'])
preview=A/'overview.jpg'; im.save(preview,quality=94,subsampling=0)
I['preview']={'path':preview.as_posix(),'sha256':sha(preview),'pixels':[W,H],'createdAt':now,'kind':'mechanical-downsample-contact-sheet-only','notGameAsset':True,'notWholeCity':True,'sourcePixelsGenerated':False,'sourcePixelsModified':False,'sources':sources,'groups':groups,'visualReview':{'status':'pending_layout_review'}}
dump(ip,I)
for key in ['generated4KCandidateCount','currentSelectedCandidateCoordinateCountAllAppearances']: S[key]=45
S['updatedAtUtc']=now
S['scope']=S['scope'].replace('44 unique','45 unique').replace('1748 missing','1747 missing')
S['currentBatchSha256']=sha(ip)
S['candidateFiles']=[Path(e['path']).relative_to(B).as_posix() for a in I['appearances'] for e in a['entries']]
S['candidatePreviewSha256']=sha(preview)
S['candidatePreviewMeaning']='45-coordinate selected snapshot; five parent repair alternatives remain separate.'
S['parentRepairPackage']=I['parentRepairPackage']
S['scopeDecision']['currentCompletePixelCandidateCount']=45
S['scopeDecision']['remainingFullPixelCoordinates']=1747
S['activeProductionRun'].update(updatedAtUtc=now,currentCompletePixelCandidateCount=45,remainingFullPixelCoordinates=1747)
S['activeProductionRun']['countMeaning']=S['activeProductionRun']['countMeaning'].replace('44 unique','45 unique')
S['latestContinuation'].update(currentWorkingCoordinates=45,updatedAtUtc=now,latestLiveDelta=ref(A/'latest-live-delta.json'))
S['latestContinuation']['checkpoint']['sha256']=sha(ip)
S['counterMeaning']=S['counterMeaning'].replace('44 counts','45 counts')
S['baselineSelectionCountMeaning']=S['baselineSelectionCountMeaning'].replace('44-coordinate','45-coordinate')
dump(B/'status.json',S)
for p in [A/'README.md',P/'README.md']:
    t=p.read_text(encoding='utf-8-sig')
    for old,new in [('44 / 1792','45 / 1792'),('44/1792','45/1792'),('当前 44 块','当前 45 块'),('1748','1747'),('总数仍为 44','总数仍为 45'),('展示 44 坐标','展示 45 坐标'),('| 仙岛中秋地图 | 5 | 251 | 0 |','| 仙岛中秋地图 | 6 | 250 | 0 |'),('仙岛日景/中秋各 5','仙岛日景 5、中秋 6')]: t=t.replace(old,new)
    if p==A/'README.md':
        t=t.replace('主城节庆 r08_c09 当前来源为 child v012','主城节庆 r08_c09 当前来源为 child v014')
        t=t.replace('渔村元宵最新修复替代稿需按当前权威索引晋升；本汇总不自行替换或重复计数。','渔村元宵 r08_c11/r08_c12 已由权威索引选为 west-final，父快照按来源核验同步，属于同坐标更新。')
        t=t.replace('本轮可靠新增仙岛日景 r10_c12；主城节庆 r08_c09、仙岛日景 r09_c12/r09_c13 是同坐标版本更新，不增加块数。','本轮可靠新增仙岛中秋 r10_c13，已核验 16 片原生来源与当前选定 manifest。主城节庆 r08_c09、渔村元宵 r08_c11/r08_c12、渔村日景 r08_c12/r08_c13 同步当前版本，不增加块数；此前仙岛日景 r10_c12 新增记录仍保留。')
        t+='\n最新增量观察：'+D['completedAt']+'（UTC）。[可靠新增与未计数原因](latest-live-delta.json)。渔村日景 c12/c13 当前集成稿仍需完成所属任务接缝 QA，未继承旧稿验收结论。\n'
    p.write_text(t,encoding='utf-8')
p=B/'README.md';t=p.read_text(encoding='utf-8');first,rest=t.split('\n\n',1)
first=first.replace('44/1792','45/1792').replace('1748','1747')
p.write_text(first+'\n\n'+rest,encoding='utf-8')
print(json.dumps({'result':'published_pending_preview_layout_view','count':45,'preview':preview.as_posix(),'indexSha':sha(ip)},ensure_ascii=True))
