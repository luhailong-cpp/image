"""Restore current festival acceptance after legacy finalizer/verifier, before packaging."""
from datetime import datetime,timezone
import repair as r
B=r.B;ROSTER=r.ROSTER
old=r.load(B/'before/qdao_chibi_roster_v11/manifest.json')['festival_edge_export']
old['completed_utc']=datetime.now(timezone.utc).isoformat();old['status']='published_supplemented_and_reverified'
for role in old['roles']:
    d=ROSTER/role['slug'];role.update(manifest_sha256=r.sha(d/'manifest.json'),qc_sha256=r.sha(d/'qc.json'),approval_sha256=r.sha(d/'processing/festival-edge-approval.json'))
old['supplement']={'status':'approved_and_published','scope':'28 portrait lower black-hair tips;166 RGB pixels;all alpha unchanged;29 SW01 correctly alpha-composited recheck retained','approval':'../qdao_festival_refinement_20260910/edge_exports/supplement_28/approval.json','approval_sha256':r.sha(B/'approval.json'),'publication':'../qdao_festival_refinement_20260910/edge_exports/supplement_28/publication.json','publication_sha256':r.sha(B/'publication.json')}
for name in ['manifest.json','validation.json']:
    p=ROSTER/name;d=r.load(p);d['festival_edge_export']=old;r.dump(p,d)
print('Current pack manifest/validation bind original batch plus166-pixel portrait supplement.')
