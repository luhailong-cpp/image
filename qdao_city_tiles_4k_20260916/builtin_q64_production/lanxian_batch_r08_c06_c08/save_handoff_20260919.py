from pathlib import Path
from PIL import Image
import json, hashlib, datetime

P = Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
B = P / 'lanxian_batch_r08_c06_c08'
S = P / 'lanxian_spring/r08_c08'
T = P / 'lanxian_spring/triple_r08_c06_c08'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def evidence(p): return {'file': str(p), 'sha256': sha(p)}
def write(p, obj):
    assert not p.exists(), p
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

selected = read(S / 'source-selection.json')
sources = []
for row in range(1, 5):
    for col in range(1, 5):
        ident = f'r{row:02d}_c{col:02d}'
        stem = selected.get(ident, {}).get('nativeStem', ident)
        path = S / 'native' / f'{stem}.record.json'
        rec = read(path)
        png = Path(rec['outputFile'])
        assert sha(png) == rec['outputSha256']
        assert sha(rec['sourceOutputPath']) == rec['sourceOutputSha256'] == rec['outputSha256']
        assert sha(rec['promptFile']) == rec['promptSha256']
        for ref in rec['submittedImages']: assert sha(ref['path']) == ref['sha256']
        with Image.open(png) as im:
            assert im.size == (1254, 1254)
            assert im.convert('RGBA').getchannel('A').getextrema() == (255,255)
        sources.append({'id': ident, 'selectedStem': stem, **evidence(path), 'sourceSha256': rec['outputSha256']})

viewed = [S / 'qa/overview_1024.png']
viewed += [S / 'qa/fullseams_20260919' / f'{a}{n}.png' for a in ('x','y') for n in (1024,2048,3072)]
viewed += [T / 'qa_v1' / n for n in ('overview.jpg', 'c07-c08-full-seam.png', 'boundary-intersection-y1024.png', 'boundary-intersection-y2048.png', 'boundary-intersection-y3072.png')]
review = {
 'schemaVersion': 1, 'createdAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status': 'needs_boundary_repairs_not_approved', 'appearance': 'lanxian_spring',
 'assembly': evidence(T / 'output_v1/assembly.json'),
 'inspectionCoverage': {'singleTileInternalFullSeams': 6, 'pixelsPerFullSeam': 4096, 'externalFullSeams': 1, 'externalSeamPixels': 4096, 'externalIntersections': 3, 'repairReturnRegions': 0},
 'inspectedFiles': [evidence(p) for p in viewed],
 'observations': [
  'Six complete c08 single-tile internal seams inspected as four unscaled 1024px segments each. No clear structural break observed in this pass.',
  'After joint assembly, c07/c08 border shows abrupt stone brushwork change between prior smoother left surface and new mottled right surface. Strongest in upper gray paving and also visible lower ivory paving.',
  'Short groove/bevel discontinuity in upper seam segment, approximately triple x8080..8140,y350..440; exact repair crop must be re-localized from full-resolution triple.',
  'Short grout highlight/dark line break near triple x8280..8330,y2200..2250, seen in boundary-intersection-y2048.png at roughly local x540..590,y606..656; exact ROI needs recheck.',
  'Three crossing crops inspected. New block remains unapproved because the external border defects are unresolved.',
  'No native generation started in this takeover. User requested cross-window handoff after mechanical join and visual inspection.'
 ],
 'pending': [
  'Prepare new versioned native boundary repair references from spring output_v1, redraw the incomplete lines and texture transition using built-in image_gen with actual reference paths recorded.',
  'Inspect all repair returns on four edges, all changed portions of c08 internal full seams and the entire c07/c08 boundary.',
  'Inspect remaining internal crossing close-ups after repairs; the six full seam strips already include intersections but nine separate crop checks were not performed in this takeover.',
  'Do not count the triple as accepted or merge spring c08 until repairs and visual checks pass.',
  'Cross-appearance exact geometry, all other outer neighbors, navigation, foreground, nearest-camera and Unity runtime acceptance remain pending.'
 ],
 'formalAcceptance': False, 'wholeCityAccepted': False, 'runtimePublished': False
}
write(T / 'visual-review-v1-20260919.json', review)
assembly = read(T / 'output_v1/assembly.json')
checkpoint = {
 'schemaVersion': 1, 'createdAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status': 'handoff_requested_by_user_no_active_generation',
 'scope': 'Lanxian only. Root ledger was not modified by this takeover.',
 'selectedExistingDay': {'directory': str(P/'lanxian_day/triple_r08_c06_c08/output_v2'), 'coordinates': ['r08_c06','r08_c07','r08_c08'], 'alreadyMergedLedger': str(B/'day-ledger-root-20260918.json'), 'visualQA': str(P/'lanxian_day/triple_r08_c06_c08/visual-review-v2.json')},
 'selectedExistingSpring': {'directory': str(P/'lanxian_spring/pair_r08_c06_c07/output'), 'version': 'pair_v6', 'coordinates': ['r08_c06','r08_c07']},
 'springC08': {
  'nativeSelectedCount': 16, 'nativePhysicalCount': len(list((S/'native').glob('*.png'))),
  'selectedSources': sources, 'retainedUnselected': ['native/r01_c03.png','native/r01_c03.record.json'],
  'nativeAndPromptAndActualInputHashesVerified': True, 'allSelectedNative1254SquareOpaque': True,
  'assembler': str(S/'assemble_builtin_single_v3.py'), 'assemblerCheckPassed': True,
  'singleTileOutput': evidence(S/'output/lanxian_spring_r08_c08_q64_4k_candidate.png'),
  'newJointDirectory': str(T/'output_v1'), 'jointAssembly': evidence(T/'output_v1/assembly.json'),
  'jointCandidateCount': 3, 'newUniqueCoordinateCountPendingQA': 1,
  'splitPixelIdentityPassed': assembly['splitPixelIdentityPassed'], 'c06PixelsUnchangedFromV6': assembly['c06PixelsUnchangedFromV6'],
  'visualQA': evidence(T/'visual-review-v1-20260919.json'),
  'approvedForRootMerge': False, 'pendingLedger': None
 },
 'newFilesThisTakeover': [str(B/'assemble_spring_triple_c08_20260919.py'), str(S/'qa/fullseams_20260919'), str(T/'output_v1'), str(T/'qa_v1'), str(T/'visual-review-v1-20260919.json')],
 'nextSteps': review['pending'],
 'nextReadOnlyCommands': [
  "& 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe' -X utf8 '" + str(S/'assemble_builtin_single_v3.py').replace('\\','/') + "' --check",
  "Get-Content -LiteralPath '" + str(T/'visual-review-v1-20260919.json').replace('\\','/') + "' -Raw"
 ],
 'warnings': [
  'Do not rerun assemble_spring_triple_c08_20260919.py: it already created output_v1 and asserts against overwrite.',
  'Do not run old prepare_lanxian_c08.py / prepare_lanxian_c08_day_guides.py / finalize_lanxian_batch.py: hard-coded previous versions can regress state.',
  'Use apply_day_c08_repairs_v2.py only as mechanical implementation reference; create separate spring version and new filenames.',
  'The old resume-checkpoint.json is stale (claims 0/16). This checkpoint supersedes it.',
  'Existing historical plan userSelectedModel still records earlier request; preserve history. New calls target configured Images 2.5 via host-managed built-in, model and quality selectors unavailable.'
 ],
 'toolEnvironment': 'Default sandbox denied launching Python; require_escalated authorized for the mechanical join and verification. view_image worked normally.',
 'formalAcceptance': False, 'wholeCityAccepted': False, 'runtimePublished': False
}
write(B/'handoff-checkpoint-20260919.json', checkpoint)
print(json.dumps({'checkpoint': str(B/'handoff-checkpoint-20260919.json'), 'selectedSources': len(sources), 'physicalNatives': checkpoint['springC08']['nativePhysicalCount'], 'approvedForMerge': False}, ensure_ascii=False))
