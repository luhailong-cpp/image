"""Postprocess one generated v9 character. Prompts and art are agent-authored."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PACK = REPO / 'q_daoist_character_pack_4096'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--id', required=True, help='Existing portrait filename stem')
    parser.add_argument('--reference-note', required=True)
    args = parser.parse_args()
    assert args.id.replace('_', '').isalnum() and 1 <= int(args.id[:2]) <= 22
    prompt = PACK / 'prompts' / f'{args.id}.prompt.txt'
    assert prompt.is_file()
    output = PACK / f'{args.id}.png'
    baseline = json.loads((HERE / 'baseline.json').read_text(encoding='utf8'))
    previous = next(row for row in baseline['assets'] if row['path'] == output.relative_to(REPO).as_posix())
    work = HERE / '.work' / args.id
    processor = Path.home() / '.agents/skills/generate2dsprite/scripts/generate2dsprite.py'
    with Image.open(args.raw) as im:
        native_size = list(im.size)
    # Preserve all available source resolution before the required 4096 export.
    cell_size = max(native_size)
    argv = [sys.executable, '-B', str(processor), 'process', '--input', str(args.raw),
            '--target', 'asset', '--mode', 'single', '--rows', '1', '--cols', '1',
            '--cell-size', str(cell_size), '--fit-scale', '0.88', '--align', 'feet',
            '--shared-scale', '--component-mode', 'all', '--min-component-area', '16',
            '--strict-qc', '--threshold', '130', '--edge-threshold', '170',
            '--prompt-file', str(prompt), '--output-dir', str(work)]
    subprocess.run(argv, check=True)
    with Image.open(work / 'sheet-transparent.png') as im:
        final = im.convert('RGBA').resize((4096, 4096), Image.Resampling.LANCZOS)
    pixels = np.asarray(final).copy()
    strong = ((pixels[:, :, 0] > 200) & (pixels[:, :, 1] < 100) &
              (pixels[:, :, 2] > 200) & (pixels[:, :, 3] > 0))
    removed = int(strong.sum())
    assert removed < 4096 * 4096 * 0.02
    pixels[strong] = 0
    final = Image.fromarray(pixels)
    alpha = final.getchannel('A')
    bbox = alpha.getbbox()
    assert alpha.getextrema() == (0, 255)
    assert min(bbox[0], bbox[1], 4096 - bbox[2], 4096 - bbox[3]) > 20
    final.save(output, optimize=True)
    record = {'file': output.name, 'art_revision': 'v9-character-diversity',
              'generator': 'built-in image_gen', 'generation_file': args.raw.name,
              'raw_sha256': digest(args.raw), 'native_generation_size': native_size,
              'export_size': [4096, 4096], 'native_4096_generation': native_size == [4096, 4096],
              'export_method': 'skill alpha cleanup at full source resolution, feet alignment, LANCZOS compatibility export',
              'prompt': prompt.relative_to(PACK).as_posix(),
              'reference_delivery': args.reference_note, 'reference_baseline': baseline['baseline_commit'],
              'previous_sha256': previous['sha256'], 'design_brief': '../qdao_character_diversity_v9/DESIGN_BRIEF.md',
              'model_preference': 'gpt-image-2', 'quality_preference': 'high',
              'model_parameter_exposed': False, 'quality_parameter_exposed': False,
              'model_and_quality_verified': False,
              'parameter_note': 'Built-in tool has no model or quality arguments; these preferences were not force-set or independently verified.',
              'alpha_range': [0, 255], 'subject_bounds': list(bbox), 'sha256': digest(output),
              'processor_qc': json.loads((work / 'pipeline-meta.json').read_text(encoding='utf8')),
              'strong_chroma_cleanup': {'predicate': 'R>200 and G<100 and B>200 and A>0', 'removed_pixels': removed},
              'art_only_not_engine_integrated': True}
    (PACK / 'records' / f'{args.id}.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: record[key] for key in ('file', 'native_generation_size', 'export_size', 'subject_bounds', 'sha256')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
