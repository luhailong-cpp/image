from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
HOST = Path('C:/Users/luyua/.codex/generated_images/01a10997-f575-7002-8029-c9cdf6a0e32a/exec-be2a3bfe-7f8f-4827-ab3d-d294a592f5e6.png')
STYLE = Path('D:/work/image/designs/gameplay-ui/04-guild.png')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
src = read(R/'context.png.generation.json')
assert sha(R/'context.png') == src['sha256']
for part in src['parts']:
    assert sha(part['source']['path']) == part['source']['sha256']

native = R/'native.png'
if not native.exists():
    shutil.copy2(HOST, native)
assert sha(native) == sha(HOST)
receipt = read(R/'tool-response.json')
original = np.array(Image.open(R/'context.png').convert('RGB'))
generated = np.array(Image.open(native).convert('RGB'))
assert original.shape == generated.shape == (1254, 1254, 3)
if not (R/'native.png.generation.json').exists():
    save(R/'native.png.generation.json', {
        'file': str(native), 'sha256': sha(native),
        'generatedAt': None, 'actualServerGeneratedAt': None,
        'generationCompletionObservedAt': receipt['ended']['current_time'],
        'generationObservationWindow': {'start': receipt['started'], 'end': receipt['ended']},
        'timeEvidence': 'Clock readings around the builtin tool call are completion/observation evidence, not an exposed server generation timestamp.',
        'width': 1254, 'height': 1254, 'format': 'PNG',
        'tool': 'image_gen.imagegen', 'route': 'builtin', 'toolCallId': None,
        'configSnapshot': read(R/'config.snapshot.json'),
        'submittedParameters': {'model': None, 'quality': None, 'size': None, 'transparent_background': False},
        'actualModel': None, 'actualQuality': None,
        'unverifiedReason': 'Host-managed builtin did not disclose actual model, quality, or server timestamp; configuration targets and prompt text are not actual model evidence.',
        'evidence': {'receipt': {'file': str(R/'tool-response.json'), 'sha256': sha(R/'tool-response.json')}, 'hostOutputPath': str(HOST), 'hostOutputSha256': sha(HOST), 'byteIdenticalCopy': True},
        'prompt': {'file': str(R/'prompt.txt'), 'sha256': sha(R/'prompt.txt')},
        'references': [
            {'file': str(R/'context.png'), 'sha256': src['sha256'], 'role': 'exact native edit target', 'generationRecord': str(R/'context.png.generation.json')},
            {'file': str(STYLE), 'sha256': sha(STYLE), 'role': 'approved painterly style only'},
        ], 'formalAccepted': False,
    })

# Disjoint local masks. No resizing, image filtering, registration or tone adjustment.
regions = [
    {'id': 'horizontal_internal_step', 'outerLTRB': [65, 220, 1130, 442], 'coreLTRB': [105, 282, 1090, 378]},
    {'id': 'center_diagonal_break', 'outerLTRB': [485, 540, 760, 745], 'coreLTRB': [550, 595, 710, 695]},
]
y, x = np.mgrid[:1254, :1254]
alpha = np.zeros((1254, 1254), np.float64)
for reg in regions:
    x0, y0, x1, y1 = reg['outerLTRB']
    a, b, c, d = reg['coreLTRB']
    t = np.minimum.reduce([(x-x0)/(a-x0), (x1-1-x)/(x1-1-c), (y-y0)/(b-y0), (y1-1-y)/(y1-1-d)])
    t = np.clip(t, 0, 1)
    alpha = np.maximum(alpha, t*t*(3-2*t))
mask = np.rint(alpha*255).astype(np.uint8)
merged = ((original.astype(np.uint32)*(255-mask[:, :, None]) + generated.astype(np.uint32)*mask[:, :, None] + 127)//255).astype(np.uint8)
assert np.array_equal(original[mask == 0], merged[mask == 0])
Image.fromarray(mask).save(R/'mask.png')
Image.fromarray(merged).save(R/'composite.png')
operation = {'kind': 'two_disjoint_local_native_AI_mask_merges', 'regions': regions,
    'sourcePixelScale': 1, 'sourceUpscaling': False, 'sourceResampling': False,
    'geometricRegistration': None, 'actualDisplacementPixels': 0, 'toneAdjustment': False, 'imageBlur': False,
    'maskFunction': 'Maximum of two rectangle smoothstep alpha fields; no artwork filtering or generated detail synthesis during merge.',
    'mask': {'file': str(R/'mask.png'), 'sha256': sha(R/'mask.png')}, 'maskZeroPixelsUnchanged': True}
inputs = [{'file': str(R/n), 'sha256': sha(R/n), 'generationRecord': str(R/(n+'.generation.json'))} for n in ['context.png', 'native.png']]
for n in ['mask.png', 'composite.png']:
    save(R/(n+'.generation.json'), {'file': str(R/n), 'sha256': sha(R/n), 'createdAt': now,
        'width': 1254, 'height': 1254, 'format': 'PNG', 'derivedFrom': inputs, 'operation': operation,
        'artifactRole': 'numeric alpha mask only' if n == 'mask.png' else 'local native artwork composite', 'formalAccepted': False})

O = R/'coupled'
O.mkdir(exist_ok=True)
outputs = []
reconstructed = Image.new('RGB', (1254, 1254))
for part in src['parts']:
    source = part['source']
    with Image.open(source['path']) as im:
        im = im.convert('RGB')
        before = np.array(im)
        box = part['cropLTRB']
        dx, dy = part['pasteXY']
        w, h = box[2]-box[0], box[3]-box[1]
        assert im.crop(box).tobytes() == Image.fromarray(original).crop((dx, dy, dx+w, dy+h)).tobytes()
        im.paste(Image.fromarray(merged).crop((dx, dy, dx+w, dy+h)), box[:2])
        f = O/(part['tile']+'.png')
        im.save(f)
        changed = np.any(before != np.array(im), axis=2)
        yy, xx = np.where(changed)
        entry = {'tileId': part['tile'], 'path': str(f), 'sha256': sha(f), 'width': 4096, 'height': 4096,
            'sourcePath': source['path'], 'sourceSha256': source['sha256'], 'changedPixels': int(changed.sum()),
            'changedBBoxLTRB': [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)], 'generationRecord': str(f)+'.generation.json'}
        save(str(f)+'.generation.json', {'file': str(f), 'sha256': sha(f), 'createdAt': now, 'width': 4096, 'height': 4096, 'format': 'PNG',
            'derivedFrom': [{'file': source['path'], 'sha256': source['sha256'], 'generationRecord': source['generationRecord']}] + inputs,
            'operation': operation, 'placement': part, 'formalAccepted': False, 'productionSelectionChanged': False})
        outputs.append(entry)
        reconstructed.paste(im.crop(box), (dx, dy))
assert reconstructed.tobytes() == Image.fromarray(merged).tobytes()
Q = R/'qa'
Q.mkdir(exist_ok=True)
boxes = {
    'horizontal-center': [40, 275, 1155, 390],
    'horizontal-north': [25, 175, 1170, 285],
    'horizontal-south': [25, 378, 1170, 492],
    'horizontal-west': [15, 180, 165, 482],
    'horizontal-east': [1030, 180, 1180, 482],
    'diagonal-center': [450, 520, 800, 770],
    'diagonal-north': [435, 490, 810, 600],
    'diagonal-south': [435, 690, 810, 795],
    'diagonal-west': [435, 500, 570, 785],
    'diagonal-east': [695, 500, 810, 785],
}
qa = []
for name, box in boxes.items():
    f = Q/(name+'.png')
    im = reconstructed.crop(box)
    im.save(f)
    item = {'name': name, 'file': str(f), 'sha256': sha(f), 'contextLTRB': box, 'nativeScale': 1, 'actuallyViewed': False}
    save(str(f)+'.generation.json', {'file': str(f), 'sha256': sha(f), 'createdAt': now, 'width': im.width, 'height': im.height,
        'format': 'PNG', 'derivedFrom': [{'file': o['path'], 'sha256': o['sha256']} for o in outputs],
        'operation': {'kind': 'exact native crop from exported-tile reconstruction', 'contextLTRB': box, 'nativeScale': 1, 'resampling': False}, 'formalAccepted': False})
    qa.append(item)
sourceChecks = [{'path': p['source']['path'], 'expectedSha256': p['source']['sha256'], 'observedSha256': sha(p['source']['path']), 'unchanged': sha(p['source']['path']) == p['source']['sha256']} for p in src['parts']]
save(R/'bindings.json', {'createdAt': now, 'status': 'local_branch_pending_native_visual_review', 'contextSource': src,
    'outputs': outputs, 'qaBoards': qa, 'operation': operation, 'sourceChecks': sourceChecks,
    'exportedTilesReconstructCompositeExactly': True, 'formalAccepted': False, 'wholeCityComplete': False,
    'productionSelectionChanged': False, 'additionalUniqueTileCount': 0,
    'integrationRule': 'Branch is based on exact original source SHA. Parent may merge nonoverlapping changed pixels with other repair branches after checking original source identity; never treat this branch as cumulative west-upper output.'})
print(json.dumps({'outputs': outputs, 'qaCount': len(qa)}, ensure_ascii=True))
