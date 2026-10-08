from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005');B=P.parent.parent;A=P/'parent_audit_20261008';E=P/'parent_expansion_20261008/child-selected'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ip=A/'verified-current-index.json';I=read(ip);assert I['summary']['completePixelCandidateCount']==51
assert I['preview']['visualReview']['status']=='passed'
oldp=A/'parent-repair-current-overlay-v2.json';op=A/'parent-repair-current-overlay-v3.json';assert not op.exists()
overlay=read(oldp);audit=read(E/'audit.json');complete=audit['selectedEntry'];assert audit['newCoordinateEligible'];assert sha(complete['file'])==complete['sha256']
old=next(e for e in overlay['candidates'] if e['tile']=='r08_c10');oldcopy=copy.deepcopy(old);old.clear();old.update(complete)
overlay['previousOverlay']=ref(oldp);overlay['retiredPartialSelectionEvidence']=oldcopy
overlay.update(createdAtUtc=datetime.now(timezone.utc).isoformat(),completeCandidateCount=12,partialCandidateCount=0,partialCandidatesPreservedVerbatim=False,completedC10SourceAudit=ref(E/'audit.json'))
overlay['supersessionScope']='Prior c09 current-child migration and five parent repair choices unchanged. Replace historical r08_c10 partial entry with already counted current child complete native candidate. This package adds zero new coordinates beyond the parent index.'
assert len({e['tile'] for e in overlay['candidates']})==len(overlay['candidates'])==12
for e in overlay['candidates']:assert sha(e['file'])==e['sha256']
dump(op,overlay)
proofp=A/'overlay-complete-c10-binding.json';proof={'createdAtUtc':overlay['createdAtUtc'],'priorOverlay':ref(oldp),'currentOverlay':ref(op),'sourceAudit':ref(E/'audit.json'),'completedCoordinate':'r08_c10','completedImage':ref(complete['file']),'parentModifiedCoordinatesUnchanged':overlay['parentModifiedCoordinates'],'parentModifiedCount':5,'completeCandidateCount':12,'partialCandidateCount':0,'parentIndexCountUnchanged':51,'formalAccepted':False,'artModified':False};dump(proofp,proof)
package=I['parentRepairPackage'];previous=copy.deepcopy(package);package['previousPackageBeforeCompleteC10Promotion']=previous;package.update(path=op.as_posix(),sha256=sha(op),completeCandidateCount=12,partialCandidateCount=0,completedC10PackageBinding=ref(proofp),validatedAt=overlay['createdAtUtc'])
I['parentPackageEntryValidation']=ref(proofp);dump(ip,I)
S=read(B/'status.json');S['parentRepairPackage']=copy.deepcopy(package);S['currentBatchSha256']=sha(ip);S['latestContinuation']['checkpoint']['sha256']=sha(ip)
for k in ['continuationWork','activeProductionRun','latestContinuation']:S[k]['parentRepairPackage']=op.relative_to(B).as_posix()
dump(B/'status.json',S)
for p in [A/'README.md',P/'README.md']:
 t=p.read_text(encoding='utf-8').replace(oldp.name,op.name)
 if p==A/'README.md':
  t=t.replace('渔村元宵 c12/c13 最新局部修补如纳入本次选择，仅沿用已绑定像素的局部检查，日景铺地几何同步仍待完成。','渔村元宵 c13 的新输出虽已完成来源与局部 QA 绑定，但观察时尚未由子任务当前选择登记，本次不计数；日景铺地几何同步仍待完成。')
  t=t.replace('这 5 处仍附在原坐标的 parentRepairCandidate 中，不增加坐标。','这 5 处仍附在原坐标的 parentRepairCandidate 中，不增加坐标。父包中的旧 c10 片段也已换为本次已计数的完整 child 候选，父包现含12完整坐标、0片段；c09迁移保持原父修补像素和当前 child 接边像素互不覆盖。')
 p.write_text(t,encoding='utf-8')
p=B/'README.md';t=p.read_text(encoding='utf-8');first,rest=t.split('\n\n',1);first=first.replace(oldp.name,op.name);p.write_text(first+'\n\n'+rest,encoding='utf-8')
validation=read(A/'latest-publication-validation.json');validation['index']=ref(ip);validation['currentParentOverlay']=ref(op);validation['completeC10OverlayBinding']=ref(proofp);dump(A/'latest-publication-validation.json',validation)
print(json.dumps({'index':ref(ip),'parentOverlay':ref(op),'verification':ref(A/'latest-publication-validation.json'),'count':51,'distribution':[len(a['entries']) for a in I['appearances']],'formal':0}))
