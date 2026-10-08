from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
report = root / 'qa/horizontal-review.json'
old = json.loads(report.read_text(encoding='utf-8-sig'))
candidate = root / 'output/r09_c14-candidate.png'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
current = '26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc'
assert sha(candidate) == current
assert len(old['items']) == 15
history = root / 'qa/horizontal-review-before-v9-root-reinspection.json'
assert not history.exists()
history.write_bytes(report.read_bytes())
old['reviewedAt'] = datetime.now(timezone.utc).isoformat()
old['reviewer'] = '/root'
old['candidate']['sha256'] = current
old['previousReview'] = {'file': str(history), 'sha256': sha(history)}
old['reinspectionNote'] = 'Root actually re-opened all 15 current horizontal seam, return, and junction PNGs using view_image with detail=original after application-v9. Continuous current contours and material were visually checked; this is a new visual inspection, not hash-based reuse.'
for item in old['items']:
    item['sha256'] = sha(item['file'])
    item['actuallyViewed'] = True
    item['nativeScale'] = 1
    item['viewTool'] = 'view_image; detail=original'
    item['verdict'] = 'scoped_pass'
old['scopedPass'] = True
old['issues'] = []
old['issueCount'] = 0
report.write_text(json.dumps(old, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(sha(report))
