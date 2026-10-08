"""Prepare guide-only north/east context when north has cores but no extended.

The audit binds three adjacent north-row cores to exact integer crops. Only the
outer 115 rows are known native context. No replacement extended image or native
south halo is invented. Native preparation must honor the explicit coverage mask.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image

from workflow import OUTPUT_ROOT, safe_output, sha256, read_json, write_json, save_image
from prepare_frontier import source_image


def rgb_hash(image):
    return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()


def tile_coordinates(tile):
    match = re.fullmatch(r'r(\d{2})_c(\d{2})', tile)
    if not match:
        raise ValueError('Invalid tile')
    row, col = map(int, match.groups())
    if not (2 <= row <= 16 and 2 <= col < 16):
        raise ValueError('Three northern cores and an east neighbor must exist in grid')
    return row, col


def audited_north_band(tile, audit_file):
    """Read/verify the three real source crops; return images and provenance only."""
    row, col = tile_coordinates(tile)
    audit_path = Path(audit_file).resolve(strict=True)
    audit = read_json(audit_path)
    if audit.get('tile') != tile:
        raise ValueError('North source audit names a different target tile')
    construction = audit['legalFirst115RowsConstruction']
    if not construction.get('available') or construction.get('fullBandPixels') != [4326, 115]:
        raise ValueError('Audit does not bind a complete native 115-row north band')
    parts = construction['parts']
    boxes = [([3981,3981,4096,4096], [0,0,115,115]),
             ([0,3981,4096,4096], [115,0,4211,115]),
             ([0,3981,115,4096], [4211,0,4326,115])]
    if len(parts) != len(boxes):
        raise ValueError('Expected three adjacent north core source parts')
    band = Image.new('RGB', (4326,115))
    mappings = []
    central = central_meta = None
    for index, (part, (source_box, destination_box)) in enumerate(zip(parts, boxes)):
        if part['sourceBoxXYXY'] != source_box or part['destinationBoxInNorthBandXYXY'] != destination_box:
            raise ValueError('Audited north mapping differs from grid geometry')
        core, meta = source_image(part['source']['file'], (4096,4096))
        if meta['sha256'] != part['source']['sha256']:
            raise ValueError('Audited north core source changed')
        expected = f'r{row-1:02d}_c{col+index-1:02d}'
        path = Path(meta['file'])
        if expected not in path.parts and path.stem != expected:
            raise ValueError('Audited north source tile identity mismatch')
        crop = core.crop(source_box)
        digest = rgb_hash(crop)
        if digest != part['rawRgbPixelSha256']:
            raise ValueError('Audited north crop pixel hash changed')
        band.paste(crop, tuple(destination_box[:2]))
        if band.crop(destination_box).tobytes() != crop.tobytes():
            raise ValueError('North crop paste lost pixel identity')
        meta.update(tile=expected, role='Real native north-row core; no extended image assumed')
        mappings.append({'source':meta, 'sourceBoxXYXY':source_box,
                         'destinationBoxInNorthBandXYXY':destination_box,
                         'rawRgbPixelSha256':digest, 'nativeSourceResampling':'none',
                         'pixelIdentityVerified':True})
        if index == 1:
            central, central_meta = core, meta
            if audit['northCore']['sha256'] != meta['sha256']:
                raise ValueError('Audit central north core identity mismatch')
    mask = Image.new('L', (4326,230), 0)
    mask.paste(255, (0,0,4326,115))
    return band, mask, central, central_meta, mappings, {
        'file':str(audit_path), 'sha256':sha256(audit_path)}


def run(args):
    row, col = tile_coordinates(args.tile)
    tile = safe_output(OUTPUT_ROOT / args.tile)
    if tile.parent != OUTPUT_ROOT or tile.name != args.tile:
        raise ValueError('Tile output identity mismatch')
    def destination(relative):
        path = safe_output(tile / relative)
        if not path.is_relative_to(tile):
            raise ValueError('Output escapes requested tile')
        return path
    names = ('context.json','target-layout-only.png','east-context-preview.png',
             'north-context-preview.png','north-core-band4326x115.png','north-known-mask4326x230.png')
    protected = [destination('regional/' + name) for name in names]
    protected.append(destination('regional/regional.png'))
    if any(path.exists() for path in protected):
        raise FileExistsError('Refusing to replace existing regional work')
    handoff_path, queue_path = OUTPUT_ROOT/'handoff.json', OUTPUT_ROOT/'production-queue.json'
    handoff, queue = read_json(handoff_path), read_json(queue_path)
    entries = [entry for entry in queue['tiles'] if entry['id'] == args.tile]
    rect = [(col-1)*4096,(row-1)*4096,4096,4096]
    if len(entries) != 1 or entries[0]['pixelRectXYWH'] != rect:
        raise ValueError('Queue geometry mismatch')
    if queue['planSha256'] != handoff['plan']['sha256']:
        raise ValueError('Plan mismatch')
    if handoff['targetCityPixels'] != [65536,65536] or handoff['targetTilePixels'] != [4096,4096]:
        raise ValueError('City/tile geometry mismatch')
    layout, layout_meta = source_image(handoff['layout']['file'])
    if layout_meta['sha256'] != handoff['layout']['sha256'] or layout_meta['pixels'] != handoff['layout']['pixels']:
        raise ValueError('Layout changed')
    north, mask, north_core, north_meta, mappings, audit_meta = audited_north_band(args.tile, args.north_source_audit)
    east_ext, east_ext_meta = source_image(args.east_extended, (4326,4326))
    east_core, east_core_meta = source_image(args.east_core, (4096,4096))
    east_tile = f'r{row:02d}_c{col+1:02d}'
    if any(east_tile not in Path(meta['file']).parts for meta in (east_ext_meta,east_core_meta)):
        raise ValueError('East source tile identity mismatch')
    if east_ext.crop((115,115,4211,4211)).tobytes() != east_core.tobytes():
        raise ValueError('East core mismatch')
    east_ext_meta.update(tile=east_tile,role='Real native east extended context')
    east_core_meta.update(tile=east_tile,role='Matching east core preview source')
    style_path = Path('D:/work/image/designs/gameplay-ui/04-guild.png')
    _, style_meta = source_image(style_path)
    x,y,_,_ = rect
    extent = [x-115,y-115,x+4211,y+4211]
    scaled = [extent[0]*layout.width/65536,extent[1]*layout.height/65536,
              extent[2]*layout.width/65536,extent[3]*layout.height/65536]
    guide = layout.transform((4326,4326),Image.Transform.EXTENT,scaled,Image.Resampling.BICUBIC)
    east_band = east_ext.crop((0,0,230,4326))
    difference = np.array(east_band.crop((0,0,230,115)),dtype=np.int16) - np.array(north.crop((4096,0,4326,115)),dtype=np.int16)
    guide.paste(east_band,(4096,0))
    guide.paste(north,(0,0))
    if guide.crop((0,0,4326,115)).tobytes() != north.tobytes():
        raise ValueError('Strict north native pixels changed')
    if guide.crop((4096,115,4326,4326)).tobytes() != east_band.crop((0,115,230,4326)).tobytes():
        raise ValueError('East native pixels changed below north priority corner')
    # All validation is complete before creating directories or files.
    for name in ('regional','native','guides','jobs','prompts','qa'):
        destination(name).mkdir(parents=True,exist_ok=True)
    if any(path.exists() for path in protected):
        raise FileExistsError('Output appeared during preparation')
    outputs = {}
    for name, image, filename in (
        ('targetLayout',guide.resize((1254,1254),Image.Resampling.LANCZOS),'target-layout-only.png'),
        ('eastPreview',east_core.resize((1254,1254),Image.Resampling.LANCZOS),'east-context-preview.png'),
        ('northPreview',north_core.resize((1254,1254),Image.Resampling.LANCZOS),'north-context-preview.png')):
        outputs[name] = save_image(destination('regional/'+filename),image)
        outputs[name].update(guideOnly=True,finalArt=False)
    band_meta = save_image(destination('regional/north-core-band4326x115.png'),north)
    band_meta.update(pixels=[4326,115],nativeSourceResampling='none',rawRgbPixelSha256=rgb_hash(north),
                     sourceMappings=mappings,role='Actual native outer115 context only; not an extended image',
                     finalArt=False)
    mask_meta = save_image(destination('regional/north-known-mask4326x230.png'),mask)
    mask_meta.update(pixels=[4326,230],knownBoxXYXY=[0,0,4326,115],unknownBoxXYXY=[0,115,4326,230],
                     knownValue=255,unknownValue=0,meaning='Native coverage only; no color/artwork pixels',
                     rawMaskPixelSha256=hashlib.sha256(mask.tobytes()).hexdigest(),finalArt=False)
    refs = [{'path':outputs['targetLayout']['file'],'role':'Guide-only framing; exact outer115 north core context and east overlap before preview reduction; north wins corner'},
            {'path':outputs['eastPreview']['file'],'role':'Matching east core preview; continuity only'},
            {'path':outputs['northPreview']['file'],'role':'Audited central north core preview; continuity only, missing south halo not inferred'},
            {'path':style_meta['file'],'role':'Approved primary painting/material style; no copied UI or objects'}]
    context = {
        'schemaVersion':2,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':args.tile,
        'pixelRectXYWH':rect,'worldRect':entries[0].get('worldRect'),'wholeCityPixels':[65536,65536],
        'guideOnly':True,'finalArt':False,'formalAccepted':False,'layout':layout_meta,
        'extentInWholeCityPixels':extent,'extentInLayoutPixels':scaled,
        'nativeTraversal':'right_to_left_top_to_bottom','guideCanvasPixels':[4326,4326],
        'exportedRegionalGuidePixels':[1254,1254],
        'northContextKind':'partial_core_band','northCore':north_meta,'northCoreBand':band_meta,
        'northKnownMask':mask_meta,'northSourceAudit':audit_meta,
        'northNativeCoverage':{'strictNativeRows':[0,115],'missingNativeHaloRows':[115,230],
            'nativeWeightInMissingRows':0,'native230BandComplete':False,'northExtendedAvailable':False,
            'unknownRowsMeaning':'Guide-only regional/layout context, plus independently sourced east context where covered; never north native evidence'},
        'eastExtended':east_ext_meta,'eastCore':east_core_meta,
        'cornerHandling':{'priority':'north_known115','overlapBoxXYXY':[4096,0,4326,115],
            'differingPixelCount':int(np.any(difference!=0,axis=2).sum()),
            'maximumAbsoluteChannelDifference':int(np.abs(difference).max()),
            'notBothSourcesExactWhenConflicting':True},
        'overlapMappings':{'east':{'source':[0,0,230,4326],'destination':[4096,0,4326,4326],
            'exactRegionExcludesNorthCorner':[4096,115,4326,4326],'pixelIdentityVerifiedBeforePreviewDownsample':True},
            'north':{'sourceMappings':mappings,'destination':[0,0,4326,115],
                'pixelIdentityVerifiedBeforePreviewDownsample':True,'sourceResampling':'none'}},
        'operation':'Guide-only BICUBIC layout extent; integer east paste then audited native north115 paste; LANCZOS previews. No replacement north extended image, no final art.',
        'guideRestriction':'Native generation must reattach the full-resolution northCoreBand with northKnownMask; rows115..229 have zero north alpha. All final artwork must come from actual builtin native generation.',
        'queue':{'file':str(queue_path),'sha256':sha256(queue_path)},
        'handoff':{'file':str(handoff_path),'sha256':sha256(handoff_path)},
        'outputs':outputs,'references':refs}
    write_json(destination('regional/context.json'),context)
    print(json.dumps({'context':str(destination('regional/context.json')),'references':refs}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tile')
    parser.add_argument('--north-source-audit',required=True)
    parser.add_argument('--east-extended',required=True)
    parser.add_argument('--east-core',required=True)
    run(parser.parse_args())
