from pathlib import Path
import json,hashlib,shutil,datetime
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'candidate-natural-body/29_he_xiangu';ev=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\29-he-xiangu-natural')
msha=hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest();assert msha=='1a6ea359e1b8b5d99653b624ceb197d204ab11300c6ce67824c301a18994070e'
for f in [r/'review/he_xiangu_natural_walk/STATUS.json',p/'candidate-source-review.json']:
 backup=ev/'before-status-finalization'/f.name;backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():shutil.copy2(f,backup)
 d=json.loads(f.read_text());d.update(status='art_approved_and_published_runtime_verification_pending',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),approved_candidate=str(p),approved_manifest_sha256=msha,visual_review=str(p/'visual-review.json'),runtime_evidence_pending=True)
 if f.name=='STATUS.json':d['previous_candidate']='candidate-stable-body/29_he_xiangu is retained history; published plain-cloth version comes from candidate-natural-body/29_he_xiangu.'
 f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest()==msha
print('Updated He Xiangu status without modifying immutable manifest; historical status preserved.')
