from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

tile=Path(__file__).resolve().parent;root=tile.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected=tile/'selected/core4096.png';c10=root/'r08_c10/selected/core4096.png'
assert sha(selected)=='f234b170956464dd3233207d38d6520d5388942b771a5b25c32683c4cecfdbeb'
assert sha(c10)=='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'
delivery=json.loads((root/'r08_c10/selected/delivery.manifest.json').read_text(encoding='utf-8'))
assert delivery['qualifiedComplete4KCandidate'] is True
ctx=json.loads((root/'r09_c10/regional/context.json').read_text(encoding='utf-8'))
assert Path(ctx['northExtended']['file']).resolve().is_relative_to(root/'r08_c10')
targets={
 'registration-west/v3/core4096.png':'d3eba987004b6d75fd3ff85ab8d244d2c4a71fa9843c14d3db3a5875d8be96f4',
 'registration-west/v3/extended4326.png':'356a6bd4981093f8c1669115a3d869a611b43a48d84dd4a2ce5d22f063119ebb'}
items=[]
for relative,digest in targets.items():
    p=(tile/relative).resolve(strict=True)
    assert p.is_relative_to(tile.resolve()) and p.parent==tile/'registration-west/v3'
    assert sha(p)==digest
    items.append({'file':str(p),'sha256':digest,'bytes':p.stat().st_size,
                  'reason':'Only active consumer r08_c10 is selected and complete; consumer native sources retired; r09 active north source is c10 WESTv3. c09 selected final exists and is the future north reference.'})
record=tile/'retired-dependency-cleanup.json'
assert not record.exists()
j={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'authorization':'User2026-09-23 final-art-only retention policy',
   'scope':'Exactly two old c09 source PNGs retained by first cleanup solely for then-unfinished c10',
   'selectedC09Sha256':sha(selected),'selectedC10Sha256':sha(c10),'items':items,'status':'validated_before_delete'}
record.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
for item in items:Path(item['file']).unlink()
j['status']='completed';j['deletedPngCount']=2;j['deletedBytes']=sum(v['bytes'] for v in items)
assert sha(selected)==j['selectedC09Sha256'] and sha(c10)==j['selectedC10Sha256']
record.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'deletedPngCount':2,'deletedBytes':j['deletedBytes']}))
