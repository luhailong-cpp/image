"""Read-only source verification and new Penglai handoff checkpoint; no artwork edits."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

B = Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
D = B / 'penglai_joint_c12_batch_20260917'
OUT = D / 'handoff-checkpoint-20260919.json'
assert not OUT.exists(), OUT

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

checks = []
counts = {}
for appearance in ['penglai_day', 'penglai_mid_autumn']:
    native = B / appearance / 'r09_c12/native'
    ids = []
    for p in sorted(native.glob('r??_c??.record.json')):
        r = json.loads(p.read_text(encoding='utf-8-sig'))
        img = p.with_name(p.name.replace('.record.json', '.png'))
        im = Image.open(img)
        assert im.size == (1254, 1254)
        assert im.mode != 'RGBA' or im.getextrema()[3] == (255, 255)
        h = sha(img)
        assert h == r['outputSha256']
        source = Path(r['sourceOutputPath'])
        assert sha(source) == h
        refs = r.get('submittedImages', [])
        for ref in refs:
            assert sha(ref['path']) == ref['sha256']
        prompt = r.get('promptFile', r.get('promptPath'))
        pp = Path(prompt)
        if not pp.is_absolute():
            pp = native.parent / pp
        assert sha(pp) == r['promptSha256']
        ids.append(r.get('id', r.get('tileId')))
        checks.append({'appearance': appearance, 'id': ids[-1], 'file': str(img), 'sha256': h,
                       'record': str(p), 'recordSha256': sha(p), 'nativePixels': list(im.size),
                       'sourceBytesPreserved': True, 'submittedReferenceHashChecks': len(refs)})
    counts[appearance] = {'tile': 'r09_c12', 'count': len(ids), 'expected': 16, 'ids': ids,
                          'missing': [f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)
                                      if f'r{r:02}_c{c:02}' not in ids]}

repairs = []
for p in sorted((D / 'audit_20260918/repairs/native').glob('*.record.json')):
    r = json.loads(p.read_text(encoding='utf-8-sig'))
    img = p.with_name(p.name.replace('.record.json', '.png'))
    assert sha(img) == r['outputSha256'] == sha(r['sourceOutputPath'])
    for ref in r.get('submittedImages', []):
        assert sha(ref['path']) == ref['sha256']
    im = Image.open(img)
    assert im.size == (1254,1254)
    assert im.mode != 'RGBA' or im.getextrema()[3] == (255,255)
    repairs.append({'id': r['id'], 'file': str(img), 'sha256': sha(img), 'record': str(p),
                    'recordSha256': sha(p), 'nativePixels': list(im.size), 'sourceBytesPreserved': True,
                    'status': 'generated_and_applied_to_day_v2_not_visually_accepted'})

day = B / 'penglai_day/r09_c10_c11_c12_joint'
qa = day / 'qa_v2_20260918'
inspected = [qa / f'internal_{axis}{pos}.png' for axis in ['x','y'] for pos in [1024,2048,3072]]
data = {
    'schemaVersion': 1,
    'createdAtUtc': datetime.now(timezone.utc).isoformat(),
    'reason': 'User requested transfer to another window; no new generation or batch started after stop request.',
    'status': 'saved_for_handoff_not_complete',
    'wholeCityComplete': False, 'formallyAccepted': False, 'runtimePublished': False,
    'scope': 'Penglai r09_c12 day and Mid-Autumn continuation only; 64K cities remain incomplete.',
    'nativeCounts': counts,
    'sourceVerification': {'passed': True, 'baseRecords': checks, 'extraRepairRecords': repairs,
                           'baseNativeCount': len(checks), 'extraNativeCount': len(repairs)},
    'generatedThisTask': [checks[-2], checks[-1]],
    'currentlySelected': {
        'penglai_day': {'tiles': ['r09_c10','r09_c11'], 'directory': str(B/'penglai_day/r09_c10_c11_joint/output')},
        'penglai_mid_autumn': {'tiles': ['r09_c10','r09_c11'], 'directory': str(B/'penglai_mid_autumn/r09_c10_c11_joint/output/v3')}
    },
    'latestUnselectedDay': {
        'directory': str(day/'output_v2_20260918'),
        'assembly': str(day/'output_v2_20260918/assembly.json'),
        'assemblySha256': sha(day/'output_v2_20260918/assembly.json'),
        'triple': str(day/'output_v2_20260918/triple-12288x4096.png'),
        'tripleSha256': sha(day/'output_v2_20260918/triple-12288x4096.png'),
        'status': 'two_native_water_repairs_applied_pending_return_and_shared_boundary_QA',
        'visualQaThisTask': {
            'overviewViewed': True,
            'allSixFullInternalLines': True,
            'method': 'Each 4096px line shown losslessly as four 300x1024 native-pixel panels; horizontal strips rotated only.',
            'evidence': [{'path': str(p), 'sha256': sha(p)} for p in inspected],
            'verdict': 'No obvious structure discontinuities found along the six complete internal lines.',
            'notYetViewed': ['four complete c11/c12 shared-boundary slices in qa_v2_20260918',
                             'two repair joined-support crops and all four return borders per ROI',
                             'repair-overlap-crossing.png', 'three intersections_y*.png sheets for v2']
        },
        'knownRepairTarget': 'Original triple had narrow water brightness/reflection-density band around x8060..8400,y2300..4096; v2 has two native repairs but no final visual acceptance.',
        'resamplingDisclosure': 'Native repair edges underwent limited optical registration (max 8 px); source PNG bytes preserved; flow/color/masks recorded in assembly.'
    },
    'midAutumn': {
        'nativeGenerationComplete': True,
        'assemblyComplete': False,
        'assemblyAttempt': {'script': str(B/'penglai_mid_autumn/r09_c12/assemble_builtin.py'),
                            'exitCode': 1, 'error': 'ValueError: Unified Q-style reference and guides are not ready; refusing assembly',
                            'cause': 'Script accepts only ready_unified_style_reference; plan truthfully uses ready_unified_local_structure. Refusal occurred before source load or output writing.'},
        'next': 'Create a versioned assembler accepting the existing ready_unified_local_structure preparation status, retain all provenance checks, verify submitted reference hashes and overlap identity, preserve current plan/native/prompt bytes. Fix inherited userSelectedModel output label so mixed historical source versions stay historical and current product target is Images 2.5, backend unverified. Assemble in a new versioned output/QA directory, then join old selected pair v3 via a versioned assemble_triple script pointing at that new context.',
        'visualQa': 'All internal full lines, intersections, shared boundary and any repairs still pending after assembly.'
    },
    'nextSteps': [
        'Review day qa_v2_20260918 boundary_y0000.png, boundary_y1024.png, boundary_y2048.png, boundary_y2842.png; both joined-support images, all return borders and repair-overlap-crossing.png. If any defect persists, create a new native repair and new output version, do not overwrite v2.',
        'Complete Mid-Autumn versioned mechanical assembly as specified, validate 16 sources, crop identity and full seam QA; then joint assembly with old pair output/v3 and inspect entire c11/c12 seam.',
        'When each selected triple passes local visual QA, write an independent ledger-update with candidates for c10/c11/c12 and only new repairRecords; root performs merge. No candidate is selected by this checkpoint.',
        'Continue next neighboring block only after the current batch checkpoint/ledger is accurate. Entire 64K, external neighbors, cross-appearance microgeometry, foreground/navigation/runtime acceptance remain outstanding.'
    ],
    'ledger': {'newCandidateLedgerReady': False, 'rootLedgerModified': False,
               'doNotMerge': str(D/'audit_20260918/ledger-update.json'),
               'reason': 'Existing audit ledger is stale and empty; neither new triple has passed final local QA. Base native records are safely on disk; two existing day extra repairs are listed above for a future incremental ledger.'},
    'commands': {
        'python': 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe',
        'note': 'Default sandbox Python startup was denied; require_escalated with user-authorized main-city asset work succeeded. Image reference path input worked normally.',
        'dayRepairScriptAlreadyExecutedDoNotRerun': str(D/'apply_day_repairs_v2_20260918.py'),
        'tripleScriptTemplateDoNotOverwriteExistingDay': str(D/'assemble_triple.py')
    },
    'model': {'requestedProduct': 'ChatGPT Images 2.5', 'route': 'builtin_image_gen',
              'backendModelVerified': False, 'modelSelectorAvailable': False, 'qualitySelectorAvailable': False,
              'actualNewNativePixels': [1254,1254], 'finalArtUpscaled': False}
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'checkpoint': str(OUT), 'nativeCounts': {a:v['count'] for a,v in counts.items()},
                  'extraRepairCount': len(repairs), 'newNativeThisTask': 2, 'newSelectedCandidates': 0}, ensure_ascii=False))
