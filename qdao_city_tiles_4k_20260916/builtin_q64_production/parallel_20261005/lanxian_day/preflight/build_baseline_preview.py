import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
handoff = json.loads((OUT.parent/'handoff.json').read_text(encoding='utf-8-sig'))
tiles = handoff['baselineCandidates']
preview = Image.new('RGB', (1536, 584), (242,244,247))
draw = ImageDraw.Draw(preview)
draw.text((16,12), 'CURRENT BASELINE CANDIDATES - PREVIEW ONLY - NOT NEW ART / NOT ACCEPTED', fill=(28,32,40))
derived = []
for i, item in enumerate(tiles):
    source = Path(item['file'])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != item['sha256']:
        raise ValueError(f'Baseline changed: {source}')
    with Image.open(source) as image:
        actual = list(image.size)
        if actual != [4096,4096]:
            raise ValueError(f'Unexpected dimensions: {source}')
        preview.paste(image.convert('RGB').resize((512,512), Image.Resampling.LANCZOS), (i*512,56))
    draw.text((i*512+12,36), item['tile']+' | 4096 x 4096 source | candidate', fill=(28,32,40))
    derived.append({'file':str(source), 'sha256':digest, 'sourcePixels':actual, 'previewBoxLTRB':[i*512,56,(i+1)*512,568], 'operation':'Downsample 4096x4096 to 512x512 using Pillow LANCZOS, then place without overlap; preview only.'})
path = OUT/'current-baseline-preview.png'
preview.save(path)
record = {'createdAtUtc':datetime.now(timezone.utc).isoformat(), 'role':'current baseline candidate overview only; no new generated artwork; not full-resolution QA', 'file':str(path), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'pixels':list(preview.size), 'derivedFrom':derived, 'handoffReadyAtRead':handoff['readyForProduction'], 'countedAsNewArt':False, 'formalAccepted':False, 'completeCity':False}
(OUT/'current-baseline-preview.derivation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(path))
