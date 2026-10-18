from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;O=D/'I01-only-reviewed-20261016'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
co=rd(O/'composition.json');idx=rd(O/'evidence-index.json')
evidence=[]
for e in idx['changedEvidence']:evidence.append(dict(**e,visuallyViewedAtNativeResolution=True,status='passed_no_blocking_discontinuity_observed',finding='Short blind-end grout removed; slab texture and legitimate vertical joint, horizontal courses and gold fitting remain continuous.'))
for name in ['left-boundary','right-boundary','top-boundary','bottom-boundary']:
 p=D/'trial-v1/I01-blind-stone-grout'/(name+'-100pct.png')
 evidence.append(dict(**ev(p),name='I01-'+name,scale='1:1',visuallyViewedAtNativeResolution=True,status='passed_no_visible_mask_boundary'))
qa=dict(schemaVersion=1,tile='r15_c16',reviewer='/root/assembly_resume',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),composition=ev(O/'composition.json'),core=co['core'],context=co['context'],status='internal_passed_external_west_W01_still_pending',internalStatus='passed_all_33_internal_items_via_29_unchanged_prior_and_4_reinspected',northStatus='prior_pass_reused_unchanged',westStatus='q0_q1_q2_prior_pass_reused_q3_W01_failed_unchanged',southStatus='south384_exact_root_local_QA_reusable_external_join_separate',eastStatus='not_in_scope',reusedEvidence=idx['reusedEvidence'],newEvidence=evidence,independentScalarReplayExact=True,outsideMaskExact=True,south384PixelsExact=True,west384PixelsExact=True,formalAccepted=False,published=False,rootIndependentReview='pending')
write(O/'visual-qa.json',qa)
trialreview=dict(schemaVersion=1,tile='r15_c16',reviewer='/root/assembly_resume',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempts=2,selectedProposal=co['core'],selectedScope='I01 only; preserve original west boundary pending W01',issues=[dict(id='I01',status='passed_local_pending_root_review',coreBox=[2010,950,2164,1024],native=co['actualNative'],evidence=ev(O/'visual-qa.json')),dict(id='W01',status='failed_pending_retained_original_after_two_native_attempts',coreBox=[0,3515,140,3705],trial1=ev(D/'trial-v1/W01-west-capstone/composition.json'),trial2=ev(D/'trial-v2/composition.json'),finding='Trial1 removes original upper capstone shoulder but leaves a small lower bevel notch near child x20..60,y3670..3711 and the west material transition is still apparent. Trial2 raw native is straighter but protected y3712+ composite retains a short lower edge step; not accepted. Keep original west capstone, do not represent either trial as passed.',protectedCoreBox=[0,3712,4096,4096],nextAction='Deferred per two-attempt limit; future repair must accommodate immutable southern anchor geometry or coordinated downstream revision. No further retry in this batch.')],formalAccepted=False,activeSourcesModified=False,baseCandidateModified=False)
write(D/'repair-review-20261016.json',trialreview)
print(json.dumps(dict(qa=ev(O/'visual-qa.json'),review=ev(D/'repair-review-20261016.json'),core=co['core'],context=co['context'])))

