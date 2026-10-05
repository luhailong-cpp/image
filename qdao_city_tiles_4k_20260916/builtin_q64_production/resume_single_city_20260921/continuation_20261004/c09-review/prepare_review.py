from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
SESSION = OUT.parent.parent
PAIR = SESSION / 'next_tile_r08_c09/continuation-20260923/versions/cross-boundary-pair-v1-20260923T125829004582Z'
ROOT = Path('D:/work/image')

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def info(p):
    return {'file': str(p), 'sha256': sha(p)}

def write(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def local(path):
    value = path.replace('\\', '/')
    for old in ['D:/luyuan/wuxingqitan/image', 'E:/work/image']:
        if value.startswith(old + '/'):
            return ROOT / value[len(old)+1:]
    return Path(value)

assembly = read(PAIR / 'assembly.json')
index = read(PAIR / 'qa/index.json')
tiles = {name: Image.open(PAIR / (name + '.png')).convert('RGB') for name in ['r08_c09', 'r09_c09']}
assert all(im.size == (4096, 4096) for im in tiles.values())
for entry in assembly['candidates']:
    assert sha(local(entry['candidate']['file'])) == entry['candidate']['sha256']

joined = Image.new('RGB', (4096, 8192))
joined.paste(tiles['r08_c09'], (0, 0))
joined.paste(tiles['r09_c09'], (0, 4096))

evidence = []
for item in index['evidence']:
    f = local(item['file'])
    im = Image.open(f).convert('RGB')
    expected = None
    iid = item['id']
    scope = item['scope']
    if iid.startswith('shared-wide-'):
        x0, x1 = scope['xRange']
        expected = joined.crop((x0, 3469, x1, 4723))
    elif '-full-' in iid and iid.startswith(('r08_c09', 'r09_c09')):
        expected = Image.new('RGB', (1024, 2048))
        name = iid[:7]
        for n, box in enumerate(scope['segmentsLTRB']):
            part = tiles[name].crop(box)
            if scope['rotation90ForVertical']:
                part = part.transpose(Image.Transpose.ROTATE_90)
            expected.paste(part, (0, n * 512))
    elif iid.endswith('-nine-junctions'):
        expected = Image.new('RGB', (1536, 1536))
        name = iid[:7]
        for n, (x, y) in enumerate(scope['centersXY']):
            expected.paste(tiles[name].crop((x-256, y-256, x+256, y+256)), ((n % 3)*512, (n // 3)*512))
    elif '-external-full' in iid:
        neighbor = local(scope['neighbor']['file'])
        assert sha(neighbor) == scope['neighbor']['sha256']
        arr = np.asarray(Image.open(neighbor).convert('RGB'))
        cur = np.asarray(tiles['r09_c09'])
        side = scope['side']
        if side == 'left':
            edge = np.concatenate([arr[:, -256:], cur[:, :256]], axis=1)
        elif side == 'right':
            edge = np.concatenate([cur[:, -256:], arr[:, :256]], axis=1)
        else:
            edge = np.concatenate([cur[-256:], arr[:256]], axis=0)
        expected = Image.new('RGB', (1024, 2048))
        for n in range(4):
            part = Image.fromarray(edge[n*1024:(n+1)*1024] if side != 'bottom' else edge[:, n*1024:(n+1)*1024])
            if side != 'bottom':
                part = part.transpose(Image.Transpose.ROTATE_90)
            expected.paste(part, (0, n*512))
    assert expected is not None, iid
    pixel_equal = np.array_equal(np.asarray(im), np.asarray(expected))
    assert pixel_equal, iid
    current_sha = sha(f)
    assert current_sha == item['sha256'], iid
    evidence.append({'id': iid, **info(f), 'size': im.size, 'indexShaMatches': True,
                     'reconstructedFromCurrentCandidatePixelsEqual': pixel_equal, 'sourceScope': scope,
                     'viewedThisTurn': True, 'viewedAt': '1:1 pixels via view_image detail=original',
                     'formalAccepted': False})

targets = [
    {'id': 'shared-segment-02', 'file': 'repair-shared-segment-02-context-1254.png',
     'space': 'r08_c09+r09_c09 vertical pair', 'box': [909, 3469, 2163, 4723],
     'boundaryYInContext': 627, 'tileBoundaryY': 4096,
     'description': '共边第2段：跨上图最后627行和下图最前627行；包含两侧115像素上下文。',
     'im': joined.crop((909, 3469, 2163, 4723)), 'sources': ['r08_c09', 'r09_c09']},
    {'id': 'lower-return-segment-04', 'file': 'repair-lower-return-segment-04-context-1254.png',
     'space': 'r09_c09 local', 'box': [2842, 0, 4096, 1254],
     'oldReturnYInContext': 448,
     'description': '第4段下回接：保留r09顶部及旧回接以下806行；涵盖裂纹与光滑材质的整块结构，避免仅移动矩形回接。',
     'im': tiles['r09_c09'].crop((2842, 0, 4096, 1254)), 'sources': ['r09_c09']}
]
outputs = []
for target in targets:
    f = OUT / target['file']
    target['im'].save(f)
    assert Image.open(f).size == (1254, 1254)
    meta = {k: v for k, v in target.items() if k not in ['im', 'sources']}
    record = {'schemaVersion': 1, **info(f), 'width': 1254, 'height': 1254,
              'format': 'PNG', 'createdAt': datetime.now(timezone.utc).isoformat(),
              'kind': 'mechanical_native_pixel_reference_crop',
              'derivedFrom': [{**info(PAIR / (name + '.png')), 'sourceRecord': info(PAIR / 'assembly.json')} for name in target['sources']],
              'operation': {'type': 'crop' if len(target['sources']) == 1 else 'concatenate_vertical_then_crop',
                            'coordinateSpace': target['space'], 'cropLTRB': target['box'],
                            'resampling': 'none', 'resized': False, 'colorAdjustment': 'none', 'newModelCalls': 0},
              'actualModel': None, 'actualQuality': None,
              'unverifiedReason': '源图assembly中本次宿主管理图像模型/质量未披露；本裁图未调用模型。',
              'formalAccepted': False, 'purpose': 'Next image-generation reference; not a game tile'}
    write(str(f) + '.generation.json', record)
    outputs.append({**meta, **info(f), 'generationRecord': info(str(f) + '.generation.json')})

write(OUT / 'source-verification.json', {
    'checkedAtUtc': datetime.now(timezone.utc).isoformat(),
    'sourceAssembly': info(PAIR / 'assembly.json'), 'sourceIndex': info(PAIR / 'qa/index.json'),
    'candidates': [info(PAIR / (name + '.png')) for name in tiles],
    'all21QaFileHashesMatchHistoricalIndex': len(evidence) == 21,
    'all21QaImagesReconstructedFromCurrentPixelsMatchExactly': True,
    'evidence': evidence, 'nextRepairReferences': outputs,
    'selectionChanged': False, 'formalAccepted': False, 'clientRuntimeAccepted': False})
print(json.dumps({'evidenceCount': len(evidence), 'references': outputs}, ensure_ascii=True, indent=2))
