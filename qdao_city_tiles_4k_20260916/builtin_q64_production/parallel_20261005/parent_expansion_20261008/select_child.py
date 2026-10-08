from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,numpy as np
E=Path(__file__).resolve().parent;O=E/'child-selected';p=O/'audit.json'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=load(p)
for q in m['qa']:
 assert sha(q['file'])==q['sha256'];q['actuallyViewed']=True;q['viewDetail']='original';q['reviewer']='/root/complete_expansion';q['result']='No confirmed newly introduced hard geometry or triangle tone cut in reviewed returns; child geometry preferred over parent competing patches.'
m['reviewedAt']=datetime.now(timezone.utc).isoformat();m['status']='complete_native_candidate_sources_and_local_returns_verified';m['localNativeReturnReviewAccepted']=True;m['limitations']=['Only scoped current c01/c03 fill and west return review; whole4K all prior seams and wholecity/runtime not accepted.','Faint inherited horizontal highlight junction at c09 x3896..3970,yapproximately2015 lies outside child new left-return patch; no whole west-edge acceptance.','Native source baseline before v016 is inherited from earlier verified audit; this audit reconstructs every later relevant assembly through frozen current selection.'];save(p,m)
selection=dict(createdAt=datetime.now(timezone.utc).isoformat(),status='selected_child_complete_candidate_with_compatible_parent_west',candidates=[m['selectedEntry'],dict(m['parentCompatibleWest'],tile='r08_c09',pixels=[4096,4096],generationRecord=str(O/'r08_c09.png.generation.json'))],sourceAudit=dict(file=str(p),sha256=sha(p)),newCoordinateCount=1,formalAccepted=False,wholeCityComplete=False,parentCompetingGeometrySelected=False,childSelectionModified=False)
save(O/'current-selection.json',selection)
work=load(E/'current-work.json');work.update(updatedAt=datetime.now(timezone.utc).isoformat(),status='child_complete_candidate_selected_after_native_reconstruction_and_scoped_QA; unused_parent_images_ready_for_retirement',selected=str(O/'current-selection.json'),sourceAudit=str(p),newComplete4KTiles=0,childNewCoordinateCount=1,sameCoordinateChildMustNotBeDoubleCounted=True,parentGeometrySelected=False,nextAction='Root publish selected child c10 and compatible parent c09; retire unselected parent expansion rasters only after active reference scan.')
save(E/'current-work.json',work)
print(json.dumps({'audit':str(p),'auditSha':sha(p),'selection':str(O/'current-selection.json'),'selectionSha':sha(O/'current-selection.json'),'selectedEntry':m['selectedEntry'],'west':m['parentCompatibleWest']['sha256']}))
