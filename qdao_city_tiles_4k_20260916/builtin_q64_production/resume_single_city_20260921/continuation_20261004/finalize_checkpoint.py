"""Bind the latest real editing artifacts without promoting production acceptance."""
import datetime, hashlib, json
from pathlib import Path
from PIL import Image
RUN=Path(__file__).resolve().parent;SESSION=RUN.parent;ART=SESSION.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):return {'file':Path(p).relative_to(ART).as_posix(),'sha256':sha(p)}
entries=[
 ('r08_c07','c07-recovery/repair-return/candidate-v4/r08_c07.png','c07-recovery/repair-return/candidate-v4/repair.json','c07-recovery/repair-return/visual-review.json'),
 ('r08_c08','c08/v3/r08_c08.png','c08/v3/r08_c08.png.generation.json','c08/v3/visual-review.json'),
 ('r08_c09','c09-pair-v2/r08_c09.png','c09-pair-v2/assembly.json','c09-pair-v2/visual-review.json'),
 ('r09_c09','c09-pair-v2/r09_c09.png','c09-pair-v2/assembly.json','c09-pair-v2/visual-review.json'),
]
ledger=read(SESSION/'current-coverage-ledger.json')
working={}
for t in ledger['tiles']:
    c=t.get('candidate')
    if not c:continue
    p=ART/c['file'];assert p.is_file() and sha(p)==c['sha256']
    working[t['tile']]={'tile':t['tile'],'candidate':c,'role':'baseline_work_in_progress_candidate','formalAccepted':False,'runtimePublished':False}
outputs=[]
for tile,f,record,review in entries:
    p=RUN/f
    with Image.open(p) as im:im.load();assert im.size==(4096,4096)
    row={'tile':tile,'candidate':{**info(p),'pixels':[4096,4096]},'record':info(RUN/record),'review':info(RUN/review),'role':'latest_work_in_progress_repair_candidate','formalAccepted':False,'runtimePublished':False}
    working[tile]=row;outputs.append(row)
native_records=['c07-cross-3072-1024/native.png.generation.json','c07-recovery/repair-return/native.png.generation.json','c08/cross-repair.native.png.generation.json','c08/repair-02/native.png.generation.json','c08/repair-03/native.png.generation.json','c09-shared-02/native.png.generation.json','c09-return-04/native.png.generation.json']
assert len(native_records)==7
for f in native_records:assert (RUN/f).is_file()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
checkpoint={'schemaVersion':1,'updatedAtUtc':now,'clientDate':'2026-10-04','appearance':'tianyong_festival','role':'Latest editing checkpoint; not a production manifest and not formal acceptance','cityPixels':[65536,65536],'grid':[16,16],'tilePixels':[4096,4096],
 'baselineLedger':info(SESSION/'current-coverage-ledger.json'),'counts':{'baselineSelectedCoordinates':10,'currentWorkingCoordinates':len(working),'missingFullWorkingCandidates':256-len(working),'updated4KWorkingCandidatesThisRun':4,'newNativeRepairImagesThisRun':7,'recoveredPriorNativeRepairImages':1,'newFormallyAcceptedTiles':0,'formalAcceptedTilesTotal':0},
 'currentOutputs':outputs,'workingCandidates':[working[k] for k in sorted(working)],'generationRecords':[info(RUN/f) for f in native_records],'modelCapability':info(RUN/'model-capability.json'),'actualModel':None,'actualQuality':None,
 'acceptanceNote':'The new editing candidates contain known remaining seams and missing-neighbor gates. Previous candidate-SHA-bound seam reviews do not automatically apply to these versions. No runtime asset or production manifest changed.',
 'retentionNote':'After scoped cleanup, historical image paths in source records may be retired. See cleanup-receipt.json. Preserved text/hash evidence is not a claim that deleted source pixels remain available.',
 'next':['Use these four currentOutputs for future repairs, not the superseded sources.','Finish remaining internal seams on r08_c07/c08/c09 before expanding r08_c10.','Keep r08_c09 and r09_c09 as a coupled working pair and rebind all affected neighbor checks.','Complete missing coordinates, full seam/junction QA, navigation and runtime inspection before acceptance.'],
 'formalAccepted':False,'runtimePublished':False}
write(RUN/'current-work.json',checkpoint)
pointer={'readme':str((RUN/'README.md').relative_to(ART)).replace('\\','/'),'checkpoint':info(RUN/'current-work.json'),'updatedAtUtc':now,'currentWorkingCoordinates':len(working),'newNativeRepairs':7,'recoveredPriorNativeRepairs':1,'updated4KWorkingCandidates':4,'formalAcceptedTiles':0,'role':'editing_progress_not_production_acceptance'}
for p in [ART/'status.json',SESSION/'session-state.json']:
    data=read(p);data['latestContinuation']=pointer;write(p,data)
print(json.dumps({'currentWorkingCoordinates':len(working),'outputs':outputs,'newNativeRepairImages':7,'formalAccepted':0},ensure_ascii=False))
