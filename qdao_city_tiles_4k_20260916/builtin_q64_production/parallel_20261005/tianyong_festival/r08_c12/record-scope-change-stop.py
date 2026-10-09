from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
N=Path(__file__).resolve().parent;D=N/'r01_c04-v1';O=D/'join-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
review={'createdAtUtc':stamp,'image':ref(O/'joined.png'),'reviewer':'close_c03','viewedNativeImages':[ref(O/n) for n in ['joined.png','top-native-qa.png','left-native-qa.png']],'nativeScale':1,'localVisualAccepted':True,'formalAccepted':False,'fullyPaintedNativeTileReviewed':False,'findings':[],'observation':'Actually viewed native 1254-square joined, 1654x660 top and 660x1654 left windows. Teal roof, golden curled eave, lantern, yellow flowers and stone road keep a clean rounded Q style. Known top and left seams continue without visible duplicate contours or rectangular edge. Missing outside east/northeast portions of QA canvas were excluded; the top gold patch beyond tile x4096 is unused halo.','productionStatus':'Retained in-flight native output after scope changed to 8x8. No ROI manifest packaged, no local checkpoint advance, no root commit.','limits':'Only this window and known top/left seams reviewed. Unbuilt neighboring edges, whole tile and runtime remain pending.'}
save(O/'visual-review.json',review)
cp=json.loads((N/'local-source-checkpoint.json').read_text(encoding='utf-8-sig'))
status={'createdAtUtc':stamp,'reason':'Upstream 8x8 layout replaces old 16x16 expansion; stop at next tool boundary','tile':'r08_c12','lastPackagedManifest':cp['manifest'],'packagedPatchCount':len(cp['manifestChain']),'coveredNativePixelsInLocalChain':cp['coveragePixels'],'localCheckpoint':ref(N/'local-source-checkpoint.json'),'inFlightPreserved':{'patch':'r01_c04-v1','native':ref(D/'native.png'),'joined':ref(O/'joined.png'),'visualReview':ref(O/'visual-review.json'),'manifestCreated':False,'localCheckpointAdvanced':False},'notPreparedOrGenerated':['r02_c04','r03_c04','r04_c04'],'actualBuiltinCalls':15,'primaryGenerations':13,'localAIRepairs':2,'actualModel':None,'actualQuality':None,'rootCheckpointModified':False,'legacyProductionStopped':True,'formalAccepted':False}
save(N/'scope-change-stop-record.json',status)
print(json.dumps({'review':ref(O/'visual-review.json'),'stopRecord':ref(N/'scope-change-stop-record.json')}))

