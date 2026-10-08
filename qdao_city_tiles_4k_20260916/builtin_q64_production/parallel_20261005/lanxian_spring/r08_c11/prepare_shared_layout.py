"""Derive shared day/spring layout guides; no image generation or production pixels.

All writes are confined to this script's r08_c11 directory. The 1254 full-map
reference is sampled at its true 65536 mapped extent, never treated as HD art.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
REPO = Path('D:/work/image')
DATA = REPO / 'qdao_city_tiles_4k_20260916'
BASE = OUT.parent
DAY = BASE.parent / 'lanxian_day'
LAYOUT = DATA / 'builtin_q64_all_city_references/lanxian_day/map-native-layout-reference.png'
STYLE = REPO / 'designs/gameplay-ui/04-guild.png'
PLAN = DATA / 'q64_production_plans/lanxian_spring.json'
NAV = REPO / 'qdao_large_city_maps_20260912/runtime/lanxian-navigation.json'
PRIOR_NAV = BASE / 'preflight/navigation-contract.json'
WEST = BASE / 'r08_c10/selected-v2'
DELIVERY = WEST / 'delivery.manifest.json'
CORE = (40960, 28672, 45056, 32768)
EXTENT = (40845, 28557, 45171, 32883)
SCALE = 65536 / 1254
NOW = datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    assert path.resolve().is_relative_to(OUT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def info(path, role):
    p = Path(path)
    result = {'file': p.as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size, 'role': role}
    if p.suffix.lower() == '.png':
        with Image.open(p) as im:
            result.update(pixels=list(im.size), mode=im.mode)
    return result


def save_image(im, name, sources, operation, **extra):
    path = OUT / 'guides' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    rec = {**info(path, 'shared day/spring structural planning guide only'),
           'createdAtUtc': NOW, 'newAIGeneration': False, 'derivedFrom': sources,
           'operation': operation, 'productionPixelsAllowed': False,
           'formalAccepted': False, 'crossAppearancePairVerificationPending': True, **extra}
    write(Path(str(path) + '.derivation.json'), rec)
    return rec


def clip(poly, rect):
    points = [tuple(p) for p in poly]
    for axis, edge, less in [(0, rect[0], False), (0, rect[2], True), (1, rect[1], False), (1, rect[3], True)]:
        result = []
        if not points:
            break
        for a, b in zip(points[-1:] + points[:-1], points):
            ina = a[axis] <= edge if less else a[axis] >= edge
            inb = b[axis] <= edge if less else b[axis] >= edge
            if ina != inb:
                t = (edge - a[axis]) / (b[axis] - a[axis])
                result.append(tuple(edge if j == axis else a[j] + t * (b[j] - a[j]) for j in range(2)))
            if inb:
                result.append(b)
        points = result
    return [[round(v, 6) for v in p] for p in points]


assert OUT.name == 'r08_c11'
assert not (DAY / 'r08_c11').exists(), 'Day counterpart appeared. Inspect/reuse it before preparing a competing base.'
assert DELIVERY.exists(), 'WAIT: west selected delivery manifest is required.'
delivery_hash = sha(DELIVERY)
delivery = read(DELIVERY)
assert delivery['qualifiedComplete4KCandidate'] is True
assert delivery['tile'] == 'r08_c10'
assert read(BASE / 'current-selection.json')['currentCandidates']
west_plan_entry = next(x for x in read(PLAN)['tiles'] if x['id'] == 'r08_c10')
assert west_plan_entry['finalPixelRect'] == [36864, 28672, 4096, 4096]
for key in ('core4096.png', 'extended4326.png'):
    rec = delivery['outputs'][key]
    assert sha(rec['file']) == rec['sha256'], f'West {key} differs from delivery manifest.'
    record = Path(rec['file'] + '.generation.json')
    if record.exists():
        assert read(record)['sha256'] == rec['sha256']
with Image.open(delivery['outputs']['extended4326.png']['file']) as im:
    assert im.size == (4326, 4326)
    extended = im.convert('RGB')
with Image.open(delivery['outputs']['core4096.png']['file']) as im:
    assert im.size == (4096, 4096)
    core = im.convert('RGB')
assert extended.crop((115, 115, 4211, 4211)).tobytes() == core.tobytes()
with Image.open(LAYOUT) as im:
    assert im.size == (1254, 1254)
    layout = im.convert('RGB')
plan = read(PLAN)
entry = next(x for x in plan['tiles'] if x['id'] == 'r08_c11')
assert entry['finalPixelRect'] == [40960, 28672, 4096, 4096]
day_entry = next(x for x in read(DATA/'q64_production_plans/lanxian_day.json')['tiles'] if x['id'] == 'r08_c11')
assert entry['finalPixelRect'] == day_entry['finalPixelRect'] and entry['worldRect'] == day_entry['worldRect']

layout_source = info(LAYOUT, 'Canonical original day full-map topology. 1254 square; layout only, not native HD.')
west_source = info(delivery['outputs']['extended4326.png']['file'], 'SHA-verified selected r08_c10 extended native assembly; qualified candidate, not formal accepted')
west_manifest = info(DELIVERY, 'Frozen selection qualification and native/source provenance')
source_box = [v / SCALE for v in EXTENT]
guide = layout.transform((4326, 4326), Image.Transform.EXTENT, source_box, Image.Resampling.BICUBIC)
guide_rec = save_image(guide, 'common-day-layout-only-4326.png', [layout_source],
    'Pillow EXTENT BICUBIC from exact fractional 1254 source box; enlargement solely for geometry planning',
    source1254ExtentLTRB=source_box, wholeCityExtentLTRB=list(EXTENT), coreInExtendedLTRB=[115, 115, 4211, 4211])
strip = extended.crop((4096, 0, 4326, 4326))
strip_rec = save_image(strip, 'west-r08_c10-exact230x4326.png', [west_source, west_manifest],
    'Exact crop without resampling', sourceCropLTRB=[4096, 0, 4326, 4326], targetExtendedLTRB=[0, 0, 230, 4326],
    wholeCityExtentLTRB=[40845, 28557, 41075, 32883], nativePixelContext=True,
    neighborCoreInsideStripLTRB=[0, 115, 115, 4211],
    provisionalNeighborHaloInsideStripLTRBs=[[115, 0, 230, 4326], [0, 0, 115, 115], [0, 4211, 115, 4326]],
    finalReusePolicy='Only the exact frozen overlap may constrain native pieces. No enlarged layout pixels may enter production.')
assert strip.crop((0, 115, 115, 4211)).tobytes() == core.crop((3981, 0, 4096, 4096)).tobytes()
combined = guide.copy()
combined.paste(strip, (0, 0))
combined_rec = save_image(combined, 'shared-layout-with-west-context-4326.png', [guide_rec, strip_rec],
    'Exact unblended west230 paste at x0 over layout-only fractional crop',
    pasteBoundaryX230IsNotSceneGeometry=True, alignmentAccepted=False,
    preserveExact230BandDuringNativeDetailProduction=True)
preview_rec = save_image(combined.resize((1254, 1254), Image.Resampling.LANCZOS),
    'shared-layout-with-west-context-1254.png', [combined_rec],
    '4326 to 1254 LANCZOS for regional reference only; west band now spans about66.67 display pixels',
    exactContextAvailableSeparately=strip_rec['file'])

nav = read(NAV)
shapes = []
for field, kind in [('allowed_floor_polygons', 'historical_allowed_floor'), ('excluded_obstacle_polygons', 'historical_excluded_obstacle')]:
    for shape in nav[field]:
        whole = [[x * SCALE, y * SCALE] for x, y in shape['vertices']]
        local = [[x - CORE[0], y - CORE[1]] for x, y in whole]
        clipped = clip(local, (-115, -115, 4211, 4211))
        if not clipped:
            continue
        shapes.append({'name': shape['name'], 'kind': kind,
            'source1254Vertices': shape['vertices'], 'wholeCity65536Vertices': whole,
            'coreLocalUnclippedVertices': local, 'extendedClippedCoreLocalVertices': clipped,
            'coreClippedVertices': clip(local, (0, 0, 4096, 4096)),
            'referenceOnlyNoNewArtworkAcceptance': True})
routes = []
for route in nav.get('manually_traced_route_strips', []):
    points = route['centerline']
    half = route['width_pixels'] / 2
    xs, ys = zip(*points)
    if max(xs) + half < source_box[0] or min(xs) - half > source_box[2] or max(ys) + half < source_box[1] or min(ys) - half > source_box[3]:
        continue
    routes.append({**route, 'intersectionTest': 'conservative bounding box including half width; not exact clipping',
        'wholeCityWidth': route['width_pixels'] * SCALE,
        'coreLocalCenterline': [[x * SCALE - CORE[0], y * SCALE - CORE[1]] for x, y in points]})
navigation = {'schemaVersion': 1, 'createdAtUtc': NOW, 'tile': 'r08_c11',
    'sources': [info(NAV, 'Historical navigation geometry; artwork differs from current full-map guide'), info(PRIOR_NAV, 'Historical mask/source reconstruction evidence')],
    'sourceArtworkDiffersFromCurrentLayout': True, 'sourceMaps': nav['source_maps'],
    'historicalGeometryPolicy': nav['geometry_policy'], 'historicalWalkableGrid': nav['walkable_grid'],
    'cellSizeWorld': nav['cell_size_world'], 'intersectingPolygons': shapes,
    'possiblyIntersectingRouteStrips': routes, 'historicalMaskEvidence': read(PRIOR_NAV).get('historicalMask'),
    'coordinates': {'wholeCityCoreLTRB': list(CORE), 'wholeCityExtendedLTRB': list(EXTENT),
        'source1254CoreLTRB': [v / SCALE for v in CORE], 'source1254ExtendedLTRB': source_box,
        'worldRectXZ': entry['worldRect'], 'runtimeWorldRect': entry['runtimeWorldRect'],
        'origin': 'top-left; x right; y down; rectangles endpoint exclusive',
        'sourceToCityScale': SCALE, 'cityToWorld': ['x = 50 + X/65536*300', 'z = 300 - Y/65536*300'],
        'coreToExtended': ['u = x + 115', 'v = y + 115']},
    'rules': ['Keep all existing structure, ground, shore and vegetation footprints; exact visible contents require actual mapped-guide inspection.',
        'Water, walls and planting remain blocked; keep bridge/walkway routes and all original openings unobstructed.',
        'Do not infer a new obstacle or road boundary from the mixed-resolution guide paste at x230.',
        'Use the original day crop for topology and exact west native band for boundary continuity; unresolved disagreement requires structural review, not blur or warp.',
        'Historical route names identify old navigation data only; they are not new game place names or verified HD alignment.',
        'The selected shared native geometry must be reused for the future day counterpart; seasonal changes may only alter existing material surfaces.'],
    'newArtworkNavigationAccepted': False, 'alignmentAccepted': False, 'formalAccepted': False,
    'crossAppearancePairVerificationPending': True}
navigation['southContextPending'] = True
navigation['mustRefreshSouthBeforeGeneration'] = True
write(OUT / 'navigation-contract.json', navigation)

write(OUT / 'source-evidence/west-delivery.snapshot.json', delivery)
if (WEST / 'extended4326.png.generation.json').exists():
    write(OUT / 'source-evidence/west-extended.generation.snapshot.json', read(WEST / 'extended4326.png.generation.json'))
write(OUT / 'source-evidence/config-snapshot.json', read(REPO / 'config/image-generation.json'))
for rec in (guide_rec, strip_rec, combined_rec, preview_rec):
    assert sha(rec['file']) == rec['sha256']
assert sha(DELIVERY) == delivery_hash, 'West manifest changed during derivation; recheck selected sources.'

native_cells = []
for r in range(1, 5):
    for c in range(1, 5):
        x, y = (c - 1) * 1024, (r - 1) * 1024
        native_cells.append({'cell': f'r{r:02d}_c{c:02d}', 'requiredNativePixels': [1254, 1254],
            'cropInExtendedGuideLTRB': [x, y, x + 1254, y + 1254],
            'retainedCoreInNativeLTRB': [115, 115, 1139, 1139],
            'corePlacementInFinal4096XY': [x, y],
            'wholeCityNativeExtentLTRB': [EXTENT[0] + x, EXTENT[1] + y, EXTENT[0] + x + 1254, EXTENT[1] + y + 1254],
            'externalWestExactBand': [0, y, 230, y + 1254] if c == 1 else None,
            'externalSouthBandPending': [x,4096,x+1254,4326] if r == 4 else None,
            'status': 'not_generated'})
contract = {'schemaVersion': 1, 'createdAtUtc': NOW, 'tile': 'r08_c11',
    'status': 'west_ready_south_pending_must_refresh_before_generation',
    'canonicalStructuralBaseIntent': 'One neutral common geometry for day and spring. Hosted here because day r08_c11 does not exist; not an independently invented seasonal layout.',
    'writeScope': OUT.as_posix(), 'newAIGenerationCount': 0, 'newComplete4KTiles': 0,
    'formalAccepted': False, 'runtimePublished': False, 'crossAppearancePairVerificationPending': True,
    'counterpartAtPreparation': {'directory': (DAY / 'r08_c11').as_posix(), 'exists': False, 'checkedAtUtc': NOW},
    'geometry': {'wholeCityPixels': [65536, 65536], 'grid': [16, 16], 'row': 8, 'column': 11,
        'corePixels': [4096, 4096], 'extendedPixels': [4326, 4326], 'haloPerSide': 115,
        'wholeCityCoreLTRB': list(CORE), 'wholeCityExtendedLTRB': list(EXTENT),
        'coreInExtendedLTRB': [115, 115, 4211, 4211], 'source1254ExtendedLTRB': source_box,
        'source1254CoveragePerSide': source_box[2] - source_box[0],
        'worldRect': entry['worldRect'], 'runtimeWorldRect': entry['runtimeWorldRect'],
        'nativeAssembly': '16 distinct 1254-square natives arranged4x4 at1024 stride; keep1024 core and115 halo per side; never enlarge guide into final pixels'},
    'sources': [layout_source, west_source, west_manifest, info(PLAN, 'Coordinate plan only; spring full-map image is not a geometry source'), info(STYLE, 'User-confirmed painting and material style only')],
    'sourceQualification': {'deliveryManifestPresent': True, 'westHashesVerified': True, 'westCoreEqualsExtendedCrop': True,
        'exactWest230CropVerified': True, 'neighborQualifiedComplete4KCandidate': True, 'neighborFormalAccepted': delivery['formalAccepted'],
        'notes': 'SHA-frozen boundary source is available; global geometry alignment, c11 art quality and cross-appearance pair are unverified.'},
    'artifacts': [guide_rec, strip_rec, combined_rec, preview_rec],
    'nativePieceContract': native_cells,
    'beforeGeneration': ['Actually view the1254 mixed guide and separate exact230 band; inspect geometric disagreements.',
        'Check whether a day counterpart has appeared, then adopt shared geometry instead of generating a competing layout.',
        'Recheck source image/manifest SHA before each dependent native batch.',
        'Attach confirmed style image and exact relevant neighbor strips to the tool; keep the regional output guide-only.',
        'Review structure/shore continuity across x230 without interpreting that guide paste seam as a new physical border.',
        'South r09_c11 is unfinished at preparation. Before ANY generation refresh from its selected qualified 4326 native halo, verify source SHA, paste exact source top230 to target bottom230, and inspect southwest corner consistency; no invented south context.'],
    'rejectedEvidencePolicy': 'Discarded r08_c10 independent regional/native geometry is not a source. r08_c10 is used only through its final selected verified east strip.',
    'navigationContract': (OUT / 'navigation-contract.json').as_posix(),
    'southNeighbor': {'tile':'r09_c11','status':'pending_selected_complete_native_candidate','sourceFile':None,'sourceSha256':None,'noSouthPixelsFabricated':True,'mustRefreshBeforeGeneration':True,'requiredSourceCropLTRB':[0,0,4326,230],'requiredTargetExtendedLTRB':[0,4096,4326,4326],'wholeCityOverlapLTRB':[40845,32653,45171,32883],'cornerConsistencyReviewRequired':True},
    'generationAllowedInThisPreparationStep':False,
    'generationHoldReason':'Parent task requires completed native south source to be refreshed before generation; this is dependency readiness, not a user-permission gate.'}
write(OUT / 'preparation.json', contract)
print(json.dumps({'output': OUT.as_posix(), 'extent': EXTENT, 'sourceBox': source_box,
    'westSha256': west_source['sha256'], 'navigationPolygons': [(x['name'], x['kind']) for x in shapes],
    'routes': [x['name'] for x in routes], 'sharedPairPending': True}, ensure_ascii=False))
