from pathlib import Path
from datetime import datetime,timezone
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont
import argparse,json,hashlib,copy
ap=argparse.ArgumentParser();ap.add_argument('--root-review',required=True);ap.add_argument('--include-c14',action='store_true');args=ap.parse_args()
B=Path('D:/work/image/qdao_city_tiles_4k_20260916');P=B/'builtin_q64_production/parallel_20261005';A=P/'parent_audit_20261008';T=P/'parent_repairs_20261008/west-upper-tone'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();ip=A/'verified-current-index.json';I=read(ip);before=sha(ip)
assert I['summary']['completePixelCandidateCount']==48
root_review=Path(args.root_review);root_record=read(root_review)
TM=read(T/'final-manifest.json');IR=read(A/'west-upper-tone-independent-review.json')
assert IR['result']=='pass_requested_local_scopes'
assert IR['joined']['sha256']==TM['joined']['sha256']
assert [q['sha256'] for q in IR['qa']]==[q['sha256'] for q in TM['qa']]
assert [x['image']['sha256'] for x in IR['mechanicalBindingChecks']['sourceOutputs']]==[o['sha256'] for o in TM['outputs']]
assert sha(root_review)=='b42c8eb1a85401ee8bb18cc374c77e6e6f9f98ba4367bb38352e62e012945e78'
assert sha(T/'final-manifest.json')=='6b78680e6923f17dbb8a17e898d72e28b70d431a1e99c34f91bdc4683352ca47'
base_selection=P/'parent_repairs_20261008/current/current-selection.json';base=read(base_selection)
overlay=copy.deepcopy(base)
overlay['baseSelection']=ref(base_selection);overlay['createdAtUtc']=now
overlay['status']='parent_overlay_candidates_with_scoped_tone_refinement_not_formal_acceptance'
overlay['overlayReview']={'root':ref(root_review),'independent':ref(A/'west-upper-tone-independent-review.json')}
overlay['sourceToneManifest']=ref(T/'final-manifest.json')
overlay['supersessionScope']='Only r08_c07/r08_c08 parent repair paths replaced. Other parent modifications inherited from exact unchanged base candidates. Child selections untouched.'
for o in TM['outputs']:
    assert sha(o['file'])==o['sha256']
    tile=o['source']['tile'];e=next(e for e in overlay['candidates'] if e.get('tile')==tile)
    e['baseParentCandidate']=copy.deepcopy(e)
    e.update(file=o['file'],sha256=o['sha256'],generationRecord=o['file']+'.generation.json',formalAccepted=False)
    e['additionalScopeReview']=overlay['overlayReview']
    e['priorQATransferPolicy']='Earlier source-bound QA may be reused only for exactly unchanged pixel scopes. New mask and return scopes are reviewed by tone final and independent records. No current full4096 edge acceptance is inferred.'
    e['remainingLimitations']=['Tone straight line and gold-highlight step cleared only within the new1254 window and eight native QA crops.','Other unreviewed full tile edges, missing neighbors, complete city and client/navigation remain pending.']
op=A/'parent-repair-current-overlay.json';dump(op,overlay)
tian=next(a for a in I['appearances'] if a['appearance']=='tianyong_festival')
for o in TM['outputs']:
    e=next(e for e in tian['entries'] if e['tileId']==o['source']['tile']);old=copy.deepcopy(e['parentRepairCandidate'])
    p=copy.deepcopy(old);p['previousParentCandidate']=old
    p.update(path=Path(o['file']).as_posix(),sha256=o['sha256'],generationRecord=ref(o['file']+'.generation.json'),selectionSource=ref(op))
    p['repairBranches']=old['repairBranches']+['west-upper-tone','west-upper-tone/trim-gap']
    p['qaEvidence']={'baseScopedEvidence':old['qaEvidence'],'baseEvidenceTransferPolicy':'Only unchanged pixel scopes may inherit old QA; old full-image hashes are historical identity.','rootToneReview':ref(root_review),'independentToneReview':ref(A/'west-upper-tone-independent-review.json'),'toneManifest':ref(T/'final-manifest.json')}
    p['validationScope']='New1254 tone window plus8 native return/detail crops; output/QA pixel reconstruction and unchanged-mask checks passed. No complete4096 edge or whole-tile acceptance.'
    e['parentRepairCandidate']=p
previous_package=copy.deepcopy(I['parentRepairPackage']);I['parentRepairPackage']['previousBasePackage']=previous_package
I['parentRepairPackage'].update(path=op.as_posix(),sha256=sha(op),role='parent_repair_overlay_candidate_package_not_child_authoritative_selection',overlayReview=overlay['overlayReview'],toneRefinementCoordinates=['r08_c07','r08_c08'],toneRefinementManifest=ref(T/'final-manifest.json'))
I['parentRepairPackage']['remainingKnownLimitations']=['Right-corner faint upper ground tone transition outside masks','Other unreviewed complete tile edges, missing neighbors, wholecity and client/navigation/runtime pending']
DA=read(A/'donghai-c13-current-update-audit.json');assert DA['eligibleSameCoordinateC13Update']
fish=next(a for a in I['appearances'] if a['appearance']=='donghai_day')
updated=[]
for o in DA['currentOutputs']:
    if o['tile']=='r08_c14' and not args.include_c14:continue
    assert sha(o['file'])==o['sha256'];e=next(e for e in fish['entries'] if e['tileId']==o['tile'])
    old=copy.deepcopy(e);e['previousSelectedSnapshot']=old
    e.update(path=Path(o['file']).as_posix(),sha256=o['sha256'],generationRecord=ref(o['file']+'.generation.json'),selectionSource=DA['integrationManifest'],qaEvidence=[DA['ownerScopedVisualReview'],ref(A/'donghai-c13-current-update-audit.json')],qaStatus='Current c13/c14 common-edge and insertion QA bound to new outputs; source/native/mask reconstruction independently exact. No whole-tile or city acceptance.',auditSource=ref(A/'donghai-c13-current-update-audit.json'),auditEntryPointer='/currentOutputs/'+str(DA['currentOutputs'].index(o)),observedAt=now)
    e['issues']=['Only the current common-edge and insertion scopes plus explicitly unchanged historical scopes are accepted; missing outside neighbors, wholecity and client remain pending.']
    updated.append(o['tile'])
I.setdefault('priorDeltaAudits',[]).append(I['latestDeltaAudit'])
I['latestDeltaAudit']=ref(A/'donghai-c13-current-update-audit.json');I['latestParentToneReview']=overlay['overlayReview'];I['updatedAt']=now
repairs_before={e['tileId']:copy.deepcopy(e['parentRepairCandidate']) for a in I['appearances'] for e in a['entries'] if 'parentRepairCandidate'in e}
# Reuse only the already-reviewed mechanical thumbnail renderer, not its publication logic.
renderer=(A/'publish-48.py').read_text(encoding='utf-8').split('# Mechanical, proportion-preserving thumbnail display only. No production pixels altered.\n',1)[1].split("I['liveAggregationValidation']=",1)[0]
renderer=renderer.replace('渔村日景 r08_c14 已重建并核验当前来源。','父修补与渔村当前接缝稿已核验来源。')
exec(compile(renderer,str(A/'publish-48.py')+'::preview','exec'))
I['liveAggregationValidation']={'checkedAt':now,'sourceCount':48,'uniqueCoordinateCount':48,'allSourceHashesMatchedBeforePreviewWrite':True,'allSourcesDecoded4096':True,'allSourcesFullyOpaque':True,'sameCoordinateUpdates':len(updated),'newCoordinates':0,'parentRepairOverlaysUpdated':2,'formalAcceptedCount':0,'wholeCityCompleteCount':0,'fiveParentRepairAlternativesPreserved':True,'source':ref(A/'donghai-c13-current-update-audit.json')}
dump(ip,I)
S=read(B/'status.json');S['updatedAtUtc']=now;S['currentBatchSha256']=sha(ip);S['latestContinuation']['checkpoint']['sha256']=sha(ip);S['latestContinuation']['updatedAtUtc']=now
S['candidateFiles']=[Path(e['path']).relative_to(B).as_posix() for a in I['appearances'] for e in a['entries']];S['candidatePreviewSha256']=sha(A/'overview.jpg');S['parentRepairPackage']=I['parentRepairPackage'];S['activeProductionRun']['parentRepairPackage']=op.relative_to(B).as_posix();S['latestContinuation']['parentRepairPackage']=op.relative_to(B).as_posix();dump(B/'status.json',S)
p=A/'README.md';text=p.read_text(encoding='utf-8')
text=text.replace('[5 个同坐标修补稿与来源](../parent_repairs_20261008/current/current-selection.json)','[5 个同坐标修补稿与来源](parent-repair-current-overlay.json)')
for tile in ['r08_c07','r08_c08']:text=text.replace(f'(../parent_repairs_20261008/current/{tile}.png)',f'(../parent_repairs_20261008/west-upper-tone/final-output/{tile}.png)')
text=text.replace('仍保留西上方灰石材旧明暗接线、右角修补范围外地面轻微色阶及其他尚未审查区域的限制。','西上方灰石明暗直缝与斜金边高光台阶已在新增1254窗口和8张原尺寸QA范围内修复，并通过root及独立复核。旧37个QA仅沿用逐像素不变区域；右角修补范围外地面轻微色阶和其他未审查区域仍保留限制。')
text+='\n本次同坐标同步：父修补 r08_c07/r08_c08 使用新增tone覆盖层；渔村日景 '+ '/'.join(updated)+' 更新为已绑定公共边/嵌入回边QA的当前稿。数量仍48，正式验收0。[原生来源与逐像素QA绑定](donghai-c13-current-update-audit.json) · [父tone独立复核](west-upper-tone-independent-review.json)。\n'
text=text.replace('渔村日景 c12/c13 当前集成稿仍需完成所属任务接缝 QA，未继承旧稿验收结论。','渔村日景 c12/c13 共边已在父任务原尺寸查看且转移到当前字节；本次更新的 c13/c14 所属任务公共边与回接 QA 另有当前 SHA 绑定。未扩展为整图验收。')
p.write_text(text,encoding='utf-8')
for p in [P/'README.md',B/'README.md']:
    text=p.read_text(encoding='utf-8');text=text.replace('parent_repairs_20261008/current/current-selection.json','parent_audit_20261008/parent-repair-current-overlay.json');p.write_text(text,encoding='utf-8')
vp=A/'tone-and-fishing-update-validation.json';dump(vp,{'updatedAt':now,'index':ref(ip),'parentRepairOverlay':ref(op),'rootReview':ref(root_review),'sameCoordinateFishUpdates':updated,'count':48,'missing':1744,'formalAccepted':0,'wholeCities':0,'childSelectionsModified':False,'previewLayoutReviewPending':True})
print(json.dumps({'index':ref(ip),'overlay':ref(op),'fishUpdates':updated,'count':48,'previewReview':'pending'},ensure_ascii=False))
