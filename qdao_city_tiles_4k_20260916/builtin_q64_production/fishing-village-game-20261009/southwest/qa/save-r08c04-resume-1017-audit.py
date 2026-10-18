import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def entry(name,status,note):return {**ref(q/name),'status':status,'viewedNativeResolution':True,'note':note}
tr=q/'external-r08c04-1017-v8-trace.json';d=json.loads(tr.read_text())
audit={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'repair_required','tile':'r08_c04','trace':ref(tr),'tiles':d['tiles'],'recovery':{'recoveredNative':ref(z/'native/r08_c04_repair_d_external_1016_v2.png'),'receipt':ref(z/'native/r08_c04_repair_d_external_1016_v2.receipt.json'),'generationAlreadyExisted':True,'nativeDimensions':[1254,1254],'duplicateGenerationAvoided':True},'selectedPartialCandidate':'external-r08c04-1017-v8, NOT exportable','freshNativeRepairs':[ref(z/'native/r08_c04_repair_e_external_1017_v2.png'),ref(z/'native/r08_c04_repair_f_external_1017_v2.png')],'actualModel':None,'route':'builtin','checked':[
entry('external-r08c04-1017-v7-d2-top-100pct.png','pass','Top stair perimeter remains continuous.'),
entry('external-r08c04-1017-v7-d2-left-100pct.png','pass','Paving and foliage silhouettes remain continuous; stair side terminates at walkway.'),
entry('external-r08c04-1017-v7-d2-right-100pct.png','partial_pass','Main stair nosings now align across right join; bottom sliver belongs to unresolved footer.'),
entry('external-r08c04-1017-v8-stair-footer-100pct.png','repair_required','Native replacement cuts into lowest riser and pavement joints, in mosaic x 3180..4254, y 1870..2100.'),
entry('external-r08c04-1017-v8-e2-after-1254.png','rejected','e2 fixes footer center but shifts paving pattern; its right boundary x approx 4180..4254,y1950..2150 still clips joints. e2 is not selected.'),
entry('external-r08c04-1017-v8-f2-after-1254.png','pass','Interrupted pavement grout is closed. Full 1254 crop includes all local source-mask perimeters.'),
entry('external-r08c04-1017-v8-four-corner-100pct.png','pass','Four-core intersection has continuous wall-base plants, stone courses and pavement joints.'),
entry('external-r08c04-1017-v8-wall-top-join-100pct.png','repair_required','Separate wall-face splice above f1: diagonal stone joint clips at mosaic x approx 4096,y3500..3560.')
],'openIssues':[{'id':'stair_footer','coreMosaicBox':[3180,1870,4254,2150],'status':'deferred_unpassed','attempts':['e_external_1016_v1','e_external_1017_v2'],'reason':'Repeated local edits move the edge mismatch rather than producing a closed valid replacement; retain source versions and defer per project rule.'},{'id':'wall_top_face','coreMosaicBox':[4000,3430,4170,3600],'status':'repair_required','reason':'Residual vertical source switch interrupts diagonal wall joint above the repaired four-core intersection.'}],'acceptance':{'internalPriorQA':'Existing recorded internal QA outside changed source regions remains eligible for hash-based reuse; this audit does not claim all 39 current candidate crops pass.','externalAllPassed':False,'exportAllowed':False,'wholeMapAccepted':False},'preservation':{'noImageOverwrite':True,'noGit':True,'noIndexOrProgressWrites':True,'acceptedNeighborVersionsRetained':True,'c06Facing230PixelsUnchanged':True,'sourcePixelIdentity':True},'next':'Continue independent missing r08_c03 after coordinate conflict check; retain these unresolved points for concentrated structural repair.'}
p=q/'r08c04-resume-1017-native-art-audit-v1.json';assert not p.exists();p.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'audit':ref(p),'trace':ref(tr),'status':audit['status'],'openIssues':audit['openIssues']}))

