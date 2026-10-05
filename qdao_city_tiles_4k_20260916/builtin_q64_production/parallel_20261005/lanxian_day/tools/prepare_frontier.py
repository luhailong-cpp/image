"""Prepare guide-only regional framing from the production queue and a west tile.

Usage: prepare_frontier.py r08_c10 --west-extended EXTENDED.png --west-core CORE.png
No generation, acceptance, progress changes, source writes, or image deletion.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from PIL import Image

from workflow import OUTPUT_ROOT, read_json, safe_output, save_image, sha256, write_json


CORE, HALO, EXTENDED, PREVIEW = 4096, 115, 4326, 1254
SUBDIRECTORIES = ('guides', 'regional', 'native', 'prompts', 'jobs', 'qa')
REPO = Path('D:/work/image')


def source_image(value, size=None):
    path = Path(value).resolve(strict=True)
    with Image.open(path) as image:
        if image.format != 'PNG' or image.mode not in ('RGB', 'RGBA'):
            raise ValueError(f'Expected RGB/RGBA PNG: {path}')
        if size is not None and image.size != size:
            raise ValueError(f'Expected {size}, received {image.size}: {path}')
        if image.mode == 'RGBA' and image.getextrema()[3] != (255, 255):
            raise ValueError(f'West/layout source must be opaque: {path}')
        image.load()
        decoded = image.convert('RGB')
        metadata = {'file': str(path), 'sha256': sha256(path),
                    'pixels': list(image.size), 'mode': image.mode, 'format': 'PNG'}
    return decoded, metadata


def tile_coordinate(tile_name):
    match = re.fullmatch(r'r(\d{2})_c(\d{2})', tile_name)
    if match is None:
        raise ValueError('Tile must use one-based rNN_cNN notation')
    row, col = map(int, match.groups())
    if not (1 <= row <= 16 and 2 <= col <= 16):
        raise ValueError('Tile must lie in 16x16 grid and have a west neighbor')
    return row, col


def prepare(tile_name, west_extended_file, west_core_file):
    row, col = tile_coordinate(tile_name)
    tile = safe_output(OUTPUT_ROOT / tile_name)
    regional = safe_output(tile / 'regional')
    target_path = safe_output(regional / 'target-layout-only.png')
    west_preview_path = safe_output(regional / 'west-context-preview.png')
    context_path = safe_output(regional / 'context.json')
    outputs = [target_path, west_preview_path, context_path]
    if any(path.exists() for path in outputs):
        raise FileExistsError('Refusing to overwrite existing regional context or guides')

    queue_path, handoff_path = OUTPUT_ROOT / 'production-queue.json', OUTPUT_ROOT / 'handoff.json'
    queue, handoff = read_json(queue_path), read_json(handoff_path)
    entries = [entry for entry in queue['tiles'] if entry['id'] == tile_name]
    if len(entries) != 1:
        raise ValueError('Requested tile must occur exactly once in production-queue.json')
    rect = entries[0]['pixelRectXYWH']
    expected_rect = [(col - 1) * CORE, (row - 1) * CORE, CORE, CORE]
    if rect != expected_rect:
        raise ValueError(f'Queue XYWH disagrees with tile coordinates: {rect}')
    city_pixels = handoff['targetCityPixels']
    if city_pixels != [65536, 65536] or handoff['targetTilePixels'] != [CORE, CORE]:
        raise ValueError('Unexpected city/tile dimensions in handoff')
    if queue.get('planSha256') != handoff['plan']['sha256']:
        raise ValueError('Queue and handoff refer to different production plans')

    layout, layout_meta = source_image(handoff['layout']['file'])
    if layout_meta['sha256'] != handoff['layout']['sha256']:
        raise ValueError('Layout source SHA256 no longer matches handoff')
    if layout_meta['pixels'] != handoff['layout']['pixels']:
        raise ValueError('Layout dimensions no longer match handoff')
    west_extended, extended_meta = source_image(west_extended_file, (EXTENDED, EXTENDED))
    west_core, core_meta = source_image(west_core_file, (CORE, CORE))
    _, style_meta = source_image(REPO / 'designs/gameplay-ui/04-guild.png')
    if west_extended.crop((HALO, HALO, HALO + CORE, HALO + CORE)).tobytes() != west_core.tobytes():
        raise ValueError('West core pixels must match the center 4096 square of west extended')
    # Read and verify everything before creating any output directories or files.
    source_paths = {Path(entry['file']).resolve() for entry in (layout_meta, extended_meta, core_meta)}
    if any(path in source_paths for path in outputs):
        raise ValueError('An output would overwrite an input source')

    x, y, width, height = rect
    extent_city = [x - HALO, y - HALO, x + width + HALO, y + height + HALO]
    sx, sy = layout.width / city_pixels[0], layout.height / city_pixels[1]
    extent_layout = [extent_city[0] * sx, extent_city[1] * sy,
                     extent_city[2] * sx, extent_city[3] * sy]
    guide = layout.transform((EXTENDED, EXTENDED), Image.Transform.EXTENT,
                             extent_layout, Image.Resampling.BICUBIC)
    overlap = west_extended.crop((4096, 0, 4326, 4326))
    guide.paste(overlap, (0, 0))
    if guide.crop((0, 0, 230, 4326)).tobytes() != overlap.tobytes():
        raise ValueError('West native overlap placement failed')

    for subdirectory in SUBDIRECTORIES:
        safe_output(tile / subdirectory).mkdir(parents=True, exist_ok=True)
    target_meta = save_image(target_path, guide.resize((PREVIEW, PREVIEW), Image.Resampling.LANCZOS))
    preview_meta = save_image(west_preview_path, west_core.resize((PREVIEW, PREVIEW), Image.Resampling.LANCZOS))
    target_meta.update(guideOnly=True, finalArt=False,
                       operation='BICUBIC layout extent to 4326; exact west 230x4326 paste; LANCZOS downsample to 1254')
    preview_meta.update(guideOnly=True, finalArt=False,
                        operation='LANCZOS downsample of selected west core 4096 to 1254 for visual context only')
    west_tile = f'r{row:02d}_c{col - 1:02d}'
    extended_meta.update(tile=west_tile, role='Real native west extended context, including both sides of shared boundary')
    core_meta.update(tile=west_tile, role='Matching west effective core for preview context')
    layout_meta['role'] = 'Whole-city layout/style only; never final high-resolution pixels'
    references = [
        {'path': str(target_path), 'sha256': target_meta['sha256'],
         'role': 'Target extended framing and provisional geometry only; left 230px at 4326 scale originated in selected west native context'},
        {'path': str(west_preview_path), 'sha256': preview_meta['sha256'],
         'role': 'Selected west core preview for shape continuity, materials and daylight; no independent geometric alignment claim'},
        {'path': style_meta['file'], 'sha256': style_meta['sha256'],
         'pixels': style_meta['pixels'],
         'role': 'User-confirmed primary painting/material style; no copied UI, objects or cast shadows'},
    ]
    context = {
        'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
        'tile': tile_name, 'guideOnly': True, 'finalArt': False, 'formalAccepted': False,
        'pixelRectXYWH': rect, 'worldRect': entries[0].get('worldRect'),
        'wholeCityPixels': city_pixels, 'guideCanvasPixels': [EXTENDED, EXTENDED],
        'exportedRegionalGuidePixels': [PREVIEW, PREVIEW],
        'queue': {'file': str(queue_path), 'sha256': sha256(queue_path)},
        'handoff': {'file': str(handoff_path), 'sha256': sha256(handoff_path)},
        'handoffReadyAtRead': handoff.get('readyForProduction'),
        'layout': layout_meta, 'westExtended': extended_meta, 'westCore': core_meta,
        'westCoreMatchesExtendedCenter': True,
        'derivedFrom': [layout_meta, extended_meta, core_meta],
        'extentInWholeCityPixels': extent_city, 'extentInLayoutPixels': extent_layout,
        'westOverlap': {'sourceBoxLTRB': [4096, 0, 4326, 4326],
                        'destinationBoxLTRB': [0, 0, 230, 4326],
                        'pixelIdenticalBeforePreviewDownsample': True,
                        'resamplingBeforePaste': 'none'},
        'operation': 'Provisional layout extent resampled to 4326 for guide only; native west 230x4326 context pasted at left; guide and west core downsampled to 1254. No output is production art.',
        'resampling': {'layoutToGuide': 'BICUBIC', 'previews': 'LANCZOS'},
        'guideRestriction': 'Never use upscaled layout or downsampled guide pixels in final art; native detail generation must reattach the full-resolution westExtended bands.',
        'outputs': {'targetLayout': target_meta, 'westPreview': preview_meta},
        'references': references,
    }
    write_json(context_path, context)
    return {'tile': tile_name, 'context': str(context_path), 'references': references,
            'westExtendedSha256': extended_meta['sha256'], 'westCoreSha256': core_meta['sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tile')
    parser.add_argument('--west-extended', required=True, type=Path)
    parser.add_argument('--west-core', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.tile, args.west_extended, args.west_core), ensure_ascii=False, indent=2))
