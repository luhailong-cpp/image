"""Native day-to-lantern c15 expansion; own tile and c15progress.json only.

Commands: init | prepare ROW COL | record PATCH_ID RAW_PATH | status
This script prepares inputs and records actual built-in results; it makes no API
calls and never updates production.py, current-work.json, progress.json or c14.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = Path('D:/work/image')
DAY = ROOT.parent / 'donghai_day/r08_c15'
TILE = ROOT / 'r08_c15'
STYLE = PROJECT / 'designs/gameplay-ui/04-guild.png'
WEST = ROOT / 'r08_c14/native/r01_c04.png'
WEST_SHA = 'bd57f360605e1e2d3a14c568c3866963c650f213594fa57091d05addb4b4ac48'
CORE_ORIGIN = (57344, 28672)
NATIVE_ORIGIN = (57229, 28557)


def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def item(path, role): return {'file': str(path), 'sha256': sha(path), 'role': role}


def write(path, value):
    path = Path(path).resolve()
    assert path.is_relative_to(TILE.resolve()) or path == (ROOT / 'c15progress.json').resolve(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.c15-', suffix='.writing', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def validate_image(path, expected_size, expected_sha):
    assert sha(path) == expected_sha, f'SHA changed: {path}'
    with Image.open(path) as image:
        image.load()
        assert image.size == expected_size and image.mode in ('RGB', 'RGBA'), (path, image.size, image.mode)
        if image.mode == 'RGBA': assert image.getchannel('A').getextrema() == (255, 255), path
        return image.convert('RGB')


def native(path):
    path = Path(path)
    record_path = Path(str(path) + '.generation.json')
    record = read(record_path)
    assert Path(record['file']).resolve() == path.resolve(), path
    assert [record['width'], record['height']] == [1254, 1254], path
    assert record['resizedAfterGeneration'] is False and record.get('finalArtUpscaled') is not True, path
    return validate_image(path, (1254, 1254), record['sha256']), record


def init():
    west = validate_image(WEST, (1254, 1254), WEST_SHA)
    for folder in ('guides', 'native', 'prompts', 'qa', 'output'):
        (TILE / folder).mkdir(parents=True, exist_ok=True)
    tone = TILE / 'guides/neighbor-tone-native.png'
    crop = [0, 0, 1254, 1254]
    if not tone.exists(): west.crop(crop).save(tone)
    assert list(Image.open(tone).size) == [1254, 1254], tone
    write(str(tone) + '.generation.json', {
        'file': str(tone), 'sha256': sha(tone), 'operation': 'exact unscaled c14 native; palette only',
        'cropXYXY': crop, 'derivedFrom': [item(WEST, 'pinned west festival native c14 r01_c04; fragment only')],
        'finalArt': False, 'referenceRole': 'palette and existing material rendering; never target geometry',
    })
    write(TILE / 'source-contract.json', {
        'createdAtUtc': now(), 'tile': 'r08_c15', 'dayDirectory': str(DAY),
        'west': item(WEST, 'pinned c14 native palette source; west context is verified per-row c14 native'),
        'westSourceSha256': WEST_SHA, 'globalCoreXYWH': [*CORE_ORIGIN, 4096, 4096],
        'nativeWindowOriginXY': list(NATIVE_ORIGIN), 'nativePixels': [1254, 1254],
        'corePixels': 1024, 'haloPixels': 115, 'adjacentOverlapPixels': 230,
        'geometryPolicy': 'Each day native patch SHA is the exact geometry authority for the corresponding festival patch; no independent layout substitution.',
        'unknownNorthHaloIsNotExistingFestivalPixels': True,
        'formalAccepted': False, 'wholeCityComplete': False,
    })
    return status()


def status():
    files = sorted((TILE / 'native').glob('r??_c??.png'))
    valid = []
    for path in files:
        _, record = native(path)
        valid.append({'id': path.stem, 'file': str(path), 'sha256': record['sha256']})
    state = {'updatedAtUtc': now(), 'appearance': 'donghai_lantern', 'tile': 'r08_c15',
             'globalRectXYWH': [*CORE_ORIGIN, 4096, 4096], 'nativePatchesSaved': len(valid),
             'nativePatchesRequired': 16, 'nativeSources': valid,
             'dayNativePatchesAvailable': len(list((DAY / 'native').glob('r??_c??.png'))),
             'completePixelCandidateProduced': False, 'fragmentsCountAsTiles': False,
             'formalAccepted': False, 'wholeCityComplete': False, 'clientAccepted': False,
             'phase': 'native_expansion_in_progress', 'globalStateFilesModified': False}
    write(ROOT / 'c15progress.json', state)
    return state


def prepare(row, column):
    assert 1 <= row <= 4 and 1 <= column <= 4
    name = f'r{row:02}_c{column:02}'
    assert not (TILE / 'native' / f'{name}.png').exists(), 'Do not overwrite an existing native result'
    if not (TILE / 'source-contract.json').exists(): init()
    west = validate_image(WEST, (1254, 1254), WEST_SHA)
    source = DAY / 'native' / f'{name}.png'
    geometry_image, day_record = native(source)
    source_record_path = Path(str(source) + '.generation.json')
    source_record_sha = sha(source_record_path)
    frozen_source = TILE / 'guides' / f'{name}-day-source.png'
    shutil.copyfile(source, frozen_source)
    assert sha(frozen_source) == day_record['sha256'], 'DAY source changed while snapshotting; prepare again'
    frozen_record = Path(str(frozen_source) + '.generation.json')
    write(frozen_record, {'file': str(frozen_source), 'sha256': sha(frozen_source),
                        'operation': 'exact original-byte snapshot of verified DAY source at prepare time; no resampling',
                        'derivedFrom': [{**item(source, 'current DAY geometry authority'), 'generationRecord': str(source_record_path), 'generationRecordSha256': source_record_sha}],
                        'sourceGenerationRecordSnapshot': day_record, 'finalArt': False})
    geometry = {**item(frozen_source, 'exact native DAY geometry snapshot; preserve every object, edge crossing, footprint, paving joint and cast-shadow silhouette'),
                'dayAuthorityFile': str(source), 'dayAuthoritySha256': day_record['sha256'],
                'generationRecord': str(frozen_record), 'generationRecordSha256': sha(frozen_record)}
    ox, oy = (column - 1) * 1024, (row - 1) * 1024
    guide, context = geometry_image.copy(), []
    if column == 1:
        west_context = ROOT / 'r08_c14' / 'native' / f'r{row:02}_c04.png'
        west_native, west_record = native(west_context)
        crop, paste = [1024, 0, 1254, 1254], [0, 0]
        guide.paste(west_native.crop(crop), paste)
        context.append({**item(west_context, 'exact c14 eastern native overlap at the identical global coordinates; fragment context only, assembly and tone may change later'), 'generationRecord': str(west_context) + '.generation.json', 'generationRecordSha256': sha(str(west_context) + '.generation.json'), 'sourceCropXYXY': crop, 'pasteXY': paste, 'resized': False})
    if column > 1: assert (TILE / 'native' / f'r{row:02}_c{column-1:02}.png').exists(), 'Left native context is required'
    if row > 1: assert (TILE / 'native' / f'r{row-1:02}_c{column:02}.png').exists(), 'Upper native context is required'
    for rr, cc in ((row - 1, column - 1), (row - 1, column), (row - 1, column + 1), (row, column - 1)):
        path = TILE / 'native' / f'r{rr:02}_c{cc:02}.png'
        if not path.exists(): continue
        neighbor, neighbor_record = native(path)
        px, py = (cc - 1) * 1024, (rr - 1) * 1024
        x0, y0, x1, y1 = max(ox, px), max(oy, py), min(ox + 1254, px + 1254), min(oy + 1254, py + 1254)
        if x1 <= x0 or y1 <= y0: continue
        crop, paste = [x0 - px, y0 - py, x1 - px, y1 - py], [x0 - ox, y0 - oy]
        guide.paste(neighbor.crop(crop), paste)
        context.append({**item(path, 'exact generated festival neighbor overlap at shared coordinates'), 'sourceCropXYXY': crop, 'pasteXY': paste, 'resized': False})
    output = TILE / 'guides' / f'{name}.png'
    guide.save(output)
    write(str(output) + '.generation.json', {
        'file': str(output), 'sha256': sha(output), 'operation': 'native day geometry copy plus exact existing festival overlap; no resizing',
        'derivedFrom': [geometry] + context, 'context': context,
        'globalRectXYWH': [NATIVE_ORIGIN[0] + ox, NATIVE_ORIGIN[1] + oy, 1254, 1254], 'finalArt': False,
    })
    references = [geometry, item(output, 'edit target: same DAY geometry with exact FESTIVAL neighbor context strips'),
                  item(STYLE, 'PRIMARY confirmed Daoist Q art style; ignore UI, text and layout'),
                  item(TILE / 'guides/neighbor-tone-native.png', 'existing c14 FESTIVAL palette/material reference only; no geometry transfer')]
    prompt = f'''Use case: lighting-weather.
Asset: 五行奇谈 original fishing-village Lantern Festival map, internal donghai_lantern, tile r08_c15, native fragment {name}.
Image1 is the exact native DAY GEOMETRY authority. Image2 is the same fixed crop with genuine already-FESTIVAL neighboring pixel strips. Image3 is the user-confirmed PRIMARY rendering style. Image4 is ONLY the adjacent c14 FESTIVAL palette and material reference.
Convert image2's remaining day appearance into the same bright Lantern Festival look. Join the existing festival context without a paste boundary. Preserve image1's exact shape and location of every roof tile, timber joint, post, rail, paving joint, tree/leaf outline, wall footprint, entrance, water ripple, reflected silhouette, shoreline and edge crossing. Keep scale, camera, framing and occlusion unchanged. Do not reinterpret the composition from image4. No new props, buildings, lanterns, characters or vegetation. Existing lanterns may glow softly.
Follow image3's rounded, full, clean hand-painted Daoist Q rendering and image4's neighboring restrained warm palette: honey timber, cream stone, gentle peach highlights, soft lavender shaded planes and green foliage. Keep every roof's original material hue from image1, including orange-red tiles where present; keep water a distinct clean blue base with soft violet shade and restrained warm reflected light matching the actual festival overlaps; retain its precise ripple and reflected structural silhouettes. Add only matching festival light. Match the nearby native festival pixels while avoiding exaggerated orange wash, saturated yellow flood, new glitter, extra glow or over-dark shadows. Preserve distinct material colors and smooth lighting across overlaps; avoid straight or jagged color bands.
Return one opaque 1254x1254 image at exactly the same crop. Central1024 core plus115 context each side, native detailed painting with no enlargement. Crisp structure; no blur, grain, noise, sharpening halo, grid, border, writing, UI or watermark. Highest visual completion; configured target gpt-image-2.5-sunburst/max is a target, not an exposed selector.
Native globalXYWH={[NATIVE_ORIGIN[0]+ox,NATIVE_ORIGIN[1]+oy,1254,1254]}; coreglobalXYWH={[CORE_ORIGIN[0]+ox,CORE_ORIGIN[1]+oy,1024,1024]}. Do not render coordinate labels.'''
    prompt_path = TILE / 'prompts' / f'{name}.txt'
    prompt_path.write_text(prompt, encoding='utf-8')
    request = {'prompt': prompt, 'referenced_image_paths': [ref['file'] for ref in references], 'transparent_background': False}
    write(TILE / 'prompts' / f'{name}.references.json', references)
    write(TILE / 'prompts' / f'{name}.request.json', request)
    return request


def record(name, raw_path):
    assert re.fullmatch(r'r0[1-4]_c0[1-4]', name), name
    raw, output = Path(raw_path), TILE / 'native' / f'{name}.png'
    assert not output.exists(), output
    raw_sha = sha(raw)
    image = validate_image(raw, (1254, 1254), raw_sha)
    request_path = TILE / 'prompts' / f'{name}.request.json'
    request, references = read(request_path), read(TILE / 'prompts' / f'{name}.references.json')
    for reference in references: assert sha(reference['file']) == reference['sha256'], reference['file']
    shutil.copyfile(raw, output)
    prompt = TILE / 'prompts' / f'{name}.txt'
    write(str(output) + '.generation.json', {
        'file': str(output), 'sha256': raw_sha, 'generatedAt': now(), 'width': 1254, 'height': 1254, 'format': 'PNG',
        'tool': 'image_gen.imagegen', 'route': 'builtin', 'configSnapshot': read(ROOT / 'batch-model-check.json')['configSnapshot'],
        'submittedParameters': {'model': None, 'quality': None, **request}, 'actualModel': None, 'actualQuality': None,
        'unverifiedReason': 'Host managed; no model/quality selectors or returned model/quality metadata.',
        'evidence': {'toolResultSourcePath': str(raw), 'sha256': raw_sha, 'toolResultSha256': raw_sha},
        'prompt': str(prompt), 'promptSha256': sha(prompt), 'requestFile': str(request_path), 'requestSha256': sha(request_path),
        'references': references, 'geometryMatchedTo': references[0],
        'resizedAfterGeneration': False, 'finalArtUpscaled': False, 'sourceBytesPreserved': True,
        'role': '1024 native core with115 context; fragment not a4K tile', 'visualQA': 'pending',
    })
    status()
    return {'file': str(output), 'sha256': raw_sha, 'pixels': list(image.size)}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    command = sys.argv[1]
    if command == 'init': result = init()
    elif command == 'status': result = status()
    elif command == 'prepare': result = prepare(int(sys.argv[2]), int(sys.argv[3]))
    elif command == 'record': result = record(sys.argv[2], sys.argv[3])
    else: raise SystemExit('Unknown command')
    print(json.dumps(result, ensure_ascii=False))

