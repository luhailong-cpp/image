from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
GEN=HERE.parents[1]/'10-generation'
rows={
 'N01-v1': ('L','L+R','Left boot farther away; right trailing sole faces rear at toe-off.','provisional_key_pose','Colored fringe around spear and fabric; edge approval pending.'),
 'N02-v1': ('L','L','Left far boot takes weight; right trailing heel raised.','provisional_phase','Colored fringe; full cycle and normalized scale pending.'),
 'N03-v1': ('L','L','Left planted; right behind has lifted, visible underside.','provisional_phase','Raised sole is conspicuous; assess through cycle.'),
 'N04-v1': ('L','L','Left planted, right low recovering near support ankle.','provisional_phase','Colored fringe and normalized-scale continuity pending.'),
 'N05-v3': ('L','L','Left support under body; right slightly lifted passing.','provisional_key_pose','Key support swap to N13 is visible; colored fringe remains.'),
 'N06-v1': ('R','L','Left support behind, right advanced into distance with slight clearance.','provisional_phase','Edge and complete cycle pending.'),
 'N07-v1': ('R','L','Left heel raised behind, right far boot descends.','provisional_phase','No floor in sprite; support inferred anatomically; edge approval pending.'),
 'N08-v1': ('R','L','Right far boot reaches toward contact; left trailing toe support.','provisional_phase','Precontact clearance subtle; needs 07/08/09 sequence.'),
 'N09-v2': ('R','L+R','Right boot far and planted; left trails toward viewer.','provisional_key_pose','Leg ordering opposite N01 visible; edge approval pending.'),
 'N13-v1': ('R','R','Right planted under body; left passes low with underside visible.','provisional_key_pose','Support opposite N05 visible; edge approval pending.'),
 'NE01-v2': ('L','L+R','Far left boot ahead; near right leg trails lower left.','key_group_pending','Camera/back design differ from NE09/13.'),
 'NE05-v1': ('L','L','Far left boot planted; near right is lifted in passing.','key_group_pending','Lifted sole large; camera/back design differ from NE09/13.'),
 'NE09-v3': ('R','L+R','Near right boot ahead; far left boot trails.','needs_camera_rework','More side-on with exposed right ear and different hair overlap vs NE01/05.'),
 'NE13-v1': ('R','R','Near right planted; far left lifted.','needs_camera_rework','More side-on than NE01/05; large raised sole.'),
 'N10-v1': ('R','R','Right loading stance; left trailing heel raised.','needs_grip_review','Additional visible hand near left shoulder suggests lower grip moved too high; not selected.'),
 'N11-v1': ('R','R','Right planted; left early recovery boot airborne behind.','provisional_phase','Rear direction and grip occlusion coherent; colored fringe persists and cycle untested.'),
 'N12-v1': ('R','R','Right planted; left low recovery near support with less underside visible than N11.','provisional_phase','Camera and grip coherent; colored fringe and full cycle unapproved.'),
 'N14-v1': ('L','R','Right planted behind body, left forward boot projects farther/higher with little sole.','provisional_phase','Visible grip coherent; colored fringe and full cycle pending.'),
 'N15-v1': ('L','R','Left forward boot descends into distance; right trailing forefoot support.','provisional_phase','Difference from N01 subtle; need normalized seam playback; edge pending.'),
 'N16-v1': ('L','R','Left forward precontact, right rear forefoot support with raised heel.','provisional_phase_needs_edge_fix','Detached red pixels at far right above ribbon and below spear tail; colored fringe; seam untested.'),
 'Nidle-v1': (None,'L+R','Independent rear idle, both complete soles down at same ground depth.','provisional_idle','Static stance distinct from walk; colored fringe and normalized comparison pending.'),
 'N10-v2': ('L','L','Left boot planted with right raised, contrary to intended right loading response.','rejected_wrong_leg_phase','Grip fixed but support leg wrong for10; do not select.'),
 'N10-v3': ('R','R','Right boot far/planted, left trailing heel raised; shoulder hand artifact removed.','provisional_phase','Leg phase and grip coherent; actual composite edge and loop pending.'),
 'NE09-v4': ('L','L','Near right leg continues trailing, no reliable opposite stride.','rejected_weapon_and_pose','Spear projection reversed to upper-right vs intended upper-left; not selected.'),
}
review=[]
for attempt,(leading,support,contact,decision,issue) in rows.items():
 p=GEN/attempt/'raw.png'
 if not p.exists():continue
 review.append(dict(attempt=attempt,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),anatomicalLeadingLeg=leading,supportLeg=support,contactState=contact,decision=decision,issue=issue,edgeLight='pending_actual_composite',edgeDark='pending_actual_composite_raw_RGBA_preview_shows_low_alpha_color_points',loop30ms='not_tested'))
dest=HERE/'visual-review-20260923.json'
dest.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),method='Actual native images viewed with view_image and generatedImage; no browser loop approval',NKeyPoseGate='provisional_leg_swap_observed',NEKeyPoseGate='not_passed_camera_drift',approvedForGame=False,rows=review),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sel=json.loads((HERE/'selection.json').read_text(encoding='utf-8'))
sel['N08']={'archive':'N08-v1','review':'provisional: rear view and expected low precontact phase observed; edge, size and full cycle pending'}
for slot in ['NE09','NE13']:sel.pop(slot,None)
(HERE/'selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(dest),'reviewed':len(review),'selected':len(sel)}))
