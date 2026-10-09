from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys
N=Path(__file__).parent;T=N.parent;D=N/'full-review-v016'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
idx=read(D/'native-crop-index.json');cp=read(T/'source-checkpoint.json');assert cp['fragment']['sha256']==idx['source']['sha256']
for s in list(idx['sources'].values())+idx['crops']:assert sha(s['file'])==s['sha256']
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','source':idx['source'],'nativeCropIndex':ref(D/'native-crop-index.json'),'viewedNativeImages':idx['crops'],'nativeScale':1,'fullyPaintedNativeTileReviewed':True,'openInternalFindings':[],'knownNorthWestEdgesReviewed':True,'knownCornerPortionsReviewed':True,'formalAccepted':False,'pendingExternalChecks':idx['pendingExternalChecks'],'observations':['Actually inspected all nine overlapping1536x1536 full-coverage native windows after finalv016; ornamental curls, bevel corners and paving joints remain coherent without floating seams or doubled boundaries.','Inspected all three north1536x640 and all three west640x1536 windows against their exact current source snapshots; no visible seam at the320px ownership boundary.','Inspected native768x768 northwest, northeast and southwest corners. Northwest fully continuous; northeast/southwest only existing opaque portions reviewed. Black/transparent quadrants are missing future tiles and are not accepted.','The r03c04 local genuineAI repair remains clean in full-33; r04c03 retry and r02c03 overlap corrections remain aligned.'],'limits':'Complete native composite candidate only. Unbuilt east/south, whole-city256 geometry/navigation and nearest-camera client validation remain pending.'}
save(D/'root-release-review.json',review);print(json.dumps(ref(D/'root-release-review.json')))
subprocess.run([sys.executable,str(T/'export_full_candidate.py'),'--checkpoint-sha',sha(T/'source-checkpoint.json'),'--review',str(D/'root-release-review.json')],check=True)
subprocess.run([sys.executable,str(T/'select_native_tile.py'),'--tile','r09_c11','--anchor-tile','r08_c11','--anchor-side','north','--checkpoint-sha',sha(T/'source-checkpoint.json'),'--review',str(D/'root-release-review.json')],check=True)
