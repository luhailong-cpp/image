"""Verify r09_c09 completely, then copy its selected outputs unchanged.

This script is intentionally separate from cleanup. Running it creates selection
artifacts; importing or parsing it does not. It refuses to overwrite a selection.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
TILE = OUT.parent
ROOT = TILE.parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(path):
    return str(Path(path).resolve()).casefold()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def ref(path):
    path = Path(path)
    return {'file': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def write(path, data):
    path = Path(path).resolve()
    require(path.parent == OUT.resolve(), 'Selection metadata must stay inside selected')
    require(not path.exists(), 'Refuse to overwrite: ' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify_hash(path, expected):
    actual = sha(path)
    require(actual == expected, 'Hash mismatch: ' + str(path))
    return actual


def pixels(path, expected=None):
    with Image.open(path) as im:
        require(im.format == 'PNG' and im.mode == 'RGB', 'Expected RGB PNG: ' + str(path))
        if expected is not None:
            require(im.size == tuple(expected), 'Pixel dimensions differ: ' + str(path))
        return np.array(im)


def verify_references(references):
    result = []
    for item in references:
        path = Path(item['path'])
        verify_hash(path, item['sha256'])
        with Image.open(path) as im:
            dims = list(im.size)
        expected = item.get('pixels', [item.get('width'), item.get('height')])
        require(dims == expected, 'Reference dimensions mismatch: ' + str(path))
        require(bool(item.get('role')), 'Reference role missing')
        result.append({**item, 'pixels': dims, 'hashVerifiedAtSelection': True})
    return result


def verify_generation(gp, expected_source=None, native_job_required=False, explicit_job=None):
    """Read the actual receipt from evidence, independent of its folder/name."""
    g = load(gp)
    require(g['tool'] == 'image_gen.imagegen' and g['route'] == 'builtin', 'Unexpected generation route')
    require(g['actualModel'] is None and g['actualQuality'] is None, 'Actual identity unexpectedly changed')
    submitted = g['submittedParameters']
    require(submitted['model'] is None and submitted['quality'] is None, 'Host-managed selectors must remain null')
    source = Path(g['file'])
    verify_hash(source, g['sha256'])
    pixels(source, (1254, 1254))
    if expected_source is not None:
        require(norm(source) == norm(expected_source['file']) and g['sha256'] == expected_source['sha256'], 'Assembly source/generation identity mismatch')
        verify_hash(gp, expected_source['generationRecordSha256'])
    evidence = g['evidence']
    receipt_path = Path(evidence['toolResultPath'])
    verify_hash(receipt_path, evidence['toolResultSha256'])
    receipt = load(receipt_path)
    tool_source = Path(evidence['sourceOutputPath'])
    verify_hash(tool_source, evidence['sourceOutputSha256'])
    require(evidence['sourceOutputSha256'] == g['sha256'], 'Ingested source is not the tool output')
    require(norm(receipt['sourceOutputPath']) == norm(tool_source), 'Receipt output path differs')
    pixels(tool_source, (1254, 1254))
    if 'sourceOutputSha256' in receipt:
        verify_hash(tool_source, receipt['sourceOutputSha256'])
    require(receipt['generatedAt'] == g['generatedAt'], 'Recorded generation time differs')
    require(receipt.get('actualModel') is None and receipt.get('actualQuality') is None, 'Receipt actual identity unexpectedly changed')
    actual_prompt = receipt['prompt']
    require(actual_prompt == submitted['prompt'], 'Submitted/receipt prompt mismatch')
    prompt_file = g.get('promptFile')
    if prompt_file is None and native_job_required:
        prompt_file = g['prompt']
    prompt_record = {'actualPrompt': actual_prompt, 'actualPromptUtf8Sha256': hashlib.sha256(actual_prompt.encode('utf-8')).hexdigest()}
    if prompt_file:
        verify_hash(prompt_file, g['promptSha256'])
        require(Path(prompt_file).read_text(encoding='utf-8-sig').rstrip('\r\n') == actual_prompt.rstrip('\r\n'), 'Prompt file differs from actual receipt')
        prompt_record['fileEvidence'] = ref(prompt_file)
    else:
        require(g['prompt'] == actual_prompt, 'Inline prompt differs')
        prompt_record['fileEvidence'] = None
        prompt_record['storage'] = 'Exact inline prompt in immutable receipt and generation record'
    references = verify_references(g['references'])
    reference_paths = [norm(x['path']) for x in references]
    require(reference_paths == [norm(x['path']) for x in receipt['references']], 'Receipt references differ')
    require(reference_paths == [norm(x) for x in submitted['referenced_image_paths']], 'Submitted references differ')
    require([x['role'] for x in references] == [x['role'] for x in receipt['references']], 'Reference roles differ')
    job_record = None
    job_path = g.get('sourceJob', explicit_job)
    if native_job_required:
        require(job_path is not None, 'Native source job missing')
        verify_hash(job_path, g['sourceJobSha256'])
    if job_path is not None:
        job = load(job_path)
        require(job['prompt'] == actual_prompt, 'Job prompt differs from actual receipt')
        require(norm(job['toolResultPath']) == norm(receipt_path), 'Job/receipt path differs')
        require(norm(job['sourceOutputPath']) == norm(tool_source), 'Job/source path differs')
        require(job['expectedSha256'] == g['sha256'], 'Job output hash differs')
        require([norm(x['path']) for x in job['references']] == reference_paths, 'Job reference list differs')
        require(job['configSnapshot'] == g['configSnapshot'], 'Job configuration snapshot differs')
        job_record = {**ref(job_path), 'expectedHashInGenerationRecord': g.get('sourceJobSha256'), 'semanticIdentityVerified': True}
    return {
        'generationRecord': ref(gp), 'generation': g, 'source': ref(source),
        'nativePixels': [1254, 1254], 'toolSource': ref(tool_source),
        'actualReceipt': ref(receipt_path), 'promptEvidence': prompt_record,
        'sourceJobEvidence': job_record, 'references': references,
        'actualModel': None, 'actualQuality': None,
        'allAvailableHashesDimensionsAndReceiptIdentityVerified': True,
    }


def verify_qa(assembly):
    root_path = TILE / 'qa/root-final-review.json'
    root = load(root_path)
    require(root['tile'] == TILE.name and root['requiresRepair'] is False, 'Root review not ready')
    for flag in ['formalAccepted', 'clientValidated', 'wholeCityComplete']:
        require(root[flag] is False, 'Root status must remain pending: ' + flag)
    for key, role in [('sourceCore', 'core'), ('sourceExtended', 'extended')]:
        verify_hash(root[key]['file'], root[key]['sha256'])
        require(norm(root[key]['file']) == norm(assembly['outputs'][role]['file']) and root[key]['sha256'] == assembly['outputs'][role]['sha256'], 'Root review source mismatch')
    coverage = root['coverage']
    require(coverage['exportedTotal'] == 93 and coverage['coveredScopes'] == 93 and coverage['allExportedScopesCoveredByActualViewsAndByteIdentity'] is True, 'Root coverage incomplete')
    overview = root['overview']
    require(overview['actuallyViewed'] is True, 'Root overview not viewed')
    verify_hash(overview['file'], overview['sha256'])
    reports_by_path = {norm(x['file']): x for x in root['reports']}
    for record in root['reports']:
        verify_hash(record['file'], record['sha256'])
    exports = {}
    export_records = []
    for name, expected_count in [('qa.manifest.json', 53), ('guide-bands/manifest.json', 32), ('external-north.manifest.json', 4), ('external-east.manifest.json', 4)]:
        path = TILE / 'qa' / name
        manifest = load(path)
        require(manifest['source']['sha256'] == assembly['outputs']['core']['sha256'], 'QA export source mismatch')
        require(len(manifest['checks']) == expected_count, 'QA export count differs: ' + name)
        export_records.append(ref(path))
        for item in manifest['checks']:
            key = norm(item['file'])
            require(key not in exports, 'Duplicate exported scope')
            verify_hash(item['file'], item['sha256'])
            exports[key] = item
    covered = {}
    report_records = []
    for name, item_key, expected_count in [('final-internal-review.json', 'checks', 49), ('final-neighbor-review.json', 'items', 44)]:
        path = TILE / 'qa' / name
        require(norm(path) in reports_by_path, 'Root omits final report: ' + name)
        report = load(path)
        require(report['requiresRepair'] is False and len(report[item_key]) == expected_count, 'Final report not ready')
        report_records.append(ref(path))
        for item in report[item_key]:
            key = norm(item['file'])
            require(key not in covered and key in exports, 'Duplicate or unexpected reviewed scope')
            require(item['requiresRepair'] is False and item['sha256'] == exports[key]['sha256'], 'Scope requires repair or differs from export')
            arr = pixels(item['file'])
            rgb_hash = hashlib.sha256(arr.tobytes()).hexdigest()
            require(rgb_hash == item.get('decodedRgbSha256', item.get('rawRGBSha256')), 'Reviewed decoded pixels differ')
            if item_key == 'checks':
                require(item['finalCropEqualsCoreBox'] is True, 'Internal crop source unverified')
                if not item['newlyActuallyViewed']:
                    inherited = item['inheritance']
                    require(inherited['earlierActuallyViewed'] and inherited['decodedRgbExactlyEqual'] and inherited['sameTargetCoreBox'], 'Internal inheritance incomplete')
                    verify_hash(inherited['reviewFile'], inherited['reviewFileSha256'])
                    verify_hash(inherited['earlierCropFile'], inherited['earlierCropSha256'])
                    require(hashlib.sha256(pixels(inherited['earlierCropFile']).tobytes()).hexdigest() == rgb_hash, 'Inherited internal crop differs')
            else:
                require(item['sourcePixelsReconstructedAndVerified'] is True, 'Neighbor scope reconstruction unverified')
                require(item['actuallyViewedByThisReviewer'] or item['inheritedEvidence'] is not None, 'Neighbor visual evidence missing')
            covered[key] = {'file': item['file'], 'sha256': item['sha256'], 'decodedRgbSha256': rgb_hash, 'report': str(path)}
    require(len(exports) == len(covered) == 93 and set(exports) == set(covered), 'Final scope set does not equal four export manifests')
    additional = root['additionalRootChecks']
    require(len(additional) == 1, 'Expected the additional northeast junction review')
    junction_review = additional[0]
    require(junction_review['kind'] == 'northeast_four_tile_junction' and junction_review['actuallyViewed'] is True and junction_review['requiresRepair'] is False, 'Additional junction review not ready')
    for key in ['image', 'manifest']:
        verify_hash(junction_review[key]['file'], junction_review[key]['sha256'])
    junction_manifest = load(junction_review['manifest']['file'])
    require(junction_manifest['output'] == junction_review['image'], 'Junction output identity differs')
    junction = pixels(junction_review['image']['file'], (1024, 1024))
    reconstructed = np.empty_like(junction)
    junction_coverage = np.zeros(junction.shape[:2], np.uint8)
    require(len(junction_manifest['pixelMappings']) == 4, 'Expected four corner mappings')
    for mapping in junction_manifest['pixelMappings']:
        verify_hash(mapping['file'], mapping['sha256'])
        src = pixels(mapping['file'], (4096, 4096))
        x0, y0, x1, y1 = mapping['sourceBoxXYXY']
        dx, dy = mapping['destinationXY']
        crop = src[y0:y1, x0:x1]
        require(crop.shape == (512, 512, 3), 'Expected a native 512-square corner')
        require(hashlib.sha256(crop.tobytes()).hexdigest() == mapping['cropRawRGBSha256'], 'Junction corner pixels differ')
        require(dx in [0, 512] and dy in [0, 512], 'Junction destination differs')
        reconstructed[dy:dy + 512, dx:dx + 512] = crop
        junction_coverage[dy:dy + 512, dx:dx + 512] += 1
    require(np.all(junction_coverage == 1) and np.array_equal(junction, reconstructed), 'Junction is not exact four-source reconstruction')
    return root, {'rootFinalReview': ref(root_path), 'teamReports': report_records, 'exportManifests': export_records, 'rootCoverage': coverage, 'exactScopeFileSetVerified': True, 'exportedScopes': 93, 'coveredScopeEvidence': list(covered.values()), 'overview': overview, 'additionalRootChecks': additional, 'northeastFourTileJunctionReconstructedExactly': True, 'totalScopesIncludingRootJunction': 94, 'noNewRepairRequired': True}


def external_refs():
    found = {}
    def walk(value, record):
        if isinstance(value, dict):
            for child in value.values():
                walk(child, record)
        elif isinstance(value, list):
            for child in value:
                walk(child, record)
        elif isinstance(value, str) and len(value) < 400 and value.lower().endswith('.png') and '\n' not in value:
            path = Path(value)
            if path.is_absolute() and path.resolve().is_relative_to(TILE.resolve()):
                found.setdefault(str(path.resolve()), []).append(str(record))
    for sibling in ROOT.iterdir():
        if not sibling.is_dir() or sibling.resolve() == TILE.resolve():
            continue
        for record in sibling.rglob('*.json'):
            try:
                walk(load(record), record)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    return [{'file': path, 'exists': Path(path).exists(), 'sha256': sha(path) if Path(path).exists() else None, 'referencingRecords': sorted(set(records)), 'retention': 'Conservative external reference; review before any separate cleanup'} for path, records in sorted(found.items())]


def main():
    require(TILE.name == 'r09_c09', 'This script is specific to r09_c09')
    names = ['core4096.png', 'extended4326.png', 'preview1024.png', 'delivery.manifest.json', 'selection-proof.json', 'native-call-audit.json', 'external-consumer-audit.json']
    require(all(not (OUT / name).exists() for name in names), 'Refuse to overwrite any prior selected output')
    now = datetime.now(timezone.utc).isoformat()
    assembly_path = TILE / 'candidate/assembly.manifest.json'
    a = load(assembly_path)
    for role, dims in [('core', (4096, 4096)), ('extended', (4326, 4326)), ('preview', (1024, 1024))]:
        item = a['outputs'][role]
        require(Path(item['file']).resolve().parent == (TILE / 'candidate').resolve(), 'Candidate path outside tile')
        verify_hash(item['file'], item['sha256'])
        pixels(item['file'], dims)
    core = pixels(a['outputs']['core']['file'])
    extended = pixels(a['outputs']['extended']['file'])
    require(a['geometry']['coreInExtended'] == [115, 115, 4211, 4211], 'Unexpected halo geometry')
    require(np.array_equal(core, extended[115:4211, 115:4211]), 'Core is not exact extended center crop')
    mappings = {item['cell']: item for item in a['pixelMappings']}
    expected_cells = {f'r{row:02d}_c{col:02d}' for row in range(1, 5) for col in range(1, 5)}
    require(len(a['pixelMappings']) == len(a['derivedFrom']) == 16 and set(mappings) == expected_cells, 'Expected sixteen unique source mappings')
    reconstructed_core = np.empty_like(core)
    reconstructed_extended = np.empty_like(extended)
    core_coverage = np.zeros(core.shape[:2], np.uint8)
    extended_coverage = np.zeros(extended.shape[:2], np.uint8)
    native = []
    native_by_cell = {}
    for source in a['derivedFrom']:
        cell = source['cell']
        require(cell not in native_by_cell and cell in expected_cells, 'Duplicate/unexpected native source')
        evidence = verify_generation(source['generationRecord'], source, native_job_required=True)
        native_by_cell[cell] = evidence
        native.append({**source, 'identityAndEvidence': evidence, 'sourcePixelsCopiedExactly': True, 'retention': 'Selected game output supersedes this native PNG after separately authorized cleanup; complete text provenance retained'})
        im = pixels(source['file'], (1254, 1254))
        m = mappings[cell]
        for reconstructed, coverage, source_key, dest_key in [(reconstructed_core, core_coverage, 'coreSourceBox', 'coreDestinationXY'), (reconstructed_extended, extended_coverage, 'sourceBox', 'extendedDestinationXY')]:
            x0, y0, x1, y1 = m[source_key]
            dx, dy = m[dest_key]
            require(0 <= x0 < x1 <= 1254 and 0 <= y0 < y1 <= 1254, 'Invalid native source box')
            require(0 <= dx and 0 <= dy and dx + x1 - x0 <= reconstructed.shape[1] and dy + y1 - y0 <= reconstructed.shape[0], 'Invalid destination box')
            reconstructed[dy:dy + y1 - y0, dx:dx + x1 - x0] = im[y0:y1, x0:x1]
            coverage[dy:dy + y1 - y0, dx:dx + x1 - x0] += 1
    require(np.all(core_coverage == 1) and np.all(extended_coverage == 1), 'Every core/extended pixel must be covered exactly once')
    require(np.array_equal(core, reconstructed_core) and np.array_equal(extended, reconstructed_extended), 'Assembled candidate pixels differ from native mappings')
    rejected_paths = sorted((TILE / 'jobs').glob('r??_c??.attempt*.generation.json'))
    require([p.name for p in rejected_paths] == ['r04_c04.attempt01.generation.json'], 'Unexpected native rejection count')
    rejected = verify_generation(rejected_paths[0])
    rejected_g = rejected['generation']
    require(rejected_g['inSelectedAssembly'] is False and rejected_g['status'] == 'rejected_not_ingested', 'Rejected status differs')
    edit_child = native_by_cell['r04_c04']
    require(any(r['sha256'] == rejected['source']['sha256'] and norm(r['path']) == norm(rejected['toolSource']['file']) for r in edit_child['references']), 'Rejected native edit-ancestor chain missing')
    used = rejected_g['usedAsEditTargetFor']
    verify_hash(used['file'], used['sha256'])
    verify_hash(used['generationRecord'], used['generationRecordSha256'])
    require(used['sha256'] == edit_child['source']['sha256'], 'Native edit child differs')
    config_evidence = rejected_g['configSnapshotEvidence']
    verify_hash(config_evidence['file'], config_evidence['sha256'])
    selected_hashes = {entry['source']['sha256'] for entry in native_by_cell.values()}
    receipt_paths = {norm(entry['actualReceipt']['file']) for entry in native_by_cell.values()}
    require(len(selected_hashes) == len(receipt_paths) == 16 and rejected['source']['sha256'] not in selected_hashes, 'Expected seventeen distinct recorded native output calls')
    selected_regional = verify_generation(TILE / 'regional/generation.json', explicit_job=TILE / 'jobs/regional.json')
    rejected_regional = verify_generation(TILE / 'jobs/regional.attempt01.generation.json')
    require(selected_regional['generation']['guideOnly'] and rejected_regional['generation']['guideOnly'], 'Regional art must remain guide-only')
    require(any(r['sha256'] == rejected_regional['source']['sha256'] and norm(r['path']) == norm(rejected_regional['toolSource']['file']) for r in selected_regional['references']), 'Regional edit-ancestor chain missing')
    require(selected_regional['source']['sha256'] != rejected_regional['source']['sha256'], 'Regional calls must be distinct')
    require(not ({selected_regional['source']['sha256'], rejected_regional['source']['sha256']} & (selected_hashes | {rejected['source']['sha256']})), 'Native/regional calls overlap')
    context_path = TILE / 'regional/context.json'
    context = load(context_path)
    require(context['tile'] == TILE.name and context['pixelRectXYWH'] == [32768, 32768, 4096, 4096], 'Tile origin differs')
    neighbor_context = {}
    for key in ['northCore', 'northExtended', 'eastCore', 'eastExtended']:
        record = context[key]
        verify_hash(record['file'], record['sha256'])
        pixels(record['file'], record['pixels'])
        neighbor_context[key] = record
    root_review, qa_summary = verify_qa(a)
    consumers = external_refs()
    regional_review_path = TILE / 'regional/visual-review.json'
    regional_review = ref(regional_review_path)
    # No output is written until all source, reconstruction and QA gates above pass.
    edit_chain = {'native': {'rejectedAncestor': rejected, 'selectedChildCell': 'r04_c04', 'selectedChildGeneration': edit_child['generationRecord'], 'directAssemblyUseOfRejected': False, 'ancestorUsePreserved': True}, 'regional': {'rejectedAncestor': rejected_regional, 'selectedChildGeneration': selected_regional['generationRecord'], 'directProductionPixelUse': False, 'ancestorUsePreserved': True}}
    audit = {'createdAtUtc': now, 'nativeBuiltinCallsWithDistinctRecordedOutput': 17, 'selectedNativeImages': 16, 'rejectedNativeOutputs': 1, 'rejectedNativeCell': 'r04_c04', 'selectedReceiptEvidence': [entry['actualReceipt'] for entry in native_by_cell.values()], 'rejected': [rejected], 'rejectedOutputIsSelectedEditAncestor': True, 'regionalCallsSeparately': 2, 'regionalSelected': 1, 'regionalRejected': 1, 'regionalRejectedOutputIsSelectedGuideEditAncestor': True, 'allActualModelQualityNull': True, 'countMethod': 'Sixteen selected actual receipt/output identities plus one distinct rejected native output, with its selected edit child. Two distinct regional calls counted separately. Receipt paths are taken from each generation evidence, not guessed from jobs filenames.'}
    proof = {'createdAtUtc': now, 'sourceAssembly': ref(assembly_path), 'coreExactlyCenterCrop': True, 'all16CoreMappingsExactlyNativePixels': True, 'all16ExtendedMappingsExactlyNativePixels': True, 'coreCoverageEveryPixelExactlyOnce': True, 'extendedCoverageEveryPixelExactlyOnce': True, 'nativeDimensions': [1254, 1254], 'productionAssemblyResampling': 'none', 'postAssemblyFlowApplied': False, 'postAssemblyToneApplied': False, 'postAssemblyNativeAIPatchesApplied': False, 'selectedCopyByteIdenticalToCandidate': True, 'allSourcePromptJobReferenceReceiptHashesVerified': True, 'rootReviewHashVerified': True, 'allReferencedTeamReviewHashesVerified': True, 'coveredScopesEqualFourExportManifestFileSets': True, 'coreLeft230RawRGBSha256': hashlib.sha256(core[:, :230].tobytes()).hexdigest(), 'extendedLeft230RawRGBSha256': hashlib.sha256(extended[:, :230].tobytes()).hexdigest()}
    outputs = {}
    for role, name in [('core', 'core4096.png'), ('extended', 'extended4326.png'), ('preview', 'preview1024.png')]:
        source = Path(a['outputs'][role]['file'])
        dest = OUT / name
        require(not dest.exists(), 'Destination appeared during checks: ' + str(dest))
        verify_hash(source, a['outputs'][role]['sha256'])
        shutil.copyfile(source, dest)
        verify_hash(dest, a['outputs'][role]['sha256'])
        with Image.open(dest) as im:
            dims = list(im.size)
        outputs[role] = {**ref(dest), 'pixels': dims, 'productionPixels': role != 'preview'}
    write(OUT / 'native-call-audit.json', audit)
    write(OUT / 'selection-proof.json', proof)
    write(OUT / 'external-consumer-audit.json', {'checkedAtUtc': now, 'scanScope': 'JSON records under sibling directories; exact absolute PNG references into this tile', 'references': consumers, 'futureConsumerPolicy': 'Use selected core4096.png and selected extended4326.png only for later neighbor generation'})
    manifest = {
        'schemaVersion': 1, 'createdAtUtc': now, 'tile': TILE.name,
        'status': 'qualified_complete_4k_candidate_pending_remaining_adjacent_edges_and_formal_acceptance',
        'qualifiedComplete4KCandidate': True, 'formalAccepted': False, 'clientValidated': False,
        'wholeCityComplete': False, 'runtimePublished': False,
        'geometry': a['geometry'], 'pixelRectXYWH': context['pixelRectXYWH'], 'worldRect': context['worldRect'],
        'outputs': outputs, 'selectionProof': ref(OUT / 'selection-proof.json'),
        'sourceChain': {'assembly': ref(assembly_path), 'rawCore': ref(a['outputs']['core']['file']), 'rawExtended': ref(a['outputs']['extended']['file']), 'nativeSources': native, 'nativeCallAudit': ref(OUT / 'native-call-audit.json'), 'regionalSeparate': {'selected': selected_regional, 'rejected': rejected_regional, 'review': regional_review, 'context': ref(context_path), 'role': 'Separate composition guide only; not enlarged into final production pixels', 'actualCallCount': 2}, 'editAncestorChains': edit_chain, 'northAndEastSelectedContext': neighbor_context, 'additionalRootJunctionEvidence': root_review['additionalRootChecks']},
        'nativeCounts': {'selected': 16, 'rejected': 1, 'actualNativeCalls': 17, 'regionalCallsSeparately': 2, 'regionalSelected': 1, 'regionalRejected': 1, 'countAudit': ref(OUT / 'native-call-audit.json')},
        'processingDeclaration': {'nativeRoute': 'builtin image_gen.imagegen', 'configuredTarget': {k: native[0]['identityAndEvidence']['generation']['configSnapshot'][k] for k in ['model', 'quality']}, 'submittedModel': None, 'submittedQuality': None, 'actualModel': None, 'actualQuality': None, 'modelQualityEvidence': 'The host-managed tool disclosed neither explicit model/quality selectors nor verified returned identity; configured targets do not establish actual backend identity.', 'nativeSourceCreation': 'Sixteen selected 1254-square outputs plus one rejected native output used as the edit target of selected r04_c04. Two separate regional calls include a rejected guide used as the edit target of the selected regional guide.', 'assembly': 'Exact integer crop/paste from sixteen selected native outputs; independent reconstruction proves every core and extended pixel has exactly one native source mapping.', 'noNativeEnlargement': True, 'productionScaling': False, 'postAssemblyFlow': False, 'postAssemblyToneCorrection': False, 'postAssemblyAIPatch': False, 'blur': False, 'feather': False, 'registration': False, 'productionResampling': 'none', 'preview': '1024 LANCZOS overview only, not production pixels or pixel-level QA evidence', 'selection': 'Byte-identical copy of candidate PNG files'},
        'qaSummary': {**qa_summary, 'scopeLimit': 'Ninety-three standard exported scopes covered by actual visual evidence or verified exact-pixel inheritance, plus the separately viewed northeast four-tile junction and root overview. No claim of formal whole-city acceptance.'},
        'futureEastReferenceForR09C08': {'core': outputs['core'], 'extended': outputs['extended'], 'coreLeft230RawRGBSha256': proof['coreLeft230RawRGBSha256'], 'extendedLeft230RawRGBSha256': proof['extendedLeft230RawRGBSha256'], 'useSelectedOnly': True, 'westNeighborSeamNotYetValidated': True},
        'remaining': [{'kind': 'minor_material_variation', 'details': root_review.get('minorObservations', [])}, {'kind': 'adjacent_edges', 'edges': ['west', 'south'], 'description': 'West and south external neighboring joins remain unverified. Own-edge inspection does not accept those future joins.'}, {'kind': 'other_four_tile_corner_junctions', 'description': 'The northeast four-tile junction was actually viewed and required no repair in that native scope. Other junctions involving unfinished neighbors remain unverified; this is not formal every-pixel acceptance.'}, {'kind': 'formal_client_whole_city', 'description': 'Formal art acceptance, client loading/navigation, runtime publication and whole-city completion remain false.'}],
        'retention': {'state': 'selected_verified_cleanup_pending', 'keep': 'Selected game outputs, current external consumers, required technical files and all non-PNG provenance records', 'cleanupPerformedByThisScript': False, 'deleteScopeForSeparateCleanup': 'Only superseded PNG files inside the resolved r09_c09 tree; no cross-tile or host-generated_images deletion', 'externalConsumerAudit': ref(OUT / 'external-consumer-audit.json'), 'historicalReferencePolicy': 'Removed PNG paths remain historical provenance with original hashes in a per-file cleanup ledger; preserve all generation, rejected-attempt, actual-receipt, prompt, mapping and review text records.'},
    }
    write(OUT / 'delivery.manifest.json', manifest)
    print(json.dumps({'outputs': outputs, 'deliveryManifest': ref(OUT / 'delivery.manifest.json'), 'nativeCalls': 17, 'selectedNative': 16, 'rejectedNativeEditAncestors': 1, 'regionalSeparateCalls': 2, 'qaScopes': 93, 'cleanupPerformed': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
