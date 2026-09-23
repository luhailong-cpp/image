from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent;TOOLS=HERE.parent;ROOT=TOOLS.parents[2];GEN=TOOLS.parent/'06-generation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
old=ROOT/'qdao_original_roster_v13/candidate/06_thunder_caster_boy/walk/S/15.png'
assert sha(old)==read(TOOLS/'work-S-first-final/legacy-byte-manifest.json')['15.png']
reasons={2:'Rejected: head/hands/plaque and coat all over-enlarged relative to clean14; raw visible height1202 and width985.',3:'Rejected: width and head/hand scale close to14, but body-to-support-foot distance compressed; raw height1050.'}
for version in (2,3,4):
    folder=GEN/f'S15-edge-final-v{version}';im=Image.open(folder/'raw.png')
    bbox=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox()
    record={'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'review_s_first8','frame':'S15','batch':folder.name,
      'raw_sha256':sha(folder/'raw.png'),'native_size':list(im.size),'alpha_bbox_gt32':list(bbox),
      'status':'passed_raw_review_pending_parent_export' if version==4 else 'rejected',
      'visual_assessment':reasons.get(version,'Head/face/hands/plaque/chest scale now matches clean14. Torso-to-support-boot length remains full. Screen-left leg swings forward and lowers with visible raised-toe sole; screen-right leg supports and shows a frontal toe band. No swapped hands, broken anatomy or visible magenta/white/dark halo on native dark/light composites. This is phase-equivalent redrawing, not pixel-identical old512 geometry.'),
      'old512_sha256':sha(old),'old512_bytes_unchanged':True,'source_edit_route':'builtin','paid_api_calls':0,
      'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际版本与质量。',
      'staging_import_performed_by_reviewer':False,'numeric_image_resize_performed_by_reviewer':False,
      'limitations':['Native raw visual check only. Parent must serialize staging import and verify fixed whole-cell export and full-circle playback.']}
    if version==4:
        record.update({'reviewed_composites':['raw-review-dark.png','raw-review-light.png'],
          'comparison_raw':'../S14-edge-final-v1/raw.png','expected_fixed_export_height_approx':round((bbox[3]-bbox[1])*901/1254),
          'phase_detail':'Swinging sole lies slightly above supporting sole; clearly lower than14. Preserve this forward-lowering relationship in parent circle review.'})
    (folder/'raw-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted_archive':str(GEN/'S15-edge-final-v4'),'raw_review':str(GEN/'S15-edge-final-v4/raw-review.json'),'imported':False},ensure_ascii=False))
