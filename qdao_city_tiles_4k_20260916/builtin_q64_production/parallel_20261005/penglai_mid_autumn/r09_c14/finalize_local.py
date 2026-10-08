"""Validate recorded visual QA; write scoped acceptance only with --approve.

This script never accepts artwork automatically or changes candidate pixels.
Historical visual reviews can apply only when their exact QA image SHA remains
unchanged and that QA image is independently reproduced from the final pixels.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from PIL import Image

FOLDER = Path(__file__).resolve().parent
TILE = 'r09_c14'
MISSING = ['north', 'east', 'south']
PASS = {'pass', 'scoped_pass', 'current_pixels_inspected_neighbor_unverified'}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ref(path):
    return {'file': str(path), 'sha256': sha(path)}


def key(path):
    return str(Path(path).resolve()).casefold()


def fold(band, vertical=False):
    sheet = Image.new('RGB', (1024, 1280))
    for index in range(4):
        box = (0, index*1024, 320, (index+1)*1024) if vertical else (index*1024, 0, (index+1)*1024, 320)
        piece = band.crop(box)
        if vertical:
            piece = piece.transpose(Image.Transpose.ROTATE_90)
        sheet.paste(piece, (0, index*320))
    return sheet


def strip(image, axis, position):
    box = (position-160, 0, position+160, 4096) if axis == 'x' else (0, position-160, 4096, position+160)
    return fold(image.crop(box), axis == 'x')


def expected_images(candidate, west):
    images = {}
    for axis in ['x', 'y']:
        for position in [1024, 2048, 3072]:
            images[f'internal-{axis}{position}-full.png'] = strip(candidate, axis, position)
            images[f'internal-{axis}{position}-return-256-full.png'] = strip(candidate, axis, position+256)
    for y in [1024, 2048, 3072]:
        for x in [1024, 2048, 3072]:
            images[f'junction-{x}-{y}.png'] = candidate.crop((x-160, y-160, x+160, y+160))
    images['north-return-256-full.png'] = strip(candidate, 'y', 256)
    images['west-return-256-full.png'] = strip(candidate, 'x', 256)
    band = Image.new('RGB', (320, 4096))
    band.paste(west.crop((3936, 0, 4096, 4096)), (0, 0))
    band.paste(candidate.crop((0, 0, 160, 4096)), (160, 0))
    images['west-shared-full.png'] = fold(band, True)
    images['east-no-neighbor-unverified.png'] = fold(candidate.crop((3776, 0, 4096, 4096)), True)
    images['south-no-neighbor-unverified.png'] = fold(candidate.crop((0, 3776, 4096, 4096)))
    check(len(images) == 26, 'Expected exactly 26 standard QA images')
    return images


def verify_pixels(path, expected):
    with Image.open(path) as actual:
        check(actual.size == expected.size and actual.convert('RGB').tobytes() == expected.tobytes(),
              f'QA pixels do not match current candidate: {path}')


def load_review(path, flag, candidate_path, finalsha):
    report = read(path)
    check(report.get(flag) is True, f'Review has not passed: {path}')
    check(report.get('issueCount', 0) == 0 and report.get('issues', []) == [], f'Unresolved issues: {path}')
    source_candidate = report.get('candidate', {})
    check(key(source_candidate.get('file', '')) == key(candidate_path), f'Wrong reviewed candidate path: {path}')
    source_sha = source_candidate.get('sha256', '')
    check(re.fullmatch('[0-9a-f]{64}', source_sha) is not None, f'Missing reviewed candidate SHA: {path}')
    items = report.get('items', report.get('mainQA', []))
    check(bool(items), f'Empty review: {path}')
    checked = {}
    for item in items:
        qp = Path(item['file'])
        check(qp.resolve().is_relative_to((FOLDER/'qa').resolve()), f'QA outside tile: {qp}')
        check(item.get('actuallyViewed') is True and item.get('nativeScale') == 1, f'No actual native-scale view: {qp}')
        check(item.get('verdict') in PASS, f'Non-passing QA verdict: {qp}')
        check(sha(qp) == item.get('sha256'), f'QA changed since visual review: {qp}')
        check(key(qp) not in checked, f'Duplicate item in review: {qp}')
        applied = copy.deepcopy(item)
        applied['sourceReview'] = ref(path)
        applied['sourceReviewCandidateSha256'] = source_sha
        applied['appliedToCandidateSha256'] = finalsha
        applied['newVisualInspectionClaimed'] = source_sha == finalsha
        if source_sha != finalsha:
            applied['reviewReuse'] = {
                'originalCandidateSha256': source_sha,
                'originalReview': ref(path),
                'originalQAImageSha256': item['sha256'],
                'currentQAImageSha256': sha(qp),
                'exactQAImageSha256Match': True,
                'reason': 'The QA PNG is byte-for-byte unchanged from its actual visual review; validation also reproduces this inspection image from the final candidate pixels. This is reuse of that review, not a claim of a new visual inspection.'}
        checked[key(qp)] = applied
    return report, checked


def validate(finalsha):
    check(re.fullmatch('[0-9a-f]{64}', finalsha) is not None, 'Supply an explicit lowercase SHA256 with --finalsha')
    candidate_path = FOLDER/'output/r09_c14-candidate.png'
    check(sha(candidate_path) == finalsha, 'Candidate does not match explicit --finalsha')
    candidate = Image.open(candidate_path).convert('RGB')
    check(candidate.size == (4096, 4096), 'Candidate must be 4096 by 4096')
    generation_path = Path(str(candidate_path) + '.generation.json')
    generation = read(generation_path)
    check(generation.get('sha256') == finalsha, 'Current candidate generation record is stale')
    plan = read(FOLDER/'plan.json')
    check(plan['tile']['id'] == TILE, 'Wrong tile plan')
    check(not plan.get('northCandidate') and not plan.get('northWestCandidate'), 'This finalizer only supports the west-neighbor scope')
    west_path = Path(plan['westCandidate'])
    check(sha(west_path) == plan['westCandidateSha256'], 'West neighbor changed')
    west = Image.open(west_path).convert('RGB')
    check(west.size == (4096, 4096), 'West neighbor must be 4096 by 4096')
    originals = read(FOLDER/'output/native-assembly.json')
    check(originals['tile'] == TILE and originals.get('sourceCount') == 16, 'Invalid assembly source')
    standard = expected_images(candidate, west)
    expected = {key(FOLDER/'qa/native-candidate'/name): (FOLDER/'qa/native-candidate'/name, pixels) for name, pixels in standard.items()}
    extra_north = FOLDER/'qa/north-no-neighbor-unverified.png'
    expected[key(extra_north)] = (extra_north, fold(candidate.crop((0, 0, 4096, 320))))
    # Optional unrotated external details still require exact latest pixels.
    for index in range(4):
        qp = FOLDER/f'qa/external-details/west-segment-{index+1}.png'
        detail = Image.new('RGB', (512, 1024))
        detail.paste(west.crop((3840, index*1024, 4096, (index+1)*1024)), (0, 0))
        detail.paste(candidate.crop((0, index*1024, 256, (index+1)*1024)), (256, 0))
        expected[key(qp)] = (qp, detail)
    covered = {}
    review_refs = []
    scopes = [
        ('horizontal-review.json', 'scopedPass', {key(FOLDER/'qa/native-candidate'/n) for n in standard if n.startswith('internal-y') or n.startswith('junction-')}),
        ('external-review.json', 'externalScopedPass', {key(FOLDER/'qa/native-candidate'/n) for n in ['west-shared-full.png', 'west-return-256-full.png']}),
        ('root-review.json', 'scopedPass', {key(FOLDER/'qa/native-candidate'/n) for n in standard if n.startswith('internal-x') or n in ['north-return-256-full.png', 'east-no-neighbor-unverified.png', 'south-no-neighbor-unverified.png']} | {key(extra_north)})]
    for name, flag, required in scopes:
        rp = FOLDER/'qa'/name
        report, items = load_review(rp, flag, candidate_path, finalsha)
        check(required.issubset(items), f'Required scope is not covered: {name}')
        for k, item in items.items():
            check(k in expected, f'Unsupported QA image; add explicit pixel verification first: {item["file"]}')
            qp, pixels = expected[k]
            verify_pixels(qp, pixels)
            item['verifiedAgainstFinalCandidatePixels'] = True
            covered[k] = item
        review_refs.append(dict(**ref(rp), reviewedCandidateSha256=report['candidate']['sha256']))
    standard_keys = {key(FOLDER/'qa/native-candidate'/n) for n in standard}
    check(standard_keys.issubset(covered) and key(extra_north) in covered, 'Incomplete standard or extra north QA')
    check(sha(candidate_path) == finalsha and sha(west_path) == plan['westCandidateSha256'], 'Pixels changed during validation')
    return candidate_path, generation_path, generation, originals, covered, review_refs, standard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finalsha', required=True, help='Explicit final candidate SHA256; never inferred')
    parser.add_argument('--approve', action='store_true', help='Write scoped manifest after all recorded reviews pass')
    args = parser.parse_args()
    p, gp, generation, assembly, covered, reports, standard = validate(args.finalsha)
    if not args.approve:
        print(json.dumps({'validationPassed': True, 'writesPerformed': False, 'candidateSha256': args.finalsha, 'standardQACount': 26}))
        return
    check(not (FOLDER/'qa/final-local-review.json').exists(), 'Refuse to overwrite finalized review')
    pending_manifest = FOLDER/'output/manifest.json'
    if pending_manifest.exists():
        check(read(pending_manifest).get('scopedLocalSeamsPassed') is not True, 'Refuse to overwrite finalized manifest')
        snapshot = FOLDER/'output/pre-finalization-manifest.json'
        check(not snapshot.exists(), 'Refuse to overwrite pending-manifest evidence')
        snapshot.write_bytes(pending_manifest.read_bytes())
    progress_path = FOLDER/'progress.json'
    if progress_path.exists():
        check(read(progress_path).get('scopedLocalSeamsPassed') is not True, 'Refuse to overwrite finalized progress')
    timestamp = now()
    final_review = dict(reviewedAt=timestamp, candidate=ref(p), sourceReviews=reports,
                        items=list(covered.values()), all26StandardQAImagesActuallyViewed=True,
                        standardQACount=26, additionalNorthBoundaryInspected=True,
                        scopedLocalSeamsPassed=True, scopedPass=True, issueCount=0, issues=[],
                        missingExternalNeighbors=MISSING, externalSeamsVerified={'west': True, 'north': False, 'east': False, 'south': False},
                        formalAccepted=False, navigationVerified=False, clientVerified=False,
                        acceptanceNote='Scoped acceptance covers the internal seams and actual west neighbor only. Historical unchanged QA is explicitly attributed to its original review; absent north/east/south shared edges remain unverified.')
    final = copy.deepcopy(assembly)
    final.update(file=str(p), sha256=args.finalsha, pixels=[4096, 4096],
                 status='native_4K_candidate_available_internal_west_QA_passed',
                 scopedLocalSeamsPassed=True, scopedReview=str(FOLDER/'qa/final-local-review.json'),
                 acceptedAtScoped=timestamp, missingExternalNeighbors=MISSING,
                 externalSeamsVerified=final_review['externalSeamsVerified'],
                 sourceManifest=ref(FOLDER/'output/native-assembly.json'),
                 assemblyCandidateSha256=assembly['sha256'], currentCandidateGeneration=ref(gp),
                 sourceRecordsHistoricalAfterRetention=False, runtimeDependencies=[ref(p)],
                 formalAccepted=False, navigationVerified=False, clientVerified=False,
                 acceptanceNote=final_review['acceptanceNote'])
    final['qa'] = []
    for name in standard:
        it = copy.deepcopy(covered[key(FOLDER/'qa/native-candidate'/name)])
        it['reviewVerdict'] = it['verdict']
        final['qa'].append(it)
    # Only metadata records are written; candidate and QA images remain untouched.
    write(FOLDER/'qa/final-local-review.json', final_review)
    final['scopedReviewRecord'] = ref(FOLDER/'qa/final-local-review.json')
    write(FOLDER/'output/manifest.json', final)
    write(FOLDER/'progress.json', dict(updatedAt=timestamp, tile=TILE, nativePatches=16,
        pixels=[4096, 4096], completePixelCoverage=True, file=str(p), sha256=args.finalsha,
        scopedLocalSeamsPassed=True, missingExternalNeighbors=MISSING,
        externalSeamsVerified=final_review['externalSeamsVerified'],
        formalAccepted=False, navigationVerified=False, clientVerified=False))
    print(json.dumps({'scopedAcceptanceWritten': True, 'candidateSha256': args.finalsha, 'standardQACount': 26}))


if __name__ == '__main__':
    main()
