"""Prepare guide-only framing south of an existing native tile.

Usage: prepare_south_frontier.py r09_c10 --north-extended EXTENDED.png --north-core CORE.png
No AI generation, acceptance, progress mutation, source writes, or deletion.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from PIL import Image

from prepare_frontier import CORE, HALO, EXTENDED, PREVIEW, SUBDIRECTORIES, REPO, source_image
from workflow import OUTPUT_ROOT, read_json, safe_output, save_image, sha256, write_json


def prepare(tile_name, north_extended_file, north_core_file):
    match = re.fullmatch(r'r(\d{2})_c(\d{2})', tile_name)
    if match is None:
        raise ValueError('Tile must use one-based rNN_cNN notation')
    row, col = map(int, match.groups())
    if not (2 <= row <= 16 and 1 <= col <= 16):
        raise ValueError('Tile must lie in the 16x16 grid and have a north neighbor')
    tile = safe_output(OUTPUT_ROOT / tile_name)
    if tile.parent != OUTPUT_ROOT or tile.name != tile_name:
        raise ValueError('Tile output resolves outside the requested tile directory')

    def destination(relative):
        path = safe_output(tile / relative)
        if not path.is_relative_to(tile):
            raise ValueError('Output escapes the requested tile directory')
        return path

    target_path = destination('regional/target-layout-only.png')
    preview_path = destination('regional/north-context-preview.png')
    context_path = destination('regional/context.json')
    outputs = [target_path, preview_path, context_path]
    if any(path.exists() for path in outputs):
        raise FileExistsError('Refusing to overwrite existing regional context or guides')
    queue_path, handoff_path = OUTPUT_ROOT / 'production-queue.json', OUTPUT_ROOT / 'handoff.json'
    queue, handoff = read_json(queue_path), read_json(handoff_path)
    entries = [entry for entry in queue['tiles'] if entry['id'] == tile_name]
    if len(entries) != 1:
        raise ValueError('Requested tile must occur exactly once in the production queue')
    rect = entries[0]['pixelRectXYWH']
    if rect != [(col - 1) * CORE, (row - 1) * CORE, CORE, CORE]:
        raise ValueError('Queue XYWH disagrees with the requested tile coordinates')
    city_pixels = handoff['targetCityPixels']
    if city_pixels != [65536, 65536] or handoff['targetTilePixels'] != [CORE, CORE]:
        raise ValueError('Unexpected city/tile dimensions in handoff')
    if queue.get('planSha256') != handoff['plan']['sha256']:
        raise ValueError('Queue and handoff refer to different production plans')

    layout, layout_meta = source_image(handoff['layout']['file'])
    if layout_meta['sha256'] != handoff['layout']['sha256'] or layout_meta['pixels'] != handoff['layout']['pixels']:
        raise ValueError('Layout source hash or dimensions no longer match handoff')
    north_extended, extended_meta = source_image(north_extended_file, (EXTENDED, EXTENDED))
    north_core, core_meta = source_image(north_core_file, (CORE, CORE))
    _, style_meta = source_image(REPO / 'designs/gameplay-ui/04-guild.png')
    if north_extended.crop((HALO, HALO, HALO + CORE, HALO + CORE)).tobytes() != north_core.tobytes():
        raise ValueError('North core must equal the exact center 4096 square of north extended')
    source_paths = {Path(m['file']).resolve() for m in (layout_meta, extended_meta, core_meta, style_meta)}
    if any(path in source_paths for path in outputs):
        raise ValueError('An output would overwrite an input source')

    x, y, width, height = rect
    extent_city = [x - HALO, y - HALO, x + width + HALO, y + height + HALO]
    sx, sy = layout.width / city_pixels[0], layout.height / city_pixels[1]
    extent_layout = [extent_city[0] * sx, extent_city[1] * sy,
                     extent_city[2] * sx, extent_city[3] * sy]
    guide = layout.transform((EXTENDED, EXTENDED), Image.Transform.EXTENT,
                             extent_layout, Image.Resampling.BICUBIC)
    source_box, target_box = [0, CORE, EXTENDED, EXTENDED], [0, 0, EXTENDED, 2 * HALO]
    overlap = north_extended.crop(source_box)
    guide.paste(overlap, (0, 0))
    if guide.crop(target_box).tobytes() != overlap.tobytes():
        raise ValueError('North native overlap placement failed')
    for subdirectory in SUBDIRECTORIES:
        destination(subdirectory).mkdir(parents=True, exist_ok=True)
    if any(path.exists() for path in outputs):
        raise FileExistsError('An output appeared during input preparation; refusing overwrite')
    target_meta = save_image(target_path, guide.resize((PREVIEW, PREVIEW), Image.Resampling.LANCZOS))
    preview_meta = save_image(preview_path, north_core.resize((PREVIEW, PREVIEW), Image.Resampling.LANCZOS))
    target_meta.update(guideOnly=True, finalArt=False,
                       operation='BICUBIC layout extent to 4326; exact north 4326x230 paste; LANCZOS to 1254')
    preview_meta.update(guideOnly=True, finalArt=False,
                        operation='LANCZOS downsample of north core4096 to1254 for context only')
    north_tile = f'r{row - 1:02d}_c{col:02d}'
    extended_meta.update(tile=north_tile, role='Native north extended context including both sides of the shared edge')
    core_meta.update(tile=north_tile, role='Matching north effective core for context preview')
    layout_meta['role'] = 'Whole-city layout/style only; never final high-resolution pixels'
    references = [
        {'path': str(target_path), 'sha256': target_meta['sha256'],
         'role': 'Guide-only target framing; top230 at4326 scale comes from exact native north context'},
        {'path': str(preview_path), 'sha256': preview_meta['sha256'],
         'role': 'North core preview for material and shape context; no independent geometric alignment claim'},
        {'path': style_meta['file'], 'sha256': style_meta['sha256'], 'pixels': style_meta['pixels'],
         'role': 'User-confirmed primary painting/material style; no copied UI, objects, or shadows'},
    ]
    world = entries[0].get('worldRect')
    expanded_world = None
    if world and all(k in world for k in ('x', 'z', 'width', 'height')):
        px, pz = world['width'] * HALO / CORE, world['height'] * HALO / CORE
        expanded_world = {'x': world['x'] - px, 'z': world['z'] - pz,
                          'width': world['width'] + 2 * px, 'height': world['height'] + 2 * pz}
    context = {
        'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
        'tile': tile_name, 'guideOnly': True, 'finalArt': False, 'formalAccepted': False,
        'pixelRectXYWH': rect, 'worldRect': world, 'expandedWorldRect': expanded_world,
        'worldRectConvention': 'Queue worldRect expanded symmetrically by115/4096 per side; no axis orientation is inferred',
        'wholeCityPixels': city_pixels, 'guideCanvasPixels': [EXTENDED, EXTENDED],
        'exportedRegionalGuidePixels': [PREVIEW, PREVIEW],
        'queue': {'file': str(queue_path), 'sha256': sha256(queue_path)},
        'handoff': {'file': str(handoff_path), 'sha256': sha256(handoff_path)},
        'handoffReadyAtRead': handoff.get('readyForProduction'),
        'layout': layout_meta, 'northExtended': extended_meta, 'northCore': core_meta,
        'northCoreMatchesExtendedCenter': True,
        'derivedFrom': [layout_meta, extended_meta, core_meta],
        'extentInWholeCityPixels': extent_city, 'extentInLayoutPixels': extent_layout,
        'targetCoreBoxInExtended': [HALO, HALO, HALO + CORE, HALO + CORE],
        'northOverlap': {'sourceBoxLTRB': source_box, 'destinationBoxLTRB': target_box,
                         'pixelIdenticalBeforePreviewDownsample': True,
                         'resamplingBeforePaste': 'none',
                         'sourceExtendedOriginWholeCityXY': [x - HALO, y - CORE - HALO],
                         'targetExtendedOriginWholeCityXY': [x - HALO, y - HALO],
                         'sharedExtentWholeCityLTRB': [x - HALO, y - HALO, x + CORE + HALO, y + HALO]},
        'operation': 'Layout extent resampled to4326 solely for a guide; native north bottom230 rows pasted at top without resize; guide and north preview downsampled to1254. No output is production art.',
        'resampling': {'layoutToGuide': 'BICUBIC', 'previews': 'LANCZOS', 'nativeOverlapBeforePreview': 'none'},
        'guideRestriction': 'Native detail preparation must reattach full-resolution northExtended bands; regional preview pixels must never be treated as final native artwork.',
        'outputs': {'targetLayout': target_meta, 'northPreview': preview_meta},
        'references': references,
    }
    write_json(context_path, context)
    return {'tile': tile_name, 'context': str(context_path), 'references': references,
            'northExtendedSha256': extended_meta['sha256'], 'northCoreSha256': core_meta['sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tile')
    parser.add_argument('--north-extended', required=True, type=Path)
    parser.add_argument('--north-core', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.tile, args.north_extended, args.north_core), ensure_ascii=False, indent=2))

