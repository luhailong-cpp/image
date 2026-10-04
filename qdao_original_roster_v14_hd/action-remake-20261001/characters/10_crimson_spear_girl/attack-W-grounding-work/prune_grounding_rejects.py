from pathlib import Path
import json,hashlib,datetime
d=Path(__file__).parent.resolve();base=d.parent.resolve()
assert d.name=='attack-W-grounding-work' and base.name=='10_crimson_spear_girl'
s=json.loads((d/'selection.json').read_text());keep={(base/r).resolve() for r in s['slots'].values()};assert len(keep)==5 and all(p.is_file() for p in keep)
removed=[]
for p in d.glob('attack-W-*-ground-v*.png'):
 p=p.resolve();assert p.parent==d
 if p in keep:continue
 mf=p.with_name(p.name+'.generation.json');m=json.loads(mf.read_text(encoding='utf8'))
 removed.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reason':'Superseded/rejected generated candidate, current selected final work-in-progress verified. Text provenance preserved.'})
 m['status']='rejected_or_superseded_image_removed';m['retention']={'imagePresent':False,'reason':removed[-1]['reason'],'removedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 mf.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');p.unlink()
(d/'retention-cleanup.json').write_text(json.dumps({'scope':str(d),'keptSelected':5,'removed':removed},indent=2),encoding='utf8')
p=d/'pose-review-progress.json';m=json.loads(p.read_text());m['status']='five_required_native_candidates_static_reviewed_dynamic_pending';m['selected']=5;m['review']='REVIEW_20261004.md';p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('kept5 unique selected; rejected/superseded PNG removed',len(removed))

