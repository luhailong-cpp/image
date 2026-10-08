from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
import json,hashlib,copy
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005');A=P/'parent_audit_20261008';E=P/'parent_expansion_20261008/child-selected';T=P/'tianyong_festival'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
now=datetime.now(timezone.utc).isoformat();ip=A/'verified-current-index.json';I=read(ip);assert I['summary']['completePixelCandidateCount']==48
tp=E/'audit.json';ta=read(tp);assert sha(tp)=='eb4ec929c21e3463c273a4601c88b9707834af8010ddf3bd50d715455752af81'
assert ta['newCoordinateEligible'] and ta['coveragePixels']==4096*4096 and not ta['formalAccepted']
for p,h in ta['checkedFileHashes'].items():assert sha(p)==h,p
for q in ta['qa']:assert sha(q['file'])==q['sha256'] and q['actuallyViewed']
current=read(T/'current-work.json');sp=Path(current['candidateSet']);selection=read(sp)
for key in ['selectedEntry','childPairedWest']:
 o=ta[key];s=next(x for x in selection['candidates'] if x['tile']==o['tile'])
 assert s['sha256']==o['sha256'] and Path(s['file']).resolve()==Path(o['file']).resolve() and s['fullyPainted'] and not s['partialFragment']
old=next(e for a in I['appearances'] if a['appearance']=='tianyong_festival' for e in a['entries'] if e['tileId']=='r08_c09')
parent=old['parentRepairCandidate'];new=ta['parentCompatibleWest'];child=ta['childPairedWest']
for o in [new,child]:assert sha(o['file'])==o['sha256']
assert sha(old['path'])==old['sha256'];assert sha(parent['path'])==parent['sha256']
b=rgb(old['path']);r=rgb(parent['path']);c=rgb(child['file']);n=rgb(new['file']);rd=np.any(r!=b,axis=2);cd=np.any(c!=b,axis=2)
overlap=int(np.count_nonzero(rd&cd));assert overlap==0
expected=c.copy();expected[rd]=r[rd];assert np.array_equal(expected,n)
assert int(np.count_nonzero(np.any(n!=c,axis=2)))==new['changedPixels']==74364
mp=A/'tian-c09-parent-migration-verification.json'
proof={'verifiedAtUtc':now,'status':'pass_disjoint_pixel_transfer_and_current_child_selection','priorChild':ref(old['path']),'priorParent':ref(parent['path']),'currentChild':ref(child['file']),'migratedParent':ref(new['file']),'sourceAudit':ref(tp),'observedCurrentSelection':ref(sp),'oldParentChangedPixels':int(rd.sum()),'currentChildChangedPixels':int(cd.sum()),'overlappingChangePixels':overlap,'outputExactlyCurrentChildPlusPriorParentDelta':True,'existingParentRepairPixelsUnchanged':True,'childChangedPixelsUnchanged':True,'qaScope':'Only source-bound historical parent repair and six owner-viewed current child return/detail crops. No whole-edge or tile acceptance.','formalAccepted':False}
dump(mp,proof)
op=A/'parent-repair-current-overlay-v2.json';overlay=read(A/'parent-repair-current-overlay.json');overlay['previousOverlay']=ref(A/'parent-repair-current-overlay.json');overlay['createdAtUtc']=now;overlay['c09Migration']=ref(mp)
oe=next(e for e in overlay['candidates'] if e.get('tile')=='r08_c09');oe['previousParentCandidate']=copy.deepcopy(oe);oe.update(file=new['file'],sha256=new['sha256'],generationRecord=new['file']+'.generation.json',formalAccepted=False,sourceMigration=ref(mp),currentChild=ref(child['file']))
overlay['supersessionScope']='Only r08_c09 migrated to current child using exact disjoint prior parent repaired pixels. Prior tone r08_c07/r08_c08 and other parent choices remain unchanged; five modified coordinates total.'
dump(op,overlay)
parent2=copy.deepcopy(parent);parent2['previousParentCandidate']=copy.deepcopy(parent);parent2.update(path=Path(new['file']).as_posix(),sha256=new['sha256'],generationRecord=ref(new['file']+'.generation.json'),selectionSource=ref(op),sourceMigration=ref(mp),currentChild=ref(child['file']))
parent2['validationScope']='Exact disjoint parent repair migration on current child c09; six current child local QA scopes bound by expansion audit. Historical parent QA transfers only along unchanged pixels. No whole edge/tile/city acceptance.'
parent2['qaEvidence']={'priorBoundLocalEvidence':parent['qaEvidence'],'currentChildScopedAudit':ref(tp),'exactMigration':ref(mp)}
changes=[]
pp=A/'penglai-new-coordinate-source-audit.json';pa=read(pp)
for p in pa['additions']:
 for k in ['core','generationRecord','selectionSource']:assert sha(p[k]['path'])==p[k]['sha256']
 entry={'tileId':p['tileId'],'path':p['core']['path'],'sha256':p['core']['sha256'],'width':4096,'height':4096,'fullPixelCandidate':True,'formalAccepted':False,'selectionSource':p['selectionSource'],'selectionSnapshot':p['selectedEntry'],'generationRecord':p['generationRecord'],'auditSource':ref(pp),'qaEvidence':p['qaEvidence'],'qaStatus':p['qaStatus'],'remainingLimitations':p['remainingLimitations'],'observedAt':now,'sourceCount':16}
 changes.append({'appearance':'penglai_day','entry':entry})
for key in ['selectedEntry','childPairedWest']:
 p=ta[key];entry={'tileId':p['tile'],'path':Path(p['file']).as_posix(),'sha256':p['sha256'],'width':4096,'height':4096,'fullPixelCandidate':True,'formalAccepted':False,'selectionSource':ref(sp),'selectionSnapshot':p,'generationRecord':ref(p['generationRecord']),'auditSource':ref(tp),'qaEvidence':[ref(tp)],'qaStatus':'source reconstruction and six exact native return/detail crops checked; all other tile and city scopes pending','remainingLimitations':ta['limitations'],'observedAt':now}
 if key=='childPairedWest':entry['parentRepairCandidate']=parent2
 changes.append({'appearance':'tianyong_festival','entry':entry})
delta={'createdAtUtc':now,'baseParentIndex':ref(ip),'expectedTotal':51,'formalAcceptedCount':0,'proofs':[ref(tp),ref(pp),ref(mp),ref(op)],'changes':changes,'parentRepairOverlay':ref(op),'parentRepairMigrations':[{'appearance':'tianyong_festival','tileId':'r08_c09','oldParentSha256':parent['sha256'],'newParentSha256':new['sha256'],'proof':ref(mp)}],'newCoordinateCount':3,'sameCoordinateUpdateCount':1,'excludedUnselected':[{'appearance':'donghai_lantern','tile':'r08_c13','reason':'Source/QA binding audit is complete but latest observed child selection has not registered output; defer until next valid selected snapshot.','sourceAudit':ref(A/'donghai-lantern-c13-source-audit.json')},{'appearance':'tianyong_festival','tile':'r07_c10','reason':'Current canvas still partial, not a complete coordinate.'}],'childModified':False}
dp=A/'selected-51-delta.json';dump(dp,delta);print(json.dumps({'delta':ref(dp),'migration':ref(mp),'overlay':ref(op),'expectedTotal':51,'childSelectedAtObservation':sp.as_posix()}))
