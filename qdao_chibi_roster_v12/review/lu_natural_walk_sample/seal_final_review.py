from pathlib import Path
from PIL import Image
import json,hashlib,datetime
root=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\24_lu_dongbin')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((root/'manifest.json').read_text())
for key,source in m['sources'].items():
    assert sha(source['path'])==source['sha256'],key
    a=Path(source['path']).with_suffix('.assembly.json');assert sha(a)==source['assembly_metadata_sha256'],key
seref=next(x for x in m['sources']['nw_se']['assembly_provenance']['sources'] if x['direction']=='SE')
assert 'fix06-arm' in seref['upstream_assembly']['sources'][5]['path']
qc=json.loads((root/'qc.json').read_text());assert not qc['errors']
qc.update(status='passed',visual_review='passed',visual_review_scope='root reviewed 8 final 9-cell idle/walk boards and cross-direction phase01 at common scale; direction authors independently reviewed native leg occlusion and accessory anatomy',visual_review_date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(root/'qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'status':'passed','reviewers':['root','lu_natural_east','lu_natural_north','lu_natural_west'],'walk_and_idle_evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'cross_direction_evidence':'review/eight-directions-phase01.jpg','motion_evidence':'review/eight-directions.gif','scope':['Plain ivory and dark teal short cloth robes, youthful round face, bun swordpin, one back sword and one waist gourd; no glow or fantasy armor.','8 authored walk poses per facing, alternating near/far support legs and arm swing. SE06 real thigh occlusion and arm position corrected.','Dedicated S/N/E/SE idles regenerated from native walk cells for proportion/angle match. Other idles separately authored.','One common scale across all72 images; direction idle defines fixed head region/top; integer whole-frame translation with exact RGBA crop proof.','Final72 cells have transparent margins; no alpha content clipped, no mirrored, duplicated or interpolated walk cells.'],'limits':['Visual review is internal; user preference can still require revision.','Does not establish network movement cadence or zero foot sliding at every possible world speed.','This approval covers only the corrected24; other roster members retain their separately recorded state.']}
(root/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'visual_passed','cross_direction_height_ratio':qc['cross_direction_mean_height_ratio'],'idle_walk_height_drift':{d:round(qc['directions'][d]['idle_walk_height_drift'],4) for d in qc['directions']},'all_current_source_hashes_match':True,'SE06_arm_fix_in_processed_source':True}))
