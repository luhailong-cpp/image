from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
O=Path(__file__).resolve().parent
OUT=O/'delivery-v01';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
zones=['west','southeast','northeast','parallel'];summaries={z:read(O/z/'summary.json') for z in zones}
coverage={f'r{r:02d}_c{c:02d}':{'tileId':f'r{r:02d}_c{c:02d}','selectedCoreCount':0,'formalAccepted':False} for r in range(1,15) for c in range(1,15)}
for z in zones:
 d=summaries[z]
 for t in d['tiles']:
  if not t.get('countIncluded',True):continue
  n=t.get('usableSelectedCoreCount',t['coreCount'])
  coverage[t['tileId']]={'tileId':t['tileId'],'region':z,'selectedCoreCount':n,'candidateCoverageCoreCount':t['coreCount'],'fullSelectedCoverage':n==16,'adopted':t['adopted'],'file':t.get('file'),'sha256':t.get('sha256'),'formalAccepted':False,'evidence':(O/z/'summary.json').as_posix(),'scope':'regional frozen capture, not live production inventory'}
assert len(coverage)==196
candidates=[]
for z in zones:
 for t in read(O/z/'current-candidates.json')['candidates']:
  e={'tileId':t['tileId'],'region':z,'file':t['file'],'sha256':t['sha256'],'dimensions':t.get('dimensions',[4096,4096]),'adoptedAtRegionalCapture':t.get('adopted',False),'formalAccepted':False,'QA':t.get('QA',t.get('qa',{})),'internalQA':t.get('internalQA',t.get('qaStatus',t.get('status'))),'externalQA':t.get('externalQA',t.get('pending')),'sourceManifest':(O/z/'current-candidates.json').as_posix(),'diagnosticOnly':t.get('diagnosticOnly',False),'candidateMatchesFrozenEffectiveSelection':t.get('candidateMatchesFrozenEffectiveSelection'),'lateChange':t.get('liveSelectionChangedAfterCapture')}
  candidates.append(e)
v3=read(O/'northeast/r05_c11-v3-closeout/summary.json')
e=next(t for t in candidates if t['region']=='northeast' and t['tileId']=='r05_c11')
e.update(file=v3['candidate']['file'],sha256=v3['candidate']['sha256'],internalQA=v3['internalQA'],externalQA=v3['externalQA'],sourceManifest=(O/'northeast/r05_c11-v3-closeout/summary.json').as_posix(),lateChange=None,closeoutReplacesFrozenV2=True,openIssues=v3['openIssues'])
coverage['r05_c11'].update(file=e['file'],sha256=e['sha256'],evidence=e['sourceManifest'])
checks=[]
for t in candidates:
 p=Path(t['file']);actual=sha(p) if p.exists() else None
 checks.append({'tileId':t['tileId'],'file':p.as_posix(),'expectedSha256':t['sha256'],'actualSha256':actual,'pixelsUnchanged':actual==t['sha256']})
assert all(x['pixelsUnchanged'] for x in checks),[x for x in checks if not x['pixelsUnchanged']]
counts={'targetCoordinates':196,'frozenUniqueSelectedCores':sum(t['selectedCoreCount'] for t in coverage.values()),'targetCores':3136,'fullSelectedCoreCoordinates':sum(t['selectedCoreCount']==16 for t in coverage.values()),'partialSelectedCoordinates':sum(0<t['selectedCoreCount']<16 for t in coverage.values()),'zeroSelectedCoordinates':sum(t['selectedCoreCount']==0 for t in coverage.values()),'indexed4096Files':len(candidates),'indexedCoordinateCount':len(set(t['tileId'] for t in candidates)),'formalAcceptedCount':0,'wholeMapComplete':False}
counts['missingSelectedCores']=3136-counts['frozenUniqueSelectedCores']
write(OUT/'coverage.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'counts':counts,'scope':'Inspection-only frozen regional captures; parallel reserved coordinates replace original owner placeholders; full candidate pixels can contain held cores and do not equal selected coverage. No production record is changed.','tiles':list(coverage.values())})
write(OUT/'current-4k-index.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Version-specific inspected 4096 files; not a live selected-source list; later production deltas remain separate','counts':counts,'candidates':candidates})
write(OUT/'input-hash-check.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'only indexed current frozen 4096 outputs, not historical images','checks':checks})
reports={z:{'file':(O/z/'review.md').as_posix(),'summary':(O/z/'summary.json').as_posix(),'summarySha256':sha(O/z/'summary.json')} for z in zones}
write(OUT/'repair-index.json',{'regionIssueFiles':{z:(O/z/'repair-queue.json').as_posix() for z in zones},'r05_c11_v3':{'resolved':v3['resolvedPriorIssues'],'open':v3['openIssues'],'evidence':(O/'northeast/r05_c11-v3-closeout/summary.json').as_posix()},'priorUnchangedIssuesRemainOpen':True,'formalAccepted':False})
quick=read(O/'west/quick-delivery-group.json')
ready=[next(t for t in candidates if t['region']=='northeast' and t['tileId']==x) for x in ['r06_c12','r06_c14','r05_c11']]
ready.extend([next(t for t in candidates if t['region']=='southeast' and t['tileId']==x) for x in ['r08_c10','r14_c14']])
ready.append(next(t for t in candidates if t['region']=='parallel' and t['tileId']=='r01_c04'))
rows=['# 八仙岛可查看素材与独立检查结果','',
'本批已有素材独立检查已完成，可直接打开下列4096成图及分区报告。每张图保留当前检查版本、输入hash、内部和外边结论；正式全图验收仍为0。','',
'优先查看：','',
'| 图块 | 实际4096文件 | QA状态 |','| --- | --- | --- |']
labels={'r06_c12':'内部证据原像素核验通过；已查北边通过，其余缺邻待验。','r06_c14':'内部证据原像素核验通过；已查北边通过，其余缺邻待验。','r05_c11':'v3内部通过，旧矩形虚化解决；北边金棱小台阶仍待修，东边通过，西南缺邻。','r08_c10':'24段内部缝、9交汇独立通过；外围未闭合，生产可用选源仍有1核状态分歧。','r14_c14':'24段内部缝、9交汇独立通过；北西邻图未齐。','r01_c04':'内部及已查南边、西边底段局部连续；其余外边缺邻，未采用。'}
for t in ready:rows.append(f"| {t['tileId']} | [打开成图]({Path(t['file']).as_posix()}) | {labels[t['tileId']]} |")
rows.extend(['','西南 r10—r11、c03—c04 稳定四图小组的当前像素与既有检查一致，可先查看：',''])
for t in quick['tiles']:rows.append(f"- [{t['tileId']}]({Path(t['file']).as_posix()})")
rows.extend(['','该四图小组的内部和共享边证据可复用；r11_c03南邻r12_c03的材质问题及其余外围仍待修或待验。未重建8192拼接。','',
f"冻结检查清单按196坐标去重，共{counts['frozenUniqueSelectedCores']}个有效选中核心，{counts['fullSelectedCoreCoordinates']}处选中16核心、{counts['partialSelectedCoordinates']}处部分覆盖、{counts['zeroSelectedCoordinates']}处无选中核心。索引另列{len(candidates)}份4096文件，其中含未采用、诊断和已知失效候选；不能把文件数当作通过数。各区截点不同，后续生产仍在推进，这些数字仅用于本批检查范围，不能替代当前生产统计。",'',
'r12_c13 v04木纹修补已通过变化区检查，旧帆杆问题仍保留；r14_c11、r13_c13水面材质带、住宅金边和屋瓦断口、海岸水纹材质带等按分区问题清单保持未通过。r04_c05已拼候选落后于选中a02，r02_c12 provisional含未选失败源，均不得标为当前完整通过。','',
'- [全部4096路径与逐块QA](current-4k-index.json)','- [196坐标冻结选源覆盖](coverage.json)','- [输入hash复核](input-hash-check.json)','- [待修入口](repair-index.json)'])
for z,label in [('west','西北和西南'),('northeast','东北和海岸'),('southeast','东南'),('parallel','民居和扩展区')]:rows.append(f'- [{label}报告](../{z}/review.md)')
rows.extend(['','[r05_c11 v3完整收尾证据](../northeast/r05_c11-v3-closeout/review.md)单独绑定v3，原虚化问题已经解决，北边待修没有升级为通过。','',
'冻结后新版本入口分别保留在西区、东北、东南与并行区的增量记录。旧通过证据仅适用于像素hash未变的对应版本。当前分工已包括island_more_20261016的r04_c01/r05_c01；本包没有将旧owner空位当作这些新分工已完成或已检查。','',
'所有输出仅写入授权独立检查目录。未生成或AI修图、未修改生产选源和账本、未操作共享Git、未打断在途制作。'])
(OUT/'review.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
broken=[];links=0
for dest in re.findall(r'\]\(([^)]+)\)',(OUT/'review.md').read_text(encoding='utf-8')):
 q=Path(dest) if re.match(r'^[A-Za-z]:[/\\]',dest) else OUT/dest
 links+=1
 if not q.exists():broken.append(dest)
assert not broken,broken
write(OUT/'completion.json',{'status':'frozen_existing_material_inspection_delivery_complete','createdAtUtc':datetime.now(timezone.utc).isoformat(),'reports':reports,'counts':counts,'indexedImagesAllHashMatched':True,'reportLinksChecked':links,'brokenLinks':broken,'productionWrites':False,'gitOperations':False,'generationCalls':0,'nextWork':'later new or changed source versions and missing-neighbor boundaries only','mapComplete':False})
print(json.dumps({'counts':counts,'reportLinks':links,'brokenLinks':broken},ensure_ascii=False))
