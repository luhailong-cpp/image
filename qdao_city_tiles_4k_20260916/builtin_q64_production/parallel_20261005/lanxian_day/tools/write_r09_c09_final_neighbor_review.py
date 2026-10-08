import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
T = ROOT / 'r09_c09'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def rgb(p):
    return Image.open(p).convert('RGB')

def pix(im):
    return hashlib.sha256(im.tobytes()).hexdigest()

review_path = T / 'early-neighbor-qa/review.json'
early = read(review_path)
early_items = {Path(x['file']).name: x for x in early['items']}
core_path = T / 'candidate/core4096.png'
core_sha = sha(core_path)
core = rgb(core_path)
qa = read(T / 'qa/qa.manifest.json')
guide = read(T / 'qa/guide-bands/manifest.json')
checks = [x for x in qa['checks'] if Path(x['file']).name.startswith(('edge_', 'corner_'))]
checks += read(T / 'qa/external-north.manifest.json')['checks']
checks += read(T / 'qa/external-east.manifest.json')['checks']
checks += [x for x in guide['checks'] if x.get('axis') == 'x']
assert len(checks) == 44

notes = {
 'external_east_part4.png': 'At board x256, rounded foliage, bright leaf clusters and the lower branching trunk join continuously. No severed leaf contour, duplicated branch or seam-aligned exposure bar identified.',
 'corner_nw.png': 'Quiet ivory stone and its one shallow groove have continuous bevels and shading; no corner artifact identified.',
 'corner_sw.png': 'Only broad low-contrast oblique brush variation on ivory paving. No added groove, straight exposure boundary or corner artifact identified.',
 'corner_se.png': 'Dense rounded foliage and the branching brown trunk remain coherent; no cut contour or false straight boundary identified.',
 'edge_west_part1.png': 'Two existing paving grooves and the ivory material continue coherently to the west crop edge; no new stripe or broken bevel.',
 'edge_west_part2.png': 'Single gently slanted paving groove crosses the strip continuously. Broad oblique brush variation remains low contrast; no false vertical bar.',
 'edge_west_part3.png': 'Quiet ivory stone with broad diagonal brush forms. No additional scored line or axis-aligned band identified.',
 'edge_west_part4.png': 'One original shallow groove near the upper strip is continuous; remaining ivory material has broad oblique variation without a false straight edge.',
 'edge_south_part1.png': 'One slanted near-vertical paving groove reaches the lower edge with continuous bright bevels. No duplicated or interrupted groove.',
 'edge_south_part2.png': 'Soft elongated lamp shadows lie on uninterrupted ivory stone. No artificial horizontal edge or abrupt exposure boundary.',
 'edge_south_part3.png': 'Cropped red and gold lamp column, soft foliage shadow and dark leaf silhouette remain coherent to the bottom edge.',
 'edge_south_part4.png': 'Rounded shaded foliage, visible brown branches and small pale background gaps remain coherent; no scored grid in exposed gaps.',
 'edge_east_part4.png': 'Rounded foliage clusters and the lower brown trunk are coherent throughout the rightmost strip. The corresponding east-neighbor comparison also shows a continuous join.',
 'vertical_c1_r1.png': 'Both shallow paving grooves continue across guide boundary x909 without a step, dead end or straight color bar.',
 'vertical_c1_r2.png': 'The shallow paving groove and surrounding ivory shading continue across x909; no guide-transition stripe identified.',
 'vertical_c1_r3.png': 'Broad diagonal low-contrast brush variation on quiet stone; no vertical transition contour at x909.',
 'vertical_c1_r4.png': 'Upper slanted paving groove crosses x909 continuously. Remaining stone has broad oblique brush forms without a straight transition line.',
 'vertical_c2_r1.png': 'Brown tree trunk, leaf clusters and lower curved planter edge remain coherent across x1933; no cut or doubled contour.',
 'vertical_c2_r2.png': 'Curved planter edge near the top and slanted paving groove continue across x1933 without guide-band steps.',
 'vertical_c2_r3.png': 'Red curled lamp arm and lower stone groove have continuous contours across x1933; no false vertical edge.',
 'vertical_c2_r4.png': 'Cropped lamp arm, quiet ivory ground and soft shadow remain smooth across x1933. No hard guide boundary.',
 'vertical_c3_r1.png': 'Orange planter masonry, pale rail, post edges and shaded inset remain structurally continuous across x2957.',
 'vertical_c3_r2.png': 'Two original upper masonry/paving edges remain continuous across x2957; quiet lower stone has no guide stripe.',
 'vertical_c3_r3.png': 'Slanted groove crosses x2957 without a step; lower rounded leaf silhouette and broad stone shading remain coherent.',
 'vertical_c3_r4.png': 'Rounded dark and midgreen foliage with small ivory openings stays coherent across x2957; no sliced leaf or guide edge.',
 'vertical_c4_r4.png': 'Overlapping light and dark foliage and lower brown branch continue across x3981 without a false vertical transition contour.'
}
assert len(notes) == 26
items = []
for check in checks:
    p = Path(check['file'])
    im = rgb(p)
    assert sha(p) == check['sha256'], p
    assert im.size == (check['width'], check['height']), p
    mappings = []
    if 'pixelMappings' in check:
        derived = {str(Path(x['file'])): x for x in check['derivedFrom']}
        reconstructed = Image.new('RGB', im.size)
        for m in check['pixelMappings']:
            sp = Path(m['source'])
            sh = sha(sp)
            assert sh == derived[str(sp)]['sha256']
            piece = rgb(sp).crop(m['sourceBox'])
            xy = m['destinationXY']
            reconstructed.paste(piece, xy)
            mappings.append({'source': str(sp), 'sourceSha256': sh, 'sourceBoxXYXY': m['sourceBox'], 'destinationBoxXYXY': [xy[0], xy[1], xy[0]+piece.width, xy[1]+piece.height], 'rawRGBSha256': pix(piece), 'resampling': 'none'})
    else:
        box = check.get('sourceBox', check.get('coreBox'))
        reconstructed = core.crop(box)
        mappings = [{'source': str(core_path), 'sourceSha256': core_sha, 'sourceBoxXYXY': box, 'destinationBoxXYXY': [0,0,im.width,im.height], 'rawRGBSha256': pix(reconstructed), 'resampling': 'none'}]
    assert im.size == reconstructed.size and im.tobytes() == reconstructed.tobytes(), p
    name = p.name
    inherited_name = None
    inherited_box = [0,0,im.width,im.height]
    if name.startswith('external_north_'):
        inherited_name = name.replace('external_north_', 'external-north-')
    elif name.startswith('external_east_') and not name.endswith('part4.png'):
        inherited_name = name.replace('external_east_', 'external-east-')
    elif name.startswith('edge_north_'):
        inherited_name = name.replace('edge_north_', 'external-north-')
        inherited_box = [0,256,1024,512]
    elif name.startswith('edge_east_') and not name.endswith('part4.png'):
        inherited_name = name.replace('edge_east_', 'external-east-')
        inherited_box = [0,0,256,1024]
    elif name == 'corner_ne.png':
        inherited_name = 'corner-northeast512.png'
    elif name in ['vertical_c4_r1.png','vertical_c4_r2.png','vertical_c4_r3.png']:
        inherited_name = 'guide-east-part' + name[-5] + '.png'
    inherited = None
    if inherited_name:
        ev = early_items[inherited_name]
        ep = Path(ev['file'])
        assert ev['actuallyViewed'] and not ev['requiresRepair']
        assert sha(ep) == ev['sha256']
        eim = rgb(ep)
        assert pix(eim) == ev['rawRGBSha256']
        crop = eim.crop(inherited_box)
        assert im.size == crop.size and im.tobytes() == crop.tobytes(), (name, inherited_name)
        inherited = {'review': str(review_path), 'reviewSha256': sha(review_path), 'reviewer': early['reviewer'], 'reviewedAtUtc': early['reviewedAtUtc'], 'file': str(ep), 'sha256': ev['sha256'], 'sourceImageRawRGBSha256': ev['rawRGBSha256'], 'sourceBoxXYXY': inherited_box, 'cropRawRGBSha256': pix(crop), 'byteExactRGBEqualityVerified': True, 'scopeRelation': 'entire previously viewed scope' if inherited_box == [0,0,eim.width,eim.height] else 'exact subcrop within previously viewed external-neighbor board', 'originalObservation': ev['observation']}
        observation = ev['observation'] if name.startswith(('external_', 'vertical_', 'corner_')) else 'Own edge strip is byte-exactly the mapped half of the previously viewed neighbor comparison board; its original observation is preserved in inherited evidence.'
    else:
        assert name in notes, name
        observation = notes[name]
    items.append({'file': str(p), 'sha256': sha(p), 'pixels': list(im.size), 'rawRGBSha256': pix(im), 'pixelMappings': mappings, 'sourcePixelsReconstructedAndVerified': True, 'resampling': 'none', 'scope': check.get('kind', 'vertical_guide_transition' if 'axis' in check else 'external_north' if 'north' in name else 'external_east'), 'guideCoreCoordinate': check.get('coreCoordinate'), 'visualEvidence': 'inherited_byte_exact_pixels' if inherited else 'new_actual_native_view', 'actuallyViewedByThisReviewer': not bool(inherited), 'viewMethod': None if inherited else 'tools.view_image(detail=original)', 'inheritedEvidence': inherited, 'requiresRepair': False, 'observation': observation})

result = {'schemaVersion': 1, 'tile': 'r09_c09', 'reviewer': 'c09_final_neighbor', 'reviewedAtUtc': datetime.now(timezone.utc).isoformat(), 'candidateSource': {'file': str(core_path), 'sha256': core_sha, 'pixels': list(core.size)}, 'scopeCount': len(items), 'coverage': {'outerEdges': 16, 'outerCorners': 4, 'externalNorth': 4, 'externalEast': 4, 'verticalGuideTransitions': 16}, 'newActualOriginalPixelViews': sum(x['actuallyViewedByThisReviewer'] for x in items), 'inheritedExactPixelScopes': sum(bool(x['inheritedEvidence']) for x in items), 'allListedScopesHaveActualPixelVisualEvidence': True, 'allPixelSourceReconstructionsVerified': True, 'items': items, 'findings': [], 'requiresRepair': False, 'minorObservations': ['Ivory paving retains broad low-contrast oblique/faceted brush variation; no distinct seam-aligned stripe identified in these scopes.'], 'imagesModified': False, 'formalAccepted': False, 'clientValidated': False, 'qualifiedComplete4KCandidate': False, 'wholeCityComplete': False, 'limitations': ['This review covers only the 44 explicitly listed native crops, not every pixel of the tile.', 'Own west and south edge inspections do not establish continuity with future unfinished neighbors.', 'The full four-tile northeast junction is outside these scopes. Horizontal guide bands and internal seams are covered by other reviews.']}
assert result['newActualOriginalPixelViews'] == 26
assert result['inheritedExactPixelScopes'] == 18
out = T / 'qa/final-neighbor-review.json'
assert out.resolve().is_relative_to(ROOT)
assert not out.exists(), 'Do not overwrite an existing QA record'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'file': str(out), 'sha256': sha(out), 'scopes': len(items), 'newViews':26, 'inherited':18, 'requiresRepair':False}))
