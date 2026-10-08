"""Unscaled row-four core joins and explicit diagonal halo-source comparison."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
TILE = OUT.parents[1]
sys.path.insert(0, str(TILE / 'tools'))
from common import load_neighbors, load_native, load_png, read, write, info, sha, now, differences, unchanged


def save(image, name, sources, operation, **extra):
    target = OUT / name
    image.save(target)
    entry = {**info(target), 'size': list(image.size), 'newAIGeneration': False,
             'actualModel': None, 'actualQuality': None, 'derivedFrom': sources,
             'operation': operation, 'resized': False, 'filtered': False,
             'viewed': False, 'visualAccepted': False, **extra}
    write(str(target) + '.derivation.json', entry)
    return entry


def edge_metric(image, axis, at):
    arr = np.asarray(image).astype(np.int16)
    a, b = (arr[:, at-1], arr[:, at]) if axis == 'x' else (arr[at-1], arr[at])
    delta = np.abs(a-b)
    return {'axis': axis, 'boundary': at, 'meanAbsoluteRGB': delta.mean(axis=0).tolist(),
            'maxAbsoluteRGB': delta.max(axis=0).tolist(),
            'luminanceLikeMeanRGBAbs95thPercentile': float(np.percentile(delta.mean(axis=1), 95)),
            'establishesVisualAcceptance': False}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    neighbor, boundary = load_neighbors()
    diag_manifest = TILE.parent / 'r09_c10/selected-v2/delivery.manifest.json'
    dm = read(diag_manifest)
    assert dm['tile'] == 'r09_c10' and dm['qualifiedComplete4KCandidate'] is True
    dsrc = dm['outputs']['extended']
    assert sha(dsrc['file']) == dsrc['sha256']
    diagonal = load_png(dsrc['file'], (4326, 4326))
    ds = {**dsrc, 'deliveryManifest': info(diag_manifest)}
    natives, native_sources = [], []
    for col in range(1, 5):
        im, source = load_native(4, col)
        natives.append(im); native_sources.append(source)
    records = []
    for col in range(4):
        x = col * 1024
        upper_box = [115, 979, 1139, 1139]
        lower_box = [115+x, 115, 1139+x, 275]
        sheet = Image.new('RGB', (1024, 320))
        sheet.paste(natives[col].crop(upper_box), (0, 0))
        sheet.paste(neighbor['south'].crop(lower_box), (0, 160))
        record = save(sheet, f'south-segment{col+1:02d}-1to1.png',
                      [{'source': native_sources[col], 'cropLTRB': upper_box},
                       {'source': boundary['south'], 'cropLTRB': lower_box}],
                      'Exact source core crops adjacent at y160; upper new r08_c11, lower selected r09_c11',
                      coreSpanLTRB=[x, 3936, x+1024, 4096], seam=edge_metric(sheet, 'y', 160))
        records.append(record)
    west_box, east_box = [4051, 3187, 4211, 4211], [115, 115, 275, 1139]
    sheet = Image.new('RGB', (320, 1024))
    sheet.paste(neighbor['west'].crop(west_box), (0, 0))
    sheet.paste(natives[0].crop(east_box), (160, 0))
    records.append(save(sheet, 'west-bottom-segment-1to1.png',
                        [{'source': boundary['west'], 'cropLTRB': west_box},
                         {'source': native_sources[0], 'cropLTRB': east_box}],
                        'Exact adjacent core crops at x160; left selected r08_c10, right new r08_c11',
                        seam=edge_metric(sheet, 'x', 160)))
    for size in (160, 320):
        quadrants = [
            (neighbor['west'], [4211-size, 4211-size, 4211, 4211], (0, 0), boundary['west'], 'NW r08_c10'),
            (natives[0], [115, 1139-size, 115+size, 1139], (size, 0), native_sources[0], 'NE r08_c11'),
            (diagonal, [4211-size, 115, 4211, 115+size], (0, size), ds, 'SW r09_c10'),
            (neighbor['south'], [115, 115, 115+size, 115+size], (size, size), boundary['south'], 'SE r09_c11'),
        ]
        sheet = Image.new('RGB', (size*2, size*2))
        sources = []
        for image, box, xy, source, role in quadrants:
            sheet.paste(image.crop(box), xy)
            sources.append({'source': source, 'cropLTRB': box, 'destinationXY': list(xy), 'role': role})
        records.append(save(sheet, f'four-core-corner-{size*2}-1to1.png', sources,
                            'Four committed/native cores joined without resampling; quadrant labels in sidecar only',
                            seamCrossXY=[size, size]))
    halo_boxes = {
        'south': (neighbor['south'], [0, 115, 115, 230], boundary['south']),
        'diagonal': (diagonal, [4096, 115, 4211, 230], ds),
        'west': (neighbor['west'], [4096, 4211, 4211, 4326], boundary['west']),
    }
    fragments, halo_record = {}, {}
    strip = Image.new('RGB', (345, 115))
    for index, (name, (im, box, source)) in enumerate(halo_boxes.items()):
        crop = im.crop(box); fragments[name] = crop
        strip.paste(crop, (index*115, 0))
        halo_record[name] = save(crop, f'exterior-halo-from-{name}-115.png',
                                 [{'source': source, 'cropLTRB': box}], 'Exact 115 square source crop',
                                 rawRGBPixelSha256=hashlib.sha256(np.asarray(crop).tobytes()).hexdigest())
    contact = save(strip, 'exterior-halo-south-diagonal-west-1to1.png', list(halo_record.values()),
                   'Left south, middle diagonal, right west; 115 pixels each, exact pixel paste')
    comparisons = {f'{a}_vs_{b}': differences(fragments[a], fragments[b])
                   for a, b in [('south', 'diagonal'), ('west', 'diagonal'), ('west', 'south')]}
    unchanged(boundary); unchanged(native_sources); unchanged([ds])
    write(OUT / 'source-and-crop-audit.json', {
        'createdAtUtc': now(), 'sourcesUnchanged': True, 'actualSourcePixelsOnly': True,
        'resamplingOperations': 0, 'coreJoinImages': records, 'haloFragments': halo_record,
        'haloContact': contact, 'haloComparisons': comparisons,
        'recommendedExteriorHaloOwner': 'south' if comparisons['south_vs_diagonal']['byteEqual'] else None,
        'visualReviewPending': True, 'formalAccepted': False, 'fullTileAccepted': False,
    })
    print(json.dumps({'qaDirectory': str(OUT), 'haloComparisons': comparisons,
                      'sourcesUnchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
