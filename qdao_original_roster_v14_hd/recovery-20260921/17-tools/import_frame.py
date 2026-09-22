"""Import one real character 17 walk/idle into a fresh isolated attempt stage."""
from pathlib import Path
from types import SimpleNamespace
import argparse, json
import numpy as np
from PIL import Image, ImageDraw
from common import *

def reconstruct_one(out, key):
    records = read(out / 'processing/frame-sources.json')
    record = records[key]
    raw_path = out / record['source']['path']
    require(sha(raw_path) == record['source']['sha256'], 'Raw SHA changed')
    with Image.open(raw_path) as image:
        raw = image.convert('RGBA')
    require(record['source']['grid'] == [1, 1] and min(raw.size) >= 1024, 'Need a complete native single frame')
    require(record['common_scale'] == .88, 'Character-wide scale must remain .88')
    prepared = np.array(raw)
    prepared[:, :, 3][prepared[:, :, 3] <= record['alpha_cleanup_threshold']] = 0
    keyer = module('ghost_verify_keyer', PACKAGE / 'tools/vendor/generate2dsprite.py')
    edge = module('ghost_verify_edge', PACKAGE / 'tools/vendor/edge_despill.py')
    keyed = keyer.remove_bg_magenta(Image.fromarray(prepared, 'RGBA'), *record['chroma_thresholds'])
    factor = 1024 / max(raw.size) * .88
    require(0 < factor <= 1 and factor == record['whole_cell_scale'], 'Scale contract differs')
    normal = keyed.resize((round(raw.width * factor), round(raw.height * factor)), Image.Resampling.LANCZOS)
    clean, stats = edge.despill(normal, radius=4, reference_radius=12)
    require(np.array_equal(np.asarray(normal)[:, :, 3], np.asarray(clean)[:, :, 3]), 'Despill changed alpha')
    y, x = np.where(np.asarray(clean)[:, :, 3] > 8)
    top = int(y.min())
    ax = float(np.median(x[y < top + max(1, int((int(y.max()) - top) * .42))]))
    delta = [round(512 - ax), 942 - int(y.max())]
    require(delta == record['translation_px'], 'Alignment differs')
    result = Image.new('RGBA', (1024, 1024))
    result.paste(clean, tuple(delta))
    for name, image in [('cell', raw), ('keyed', keyed), ('normalized', normal), ('cleaned', clean), ('final', result)]:
        evidence = record['stages'][name]
        path = out / evidence['path']
        with Image.open(path) as stored:
            require(stored.convert('RGBA').tobytes() == image.tobytes() and sha(path) == evidence['sha256'], 'Stage reconstruction differs: ' + name)
    with Image.open(out / key) as final:
        require(final.mode == 'RGBA' and final.size == (1024, 1024) and final.tobytes() == result.tobytes(), 'Export reconstruction differs')
        alpha = np.asarray(final)[:, :, 3]
        require(alpha.min() == 0 and alpha.max() > 8, 'Missing genuine transparent background/body')
    require(sha(out / key) == record['output_sha256'], 'Output SHA changed')
    return {'status': 'single_frame_reconstructed_visual_pending', 'slot': key, 'verifiedAt': now(),
            'output_sha256': sha(out / key), 'native_size': list(raw.size), 'final_size': [1024, 1024],
            'alpha_min_max': [int(alpha.min()), int(alpha.max())], 'common_scale': .88,
            'despill_stats': stats, 'visual_review': 'pending', 'synthetic_frames_created': 0}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--chroma-profile', choices=('standard', 'purple-preserve'), default='standard')
    args = parser.parse_args()
    archive = archive_path(args.archive)
    request = request_data(archive)
    receipt = read(archive / 'generation-receipt.json')
    metadata = read(archive / 'raw.png.generation.json')
    require(receipt['generation_calls'] == 1 and receipt['paid_api_calls'] == 0, 'Need one successful builtin call and no paid API')
    require(sha(archive / 'raw.png') == metadata['sha256'] == receipt['original_sha256'], 'Archive SHA mismatch')
    require(sha(Path(receipt['original_generated_file'])) == metadata['sha256'], 'Original generated file differs')
    out = HERE / 'staging' / archive.name / 'candidate' / CHAR
    require(not out.exists(), 'Attempt already imported; preserve it and use a fresh attempt')
    pipe = module('ghost_pipeline', PACKAGE / 'tools/pipeline.py')
    pipe.output = lambda character: out if character == CHAR else (_ for _ in ()).throw(ValueError('17 only'))
    pipe.preview = lambda: None
    pipe.import_sheet(SimpleNamespace(command='import-' + request['kind'], character=CHAR, direction=request['direction'],
        source=archive / 'raw.png', prompt=archive / 'prompt.txt', receipt=archive / 'generation-receipt.json',
        batch_id=archive.name, common_scale=.88, chroma_profile=args.chroma_profile, rows=1, cols=1,
        source_cell_indices=None, idle_order=None, output_frames=str(request['frame']) if request['kind'] == 'walk' else None,
        start_frame=1))
    key = request['slot']
    validation = reconstruct_one(out, key)
    save_new(out / 'review/single-frame-validation.json', validation)
    derivative = {**image_identity(out / key), 'schemaVersion': 1, 'recordedAt': now(), 'route': 'derived-no-generation',
        'derivedFrom': [{'path': str(archive / 'raw.png'), 'sha256': metadata['sha256'], 'generationRecord': str(archive / 'raw.png.generation.json')}],
        'operation': 'recorded alpha cleanup, magenta key, whole-cell fixed .88 scale, edge despill, integer anchor [512,942]',
        'sourceRecord': {'path': str(out / 'processing/frame-sources.json'), 'slot': key, 'sha256': sha(out / 'processing/frame-sources.json')},
        'generationCalls': 0, 'paidApiCalls': 0, 'actualModel': metadata['actualModel'], 'actualQuality': metadata['actualQuality'],
        'visualApproval': False}
    save_new((out / key).with_suffix('.png.generation.json'), derivative)
    image = Image.open(out / key).convert('RGBA')
    for name, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
        canvas = Image.new('RGB', (1024, 1088), color)
        canvas.paste(image, (0, 48), image)
        ImageDraw.Draw(canvas).text((16, 16), '17 ' + key + ' / .88 / visual pending', fill='white' if name == 'dark' else 'black')
        canvas.save(out / ('review/' + name + '.png'))
    result = {'character_id': CHAR, 'slot': key, 'path': str(out / key), 'sha256': sha(out / key),
        'selected_revision': archive.name, 'visual_status': 'pending', 'source_record_file': str(out / 'processing/frame-sources.json'),
        'raw_generation_record': str(archive / 'raw.png.generation.json'), 'validation': validation,
        'canonical_modified': False, 'formal_approval': False}
    save_new(out / 'import-result.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
