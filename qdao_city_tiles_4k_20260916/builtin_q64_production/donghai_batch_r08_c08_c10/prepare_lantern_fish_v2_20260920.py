from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone

prod = Path(__file__).resolve().parent.parent
dst = prod/'donghai_lantern/r08_c08_c09_c10_joint/repairs_v2/fish_basin'
assert not dst.exists(), 'Never overwrite prepared references'
dst.mkdir(parents=True)
box = [7680,2350,8934,3604]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs = []
for i, (appearance, version, name, role) in enumerate([
    ('donghai_lantern','output_v1','lantern-target.png','edit target: lantern lighting and all surrounding objects'),
    ('donghai_day','output_v3','day-geometry.png','fish-basin geometry reference: final selected day version')],1):
    src = prod/appearance/'r08_c08_c09_c10_joint'/version/'core12288x4096.png'
    out = dst/name
    im = Image.open(src).convert('RGB').crop(box)
    assert im.size == (1254,1254)
    im.save(out,compress_level=4)
    refs.append(dict(imageIndex=i,path=str(out),sha256=sha(out),pixels=[1254,1254],role=role,sourcePath=str(src),sourceSha256=sha(src),cropXYXY=box,resized=False))
record = dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),coordinateSpace='triple_core',cropXYXY=box,references=refs,referenceCount=2,configuredModelTarget='gpt-image-2.5-sunburst',configuredQualityTarget='max',actualBackendModel=None,actualQualityPreset=None,route='builtin_image_gen',scriptSha256=sha(__file__))
(dst/'reference-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
