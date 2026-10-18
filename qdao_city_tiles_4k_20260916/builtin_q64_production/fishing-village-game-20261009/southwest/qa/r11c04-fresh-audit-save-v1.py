from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
basepath=Q/'r11_c04-internal-native-art-audit-v1.json';base=read(basepath)
for r in [base['trace'],base['candidate'],base['context']]+[{'path':v['file'],'sha256':v['sha256']} for v in base['viewed']]:assert sha(r['path'])==r['sha256']
joins=[]
bad={'west':3,'north':5,'east':1}
for direction in ['west','north','east']:
    tp=Q/f'pair-r11c04-{direction}-fresh-v1-trace.json';t=read(tp)
    viewed=[]
    for i,v in enumerate(t['qa'],1):
        assert sha(v['path'])==v['sha256']
        viewed.append({**v,'visualCheck':'view_image native 1:1 crop','result':'repair_required' if i==bad[direction] else 'pass'})
    d={'tile':'r11_c04','direction':direction,'trace':ref(tp),'inputContexts':t['inputs'],'status':'repair_required','viewedCount':5,'viewed':viewed,'sourcePixelsVerifiedByComposer':True,'exported':False,'notice':'Pair candidates are diagnostic native overlap selections; no neighbor or target tile is accepted or replaced by this audit.'}
    ap=Q/f'pair-r11c04-{direction}-fresh-v1-art-audit.json';save(ap,d);joins.append({**d,'audit':ref(ap)})
repairs=[]
for v in [1,2]:
    p=Z/f'native/r11_c04_riser_base_repair_v{v}.png';rp=Z/f'native/r11_c04_riser_base_repair_v{v}.generation.json'
    repairs.append({'version':v,'image':ref(p),'generation':ref(rp),'status':'not_selected','reason':'Both native edits remove central notch by raising lower-left base about60px, despite v2 explicitly requiring left-side preservation. A narrow local composite would transfer the geometric offset to its left boundary.'})
issues=[
 {'id':'first-riser-base-notch','status':'repair_required_deferred_after_two_unsuitable_edits','targetCoreApproxBox':[900,1900,1200,2200],'description':'Original first broad riser base is offset about60px near x1024,y2060. Local repair outputs change left-half base position across their entire left edge; neither is composited. Original full candidate retained as best known connected source, still fails this point.','attempts':repairs,'nextAction':'Re-plan the whole affected riser lower edge across its left extent; do not re-run the same narrow crop again. Coordinate any west-neighbor changes before export.'},
 {'id':'west-upper-lip-kink','status':'repair_required','targetCoreApproxBox':[60,2010,160,2160],'description':'West pair part03: upper stair top/back lip has a small geometric kink near image x445-480,y487-500, about target x100,y2095. Remaining four west windows pass.','evidence':joins[0]['viewed'][2]},
 {'id':'northeast-pavement-tone-cut','status':'repair_required','targetCoreApproxBox':[3900,0,4096,350],'description':'Near target x3981 the northern pavement/shrub transition has an abrupt vertical light/texture division; visible in north part05 and east part01. This lies at the northern/eastern corner and needs a coordinated corner context. Other eight north/east windows pass.','evidence':[joins[1]['viewed'][4],joins[2]['viewed'][0]],'nextAction':'Use current r10_c04, r10_c05, r11_c04 and r11_c05 contexts for a stable 2x2 corner repair before exporting refreshed edges.'},
 {'id':'south-neighbor-reserved','status':'not_checked','description':'r12_c04 is independently assigned. No production or edits were made to that coordinate and no southern/full-map acceptance is claimed.'}
]
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_qa_fresh','tile':'r11_c04','status':'repair_required','formalAcceptedCount':0,'readyForExport':False,'baseAudit':ref(basepath),'trace':base['trace'],'candidate':base['candidate'],'context':base['context'],'internalQa':{'originalViewedCount':39,'reusedPassCount':36,'unresolvedWindowCount':3,'allOriginalImageHashesReverified':True,'inputUnchanged':True,'noRepeatScanOfPassedWindows':True},'externalQa':{'viewedCount':15,'passCount':12,'repairRequiredWindowCount':3,'joins':joins,'allExternalJoinsVerified':False},'issues':issues,'generationRoute':'built-in image_gen__imagegen','actualModel':None,'actualModelEvidence':'Not returned by tool','noPaidApi':True,'noFinalPixelsResampledOrPaintedByCode':True,'unchangedSharedIndexAndGit':True}
out=Q/'r11_c04-fresh-native-art-audit-v2.json';save(out,audit)
handoff={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c04','status':'repair_required','audit':ref(out),'candidate':base['candidate'],'context':base['context'],'trace':base['trace'],'internalPassWindowsReused':36,'externalNewPassWindows':12,'nativeRepairCandidatesRetained':repairs,'remainingIssues':[{'id':v['id'],'status':v['status']} for v in issues],'exportAllowed':False,'nextStep':'Root can continue independent missing tiles while these localized geometry/corner repairs remain in the repair queue. Do not count r11_c04 art accepted.'}
hp=Q/'r11_c04-fresh-handoff-v2.json';save(hp,handoff)
print(json.dumps({'audit':ref(out),'handoff':ref(hp),'repairImages':[x['image'] for x in repairs]},ensure_ascii=False))
