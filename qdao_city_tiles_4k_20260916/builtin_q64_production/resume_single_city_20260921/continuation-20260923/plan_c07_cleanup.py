from pathlib import Path
import json,hashlib,datetime
from PIL import Image
S=Path(__file__).resolve().parent.parent
A=S.parent.parent
T=S/'next_tile_r08_c07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selection=T/'latest-candidate.json'
d=json.loads(selection.read_text())
for key in ('candidate','record','assembly','review','interiorReview'):
    ref=d[key]; p=A/ref['file'];assert sha(p)==ref['sha256']
candidate=A/d['candidate']['file']
with Image.open(candidate) as im:im.load();assert im.size==(4096,4096)
q=T/'continuation-20260923/qa-repair-20260923'
keep={candidate:'selected 4096 native-detail candidate',
 T/'references/full-layout-reference-only.png':'current geometry design; not a final game image',
 T/'references/master-layout-384-reference-only.png':'current source layout design; not a final game image',
 q/'repaired-v1/repair-focus-after.png':'same-version actual repair visual-review evidence'}
for p in (q/'repaired-v1/qa-current').glob('*.png'):keep[p]='same-version actual full-seam/junction/neighbor evidence'
items=[]
for p in sorted(T.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.npy'}:continue
    assert p.resolve().is_relative_to(T.resolve()) and not p.is_symlink()
    rel=p.relative_to(T).as_posix()
    reason=keep.get(p)
    if not reason:
        if rel.startswith('native/'):reason='native source now exported into selected 4096 candidate; source SHA and generation text retained'
        elif rel.startswith('guides/'):reason='consumed generation guide, current geometry design retained separately'
        elif 'interiors-current/' in rel:reason='temporary 1:1 review crop; exact crop boxes, SHA and current full candidate retained'
        elif 'hard-core-' in rel:reason='superseded assembly or its diagnostic image, replaced by selected repaired candidate'
        else:reason='consumed repair original, rejected evidence, preview or intermediate processing image; text retained'
    items.append({'file':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'action':'keep' if p in keep else 'delete','reason':reason})
out=T/'continuation-20260923/cleanup-selected-c07'
out.mkdir(exist_ok=False)
plan={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scopeRoot':str(T.resolve()),'authority':'User 2026-09-23 AGENTS retention rule, current selected export and references verified; c08/c09 active workers confirmed no dependency on c07 PNG sources.','selection':{'file':str(selection),'sha256':sha(selection)},'currentReferenceChecks':{key:d[key] for key in ('candidate','record','assembly','review','interiorReview')},'imageBackupCreated':False,'items':items}
(out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(out/'plan.json'),'planSha256':sha(out/'plan.json'),'keepCount':sum(x['action']=='keep' for x in items),'deleteCount':sum(x['action']=='delete' for x in items),'deleteBytes':sum(x['bytes'] for x in items if x['action']=='delete')}))
