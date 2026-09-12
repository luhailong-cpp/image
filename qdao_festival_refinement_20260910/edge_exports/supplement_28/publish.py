"""Publish only the reviewed 166 RGB-pixel portrait supplement and hash-bound QC."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,hashlib,json
import numpy as np
from PIL import Image
import repair as r
B=r.B;ROOT=r.ROOT;ROSTER=r.ROSTER;ROLE=ROSTER/'28_moon_rabbit_artificer'
def main():
    t=r.load(B/'trial.json');src=B/'staged/portrait.png';dest=ROLE/'portrait.png';assert r.sha(src)==t['staged_sha256'];assert r.sha(dest)==t['before_sha256'];assert r.sha(B/'repair.py')==t['processor_sha256'];a=np.array(Image.open(dest));z=np.array(Image.open(src));assert np.array_equal(a[:,:,3],z[:,:,3]);assert (np.any(a[:,:,:3]!=z[:,:,:3],axis=2)).sum()==166
    evidence=B/'festival-edge-portrait-supplement.jpg';Image.open(B/'trial.png').convert('RGB').save(evidence,quality=98)
    approval={'schema':'qdao.festival.edge-supplement.v1','status':'approved','approved_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'check_cleanup_impact','scope':'Only 28 portrait lower-left black hair tips; 166 RGB pixels in [351,420,410,432], no alpha or body changes','path':'qdao_chibi_roster_v11/28_moon_rabbit_artificer/portrait.png','previous_sha256':t['before_sha256'],'sha256':t['staged_sha256'],'trial_sha256':r.sha(B/'trial.json'),'processor_sha256':r.sha(B/'repair.py'),'mask_sha256':r.sha(B/'changed-mask.png'),'stats':t['stats'],'visual_review':{'performed':True,'method':'Pillow alpha_composite at native resolution on #172c26 and #f2eddf, no source resizing; 2x/4x nearest-neighbor enlarged composites used to locate hair versus lilac shoulder. Native before/after crop and full portrait inspected.','finding':'Small remaining red-violet hair-tip run is removed; black hair contours, lilac shoulders/collar, skin, red ties and toolbox retained.','evidence':[{'path':'trial.png','sha256':r.sha(B/'trial.png')},{'path':'festival-edge-portrait-supplement.jpg','sha256':r.sha(evidence)}]},'29_SW01_recheck':{'path':'qdao_chibi_roster_v11/29_he_xiangu/walk/SW/01.png','sha256':r.sha(ROSTER/'29_he_xiangu/walk/SW/01.png'),'decision':'retain','method':'Actual native Pillow alpha composites on dark and light backgrounds plus 2x nearest-neighbor cropped composite compared against immutable before.','finding':'No separate white/green leaked dots confirmed in correct alpha composite. Pale contours follow original white cuff/shoe designs and skin highlights. Alpha-zero hidden RGB is excluded by correct composition.','alpha_zero_pixels':206022,'alpha_zero_nonzero_hidden_rgb':337,'alpha1_to31_pixels':3288,'alpha_unchanged':True,'hidden_rgba_unchanged':True},'original_batch_approval':{'path':'../visual-approval.json','sha256':r.sha(B.parent/'visual-approval.json'),'attribution':'Original reviewed 303 export revision retained as history; current 28 portrait has this additional approval.'},'limits':['No alpha changes or engine/runtime test.','No claim of universal zero purple; lilac clothing is protected.','Supplement is not a new AI generation or pose.']}
    r.dump(B/'approval.json',approval)
    oldapproval=ROLE/'processing/festival-edge-approval.json';role_approval=r.load(oldapproval)
    previous_role_hash=r.sha(oldapproval);role_approval['approved_utc']=approval['approved_utc'];role_approval['scope']='Current final six-role export revision plus 28 portrait lower-hair RGB supplement; all original pose/alpha/design invariants preserved'
    for f in role_approval['files']:
        if f['path']=='portrait.png':f['sha256']=r.sha(src)
    role_approval['review_evidence'].append({'path':'processing/festival-edge-portrait-supplement.jpg','sha256':r.sha(evidence)})
    role_approval['supplement']={'record':'../../qdao_festival_refinement_20260910/edge_exports/supplement_28/approval.json','sha256':r.sha(B/'approval.json'),'previous_approval_sha256':previous_role_hash,'previous_approval_record':(B/'before/qdao_chibi_roster_v11/28_moon_rabbit_artificer/processing/festival-edge-approval.json').relative_to(ROOT).as_posix(),'previous_batch_attribution':'Prior batch design and pose acceptance; this supplement approves the current portrait hash.'}
    rm=r.load(ROLE/'manifest.json');qc=r.load(ROLE/'qc.json')
    for f in rm['files']:
        if f['path']=='portrait.png':f.update(sha256=r.sha(src),bytes=src.stat().st_size)
    r.dump(B/'staged/festival-edge-approval.json',role_approval)
    rm['festival_edge_export']['sha256']=r.sha(B/'staged/festival-edge-approval.json');rm['festival_edge_export']['supplement']=role_approval['supplement']
    qc['visual_review'].update(sha256=r.sha(B/'staged/festival-edge-approval.json'),reviewed_at_utc=approval['approved_utc'],review_scope='Current hash-bound 28 portrait supplement plus unchanged original 50 media; geometry and design retained')
    qc['festival_edge_supplement']={'record':role_approval['supplement']['record'],'sha256':r.sha(B/'approval.json'),'changed_rgb_pixels':166,'alpha_changed_pixels':0,'changed_frame_count':0}
    r.dump(B/'staged/manifest.json',rm);r.dump(B/'staged/qc.json',qc)
    mapping=[(src,dest),(B/'staged/manifest.json',ROLE/'manifest.json'),(B/'staged/qc.json',ROLE/'qc.json'),(B/'staged/festival-edge-approval.json',oldapproval),(evidence,ROLE/'processing/festival-edge-portrait-supplement.jpg')]
    out=[]
    for s,d in mapping:
        previous=r.sha(d) if d.exists() else None;shutil.copy2(s,d);assert r.sha(s)==r.sha(d);out.append({'path':d.relative_to(ROOT).as_posix(),'sha256':r.sha(d),'previous_sha256':previous,'kind':'media' if d==dest else 'metadata_or_visual_evidence'})
    r.dump(B/'publication.json',{'status':'published_and_reverified','published_utc':datetime.now(timezone.utc).isoformat(),'approval_sha256':r.sha(B/'approval.json'),'files':out,'scope':'166 portrait RGB pixels; no 28 frames or 29 media changed','next':'Regenerate overview, verify full pack, update current manifest/validation binding and ZIP.'})
    print('Published 28 portrait supplement:166 RGB pixels,0 alpha,0 animation changes; new current role approval.')
if __name__=='__main__':main()
