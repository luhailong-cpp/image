from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import argparse,json,hashlib,copy
B=Path('D:/work/image/qdao_city_tiles_4k_20260916');P=B/'builtin_q64_production/parallel_20261005';A=P/'parent_audit_20261008'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scope_file=P/'production-scope.json'
if scope_file.exists():
 scope=read(scope_file)
 legacy=['tianyong_festival','lanxian_day','lanxian_spring','donghai_day','donghai_lantern','penglai_day','penglai_mid_autumn']
 if scope.get('activeAppearanceIds')!=legacy or scope.get('targetTotalTiles')!=1792:
  raise SystemExit('Refusing legacy seven-appearance publication: production-scope.json changed the authorized scope. Use a scope-aware publisher; no files were written.')
ap=argparse.ArgumentParser();ap.add_argument('--delta');ap.add_argument('--finalize-layout',action='store_true');args=ap.parse_args()
ip=A/'verified-current-index.json';I=read(ip);before=sha(ip);now=datetime.now(timezone.utc).isoformat()
if args.finalize_layout:
 assert I['preview']['visualReview']['status']=='pending_layout_review'
 assert sha(I['preview']['path'])==I['preview']['sha256']
 I['preview']['visualReview']={'status':'passed','reviewedAtUtc':now,'method':'Actual view_image opened overview.jpg; verified layout, seven cards, counts, scope labels and missing-cell marks. Preview only, not native artwork acceptance.'}
 dump(ip,I);S=read(B/'status.json');S['currentBatchSha256']=sha(ip);S['latestContinuation']['checkpoint']['sha256']=sha(ip)
 S['candidateVisualReview']={'reviewedAtUtc':now,'actuallyViewed':True,'file':I['preview']['path'],'sha256':I['preview']['sha256'],'scope':'Overview layout only; seven cards, current count, labels and missing-cell marks. Not artwork acceptance.','findings':[]}
 S['continuationWork']['parentRepairPackage']=Path(I['parentRepairPackage']['path']).relative_to(B).as_posix()
 dump(B/'status.json',S)
 proof={'verifiedAtUtc':now,'index':ref(ip),'overview':ref(A/'overview.jpg'),'delta':I['latestDeltaAudit'],'count':I['summary']['completePixelCandidateCount'],'missing':I['summary']['missingFullPixelCoordinates'],'allSourcesAndParentAlternativesVerified':True,'previewLayoutActuallyViewed':True,'formalAcceptedCount':0,'wholeCityCompleteCount':0,'childModified':False}
 dump(A/'latest-publication-validation.json',proof);print(json.dumps(proof));raise SystemExit
assert args.delta
dp=Path(args.delta);D=read(dp);assert D['baseParentIndex']['sha256']==before
oldcount=I['summary']['completePixelCandidateCount'];oldmissing=1792-oldcount
repairs_before={(a['appearance'],e['tileId']):copy.deepcopy(e['parentRepairCandidate']) for a in I['appearances'] for e in a['entries'] if 'parentRepairCandidate' in e}
assert len(repairs_before)==5
for s in D['proofs']:assert sha(s['path'])==s['sha256'],s['path']
newcoords=[];samecoords=[]
for change in D['changes']:
 app=next(x for x in I['appearances'] if x['appearance']==change['appearance']);e=copy.deepcopy(change['entry'])
 assert e['fullPixelCandidate'] and e['formalAccepted'] is False
 assert sha(e['path'])==e['sha256'];assert sha(e['generationRecord']['path'])==e['generationRecord']['sha256']
 assert sha(e['selectionSource']['path'])==e['selectionSource']['sha256']
 old=next((x for x in app['entries'] if x['tileId']==e['tileId']),None)
 if old:
  if 'parentRepairCandidate' in old:
   migration=next((m for m in D.get('parentRepairMigrations',[]) if m['appearance']==change['appearance'] and m['tileId']==e['tileId']),None)
   assert migration and migration['oldParentSha256']==old['parentRepairCandidate']['sha256']
   assert e['parentRepairCandidate']['sha256']==migration['newParentSha256']
   assert sha(migration['proof']['path'])==migration['proof']['sha256']
  e['previousSelectedSnapshot']=copy.deepcopy(old);app['entries'].remove(old);samecoords.append((change['appearance'],e['tileId']))
 else:newcoords.append((change['appearance'],e['tileId']))
 app['entries'].append(e)
for a in I['appearances']:
 a['entries'].sort(key=lambda e:e['tileId']);a['completePixelCandidateCount']=len(a['entries']);a['missingOf256']=256-len(a['entries'])
count=sum(len(a['entries']) for a in I['appearances']);missing=1792-count
assert count==oldcount+len(newcoords)==D['expectedTotal']
I.setdefault('historicalAggregateSummaries',[]).append({'summary':copy.deepcopy(I['summary']),'indexSha256':before,'supersededAt':now,'scope':'Prior selected-coordinate snapshot, retained as history.'})
I['summary'].update(completePixelCandidateCount=count,missingFullPixelCoordinates=missing)
I['observedAt']=I['updatedAt']=now
I['snapshotScope']=f'七任务来源核验的 {count} 坐标快照，另附 5 个同坐标 parentRepairCandidate。完整像素候选不等于正式游戏成品；所有范围限定 QA 只沿用绑定像素。'
I.setdefault('priorDeltaAudits',[]).append(I['latestDeltaAudit']);I['latestDeltaAudit']=I['latestLiveDelta']=ref(dp)
if I.get('latestCompleteCoordinateCountAudit'):I.setdefault('historicalCompleteCoordinateCountAudits',[]).append(I['latestCompleteCoordinateCountAudit'])
I['latestCompleteCoordinateCountAudit']=ref(dp)
I.setdefault('historicalIncompleteWorkSnapshots',[]).append(I.get('activeIncompleteWork',{}));I['activeIncompleteWork']={'observedAt':now,'note':'Prior partial snapshots are historical; latest selected additions supersede only their named coordinates. Other partial and unselected repair drafts remain excluded.','source':ref(dp)}
I['currentRegistryObservations']={'observedAt':now,'source':ref(dp),'newCoordinateSelections':newcoords,'sameCoordinateSelections':samecoords}
if D.get('parentRepairOverlay'):
 overlay=D['parentRepairOverlay'];assert sha(overlay['path'])==overlay['sha256']
 previous=copy.deepcopy(I['parentRepairPackage']);I['parentRepairPackage']['previousPackageBeforeC09Migration']=previous;I['parentRepairPackage'].update(path=overlay['path'],sha256=overlay['sha256'],currentSourceMigration=ref(dp))

W,H=1808,1920;im=Image.new('RGB',(W,H),'#eef2f7');dr=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if b else 'C:/Windows/Fonts/msyh.ttc',n)
dr.text((28,20),'七套主城 · 现有区域缩略预览',font=font(32,True),fill='#1d2d44')
dr.text((28,70),f'完整像素候选 {count} / 1792  |  7 套均未完成  |  灰格为缺块  |  仅展示当前已选区域，不是整城图',font=font(20),fill='#4d5c70')
sources=[];groups=[]
for j,a in enumerate(I['appearances']):
 x,y=28+(j%2)*888,116+(j//2)*450;dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='white',outline='#d9e1eb',width=2)
 dr.text((x+18,y+16),f"{j+1:02d}  {a['title']}",font=font(24,True),fill='#1d2d44');dr.text((x+694,y+18),f"{len(a['entries'])} / 256 块",font=font(21),fill='#476483')
 coords={(int(e['tileId'][1:3]),int(e['tileId'][5:7])):e for e in a['entries']};r0,r1=min(z[0] for z in coords),max(z[0] for z in coords);c0,c1=min(z[1] for z in coords),max(z[1] for z in coords)
 dr.text((x+18,y+48),f'范围 r{r0:02d}–r{r1:02d} / c{c0:02d}–c{c1:02d} · 相同比例缩小，非原尺寸验收',font=font(14),fill='#778392')
 size=min(112,784//(c1-c0+1),336//(r1-r0+1));gx,gy=x+(864-(c1-c0+1)*size)//2,y+71+(336-(r1-r0+1)*size)//2;holes=[]
 for r in range(r0,r1+1):
  for c in range(c0,c1+1):
   px,py=gx+(c-c0)*size,gy+(r-r0)*size;tid=f'r{r:02d}_c{c:02d}';e=coords.get((r,c))
   if e:
    raw=Path(e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256']
    with Image.open(BytesIO(raw)) as src:
     assert src.size==(4096,4096);assert 'A' not in src.getbands() or src.getchannel('A').getextrema()==(255,255)
     im.paste(src.convert('RGB').resize((size,size),Image.Resampling.LANCZOS),(px,py))
    sources.append({'appearance':a['appearance'],'tileId':tid,'path':e['path'],'sha256':e['sha256'],'expectedShaMatches':True,'sourcePixels':[4096,4096],'previewPixels':[size,size],'scaleX':size/4096,'scaleY':size/4096,'resampling':'LANCZOS downsampling','stretch':False,'destinationRectXYWH':[px,py,size,size]})
   else:
    holes.append(tid);dr.rectangle((px,py,px+size-1,py+size-1),fill='#5d697a');dr.text((px+size//3,py+size//3),'缺块',font=font(20),fill='#dce1e9')
   dr.rectangle((px,py,px+size-1,py+size-1),outline='#edf0f4');dr.rectangle((px+2,py+2,px+73,py+18),fill='#1d2d44');dr.text((px+4,py+2),tid,font=font(11),fill='white')
 groups.append({'appearance':a['appearance'],'bboxTileRowsInclusive':[r0,r1],'bboxTileColumnsInclusive':[c0,c1],'tilePreviewPixels':[size,size],'missingCoordinatesInsideBBox':holes})
x,y=916,1466;dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='#1d2d44');dr.text((x+28,y+30),'当前候选总数',font=font(25,True),fill='#dce5ef');dr.text((x+28,y+82),f'{count} / 1792',font=font(58,True),fill='white');dr.text((x+28,y+164),f'尚缺完整像素图块 {missing} 块',font=font(24,True),fill='#f5c963')
for n,t in enumerate(['正式验收：0 块    整套完成：0 / 7','按真实行列缩小；灰格与细网格是预览标记。','父修补 5 个同坐标备选单独索引，不重复计数。',f'本次新增 {len(newcoords)} 坐标，同坐标同步 {len(samecoords)} 处。','新候选的接缝、跨外观及整城检查仍有限制。']):dr.text((x+28,y+224+n*33),t,font=font(19),fill='#dce5ef')
assert sha(ip)==before
for s in sources:assert sha(s['path'])==s['sha256']
for (app,tid),r in repairs_before.items():
 assert sha(r['path'])==r['sha256'];current=next(e for a in I['appearances'] if a['appearance']==app for e in a['entries'] if e['tileId']==tid)
 migration=next((m for m in D.get('parentRepairMigrations',[]) if m['appearance']==app and m['tileId']==tid),None)
 if migration:assert sha(current['parentRepairCandidate']['path'])==current['parentRepairCandidate']['sha256']==migration['newParentSha256']
 else:assert current['parentRepairCandidate']==r
assert sum('parentRepairCandidate' in e for a in I['appearances'] for e in a['entries'])==5
preview=A/'overview.jpg';im.save(preview,quality=94,subsampling=0)
I['preview']={'path':preview.as_posix(),'sha256':sha(preview),'pixels':[W,H],'createdAt':now,'kind':'mechanical-downsample-contact-sheet-only','notGameAsset':True,'notWholeCity':True,'sourcePixelsGenerated':False,'sourcePixelsModified':False,'sources':sources,'groups':groups,'visualReview':{'status':'pending_layout_review'}}
I['liveAggregationValidation']={'checkedAt':now,'sourceCount':count,'uniqueCoordinateCount':count,'allSourceHashesMatchedBeforePreviewWrite':True,'allSourcesDecoded4096':True,'allSourcesFullyOpaque':True,'newCoordinates':len(newcoords),'sameCoordinateUpdates':len(samecoords),'formalAcceptedCount':0,'wholeCityCompleteCount':0,'fiveParentRepairAlternativesPreserved':True,'source':ref(dp)}
dump(ip,I)
S=read(B/'status.json')
for k in ['generated4KCandidateCount','currentSelectedCandidateCoordinateCountAllAppearances']:S[k]=count
S.update(updatedAtUtc=now,currentBatchSha256=sha(ip),candidatePreviewSha256=sha(preview),scope=f'Seven 65536x65536 appearances in production: {count} unique complete-pixel 4096x4096 candidates of 1792; {missing} missing, 0 formally accepted, 0 complete cities. Five same-coordinate parent repair candidates add no coordinates.',candidatePreviewMeaning=f'{count}-coordinate selected snapshot; five parent repair alternatives remain separate.')
S['candidateVisualReview']={'status':'pending','actuallyViewed':False,'file':preview.as_posix(),'sha256':sha(preview),'scope':'Awaiting actual overview layout inspection.'}
S['candidateFiles']=[Path(e['path']).relative_to(B).as_posix() for a in I['appearances'] for e in a['entries']]
S['scopeDecision'].update(currentCompletePixelCandidateCount=count,remainingFullPixelCoordinates=missing)
S['activeProductionRun'].update(updatedAtUtc=now,currentCompletePixelCandidateCount=count,remainingFullPixelCoordinates=missing);S['activeProductionRun']['countMeaning']=S['activeProductionRun']['countMeaning'].replace(f'{oldcount} unique',f'{count} unique')
S['latestContinuation'].update(updatedAtUtc=now,currentWorkingCoordinates=count,tianyongWorkingCoordinates=len(I['appearances'][0]['entries']),latestLiveDelta=ref(dp));S['latestContinuation']['checkpoint']['sha256']=sha(ip)
if D.get('parentRepairOverlay'):
 overlayRelative=Path(D['parentRepairOverlay']['path']).relative_to(B).as_posix();S['activeProductionRun']['parentRepairPackage']=overlayRelative;S['latestContinuation']['parentRepairPackage']=overlayRelative
 S['parentRepairPackage']=copy.deepcopy(I['parentRepairPackage'])
 S['continuationWork']['parentRepairPackage']=overlayRelative
S['counterMeaning']=S['counterMeaning'].replace(f'{oldcount} counts',f'{count} counts');S['baselineSelectionCountMeaning']=S['baselineSelectionCountMeaning'].replace(f'{oldcount}-coordinate',f'{count}-coordinate');dump(B/'status.json',S)
rows='\n'.join(f"| {a['title']} | {len(a['entries'])} | {256-len(a['entries'])} | 0 |" for a in I['appearances'])
addition_lines='\n'.join(f"- `{app} / {tid}`" for app,tid in newcoords)
text=f'''# 七套主城当前候选汇总

来源与像素复核时间：{now}（UTC）。

**当前 {count} / 1792 块完整像素候选，尚缺 {missing} 块。7 套均未完成，正式验收 0 块。**

| 套图 | 完整像素候选 | 尚缺 / 256 | 正式验收 |
|---|---:|---:|---:|
{rows}

[统一索引](verified-current-index.json) · [本轮增量及来源]({dp.name}) · [最终汇总验证](latest-publication-validation.json)

![现有区域缩略预览](overview.jpg)

上图按真实行列等比缩小，仅展示当前已选区域，灰格是缺块；缩略图不是正式游戏素材，也不用于原尺寸验收。全部当前图像 SHA、4096×4096 完整不透明像素与父修补引用均已再次核验。

## 本次新增

{addition_lines}

新增只有完整像素候选含义。仙岛日景 r09_c14 的所属原尺寸检查明确记录内部及西侧材质直缝，r10_c13 接缝 QA 也未完成。渔村元宵 c12/c13 最新局部修补如纳入本次选择，仅沿用已绑定像素的局部检查，日景铺地几何同步仍待完成。主城新块的未检查范围以对应来源审计为准。

同坐标同步：{', '.join(app+'/'+tid for app,tid in samecoords) or '无'}。未更改七个子任务的选择或图像。未选中的加工稿、未完成片段及已拒稿来源均不重复计数。

## 父任务当前修补包

[5 个同坐标修补稿与来源]({Path(I['parentRepairPackage']['path']).name}) · [tone 局部独立复核](west-upper-tone-independent-review.json) · [37 个历史限定 QA 的像素转移](../parent_repairs_20261008/current/qa-transfer.json)

| 坐标 | 父修补候选 |
|---|---|
| r08_c07 | [4096 PNG](../parent_repairs_20261008/west-upper-tone/final-output/r08_c07.png) |
| r08_c08 | [4096 PNG](../parent_repairs_20261008/west-upper-tone/final-output/r08_c08.png) |
| r08_c09 | [4096 PNG]({next(e['parentRepairCandidate']['path'] for a in I['appearances'] for e in a['entries'] if e['tileId']=='r08_c09' and 'parentRepairCandidate' in e)}) |
| r09_c08 | [4096 PNG](../parent_repairs_20261008/current/r09_c08.png) |
| r09_c09 | [4096 PNG](../parent_repairs_20261008/current/r09_c09.png) |

这 5 处仍附在原坐标的 parentRepairCandidate 中，不增加坐标。西上方灰石明暗直缝与金边高光台阶只在新增1254窗口和8张原尺寸QA范围内通过检查。旧37个QA仅沿用像素不变区域；右角范围外轻微色阶和其他未审查边界仍有限制。完整边界、整块、整城、寻路和客户端均未验收。

## 历史证据

[前轮三块新增来源审计](live-refresh-20261008-source-audit.json) · [渔村日景 c13/c14 来源及 QA 绑定](donghai-c13-current-update-audit.json) · [共享边检查记录](shared-edge-priority.json) · [小镇 QA 补证](town/qa-binding-supplement.json)

旧报告中的候选数、文件哈希和局部结论均属于当时快照；最新选择及剩余限制以本页和统一索引为准。
'''
(A/'README.md').write_text(text,encoding='utf-8')
p=P/'README.md';t=p.read_text(encoding='utf-8');t=t.replace(f'当前 {oldcount} 块',f'当前 {count} 块').replace(f'{oldcount}/1792',f'{count}/1792').replace(f'尚缺 {oldmissing}',f'尚缺 {missing}')
if D.get('parentRepairOverlay'):t=t.replace('parent-repair-current-overlay.json',Path(D['parentRepairOverlay']['path']).name)
lines=t.splitlines()
for i,l in enumerate(lines):
 if l.startswith('2026-10-08 已核验快照'):
  counts={a['appearance']:len(a['entries']) for a in I['appearances']};lines[i]=f'2026-10-08 已核验快照为 **{count}/1792 个完整 4K 候选坐标，尚缺 {missing}；正式验收 0、完整城市 0/7**。主城节庆 {counts["tianyong_festival"]}，小镇日景/春节各 7，渔村日景 {counts["donghai_day"]}、元宵 {counts["donghai_lantern"]}，仙岛日景 {counts["penglai_day"]}、中秋 {counts["penglai_mid_autumn"]}。5 处同坐标父修补单独挂接且不增加块数；当前完整候选仍可能有接缝或跨外观检查未完成。来源与范围详见统一索引。'
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=B/'README.md';t=p.read_text(encoding='utf-8');first,rest=t.split('\n\n',1);first=first.replace(f'{oldcount}/1792',f'{count}/1792').replace(f'尚缺 {oldmissing}',f'尚缺 {missing}')
if D.get('parentRepairOverlay'):first=first.replace('parent-repair-current-overlay.json',Path(D['parentRepairOverlay']['path']).name)
p.write_text(first+'\n\n'+rest,encoding='utf-8')
print(json.dumps({'count':count,'missing':missing,'newCoordinates':newcoords,'sameCoordinateUpdates':samecoords,'indexSha256':sha(ip),'status':'published_pending_actual_layout_view'}))
