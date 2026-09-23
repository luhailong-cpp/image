"""Refresh isolated source checks and record actual static review without approval."""
from pathlib import Path
import importlib.util,json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CHAR='04_mountain_guardian_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
verifier=load('sw_final_verify',ROOT/'tools/verify.py');verifier.ROOT=HERE;verifier.mod=lambda name:load('sw_final_'+name,ROOT/'tools/vendor'/f'{name}.py')
out=HERE/'candidate'/CHAR
checks=[]
for n in (14,15,16):
 result=verifier.verify(CHAR,'SW',False,n)
 (out/f'review/validation-SW-{n:02d}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');checks.append(result)
manifest=json.loads((HERE/'preview/preview-manifest.json').read_text(encoding='utf-8'))
evidence=[{'path':p.name,'sha256':sha(p)} for p in sorted((HERE/'preview').glob('*.png'))]+[{'path':p.name,'sha256':sha(p)} for p in sorted((HERE/'preview').glob('*.gif'))]
review={'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'status':'requires_revision_and_dynamic_review','character':CHAR,'direction':'SW','scope':'Static visual inspection of native raw, transparent exports, dark/light contacts, lower-body and seam panels; built-in browser unavailable.', 'source_validation':checks,'native_single_frame_size':[1254,1254],'output_size':[1024,1024],'common_scale':.84,'body_scale_cv':manifest['body_scale_cv'],'gif_timing_validated':{'actual_decoded_frames':16,'duration_each_ms':30,'cycle_ms':480},'browser_dynamic_review':{'performed':False,'reason':'cua.createBrowserTab(iab) returned Browser is not available; cua.listBrowsers returned []'},'individual_frames':{'14':{'source_rebuild':'passed','static_pose':'plausible early lowering from SW13; staff-side support and shield-side descending leg remain readable','edge_review':'No obvious new continuous magenta fringe on reviewed light/dark export; whole-loop acceptance pending'},'15':{'source_rebuild':'passed','static_pose':'Shield-side boot lowered near floor already; more advanced than planned midpoint; review timing with revised16','edge_review':'No obvious new continuous magenta fringe on reviewed light/dark export; whole-loop acceptance pending'},'16':{'source_rebuild':'passed','static_pose':'rejected for 15-to16-to01 seam: forward boot crosses to screen-left with large sole exposure, while preserved01 forward shield-side boot lies screen-right; foot lateral placement and trouser overlap reverse abruptly','required_revision':'Keep shield-side left swing boot in screen-right lane matching preserved01; shorten lateral reach and reduce visible underside; staff-side right foot remains readable support'}},'identity_notes':['SW staff-head open ring already occurs in original SW12 and current SW references; not treated as a newly introduced missing disk.','Head/body proportions are within numeric body-scale threshold; numeric pass does not certify seamless animation.','Preserved SW01/SW13 have warmer coloration and visible historical magenta edge traces; not retouched or relabelled new problems.'],'canonical_candidate_written':False,'full_direction_approved':False,'runtime_approved':False,'evidence':evidence}
(HERE/'visual-observations.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_checks_passed':len(checks),'review_status':review['status'],'rework':[16]},ensure_ascii=False))
