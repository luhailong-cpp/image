"""Evidence audit for the two directions owned by inventory09; image content is untouched."""
from PIL import Image, ImageSequence
from common import DELIVERY, GENERATION, read_json, sha, json_bytes, utc_now

for direction in ('N', 'SW'):
    work = DELIVERY / 'work' / direction
    slots = [(f'walk/{direction}/{f:02d}.png', f) for f in range(1, 17)] + [(f'idle/{direction}.png', None)]
    records = []
    for relative, frame in slots:
        path = work / 'runtime' / relative
        source = read_json(work / 'sources' / (relative + '.json'))
        raw = source['source']['path']
        generation = read_json(source['source']['generationRecord'])
        im = Image.open(path)
        assert im.mode == 'RGBA' and im.size == (1024, 1024)
        assert min(source['nativeSize']) >= 1024
        assert sha(path) == source['outputSha256'] and sha(raw) == source['source']['sha256']
        assert source['operation']['commonScale'] == .88
        assert source['operation']['anchorAfterPx'] == [512, 942]
        assert not source['operation']['mirrored'] and not source['operation']['poseInterpolated']
        assert source['operation']['chromaProfile'] == 'none'
        records.append({'slot': relative, 'selectedBatch': __import__('pathlib').Path(raw).parent.name, 'rawSha256': sha(raw), 'outputSha256': sha(path), 'sourceRecord': str(work / 'sources' / (relative + '.json')), 'nativeSize': source['nativeSize']})
    assert len({r['rawSha256'] for r in records}) == 17
    assert len({r['outputSha256'] for r in records}) == 17
    previews = []
    for bg in ('dark', 'light'):
        path = work / 'qa' / f'walk-30ms-{bg}.gif'
        gif = Image.open(path)
        durations = [f.info['duration'] for f in ImageSequence.Iterator(gif)]
        assert durations == [30] * 16 and gif.info['loop'] == 0
        previews.append({'path': str(path), 'frameCount': 16, 'durationsMs': durations, 'cycleMs': sum(durations), 'loop': 0, 'sha256': sha(path)})
    (work / 'qa' / 'selection-audit.json').write_bytes(json_bytes({'character': '09_bamboo_archer_girl', 'direction': direction, 'auditedAt': utc_now(), 'walkCount': 16, 'idleCount': 1, 'uniqueSourceCount': 17, 'uniqueExportCount': 17, 'technicalAssertionsPassed': True, 'slots': records, 'previews': previews, 'browserPlayback': 'unverified: CUA browser inventory empty; iab returned Browser is not available', 'unityRuntime': 'not_tested'}))
    idle = Image.open(work / 'runtime' / 'idle' / (direction + '.png')).convert('RGBA')
    canvas = Image.new('RGB', (2048, 1024))
    for offset, bg in ((0, (25,32,40)), (1024, (242,239,225))):
        comp = Image.new('RGBA', idle.size, bg + (255,)); comp.alpha_composite(idle)
        canvas.paste(comp.convert('RGB'), (offset, 0))
    canvas.save(work / 'qa' / 'idle-dark-light.jpg', quality=95)
    print(direction, '17 unique native sources / 17 verified exports / two 16x30ms loops')
