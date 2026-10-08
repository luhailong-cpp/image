"""Build a parent-only review candidate from the latest child selection.

Run only after all four branch reviews are ready:
    python integrate_current.py --execute
Never changes child selections or branch source images. No image generation.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import re
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
PARALLEL = ROOT.parent
PROGRESS = PARALLEL/'tianyong_festival/progress.json'
DEST = ROOT/'current'
BRANCHES = ['west-upper', 'east-lower', 'corner-left-return', 'corner-right-return']
EXPECTED_TILES = {'r08_c07', 'r08_c08', 'r08_c09', 'r09_c08', 'r09_c09'}
CONTEXT_MARGIN = 128
fingerprints = {}

def require(value, message):
    if not value:
        raise RuntimeError(message)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def file_ref(path, expected=None):
    path = Path(path).resolve()
    require(path.is_file(), f'Missing required file: {path}')
    sha = digest(path)
    require(expected is None or sha == expected, f'SHA mismatch: {path}')
    if path in fingerprints:
        require(fingerprints[path] == sha, f'File changed during read: {path}')
    fingerprints[path] = sha
    return {'file': str(path), 'sha256': sha}

def read_json(path, expected=None):
    file_ref(path, expected)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def rgb(path, expected=None):
    file_ref(path, expected)
    with Image.open(path) as im:
        im.load()
        require(im.size == (4096, 4096), f'Not 4096 square: {path}')
        if 'A' in im.getbands():
            require(im.getchannel('A').getextrema() == (255, 255), f'Partial/transparent repaired tile: {path}')
        return np.array(im.convert('RGB'))

def tile_id(entry):
    return entry.get('tile') or entry.get('tileId') or entry.get('id')

def source_identity(output):
    source = output.get('source', {})
    path = output.get('sourcePath') or source.get('path') or source.get('file')
    sha = output.get('sourceSha256') or source.get('sha256')
    require(path and sha, 'Branch output lacks source path/SHA')
    return path, sha

def changed_box(mask):
    yy, xx = np.where(mask)
    require(len(xx) > 0, 'Repair branch has no changed pixels')
    return [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)]

def crop(array, box):
    x0, y0, x1, y1 = box
    return array[y0:y1, x0:x1]

def qa_mappings(item, board_size):
    if item.get('mappings'):
        result = []
        for m in item['mappings']:
            if m.get('source') in ['original', 'before', 'original_context']:
                continue
            context = m.get('contextRectLTRB') or m.get('contextLTRB')
            board = m.get('boardRectLTRB')
            require(context and board, 'QA mapping lacks rectangles')
            result.append((context, board))
        return result
    context = item.get('contextRectLTRB') or item.get('contextLTRB')
    require(context, f'Cannot map QA pixels: {item.get("file")}')
    w, h = context[2]-context[0], context[3]-context[1]
    if item.get('beforeAfter'):
        require(board_size == (2*w+12, h), 'Unexpected before/after board dimensions')
        return [(context, [w+12, 0, 2*w+12, h])]
    require(board_size == (w, h), 'QA crop needs explicit mapping; do not infer resizing')
    return [(context, [0, 0, w, h])]

def current_pointer():
    # Progress itself may change while the child draws; the selected checkpoint must stay stable.
    j = json.loads(PROGRESS.read_text(encoding='utf-8-sig'))
    path = Path(j['candidateSet'])
    if not path.is_absolute():
        path = PROGRESS.parent/path
    return path.resolve()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Perform integration after all branch reviews are ready')
    args = parser.parse_args()
    if not args.execute:
        print('Prepared only. No files written. Use --execute after the fourth branch is reviewed.')
        return
    require(not (DEST/'current-selection.json').exists(), 'Parent current selection already exists; review it before a new integration run.')
    snapshot_time = datetime.now(timezone.utc).isoformat()
    approvals_path = ROOT/'parent-reviewed-scopes.json'
    approval_record = read_json(approvals_path)
    approvals = {x['branch']: x for x in approval_record['branches']}
    require(set(approvals) == set(BRANCHES), 'Parent scope approval does not cover exactly four repair branches')
    for name in BRANCHES:
        a = approvals[name]
        require(a.get('limitedRepairAcceptedForMerge') is True, f'Parent local review not accepted: {name}')
        file_ref(a['bindings'], a['bindingsSha256'])
        file_ref(a['review'], a['reviewSha256'])
        for viewed in a.get('parentActuallyViewed', []):
            file_ref(viewed['file'], viewed['sha256'])
    selected_path = current_pointer()
    selected = read_json(selected_path)
    require(isinstance(selected.get('candidates'), list), 'Unsupported child candidate-set schema')
    candidates = selected['candidates']
    latest = {tile_id(c): c for c in candidates}
    require(len(latest) == len(candidates), 'Duplicate child tile coordinates')
    child_refs = {}
    for t, c in latest.items():
        child_refs[t] = file_ref(c['file'], c['sha256'])
        if c.get('generationRecord'):
            file_ref(c['generationRecord'])
    base = {}
    merged = {}
    union_masks = {}
    provenance = {}
    branches = []
    overlap_checks = []

    for name in BRANCHES:
        directory = ROOT/name
        bindings_path = next((f for f in [directory/'binding.json', directory/'bindings.json'] if f.is_file()), None)
        require(bindings_path, f'Branch not ready: {name}')
        binding = read_json(bindings_path)
        require(bindings_path.resolve() == Path(approvals[name]['bindings']).resolve(), f'Binding path differs from parent approval: {name}')
        review_link = binding.get('review')
        require(isinstance(review_link, dict) and review_link.get('file'), f'Missing bound review: {name}')
        review = read_json(review_link['file'], review_link.get('sha256'))
        context_path = directory/'context.png.generation.json'
        context = read_json(context_path)
        file_ref(context['file'], context['sha256'])
        native_ref = file_ref(directory/'native.png')
        native_gen = file_ref(directory/'native.png.generation.json')
        prompts = file_ref(directory/'prompt.txt')
        qa_items = binding.get('qaBoards') or binding.get('qa') or review.get('qaBoards') or review.get('qa')
        require(qa_items, f'No native QA boards: {name}')
        branch = {'name': name, 'binding': file_ref(bindings_path), 'review': file_ref(review_link['file']),
            'reviewScope': review.get('scope') or review.get('method'), 'recordedReviewResult': review.get('result') or review.get('verdict'),
            'context': context, 'qaItems': qa_items, 'nativeAI': native_ref, 'nativeGenerationRecord': native_gen,
            'prompt': prompts, 'sourceStatus': binding.get('status'), 'qaStatusDoesNotImplyFullEdgeAcceptance': True}
        branches.append(branch)
        require(binding.get('outputs'), f'No outputs: {name}')
        for output in binding['outputs']:
            t = tile_id(output)
            require(t in latest, f'Branch tile absent from latest child selection: {name}/{t}')
            require(not latest[t].get('partialFragment'), f'Cannot transplant into partial tile: {t}')
            old_path, old_sha = source_identity(output)
            old = rgb(old_path, old_sha)
            repaired = rgb(output['path'], output['sha256'])
            generation = file_ref(output.get('generationRecord') or (output['path']+'.generation.json'))
            changes = np.any(old != repaired, axis=2)
            box = changed_box(changes)
            x0, y0, x1, y1 = box
            halo = [max(0, x0-CONTEXT_MARGIN), max(0, y0-CONTEXT_MARGIN), min(4096, x1+CONTEXT_MARGIN), min(4096, y1+CONTEXT_MARGIN)]
            if t not in base:
                base[t] = rgb(latest[t]['file'], latest[t]['sha256'])
                merged[t] = base[t].copy()
                union_masks[t] = np.zeros((4096, 4096), bool)
                provenance[t] = []
            require(np.array_equal(crop(base[t], halo), crop(old, halo)),
                f'Latest child pixels conflict with {name}/{t} changed region +128px halo {halo}; stop, never overwrite.')
            overlap = changes & union_masks[t]
            count = int(overlap.sum())
            require(count == 0 or np.array_equal(merged[t][overlap], repaired[overlap]),
                f'Conflicting repair branches overlap on {t}: {name}')
            overlap_checks.append({'branch': name, 'tile': t, 'overlapPixels': count, 'overlapValuesIdentical': True})
            merged[t][changes] = repaired[changes]
            union_masks[t] |= changes
            provenance[t].append({'branch': name, 'source': file_ref(old_path, old_sha), 'branchOutput': file_ref(output['path'], output['sha256']),
                'branchGenerationRecord': generation, 'branchBinding': branch['binding'], 'branchQA': branch['review'],
                'branchQAScope': branch['reviewScope'], 'branchRecordedReviewResult': branch['recordedReviewResult'],
                'nativeAI': native_ref, 'nativeGenerationRecord': native_gen, 'prompt': prompts,
                'changedPixelCount': int(changes.sum()), 'changedBoundingBoxLTRB': box,
                'contextCheck': {'rectLTRB': halo, 'requestedPaddingPixels': CONTEXT_MARGIN, 'clippedAtTileBoundary': True,
                    'latestBaseMatchesBranchSourcePixelForPixel': True, 'fullFileSHAEqualityRequired': False},
                'operation': 'Copy only actual differing native RGB pixels; no resize, blending, registration or new AI generation during integration.'})
    require(set(merged) == EXPECTED_TILES, f'Expected five modified coordinates, got {sorted(merged)}')
    for t in merged:
        require(np.array_equal(merged[t][~union_masks[t]], base[t][~union_masks[t]]), f'Unexpected change outside repair union: {t}')

    # Reconstruct each final local context from the latest-base integrations.
    # QA migration is allowed only when the final crop equals its actually-viewed branch pixels.
    migrated_qa = []
    qa_images = []
    for branch in branches:
        context = branch['context']
        with Image.open(context['file']) as im:
            canvas = Image.new('RGB', im.size)
        for part in context['parts']:
            t = part['tile']
            require(t in merged, f'Unmapped branch context tile: {t}')
            canvas.paste(Image.fromarray(merged[t]).crop(part['cropLTRB']), part['pasteXY'])
        for qi, item in enumerate(branch['qaItems']):
            require(item.get('actuallyViewed') is True, f'QA not marked actually viewed: {item.get("file")}')
            qref = file_ref(item['file'], item.get('sha256'))
            with Image.open(item['file']) as board:
                board = board.convert('RGB')
                for mi, (context_box, board_box) in enumerate(qa_mappings(item, board.size)):
                    actual = canvas.crop(context_box)
                    reviewed = board.crop(board_box)
                    require(actual.size == reviewed.size and actual.tobytes() == reviewed.tobytes(),
                        f'Final QA differs from reviewed branch crop: {branch["name"]}/{qi}/{mi}; re-review required before integration.')
                    label = re.sub(r'[^a-zA-Z0-9_-]+', '-', item.get('name') or item.get('scope') or str(qi))
                    path = DEST/'qa'/branch['name']/f'{qi:02d}-{mi:02d}-{label}.png'
                    evidence = {'branch': branch['name'], 'file': str(path), 'contextLTRB': context_box,
                        'reviewedBranchBoard': qref, 'reviewedBranchBoardCropLTRB': board_box,
                        'branchReview': branch['review'], 'branchFinding': item.get('finding'), 'branchQAResult': item.get('result'),
                        'nativeScale': 1, 'finalCropEqualsActuallyViewedBranchPixels': True,
                        'newVisualReviewPerformedByIntegrationScript': False, 'acceptedScopeIsUnchanged': True}
                    migrated_qa.append(evidence)
                    qa_images.append((path, actual, evidence))

    def still_current():
        require(current_pointer() == selected_path, 'Child selected a newer checkpoint during integration; rerun against it.')
        for path, expected in fingerprints.items():
            require(digest(path) == expected, f'Input changed during integration: {path}')
    still_current()

    # All conflicts and QA checks happen before any output image is saved.
    DEST.mkdir(exist_ok=True)
    save_json(DEST/'integration-state.json', {'status': 'writing_outputs_not_a_selection', 'startedAt': snapshot_time})
    outputs = {}
    for t in sorted(merged):
        path = DEST/(t+'.png')
        Image.fromarray(merged[t]).save(path)
        changed = np.any(merged[t] != base[t], axis=2)
        output = {'tile': t, 'file': str(path), 'sha256': digest(path), 'width': 4096, 'height': 4096,
            'changedPixels': int(changed.sum()), 'changedBoundingBoxLTRB': changed_box(changed),
            'generationRecord': str(path)+'.generation.json', 'latestBase': child_refs[t], 'repairBranches': provenance[t]}
        record = {'file': str(path), 'sha256': output['sha256'], 'createdAt': datetime.now(timezone.utc).isoformat(),
            'width': 4096, 'height': 4096, 'format': 'PNG', 'derivedFrom': [dict(child_refs[t], generationRecord=latest[t].get('generationRecord'))]
                + [dict(v['branchOutput'], generationRecord=v['branchGenerationRecord']['file']) for v in provenance[t]],
            'latestChildCheckpoint': file_ref(selected_path), 'repairBranches': provenance[t],
            'operation': 'Exact differing-pixel transplant into latest child base after 128px context and overlap checks. No AI generation or resampling.',
            'changedPixelCount': output['changedPixels'], 'changedBoundingBoxLTRB': output['changedBoundingBoxLTRB'],
            'unchangedOutsideActualRepairUnionPixelEqualityVerified': True,
            'unchangedPixelCount': int((~changed).sum()), 'formalAccepted': False, 'clientVerified': False,
            'wholeCityComplete': False, 'parentReviewCandidateOnly': True, 'childSelectionModified': False}
        save_json(output['generationRecord'], record)
        outputs[t] = output
    for path, im, evidence in qa_images:
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path)
        evidence['sha256'] = digest(path)
        save_json(str(path)+'.generation.json', {'file': str(path), 'sha256': evidence['sha256'], 'createdAt': snapshot_time,
            'width': im.width, 'height': im.height, 'format': 'PNG',
            'derivedFrom': [{'file': o['file'], 'sha256': o['sha256'], 'generationRecord': o['generationRecord']} for o in outputs.values()],
            'operation': 'Native final output crop; pixel-identical to bound, previously visually reviewed branch crop.',
            'qaTransferEvidence': evidence, 'formalAccepted': False})
    still_current()
    transfer = {'observedAt': datetime.now(timezone.utc).isoformat(), 'result': 'all_final_crops_pixel_identical_to_bound_native_visual_QA',
        'parentReviewedScopes': file_ref(approvals_path),
        'latestChildCheckpoint': file_ref(selected_path), 'items': migrated_qa, 'overlapChecks': overlap_checks,
        'visualAcceptanceIsLimitedToPriorBranchScopes': True, 'newVisualReviewPerformed': False,
        'fullSharedEdgesAccepted': False, 'formalAccepted': False, 'wholeCityComplete': False}
    save_json(DEST/'qa-transfer.json', transfer)
    parent_selection = copy.deepcopy(selected)
    for item in parent_selection['candidates']:
        t = tile_id(item)
        if t in outputs:
            o = outputs[t]
            item['childEntryBeforeParentRepair'] = copy.deepcopy(item)
            item.update(file=o['file'], sha256=o['sha256'], generationRecord=o['generationRecord'], formalAccepted=False,
                parentRepairBranches=[v['branch'] for v in provenance[t]], parentReviewCandidateOnly=True,
                selectionRecord=str(DEST/'current-selection.json'))
            item.pop('selectionRecordSha256', None)
            item['inheritedLimitationsInterpretation'] = 'Original limitations are retained conservatively; only exact bound local QA scopes were migrated. No complete edge/tile acceptance.'
    parent_selection.update(createdAtUtc=datetime.now(timezone.utc).isoformat(),
        status='parent_review_candidate_collection_child_selection_unchanged', sourceChildCheckpoint=file_ref(selected_path),
        sourceChildProgressFile=str(PROGRESS), snapshotObservedAt=snapshot_time, parentModifiedCoordinates=sorted(outputs),
        parentModified4KCount=len(outputs), additionalUniqueCoordinateCount=0,
        completeCandidateCount=sum(not x.get('partialFragment', False) for x in parent_selection['candidates']),
        partialCandidateCount=sum(bool(x.get('partialFragment', False)) for x in parent_selection['candidates']),
        partialCandidatesPreservedVerbatim=True, qaTransfer=file_ref(DEST/'qa-transfer.json'),
        formalAccepted=False, wholeCityComplete=False, clientVerified=False, childSelectionModified=False)
    # Publish this parent-only pointer last. No child mutation, no branch cleanup.
    save_json(DEST/'current-selection.json', parent_selection)
    save_json(DEST/'integration-state.json', {'status': 'parent_review_candidate_ready', 'completedAt': datetime.now(timezone.utc).isoformat(),
        'selection': str(DEST/'current-selection.json'), 'selectionSha256': digest(DEST/'current-selection.json'),
        'outputs': outputs, 'sourceCheckpointStayedStable': True, 'branchImagesDeleted': False})
    print(json.dumps({'status': 'parent_review_candidate_ready', 'selection': str(DEST/'current-selection.json'),
        'modifiedTiles': sorted(outputs), 'qaTransferCropCount': len(migrated_qa), 'formalAccepted': False}, ensure_ascii=True))

if __name__ == '__main__':
    if (ROOT/'retirement.json').exists():
        print('RETIRED: branch image dependencies were removed after verified integration. Use rebase_current.py and migration-manifest.json; do not regenerate retired inputs.', file=sys.stderr)
        sys.exit(2)
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'integration_stopped', 'reason': str(exc), 'childSelectionModified': False}, ensure_ascii=True), file=sys.stderr)
        sys.exit(2)
