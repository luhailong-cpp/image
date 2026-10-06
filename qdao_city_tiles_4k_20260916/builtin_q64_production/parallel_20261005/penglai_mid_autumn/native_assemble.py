"""Native wavefront assembly and original-pixel QA; no generation or acceptance.

Import and selfcheck have no production side effects. See native_assemble.md.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ref(path):
    return {'file': str(Path(path).resolve()), 'sha256': sha(path)}


@dataclass(frozen=True)
class Layout:
    stride: int = 1024
    halo: int = 115
    count: int = 4

    @property
    def patch(self): return self.stride + 2 * self.halo
    @property
    def tile(self): return self.count * self.stride
    @property
    def extended(self): return self.tile + 2 * self.halo
    @property
    def crop(self): return [self.halo, self.halo, self.halo + self.tile, self.halo + self.tile]

    def origin(self, row, col):
        assert 0 <= row < self.count and 0 <= col < self.count
        return col * self.stride, row * self.stride

    def native_owner_mask(self, known, edges):
        if not edges:
            return ~known  # An optional standalone NW support must not be overwritten.
        yy, xx = np.indices(known.shape)
        core_side = np.ones_like(known)
        if 'left' in edges: core_side &= xx >= self.halo
        if 'top' in edges: core_side &= yy >= self.halo
        return ~known | core_side


def seed_neighbors(layout, north=None, west=None, northwest=None):
    """Real outside pixels only; unprovided NW corner remains explicitly unknown."""
    h, n, e = layout.halo, layout.tile, layout.extended
    canvas = np.zeros((e, e, 3), np.uint8)
    known = np.zeros((e, e), bool)
    records = []
    for name, image, crop, dest in [
        ('north', north, [0, n-h, n, n], [h, 0]),
        ('west', west, [n-h, 0, n, n], [0, h]),
        ('northwest', northwest, [n-h, n-h, n, n], [0, 0]),
    ]:
        if image is None: continue
        assert image.shape == (n, n, 3)
        x0, y0, x1, y1 = crop
        x, y = dest
        piece = image[y0:y1, x0:x1]
        canvas[y:y+piece.shape[0], x:x+piece.shape[1]] = piece
        known[y:y+piece.shape[0], x:x+piece.shape[1]] = True
        records.append({'role': name, 'sourceCropLTRB': crop, 'canvasPasteXY': dest, 'scale': 1})
    return canvas, known, records


def cv_module():
    sys.path.insert(0, str(ROOT / 'tools/deps'))
    import cv2
    return cv2


def smoothstep(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def register_native(context, patch, known, owner, edges, layout, max_shift=6., tone_cap=18., return_depth=256):
    """Use only real support to estimate fields. Binary ownership, no geometry feather."""
    cv = cv_module()
    size = layout.patch
    yy, xx = np.mgrid[:size, :size].astype(np.float32)
    assert context.shape == patch.shape == (size, size, 3)
    assert known.any()
    # Unknown scene pixels are identical in the two flow inputs, not fabricated context.
    reference = np.where(known[:, :, None], context, patch)
    raw = cv.calcOpticalFlowFarneback(cv.cvtColor(reference, cv.COLOR_RGB2GRAY),
                                    cv.cvtColor(patch, cv.COLOR_RGB2GRAY), None,
                                    .5, 4, 41, 5, 7, 1.5, 0)
    support = known.astype(np.float32)
    denominator = cv.GaussianBlur(support, (0, 0), 3)
    estimated = cv.GaussianBlur(raw * support[:, :, None], (0, 0), 3)
    estimated /= np.maximum(denominator[:, :, None], 1e-6)
    # Extend only measured true-support values, with a recorded finite return to zero.
    _, labels = cv.distanceTransformWithLabels((~known).astype(np.uint8), cv.DIST_L2, 5,
                                               labelType=cv.DIST_LABEL_PIXEL)
    lut = np.zeros((int(labels.max()) + 1, 2), np.float32)
    lut[labels[known]] = estimated[known]
    field = cv.GaussianBlur(lut[labels], (0, 0), 3)
    distances = []
    if 'left' in edges: distances.append(xx - layout.halo)
    if 'top' in edges: distances.append(yy - layout.halo)
    distance = np.minimum.reduce(distances)
    weight = smoothstep((return_depth - distance) / (return_depth - 32))
    magnitude = np.linalg.norm(field, axis=2)
    flow = field * np.minimum(1, max_shift / np.maximum(magnitude, 1e-6))[:, :, None]
    flow *= weight[:, :, None]
    aligned = cv.remap(patch, xx + flow[:, :, 0], yy + flow[:, :, 1], cv.INTER_CUBIC,
                       borderMode=cv.BORDER_REPLICATE)
    # Estimate color only from low-gradient, similar material support; never blur artwork.
    def gradient(image):
        gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY).astype(np.float32)
        gy, gx = np.gradient(gray)
        return np.hypot(gx, gy)
    residual = context.astype(np.float32) - aligned.astype(np.float32)
    safe = known & (gradient(context) < 12) & (gradient(aligned) < 12)
    safe &= np.max(np.abs(residual), axis=2) < 40
    correction = np.zeros_like(patch, np.float32)
    if safe.any() and tone_cap > 0:
        weights = cv.GaussianBlur(safe.astype(np.float32), (0, 0), 12)
        measured = cv.GaussianBlur(residual * safe[:, :, None], (0, 0), 12)
        measured /= np.maximum(weights[:, :, None], 1e-6)
        _, tone_labels = cv.distanceTransformWithLabels((~safe).astype(np.uint8), cv.DIST_L2, 5,
                                                        labelType=cv.DIST_LABEL_PIXEL)
        tone_lut = np.zeros((int(tone_labels.max()) + 1, 3), np.float32)
        tone_lut[tone_labels[safe]] = measured[safe]
        correction = cv.GaussianBlur(tone_lut[tone_labels], (0, 0), 12)
        correction = np.clip(correction, -tone_cap, tone_cap) * weight[:, :, None]
    matched = np.clip(np.rint(aligned.astype(np.float32) + correction), 0, 255).astype(np.uint8)
    # Interior must be exactly native, even if the interpolation implementation changes.
    matched[weight == 0] = patch[weight == 0]
    result = np.where(owner[:, :, None], matched, context)
    assert np.array_equal(result[~owner], context[~owner])
    assert np.array_equal(result[(weight == 0) & owner], patch[(weight == 0) & owner])
    dy_u, dx_u = np.gradient(flow[:, :, 0])
    dy_v, dx_v = np.gradient(flow[:, :, 1])
    jacobian = (1 + dx_u) * (1 + dy_v) - dy_u * dx_v
    report = {
        'kind': 'bounded_native_registration_from_true_support', 'edges': edges,
        'nativePixels': [size, size], 'supportPixelCount': int(known.sum()),
        'supportWidthInternal': 2 * layout.halo, 'supportWidthExternal': layout.halo,
        'flowConvention': 'source native sampled at output XY plus stored flow XY',
        'maxAllowedDisplacementVector': max_shift,
        'actualMaxDisplacementVector': float(np.linalg.norm(flow, axis=2).max()),
        'actualMaxDisplacementXY': np.abs(flow).max(axis=(0, 1)).tolist(),
        'rawSupportMaxDisplacementVector': float(np.linalg.norm(raw[known], axis=1).max()),
        'clippedSupportFraction': float(np.mean(magnitude[known] > max_shift)),
        'maxAllowedColorCorrectionRGB': tone_cap,
        'actualMaxColorCorrectionRGB': np.abs(correction).max(axis=(0, 1)).tolist(),
        'sameMaterialColorSupportPixels': int(safe.sum()),
        'returnDepthInsideCore': return_depth, 'fieldFullStrengthInsideCore': 32,
        'jacobianMinimumInAppliedPixels': float(jacobian[owner].min()),
        'foldedAppliedPixels': int(np.sum((jacobian <= 0) & owner)),
        'binaryOwnershipMask': True, 'geometryFeather': False, 'artworkBlurred': False,
        'nativePixelScale': 1, 'sourceUpscaling': False, 'resampling': 'bounded native bicubic',
        'zeroMaskPixelsUnchanged': True, 'outsideInfluencePixelsNativeUnchanged': True,
        'requiresVisualQA': True, 'largeOrMissingStructureRequiresAIRepaint': True,
    }
    return result, flow, correction, report


def load_native(path, expected_size):
    with Image.open(path) as image:
        assert image.size == (expected_size, expected_size), str(path)
        rgba = image.convert('RGBA')  # Includes P-mode tRNS and RGB transparent-color metadata.
        assert rgba.getchannel('A').getextrema() == (255, 255), str(path)
        return np.asarray(rgba.convert('RGB')).copy()


def full_strip(image, axis, pos, context=160):
    """Fold four 1024-long pieces; no resizing, including vertical strips."""
    assert image.size == (4096, 4096)
    sheet = Image.new('RGB', (1024, context * 8))
    boxes = []
    for section in range(4):
        start = section * 1024
        box = [pos-context, start, pos+context, start+1024] if axis == 'x' else [start, pos-context, start+1024, pos+context]
        piece = image.crop(box)
        if axis == 'x': piece = piece.transpose(Image.Transpose.ROTATE_90)
        sheet.paste(piece, (0, section * context * 2))
        boxes.append(box)
    return sheet, {'sourceCropLTRB': boxes, 'rotationCCW90': axis == 'x', 'axis': axis, 'position': pos}


def make_qa(final_path, neighbors, out, return_depth):
    final = Image.open(final_path).convert('RGB')
    out.mkdir(parents=True, exist_ok=True)
    records = []
    def save(image, name, operation, sources):
        path = out / (name + '.png')
        image.save(path)
        item = dict(**ref(path), pixels=list(image.size), nativeScale=1, actuallyViewed=False,
                    verdict='pending_visual_QA', operation=operation, sources=sources)
        write(str(path) + '.generation.json', item)
        records.append(item)
    candidate = ref(final_path)
    for axis in ['x', 'y']:
        for pos in [1024, 2048, 3072]:
            image, operation = full_strip(final, axis, pos)
            save(image, f'internal-{axis}{pos}-full', operation, [candidate])
            # Each patch's finite field also returns inside its core, outside the seam crop.
            returned, return_operation = full_strip(final, axis, pos + return_depth)
            return_operation['scope'] = 'internal native registration field return'
            return_operation['sourceCoreBoundary'] = pos
            save(returned, f'internal-{axis}{pos}-return-{return_depth}-full', return_operation, [candidate])
    for y in [1024, 2048, 3072]:
        for x in [1024, 2048, 3072]:
            box = [x-160, y-160, x+160, y+160]
            save(final.crop(box), f'junction-{x}-{y}', {'cropLTRB': box}, [candidate])
    for side in ['north', 'west']:
        data = neighbors.get(side)
        if data:
            old = Image.fromarray(data['pixels'])
            if side == 'north':
                band = Image.new('RGB', (4096, 320))
                band.paste(old.crop((0, 3936, 4096, 4096)), (0, 0))
                band.paste(final.crop((0, 0, 4096, 160)), (0, 160))
            else:
                band = Image.new('RGB', (320, 4096))
                band.paste(old.crop((3936, 0, 4096, 4096)), (0, 0))
                band.paste(final.crop((0, 0, 160, 4096)), (160, 0))
            sheet = Image.new('RGB', (1024, 1280))
            for i in range(4):
                box = (1024*i, 0, 1024*(i+1), 320) if side == 'north' else (0, 1024*i, 320, 1024*(i+1))
                piece = band.crop(box)
                if side == 'west': piece = piece.transpose(Image.Transpose.ROTATE_90)
                sheet.paste(piece, (0, 320*i))
            save(sheet, side + '-shared-full', {'scope': 'full 4096 actual-neighbor seam', 'oldContext': 160,
                 'newContext': 160, 'rotationCCW90': side == 'west', 'sectionLength': 1024}, [data['reference'], candidate])
        image, operation = full_strip(final, 'y' if side == 'north' else 'x', return_depth)
        operation['scope'] = 'full external-registration return; inspect even when no neighbor exists'
        save(image, side + f'-return-{return_depth}-full', operation, [candidate])
    # No east/south neighbors are supplied by this workflow. These are inspection-only.
    for side, box in [('east', [3776, 0, 4096, 4096]), ('south', [0, 3776, 4096, 4096])]:
        band = final.crop(box)
        sheet = Image.new('RGB', (1024, 1280))
        for i in range(4):
            piece = band.crop((0, i*1024, 320, (i+1)*1024)) if side == 'east' else band.crop((i*1024, 0, (i+1)*1024, 320))
            if side == 'east': piece = piece.transpose(Image.Transpose.ROTATE_90)
            sheet.paste(piece, (0, i*320))
        save(sheet, side+'-no-neighbor-unverified', {'cropLTRB': box, 'noNeighbor': True, 'seamAccepted': False}, [candidate])
    return records


def assemble(args):
    assert re.fullmatch(r'r\d{2}_c\d{2}', args.tile), 'Tile id required, e.g. r10_c13'
    row, col = map(int, [args.tile[1:3], args.tile[5:7]])
    assert 1 <= row <= 16 and 1 <= col <= 16
    folder = ROOT / args.tile
    plan_path = folder / 'plan.json'
    plan = read(plan_path)
    layout = Layout()
    assert plan['tile']['id'] == args.tile
    assert plan['tile']['finalPixelRect'] == [(col-1)*4096, (row-1)*4096, 4096, 4096]
    assert plan['core'] == 1024 and plan['halo'] == 115 and plan['nativeGrid'] == [4, 4]
    assert plan['nativePatchPixels'] == [1254, 1254]
    assert 0 <= args.max_shift <= 12 and 0 <= args.tone_cap <= 32
    assert 160 <= args.return_depth <= 512
    sources = []
    missing = []
    for r in range(4):
        for c in range(4):
            path = folder / 'native' / f'p{r+1}{c+1}.png'
            metadata = Path(str(path) + '.generation.json')
            if not path.is_file() or not metadata.is_file(): missing.append(str(path)); continue
            rec = read(metadata)
            assert rec['sha256'] == sha(path), str(path)
            assert not rec.get('sourceUpscaled', False) and not rec.get('resizedAfterGeneration', False)
            x, y = layout.origin(r, c)
            expected = [plan['tile']['finalPixelRect'][0]-115+x, plan['tile']['finalPixelRect'][1]-115+y, 1254, 1254]
            assert rec['globalPatchXYWH'] == expected, str(path)
            sources.append({'row': r, 'col': c, 'path': path, 'reference': ref(path), 'generation': ref(metadata), 'pixels': load_native(path, 1254)})
    if missing: raise RuntimeError('Native wavefront incomplete; no outputs written. Missing: ' + ', '.join(missing))
    neighbors = {}
    for role, key_name in [('north', 'northCandidate'), ('west', 'westCandidate'), ('northwest', 'northWestCandidate')]:
        if plan.get(key_name):
            path = Path(plan[key_name]);neighbors[role] = {'reference': ref(path), 'pixels': load_native(path, 4096)}
            frozen_sha = plan.get(key_name + 'Sha256')
            if frozen_sha:
                assert neighbors[role]['reference']['sha256'] == frozen_sha, 'Frozen neighbor differs from plan: ' + role
    if args.preflight:
        print(json.dumps({'tile': args.tile, 'nativeCount': len(sources), 'neighbors': list(neighbors), 'outputsWritten': False}));return
    output = folder / 'output'
    qa_folder = folder / 'qa/native-candidate'
    final_path = output / f'{args.tile}-candidate.png'
    manifest_path = output / 'native-assembly.json'
    fields_path = output / 'native-fields'
    protected_outputs = [final_path, Path(str(final_path)+'.generation.json'), manifest_path,
                         fields_path, qa_folder, output/'native-registration-failure.json']
    assert not any(p.exists() for p in protected_outputs), 'Refuse to overwrite existing images, fields, QA or retained text records.'
    canvas, covered, seed = seed_neighbors(layout, **{k: v['pixels'] for k, v in neighbors.items()})
    fields_path.mkdir(parents=True)
    reports = []
    for source in sources:
        r, c, patch = source['row'], source['col'], source['pixels']
        x, y = layout.origin(r, c);s = layout.patch
        context = canvas[y:y+s, x:x+s].copy()
        known = covered[y:y+s, x:x+s].copy()
        edges = []
        if c or 'west' in neighbors: edges.append('left')
        if r or 'north' in neighbors: edges.append('top')
        owner = layout.native_owner_mask(known, edges)
        label = f'p{r+1}{c+1}'
        if known.any() and edges and args.registration == 'bounded':
            merged, flow, tone, report = register_native(context, patch, known, owner, edges, layout,
                                                         args.max_shift, args.tone_cap, args.return_depth)
        else:
            merged = np.where(owner[:, :, None], patch, context)
            flow = np.zeros((s, s, 2), np.float32);tone = np.zeros((s, s, 3), np.float32)
            report = {'kind': 'native_binary_ownership_only', 'sourceResampling': False, 'sourceUpscaling': False,
                      'actualMaxDisplacementVector': 0, 'actualMaxColorCorrectionRGB': [0, 0, 0], 'foldedAppliedPixels': 0}
        fields = {}
        for kind, value in [('mask', owner.astype(np.uint8)*255), ('support-mask', known.astype(np.uint8)*255), ('flow', flow), ('colorCorrection', tone)]:
            dst = fields_path / f'{label}.{kind}{".png" if kind.endswith("mask") else ".npy"}'
            if kind.endswith('mask'): Image.fromarray(value).save(dst)
            else: np.save(dst, value)
            fields[kind] = ref(dst)
        report.update(id=label, source=source['reference'], generation=source['generation'], canvasXY=[x, y], fields=fields)
        reports.append(report)
        if report['foldedAppliedPixels']:
            write(output/'native-registration-failure.json', {'createdAt':now(),'report':report,'candidateWritten':False,'needsManualDiagnosisOrAIRepair':True})
            raise RuntimeError(label + ': folding detected; no candidate published.')
        canvas[y:y+s, x:x+s] = merged
        covered[y:y+s, x:x+s] = True
    for source in sources:
        assert sha(source['path']) == source['reference']['sha256'], 'Native input changed during assembly'
    for data in neighbors.values():
        assert sha(data['reference']['file']) == data['reference']['sha256'], 'Neighbor changed during assembly'
    assert covered[115:4211, 115:4211].all()
    Image.fromarray(canvas[115:4211, 115:4211]).save(final_path)
    qa = make_qa(final_path, neighbors, qa_folder, args.return_depth)
    manifest = {'createdAt': now(), 'tile': args.tile, 'file': str(final_path), 'sha256': sha(final_path),
                'pixels': [4096,4096], 'globalPixelRectXYWH': plan['tile']['finalPixelRect'],
                'plan': ref(plan_path), 'tool': ref(__file__), 'sourceCount':16, 'patchPixels':[1254,1254],
                'stride':1024, 'halo':115, 'extendedPixels':[4326,4326], 'finalCropLTRB':layout.crop,
                'seedRegions':seed, 'neighbors':{k:v['reference'] for k,v in neighbors.items()},
                'northwestTrueSupportAvailable':'northwest' in neighbors, 'patches':reports, 'qa':qa,
                'completePixelCoverage':True, 'sourcePixelScale':1, 'sourceUpscaling':False,
                'geometryFeather':False, 'automaticSceneDrawing':False,
                'status':'candidate_pending_original_pixel_visual_QA', 'scopedLocalSeamsPassed':False,
                'formalAccepted':False, 'clientVerified':False, 'navigationVerified':False,
                'missingExternalNeighbors':['east','south']+[k for k in ['north','west'] if k not in neighbors],
                'acceptanceNote':'Coverage/metrics are not seam acceptance. Inspect every native QA image. Missing or excessive geometry requires AI repaint, not stronger warping or color masking.'}
    write(manifest_path, manifest)
    generation = {'file':str(final_path),'sha256':sha(final_path),'createdAt':now(),'width':4096,'height':4096,
                  'format':'PNG','derivedFrom':[v['reference'] for v in sources], 'operation':ref(manifest_path),
                  'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,
                  'modelEvidence':'Mechanical derivative only; source image generation sidecars preserve configuration, submitted parameters and actual nulls.',
                  'productionPixels':True,'formalAccepted':False,'clientVerified':False,'navigationVerified':False}
    write(str(final_path)+'.generation.json', generation)
    print(json.dumps({'candidate':str(final_path),'sha256':sha(final_path),'qa':str(qa_folder),'qaCount':len(qa),'status':manifest['status']}))


def selfcheck():
    """Small coordinate-coded arrays only; no project images, no production output."""
    layout = Layout(stride=16, halo=3, count=4)
    n, h, p, e = layout.tile, layout.halo, layout.patch, layout.extended
    def coords(x0, y0, width, height):
        yy, xx = np.mgrid[y0:y0+height, x0:x0+width]
        return np.stack([xx%256, yy%256, (xx*3+yy*7)%256],axis=2).astype(np.uint8)
    north = coords(64,0,n,n);west=coords(0,64,n,n);nw=coords(0,0,n,n)
    truth = coords(64-h,64-h,e,e)
    canvas, known, _ = seed_neighbors(layout,north,west,nw)
    assert np.array_equal(canvas[known],truth[known])
    _, absent_corner, _ = seed_neighbors(layout,north,west)
    assert not absent_corner[:h,:h].any() and absent_corner[:h,h:h+n].all()
    coverage=np.zeros((n,n),np.uint8)
    for r in range(4):
        for c in range(4):
            x,y=layout.origin(r,c);patch=truth[y:y+p,x:x+p]
            current=canvas[y:y+p,x:x+p];support=known[y:y+p,x:x+p]
            mask=layout.native_owner_mask(support,['left','top'])
            canvas[y:y+p,x:x+p]=np.where(mask[:,:,None],patch,current)
            known[y:y+p,x:x+p]=True
            coverage[r*16:(r+1)*16,c*16:(c+1)*16]+=1
            if c:assert np.array_equal(truth[y:y+p,x:x+2*h],patch[:,:2*h])
            if r:assert np.array_equal(truth[y:y+2*h,x:x+p],patch[:2*h])
    assert np.all(coverage==1) and known[h:h+n,h:h+n].all()
    assert np.array_equal(canvas[h:h+n,h:h+n],coords(64,64,n,n))
    # Real production arithmetic, without allocating a production-size image.
    actual=Layout();assert actual.extended==4326 and actual.crop==[115,115,4211,4211]
    for r in range(4):
        for c in range(4):
            x,y=actual.origin(r,c)
            assert x+115-actual.halo==c*1024 and y+115-actual.halo==r*1024
    assert [x+actual.halo for x in [1024,2048,3072]]==[1139,2163,3187]
    for index in range(4):
        start=index*1024-115;lo=max(0,start);hi=min(4096,start+1254)
        # Native first-row/column support crops map exactly back to final-tile coordinates.
        assert 0<=lo<hi<=4096 and 0<=lo-start<hi-start<=1254
        assert start+(lo-start)==lo and start+(hi-start)==hi
        assert hi-lo==([1139,1254,1254,1139][index])
    standalone=np.zeros((p,p),bool);standalone[:h,:h]=True
    assert not layout.native_owner_mask(standalone,[])[:h,:h].any()
    # Alpha can be encoded in PNG metadata without an A band; reject both forms.
    from io import BytesIO
    for mode, transparency in [('P',0),('RGB',(0,0,0))]:
        tiny=Image.new(mode,(2,2),0);buffer=BytesIO()
        tiny.save(buffer,format='PNG',transparency=transparency);buffer.seek(0)
        try: load_native(buffer,2)
        except AssertionError: pass
        else: raise AssertionError('Transparent PNG metadata bypassed input validation')
    result={'checkedAt':now(),'result':'pass','syntheticTilePixels':[64,64], 'syntheticExtendedPixels':[70,70],
            'checks':['all16 core coordinates exactly once','native binary ownership maps exact coordinate pixels',
                      '230-equivalent internal overlap','115-equivalent real north/west/NW support',
                      'missing NW remains unknown; supplied NW remains protected',
                      'all4 clipped external native contexts map without offset',
                      '4326 crop and4096 seam offsets','P/RGB transparent PNG metadata rejected'],
            'productionImagesRead':False,'productionAssemblyRun':False,'generationCalled':False}
    print(json.dumps(result))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('selfcheck',help='small in-memory coordinate checks only')
    build=commands.add_parser('assemble',help='requires all16 immutable native patches')
    build.add_argument('--tile',required=True)
    build.add_argument('--preflight',action='store_true',help='validate all inputs and hashes, write nothing')
    build.add_argument('--registration',choices=['bounded','none'],default='bounded')
    build.add_argument('--max-shift',type=float,default=6.,help='vector displacement limit, default6; implementation permits0..12')
    build.add_argument('--tone-cap',type=float,default=18.,help='per-channel correction limit,0..32')
    build.add_argument('--return-depth',type=int,default=256,help='finite influence return inside native core,160..512')
    args=parser.parse_args()
    if args.command=='selfcheck':selfcheck()
    else:assemble(args)


if __name__=='__main__':main()
