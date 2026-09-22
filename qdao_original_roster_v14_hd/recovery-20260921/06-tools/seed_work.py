"""Seed 06-work from the byte-reconciled, isolated E audit. Refuse an existing work tree."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'06-audit'
WORK=HERE.parent/'06-work'
CHAR='06_thunder_caster_boy'
SOURCE=AUDIT/'candidate'/CHAR
TARGET=WORK/'candidate'/CHAR
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not TARGET.exists(), '06-work already exists; do not overwrite concurrent progress.'
assert json.loads((AUDIT/'reconciled-verification-summary.json').read_text(encoding='utf-8'))['all_eight_pixel_rebuilds_passed']
before={str(p.relative_to(SOURCE)).replace('\\','/'):sha(p) for p in SOURCE.rglob('*') if p.is_file()}
shutil.copytree(SOURCE,TARGET)
assert before=={str(p.relative_to(TARGET)).replace('\\','/'):sha(p) for p in TARGET.rglob('*') if p.is_file()}
evidence=WORK/'audit-seed-evidence';evidence.mkdir()
for name in ('source-audit.json','snapshot-text-reconciliation.json','reconciled-verification-summary.json','README.md'):
    shutil.copy2(AUDIT/name,evidence/name)
record={'created_at_utc':datetime.now(timezone.utc).isoformat(),'source':str(SOURCE),'target':str(TARGET),
        'copied_files':before,'all_source_bytes_preserved':True,'canonical_unchanged':True,
        'walk_inventory':['E01','E02','E03','E04','E05','E06','E09','E13'],
        'visual_pending':['E03 edge repair','complete gait and seams'],
        'historical_reconciliation':'Donor snapshot already restored exact recorded newline bytes; evidence copied without changing live history.'}
(evidence/'seed.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'target':str(TARGET),'files':len(before),'walk':8,'old_actions':'Keep V13 S16 and idle8 byte exact in final mixed review-set.'}))
