from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];p=R/'audit/contact-SE-review.json';a=json.loads(p.read_text(encoding='utf-8'))
for pair in a['positionPairs']:
 if 7 in pair['frames'] or 14 in pair['frames']:
  pair['observations']=' '.join(next(f['observations'] for f in a['frames'] if f['frame']==n) for n in pair['frames'])
p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print('updated SE pair observations to current repaired frames')

