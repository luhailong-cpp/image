from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,collections
A=Path(__file__).resolve().parent;P=A.parent;B=P.parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();ip=A/'verified-current-index.json';I=read(ip)
assert I['summary']['completePixelCandidateCount']==48
assert [len(a['entries']) for a in I['appearances']]==[11,7,7,7,5,5,6]
parents=[e['parentRepairCandidate'] for a in I['appearances'] for e in a['entries'] if 'parentRepairCandidate'in e];assert len(parents)==5
for p in parents:assert sha(p['path'])==p['sha256']
fish=next(a for a in I['appearances'] if a['appearance']=='donghai_day')
for e in fish['entries']:
    if e['tileId'] in ['r08_c13','r08_c14']:assert sha(e['path'])==e['sha256']
I['preview']['visualReview']={'checkedAt':now,'status':'layout_visually_reviewed','actuallyViewed':True,'method':'Opened new saved overview.jpg with tools.view_image after two same-coordinate fishing updates.','imageSha256':sha(A/'overview.jpg'),'findings':'All seven cards and summary fit; labels and48/1792,1744 missing,formal0 are readable. Positions and count unchanged.','scope':'Contact-sheet layout only; not native artwork acceptance.'}
I['latestCompleteCoordinateCountAudit']=I['latestLiveDelta'];I['latestLiveDelta']=ref(A/'donghai-c13-current-update-audit.json');I['updatedAt']=now
dump(ip,I)
S=read(B/'status.json');S['currentBatchSha256']=sha(ip);S['latestContinuation']['checkpoint']['sha256']=sha(ip);S['latestContinuation']['latestLiveDelta']=I['latestLiveDelta'];S['candidateVisualReview']=I['preview']['visualReview'];S['updatedAtUtc']=now;dump(B/'status.json',S)
v=read(A/'tone-and-fishing-update-validation.json');v.update(index=ref(ip),previewLayoutReviewPending=False,previewLayoutReview=I['preview']['visualReview'],verifiedAt=now);dump(A/'tone-and-fishing-update-validation.json',v)
# Keep the earlier edge inventory history, but close the now-bound child c13/c14 QA item.
E=read(A/'shared-edge-priority.json');e=next(e for e in E['edges'] if e['appearance']=='donghai_day' and e['tiles']==['r08_c13','r08_c14'])
e['previousStatus']=e['status'];e['status']='current_pair_scoped_pass_recorded';e['interpretation']='Owning task finished c13/c14 shared-edge and insertion review; parent independently reconstructed native strip/masks and10 QA crops from current outputs. No new whole-tile acceptance.'
da=read(A/'donghai-c13-current-update-audit.json');e['sources']=[{'path':Path(o['file']).as_posix(),'sha256':o['sha256']} for o in da['currentOutputs']];e['evidence']=[da['ownerScopedVisualReview'],ref(A/'donghai-c13-current-update-audit.json')];e.pop('ownerReserved',None)
E['historicalPriorityFollowups']=E['priorityFollowups'];E['priorityFollowups']=[p for p in E['priorityFollowups'] if not(p['appearance']=='donghai_day' and p['tiles']==['r08_c13','r08_c14'])]
for rank,p in enumerate(E['priorityFollowups'],1):p['rank']=rank
E['summary']['statusCounts']=dict(collections.Counter(e['status'] for e in E['edges']));E['latestScopedUpdateAt']=now;E['latestSourceIndex']=ref(ip)
E['recommendation']='No newly inspected band needs repainting. Fishing c13/c14 scoped QA is now bound and closed. Remaining highest-value items: child-owned island-day north integration and read-only c11/c12 historical-QA transfer.'
dump(A/'shared-edge-priority.json',E)
p=P/'README.md';t=p.read_text(encoding='utf-8').replace('父任务另外合并了四处修补，涉及 5 个既有坐标','父任务已合并多处局部修补，涉及 5 个既有坐标');p.write_text(t,encoding='utf-8')
print(json.dumps({'index':ref(ip),'overlay':ref(A/'parent-repair-current-overlay.json'),'validation':ref(A/'tone-and-fishing-update-validation.json'),'edgeInventory':ref(A/'shared-edge-priority.json'),'count':48,'formalAccepted':0},ensure_ascii=False))
