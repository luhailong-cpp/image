from pathlib import Path
import json,hashlib,os
root=Path(__file__).resolve().parent;old=root/'run-SW-14.png';oldr=Path(str(old)+'.generation.json');new=root/'run-SW-14-ground-v2.png';nr=Path(str(new)+'.generation.json');alt=root/'review-alternates'
alt.mkdir(exist_ok=True);assert alt.resolve().is_relative_to(root)
r=json.loads(nr.read_text(encoding='utf8'));o=json.loads(oldr.read_text(encoding='utf8'))
assert hashlib.sha256(new.read_bytes()).hexdigest()==r['sha256'];assert hashlib.sha256(old.read_bytes()).hexdigest()==o['sha256']
dest=alt/'run-SW-14-v1.png';assert dest.resolve().is_relative_to(root) and not dest.exists()
os.replace(old,dest);o.update(file='review-alternates/run-SW-14-v1.png',imageRetention='Retained for root integration review per latest request; not current selection');o['review'].update(status='unselected alternate',reason='Current selection preserves13 upper-body placement while extending rear B leg; old rise could be natural, no blanket defect claimed')
(alt/'run-SW-14-v1.png.generation.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
r.update(file=old.name,replacementOf=dict(sha256=o['sha256'],record='review-alternates/run-SW-14-v1.png.generation.json'),sourceVariant='run-SW-14-ground-v2')
r['review'].update(status='provisional static selection',observed='B right-origin rearward extension with forefoot/toe push, A raised, upper body tracks13; complete original2grip straight spear',dynamic='root full-sequence review pending')
os.replace(new,old);oldr.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');nr.unlink()
print(r['sha256'])
