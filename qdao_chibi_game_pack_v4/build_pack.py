"""Rebuild the v4 export pack from saved generated art, without generation API calls."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image, ImageOps

PACK = Path(__file__).resolve().parent
REPO = PACK.parent

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def inspect_png(path):
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        item = {'path': path.relative_to(PACK).as_posix(), 'size': list(image.size), 'mode': image.mode,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        if 'A' in image.getbands():
            alpha = image.getchannel('A')
            hist = alpha.histogram()
            item.update(alpha_range=list(alpha.getextrema()), transparent_pixels=hist[0],
                        opaque_pixels=hist[255], subject_bounds=list(alpha.getbbox() or []))
        return item

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--processor', type=Path,
        default=Path.home() / '.agents/skills/generate2dsprite/scripts/generate2dsprite.py')
    args = parser.parse_args()
    if not args.processor.is_file():
        parser.error('Skill processor missing. Install the documented Skill or pass --processor.')
    source = PACK / 'source/hero-matte.png'
    city_source = REPO / 'qdao_main_city_chibi_v1.png'
    for path in (source, city_source):
        if not path.is_file():
            parser.error(f'Missing saved source: {path}')
    work = PACK / '.work'
    work.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(args.processor.resolve()), 'process',
        '--input', 'source/hero-matte.png', '--target', 'asset', '--mode', 'single',
        '--rows', '1', '--cols', '1', '--cell-size', '1024', '--fit-scale', '0.88',
        '--align', 'feet', '--shared-scale', '--component-mode', 'largest', '--strict-qc',
        '--threshold', '130', '--edge-threshold', '170',
        '--prompt-file', 'source/hero-matte.prompt.txt', '--output-dir', '.work/hero'],
        cwd=PACK, check=True)
    hero_path = PACK / 'hero-transparent_1024.png'
    shutil.copy2(work / 'hero/sheet-transparent.png', hero_path)
    processing = json.loads((work / 'hero/pipeline-meta.json').read_text(encoding='utf-8'))
    processing['input'] = 'source/hero-matte.png'
    processing['prompt_file'] = 'source/hero-matte.prompt.txt'
    processing['processor_source'] = {
        'repo': 'https://github.com/0x0funky/agent-sprite-forge',
        'commit': '64fd0b57d3f2ae117ef0a95e4c2decc25b4c9dd2',
        'skill': 'generate2dsprite'}
    write_json(PACK / 'source/hero-processing.json', processing)
    hero_info = inspect_png(hero_path)
    assert hero_info['mode'] == 'RGBA' and hero_info['size'] == [1024, 1024]
    assert hero_info['alpha_range'] == [0, 255]
    assert hero_info['transparent_pixels'] > 100000 and hero_info['opaque_pixels'] > 100000
    left, top, right, bottom = hero_info['subject_bounds']
    assert 4 < left < right < 1020 and 4 < top < bottom < 1020, 'Character clipping detected'
    hero = Image.open(hero_path).convert('RGBA')
    residual = sum(1 for r, g, b, a in hero.get_flattened_data()
                   if a > 128 and r > 200 and b > 200 and g < 100)
    assert residual == 0, f'Opaque chroma pixels remain: {residual}'
    city_path = PACK / 'main-city_2560x1080.png'
    with Image.open(city_source) as source_image:
        source_size = source_image.size
        city = ImageOps.fit(source_image.convert('RGB'), (2560, 1080),
                            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        city.save(city_path)
    # Place by the visible feet, not the lower transparent canvas edge.
    visible_origin = [(left + right) / 2, bottom]
    display_size = 160
    scale = display_size / 1024
    feet = [1240, 680]
    xy = [round(feet[0] - visible_origin[0] * scale),
          round(feet[1] - visible_origin[1] * scale)]
    placements = {'purpose': 'visual placement example only', 'canvas': [2560, 1080],
        'background': 'main-city_2560x1080.png', 'coordinate_origin': 'top-left',
        'actors': [{'id': 'headband-daoist', 'image': 'hero-transparent_1024.png',
          'source_size': [1024, 1024], 'source_feet_anchor': visible_origin,
          'display_size': [display_size, display_size], 'feet_at': feet, 'top_left': xy}],
        'runtime_integration': False, 'collision': None}
    write_json(PACK / 'placements.json', placements)
    preview = city.convert('RGBA')
    preview.alpha_composite(hero.resize((display_size, display_size), Image.Resampling.LANCZOS), xy)
    preview.convert('RGB').save(PACK / 'preview-main-city_2560x1080.png')
    review = Image.new('RGB', (1024, 512))
    reduced = hero.resize((512, 512), Image.Resampling.LANCZOS)
    for x, color in [(0, '#F8F2E6'), (512, '#173C38')]:
        plate = Image.new('RGBA', (512, 512), color)
        plate.alpha_composite(reduced)
        review.paste(plate.convert('RGB'), (x, 0))
    review.save(work / 'hero-alpha-review.png')
    manifest = {'version': 4, 'created': '2026-09-06',
        'generation': {'tool': 'Codex built-in image_gen', 'saved_sources_only_on_rebuild': True,
                       'hero_reference': '../q_daoist_hero_chibi_headband_v3.png',
                       'hero_matte': 'source/hero-matte.png',
                       'hero_matte_prompt': 'source/hero-matte.prompt.txt'},
        'scene_export': {'source': '../qdao_main_city_chibi_v1.png', 'source_size': list(source_size),
                         'output_size': [2560, 1080], 'method': 'LANCZOS proportional center cover',
                         'resampled': True, 'new_native_resolution': False},
        'files': [inspect_png(PACK / p) for p in ['main-city_2560x1080.png',
                  'hero-transparent_1024.png', 'preview-main-city_2560x1080.png']],
        'validation': {'png_decode': 'pass', 'hero_alpha': 'pass', 'hero_margins': 'pass',
                       'opaque_magenta_pixels': residual, 'sprite_processor_strict_qc': 'pass'},
        'placements': 'placements.json', 'animation_frames': 0, 'engine_integration': False}
    write_json(PACK / 'manifest.json', manifest)
    print(json.dumps({'exports': len(manifest['files']), 'hero_alpha': hero_info['alpha_range'],
                      'subject_bounds': hero_info['subject_bounds'], 'opaque_magenta_pixels': residual}))

if __name__ == '__main__':
    main()
