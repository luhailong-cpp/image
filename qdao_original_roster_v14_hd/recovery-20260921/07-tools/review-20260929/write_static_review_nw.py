from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, struct

HERE=Path(__file__).resolve().parent
REC=HERE.parents[1]
ROOT=REC.parents[1]
OLD=REC/'07-tools/candidate/07_moon_shadow_assassin_girl'
PREVIEW=REC/'07-delivery-preview/final-candidates-20260928/preview'

def bind(p):
    b=p.read_bytes()
    d={'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    if p.suffix.lower()=='.png':
        d['dimensions']=list(struct.unpack('>II',b[16:24]));d['pngColorType']=b[25]
    return d

directions=['E','W','NE','NW']
evidence=[]
for d in directions:
    evidence.extend(bind(PREVIEW/f'{d}-{kind}-light.png') for kind in ['contact','seam'])
for d,n in [('NW',7),('NW',8),('NW',9),('NW',10),('NW',11),('NW',12),('NE',6),('NE',7)]:
    evidence.append(bind(HERE/'screenshots'/f'{d}-{n:02d}-light-512.png'))
reviewed=[bind(OLD/f'walk/{d}/{n:02d}.png') for d in directions for n in range(1,17)]
for f in ['08','09','10','11']:
    evidence.append({**bind(OLD/f'walk/NW/{f}.png'),'viewedDirectly':True})

findings={
 'E':{'staticStructure':'no_conclusive_blocker_observed','reviewedFrames':'01-16 contact; seam15-16-01-02',
      'gait':'03-05 and11-13 show rear-leg recovery/passing,06-09 and14-16 show forward extension; multiple distinct leg phases are visible.',
      'hands':'Two daggers remain in their respective hands; no detached limb or hand swap seen.',
      'seam':'15-16-01-02 has compatible head-body silhouette, feet and weapon positions; no decisive reset pop in static sequence.'},
 'W':{'staticStructure':'no_conclusive_blocker_observed','reviewedFrames':'01-16 contact; seam15-16-01-02',
      'gait':'03-05 and11-13 include lifted/passing feet;06-09 and14-16 include opening strides. Static evidence supports articulated gait, not stationary legs.',
      'hands':'Two visible held daggers throughout; no identity swap or broken wrist connection seen.',
      'seam':'15-16-01-02 is structurally compatible; minor painted contour details vary.'},
 'NE':{'staticStructure':'no_conclusive_blocker_observed','reviewedFrames':'01-16 contact; seam15-16-01-02; rendered06,07',
       'gait':'03-06 and11-14 show distinct passing/support phases, with15-16 leading into01-02.',
       'hands':'06-07 near-side forearm and dagger rise rapidly, but shoulder/elbow/hand anatomy remains connected. This alone does not establish a blocking defect.',
       'seam':'15-16-01-02 maintains northwest-opposite rear-right camera, costume identity and compatible stride.'},
 'NW':{'staticStructure':'previous_failure_withdrawn_no_conclusive_blocker','reviewedFrames':'01-16 contact; seam15-16-01-02; rendered07-12; directRGBA08-11',
       'gait':'08-11 retain lifted viewer-left boot and viewer-right support while the lifted foot advances/retracts; alternate phase is visible elsewhere in16-frame sheet.',
       'hands':'09/10 turn the near dagger upward then11 returns low; same hand retains the weapon. Treat as a segment for dynamic review, not proven broken anatomy.',
       'seam':'15-16-01-02 shows low-to-middle-to-forward arm transition and compatible foot phase; static seam itself was not the concern.'}}

candidates=[]
for frame in ['09','10']:
    attempt=REC/'07-generation'/f'review-20260929-NW{frame}-v1'
    candidate=attempt/'candidate.png';meta=json.loads(Path(str(candidate)+'.generation.json').read_text())
    selection={'status':'not_selected','reason':'No sufficiently established original blocking defect after correcting visual-coordinate mistake; candidate decreases full-figure height and has not demonstrated improved animation continuity.',
               'original':bind(OLD/f'walk/NW/{frame}.png'),'candidate':bind(candidate),
               'candidateNative':bind(attempt/'raw.png'),'candidateMetrics':meta['outputMetrics'],
               'operationScope':'Genuine built-in AI edit; only whole native canvas downsample and integer alignment in export. No local geometric head scaling.',
               'formalApproval':False,'clientIntegration':False}
    (attempt/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    candidates.append(selection)

report={'schema':'qdao-07-independent-static-review-v1','reviewedAt':datetime.now(timezone.utc).isoformat(),
 'character':'07_moon_shadow_assassin_girl','method':'Actual view_image inspection of current contact/seam images, rendered screenshots and direct original RGBA; read-only art judgment. No continuous video observation by this sub-agent.',
 'reviewedDirections':directions,'findings':findings,
 'correction':{'withdrawnClaim':'NW09/10 head top approximately12-15px versus NW11 approximately45px, implying large head-volume pop.',
               'reason':'Those visual coordinate estimates mixed ahoge and main hair crown and were not measured. Direct originals and same-scale composite do not support the claimed large jump.',
               'verifiedOriginalAlphaGt8Bounds':{'NW08':[202,56,932,943],'NW09':[191,84,899,943],'NW10':[198,94,905,943],'NW11':[232,83,913,943],'NW12':[231,90,889,943]},
               'remainingJudgment':'Slight crown/neck proportion differences and forearm/dagger rotation remain visible, but pose and shoulder-height variation prevents declaring a conclusive blocker from these static views. Original09/10 are preferred over current generated candidates.'},
 'machineEvidence':{'walkFramesBound':len(reviewed),'allBoundFrames1024':all(v['dimensions']==[1024,1024] for v in reviewed),'allBoundFramesRgbaType6':all(v['pngColorType']==6 for v in reviewed)},
 'reviewedFrameBindings':reviewed,'visualEvidence':evidence,'candidateSelections':candidates,
 'comparisonEvidence':[bind(REC/'07-generation/review-20260929-NW09-v1'/f'comparison-{t}.png') for t in ['light','dark']],
 'dynamicArtFinalAcceptance':'pending_root_continuous_playback_review','offlineAcceptanceComplete':False,'formalApproval':False,'clientIntegrationByThisAgent':False,
 'writeScope':['07-generation/review-20260929-NW09-v1','07-generation/review-20260929-NW10-v1','07-tools/review-20260929/static-review-E-W-NE-NW.json'],
 'preserved':['07-tools/candidate','07-tools/acceptance-status-20260928.json','client resources','combat resources'],
 'otherWindowSnapshotReportedByParent':{'combat':'connection/systemError interrupted; no intervention by this agent','client':'15-role local playtest integration completed;07/15 development-build restriction remains; not independently reverified in this static review'}}
dest=HERE/'static-review-E-W-NE-NW.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dest)
