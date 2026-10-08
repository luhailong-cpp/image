"""Audit this worker's row 3 provenance; write text only, never mutate pixels."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from PIL import Image
import numpy as np

T = Path(__file__).resolve().parents[1]
N = T / 'native'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def item(p):
    return {'file': str(p), 'sha256': sha(p)}

guide_index = {x['id']: x for x in read(T/'guides/index.json')['records']}
reviews = {
    'p31': 'Original-scale output viewed. Quay cap, inset wall courses and raised wood post remain in their planned positions. Local rear-beam highlight at patch x925..1000/y810..975 fades under the wall, also present in guide; flag for assembled review. Actual west boundary and row joins remain unapproved until assembly QA.',
    'p32': 'Original-scale output viewed. Stone wall, round timber post with rings and dock planks preserve framing. Temporary context rectangle is healed. Final overlaps still require assembled QA.',
    'p33': 'Original-scale output viewed. Dock railing, pier and reflected amber light preserve framing. Water has newly painted crisp wave contours; final contour continuity remains to be checked on assembled seams.',
    'p34': 'Original-scale output viewed. Cropped pier, lower-left timber post, cobalt water and reflection columns retain composition. Final north/left wave continuity remains to be checked on assembled seams.',
}
items = []
for c in range(1, 5):
    ident = f'p3{c}'
    p = N/(ident+'.png')
    reqp = N/(ident+'.request.json')
    callp = N/(ident+'.call.json')
    genp = N/(ident+'.png.generation.json')
    req, call, gen = read(reqp), read(callp), read(genp)
    assert sha(p) == gen['sha256'] == gen['evidence']['sourceOutputSha256']
    assert sha(gen['evidence']['sourceOutputPath']) == sha(p)
    assert gen['submittedParameters'] == req['submittedParameters']
    submitted = dict(req['submittedParameters'])
    assert submitted.pop('model') is None
    assert submitted.pop('quality') is None
    assert submitted == call
    assert gen['actualModel'] is None and gen['actualQuality'] is None
    assert Path(req['prompt']).read_text(encoding='utf-8') == call['prompt']
    assert sha(req['prompt']) == req['promptSha256'] == gen['promptSha256']
    assert req['references'] == gen['references']
    for ref in req['references']:
        assert sha(ref['file']) == ref['sha256']
    assert [r['file'] for r in req['references']] == call['referenced_image_paths']
    guide = T/'guides'/(ident+'.png')
    assert sha(guide) == guide_index[ident]['sha256']
    assert req['globalPatchXYWH'] == guide_index[ident]['globalPatchXYWH'] == gen['globalPatchXYWH']
    canvas = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
    for region in req['contextRegions']:
        assert sha(region['file']) == region['sha256']
        assert region['scale'] == 1
        im = Image.open(region['file']).convert('RGBA')
        canvas.paste(im.crop(region['cropLTRB']), region['pasteXY'])
    assert np.array_equal(np.asarray(canvas), np.asarray(Image.open(N/(ident+'-context.png')).convert('RGBA')))
    target = Image.open(guide).convert('RGBA')
    target.alpha_composite(canvas)
    assert np.array_equal(np.asarray(target.convert('RGB')), np.asarray(Image.open(N/(ident+'-edit-target.png')).convert('RGB')))
    native = Image.open(p).convert('RGBA')
    assert native.size == (1254, 1254)
    assert native.getchannel('A').getextrema() == (255, 255)
    assert gen['route'] == 'builtin' and not gen['sourceUpscaled'] and not gen['resizedAfterGeneration']
    items.append({**item(p), 'id': ident, 'pixels': [1254, 1254],
        'actuallyViewed': True, 'nativeScale': 1, 'referenceInputsActuallyViewedBeforeCall': True,
        'review': reviews[ident], 'verdict': 'native_detail_reviewed_pending_full_seam_QA',
        'provenancePassed': True, 'call': item(callp), 'request': item(reqp), 'generation': item(genp),
        'contextSourceCount': len(req['contextRegions'])})

report = {'createdAt': datetime.now(timezone.utc).isoformat(), 'tile': 'r10_c14',
    'worker': '/root/r09c14_row2_resume', 'row': 3, 'planAtAudit': item(T/'plan.json'),
    'nativeHelper': item(T.parent/'native_patch.py'), 'allFourSaved': True,
    'allFourProvenancePassed': True, 'pixelChangesByAudit': False,
    'actualModel': None, 'actualQuality': None,
    'modelQualityEvidence': 'Configuration target recorded in each generation; builtin exposes no explicit model or quality selector/return value.',
    'items': items, 'fullSeamQAStillRequired': True, 'formalAccepted': False,
    'pendingConcerns': [{'id': 'p31-rear-beam-highlight', 'file': str(N/'p31.png'),
        'patchRegionApproxLTRB': [925, 810, 1000, 975],
        'tileRegionApproxLTRB': [810, 2743, 885, 2908],
        'observation': 'Short rightward timber highlight behind raised post fades into/under stone wall; same local form exists in approved guide. Parent notified for assembled review.',
        'assemblyVerdict': 'unverified'}]}
out = T/'qa/native-row3-review.json'
assert not out.exists(), 'Keep prior written review; choose a versioned audit if rerunning.'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'report': str(out), 'sha256': sha(out), 'provenancePassed': True,
                  'items': [{k: v for k, v in x.items() if k in ('id','sha256')} for x in items]}))
