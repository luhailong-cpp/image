"""Import one 05 frame in any direction into isolated staging, without selection or approval."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import importlib.util
import json
import re
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
PACKAGE = RECOVERY.parent
CHARACTER = '05_celestial_musician_girl'
DIRECTIONS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


metadata = module('musician_archive_metadata', HERE / 'archive_metadata.py')
require, read, sha = metadata.require, metadata.read, metadata.sha


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--direction', choices=DIRECTIONS, required=True)
    parser.add_argument('--frame', type=int, choices=range(1, 17), required=True)
    parser.add_argument('--staging-root', type=Path, required=True)
    args = parser.parse_args()
    require(re.fullmatch(r'[A-Za-z0-9_-]+', args.batch_id), 'Invalid batch ID')
    archive, stage = args.archive.resolve(), args.staging_root.resolve()
    require(archive.is_relative_to(RECOVERY / '05-generation'), 'Archive must remain in recovery/05-generation')
    require(stage.is_relative_to(archive) or stage.is_relative_to(HERE), 'Staging must be inside this archive or 05-tools')
    out = stage / 'candidate' / CHARACTER
    require(not (out / 'manifest.json').exists(), 'Use fresh per-attempt staging; existing manifests are immutable')
    receipt = read(archive / 'generation-receipt.json')
    require(1 <= len(receipt['actual_request'].get('referenced_image_paths', [])) <= 5, 'Use one to five actual local references')
    # Validate complete actual bindings before processing; this also creates only the raw sidecar if absent.
    metadata_result = metadata.archive_metadata(archive)
    record = read(archive / 'raw.png.generation.json')
    require(min(record['width'], record['height']) >= 1024, 'Native complete single frame must be at least 1024 in both dimensions')
    evidence = {'rawMetadata': metadata_result, 'raw_sha256': sha(archive / 'raw.png'),
                'native_size': [record['width'], record['height']], 'references': record['references'],
                'prompt_sha256': sha(archive / 'prompt.txt'), 'receipt_sha256': sha(archive / 'generation-receipt.json'),
                'provenance_sha256': sha(archive / 'provenance.json'), 'paid_api_calls': 0,
                'model_actual': 'host-managed-unverified', 'visual_review': 'pending'}
    pipe = module('musician_all_direction_staging_pipeline', PACKAGE / 'tools/pipeline.py')
    pipe.output = lambda character: out if character == CHARACTER else (_ for _ in ()).throw(ValueError('05 only'))
    pipe.preview = lambda: None
    pipe.import_sheet(SimpleNamespace(command='import-walk', character=CHARACTER, direction=args.direction,
        source=archive / 'raw.png', prompt=archive / 'prompt.txt', receipt=archive / 'generation-receipt.json',
        batch_id=args.batch_id, common_scale=.84, chroma_profile='purple-preserve', rows=1, cols=1,
        source_cell_indices=None, idle_order=None, output_frames=str(args.frame), start_frame=1))
    verifier = module('musician_all_direction_staging_verifier', PACKAGE / 'tools/verify.py')
    verifier.ROOT = stage
    verifier.mod = lambda name: module('musician_all_verify_' + name, PACKAGE / 'tools/vendor' / f'{name}.py')
    validation = verifier.verify(CHARACTER, args.direction, False, args.frame)
    slot = f'walk/{args.direction}/{args.frame:02d}.png'
    output = out / slot
    mapping = read(out / 'processing/frame-sources.json')[slot]
    require(mapping['chroma_thresholds'] == [50, 75] and mapping['common_scale'] == .84, 'Character profile changed')
    write(out / f'review/validation-{args.direction}-{args.frame:02d}.json', validation)
    write(out / 'recovery-bindings' / args.batch_id / 'source-binding.json', evidence)
    result = {'character': CHARACTER, 'slot': slot, 'output': str(output), 'output_sha256': sha(output),
              'common_scale': .84, 'chroma_thresholds': [50, 75], 'single_frame_reconstruction': validation,
              'canonical_modified': False, 'visual_review': 'pending', 'selected': False, 'can_publish': False}
    write(out / 'recovery-bindings' / args.batch_id / 'import-result.json', result)
    with Image.open(output) as source:
        image = source.convert('RGBA')
    for name, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
        canvas = Image.new('RGB', (1024, 1088), color)
        canvas.paste(image, (0, 48), image)
        ImageDraw.Draw(canvas).text((16, 16), f'05 {args.direction}{args.frame:02d} / purple-preserve50/75 / fixed.84 / pending',
                                   fill='white' if name == 'dark' else 'black')
        destination = out / f'review/backgrounds/{args.direction}{args.frame:02d}-{name}.png'
        destination.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(destination)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
