from pathlib import Path
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'cleanup-plan.json').read_text(encoding='utf-8'))
keep=[];remove=p['delete']
qa_dirs=[
 'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/',
 'donghai_batch_r08_c08_c10/resume_audit_20260918/',
 'donghai_lantern/r08_c08_c09_c10_joint/output_v2/qa/',
 'resume_single_city_20260921/audit/r09_c09_review_v5/',
 'resume_single_city_20260921/next_tile_r09_c10/qa/external-v8/']
for item in p['keep']:
    reasons=item['reasons']
    if 'current_visual_review_evidence' in reasons and not any(d in item['relativeFile'] for d in qa_dirs):
        reasons.remove('current_visual_review_evidence')
    if reasons:keep.append(item)
    else:
        item.pop('reasons')
        item['reason']='unselected_historical_media_under_review_parent_directory'
        remove.append(item)
for item in list(remove):
    if '/tools/vendor/' in item['relativeFile']:
        remove.remove(item);item.pop('reason',None)
        item['reasons']=['scoped_tool_runtime_dependency'];keep.append(item)
p['keep']=sorted(keep,key=lambda x:x['relativeFile'])
p['delete']=sorted(remove,key=lambda x:x['relativeFile'])
p['summary'].update(retainedFiles=len(keep),deleteFiles=len(remove),retainedBytes=sum(x['bytes'] for x in keep),deleteBytes=sum(x['bytes'] for x in remove))
p['refinedAtUtc']=datetime.now(timezone.utc).isoformat()
assert sum(any(s.startswith('latest_selected_4K_candidate:') for s in x['reasons']) for x in keep)==26
assert sum(any(s.startswith('selected_native_patch_for_incomplete_tile:') for s in x['reasons']) for x in keep)==16
with (ROOT/'cleanup-plan-final.json').open('x',encoding='utf-8') as f:json.dump(p,f,ensure_ascii=False,indent=2)
print(json.dumps(p['summary']))
