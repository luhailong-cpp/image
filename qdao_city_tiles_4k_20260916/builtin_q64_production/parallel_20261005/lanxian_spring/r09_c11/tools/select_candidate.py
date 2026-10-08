"""Select a visually reviewed r09_c11 candidate and prepare (never execute) cleanup.

Call only after the parent explicitly chooses --candidate. The review must bind
the exact output hashes and declare scopedPass=true. Selection validates actual
files; it does not turn assembly metrics into visual acceptance. --validate-only
performs read-only checks. Cleanup is a separate, SHA-guarded PowerShell step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

TILE = Path(__file__).resolve().parents[1]
BASE = TILE.parent
EXPECTED = {f'r{r:02d}_c{c:02d}' for r in range(1, 5) for c in range(1, 5)}
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff'}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def within(path, root=TILE):
    path = Path(path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path outside allowed directory: {path}')
    return path


def info(path):
    path = Path(path).resolve()
    return {'file': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def pinned(record, root=None):
    path = Path(record['file']).resolve()
    if root is not None:
        within(path, root)
    if not path.is_file() or sha(path) != record['sha256']:
        raise ValueError(f'Missing or changed pinned file: {path}')
    return path


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def parameters_no_resampling(assembly):
    p = assembly.get('parameters', {})
    declared = p.get('resampling') is False or p.get('resizeOperations') == 0
    if not declared:
        raise ValueError('Assembly lacks explicit no-resampling evidence')
    for key in ('upscale', 'warp', 'blur'):
        if p.get(key, False) is not False:
            raise ValueError(f'Unsupported assembly operation: {key}')
    if p.get('blurOperations', 0) != 0:
        raise ValueError('Assembly uses blur')


def validate(candidate, review_path):
    candidate = within(candidate)
    assembly_path = within(candidate / 'assembly.json')
    assembly = read(assembly_path)
    if assembly.get('tile') != 'r09_c11':
        raise ValueError('Wrong tile')
    parameters_no_resampling(assembly)
    sources = assembly.get('sources', [])
    if len(sources) != 16 or {x['patchId'] for x in sources} != EXPECTED:
        raise ValueError('Exactly sixteen unique native source patches are required')
    verified = []
    for source in sources:
        path = pinned(source, TILE)
        with Image.open(path) as im:
            if im.size != (1254, 1254) or im.format != 'PNG':
                raise ValueError(f'Wrong native source dimensions/format: {path}')
        if source.get('resized') is not False:
            raise ValueError(f'Native source must explicitly say resized=false: {path}')
        record_path = pinned(source['generationRecord'], TILE)
        record = read(record_path)
        if record.get('sha256') != sha(path) or (record.get('width'), record.get('height')) != (1254, 1254):
            raise ValueError(f'Native source and generation record disagree: {path}')
        if not record.get('prompt') or not record.get('references') or not record.get('configSnapshot'):
            raise ValueError(f'Incomplete native prompt/reference/config evidence: {record_path}')
        verified.append({'patchId': source['patchId'], 'native': info(path),
                         'generationRecord': info(record_path),
                         'actualModel': record.get('actualModel'),
                         'actualQuality': record.get('actualQuality'), 'nativePixels': [1254, 1254]})
    core = pinned(assembly['outputs']['core'], candidate)
    ext = pinned(assembly['outputs']['extended'], candidate)
    with Image.open(core) as im:
        if im.size != (4096, 4096):
            raise ValueError('Core must be 4096 square')
        ca = np.asarray(im.convert('RGB'))
    with Image.open(ext) as im:
        if im.size != (4326, 4326):
            raise ValueError('Extended must be 4326 square')
        ea = np.asarray(im.convert('RGB'))
    if not np.array_equal(ca, ea[115:4211, 115:4211]):
        raise ValueError('Core is not the exact halo crop')
    review_path = within(review_path)
    review = read(review_path)
    if review.get('scopedPass') is not True:
        raise ValueError('Postreview must explicitly declare scopedPass=true')
    if review.get('formalAccepted', False) or review.get('runtimePublished', False):
        raise ValueError('Scoped review must not claim formal/runtime acceptance')
    outputs = review.get('reviewedOutputs', {})
    for name, path in [('core', core), ('extended', ext)]:
        if name not in outputs or pinned(outputs[name]) != path:
            raise ValueError(f'Review does not bind the selected {name} output')
    return assembly, review, verified, core, ext, assembly_path, review_path


def technical_references(assembly):
    retained = set()
    # Masks are technical replay evidence, not retained art-source backups.
    for value in strings(assembly):
        p = Path(value)
        if p.suffix.lower() == '.png' and ('mask' in value.lower() or 'alpha' in p.name.lower()):
            try:
                p = within(p)
            except ValueError:
                continue
            if p.is_file():
                retained.add(p)
    return retained


def external_live_references():
    """Conservatively protect r09_c11 images named by another active tile's text.

    Historical source-chain paths inside this tile are provenance only after
    selected export. Any reference outside this tile is retained for parent review.
    """
    protected = {}
    for record in BASE.rglob('*.json'):
        if record.is_relative_to(TILE):
            continue
        try:
            data = read(record)
        except (OSError, ValueError):
            continue
        for value in strings(data):
            if len(value) > 1500 or '\n' in value:
                continue
            p = Path(value)
            if p.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            try:
                p = p.resolve()
                if p.is_relative_to(TILE) and p.is_file():
                    protected.setdefault(p, []).append(str(record))
            except (OSError, ValueError):
                pass
    return protected


def prepare_cleanup(selected, assembly, review, manifest_path):
    protected = external_live_references()
    technical = technical_references(assembly)
    # A reviewer can preserve a unique in-process source explicitly; absence does
    # not authorize deletion until parent checks the concrete proposed plan.
    explicit = set()
    for value in review.get('retainCurrentImageFiles', []):
        p = within(value)
        if not p.is_file():
            raise ValueError(f'Explicit current image is missing: {p}')
        explicit.add(p)
    keep, remove = [], []
    for path in sorted(TILE.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        path = within(path)
        entry = info(path)
        if path.is_relative_to(selected):
            entry['reason'] = 'selected game output or required preview'
        elif path in technical:
            entry['reason'] = 'selected assembly technical mask'
        elif path in explicit:
            entry['reason'] = 'review explicitly retains current/unique in-process image'
        elif path in protected:
            entry['reason'] = 'referenced by another active tile/root record; retain pending reference migration'
            entry['referencedBy'] = sorted(set(protected[path]))
        else:
            entry['reason'] = 'superseded source/guide/QA/candidate raster after verified selected export; all text provenance retained'
            remove.append(entry)
            continue
        keep.append(entry)
    plan = {'schemaVersion': 1, 'createdAtUtc': now(), 'tile': 'r09_c11',
            'status': 'proposed_not_executed_parent_must_review_unique_inprocess_and_current_references',
            'parentApprovedForExecution': False, 'allowedAbsoluteDirectory': str(TILE),
            'selectedManifest': info(manifest_path), 'preserve': keep, 'delete': remove,
            'deleteCount': len(remove), 'preserveImageCount': len(keep),
            'textRecordsNeverDeleted': True, 'imagesOutsideTileNeverDeleted': True,
            'note': 'No file has been deleted by plan creation. Preserve all JSON/TXT/MD/scripts/NPZ, including original model/quality/prompt/source evidence.'}
    plan_path = TILE / 'cleanup-plan.json'
    write(plan_path, plan)
    ps = r'''# Run only after the parent reviews this exact plan and sets parentApprovedForExecution=true.
$ErrorActionPreference = 'Stop'
$planPath = Join-Path $PSScriptRoot 'cleanup-plan.json'
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ($plan.parentApprovedForExecution -ne $true) { throw 'Cleanup plan has not been reviewed for execution.' }
$scope = (Resolve-Path -LiteralPath $plan.allowedAbsoluteDirectory).Path.TrimEnd('\')
$expected = (Resolve-Path -LiteralPath $PSScriptRoot).Path.TrimEnd('\')
if ($scope -cne $expected) { throw 'Cleanup scope must be this exact tile folder.' }
$prefix = $scope + '\'
$manifest = $plan.selectedManifest
if ((Get-FileHash -LiteralPath $manifest.file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $manifest.sha256) { throw 'Selected manifest changed.' }
foreach ($item in $plan.preserve) {
    $resolved = (Resolve-Path -LiteralPath $item.file).Path
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Preserved path escaped tile.' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Retained image changed: $resolved" }
}
$targets = @()
foreach ($item in $plan.delete) {
    $resolved = (Resolve-Path -LiteralPath $item.file).Path
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Delete path escaped tile.' }
    if ((Get-Item -LiteralPath $resolved).PSIsContainer) { throw 'Directories cannot be deleted.' }
    if ([IO.Path]::GetExtension($resolved).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.tif','.tiff')) { throw 'Only explicit raster files can be deleted.' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Delete target changed: $resolved" }
    $targets += [pscustomobject]@{file=$resolved;sha256=$item.sha256}
}
# All targets were resolved, bounded and hash checked before the first removal.
$removed = @()
foreach ($item in $targets) {
    Remove-Item -LiteralPath $item.file
    if (Test-Path -LiteralPath $item.file) { throw "Delete failed: $($item.file)" }
    $removed += $item
}
foreach ($item in $plan.preserve) {
    if ((Get-FileHash -LiteralPath $item.file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Post-cleanup retained image changed: $($item.file)" }
}
[pscustomobject]@{schemaVersion=1;completedAtUtc=[DateTime]::UtcNow.ToString('o');status='executed';deletedCount=$removed.Count;deleted=$removed;preservedCount=$plan.preserve.Count;allPreservedHashesVerified=$true;textRecordsUntouched=$true;outsideTileUntouched=$true;planSha256=(Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'cleanup-executed.json') -Encoding utf8
'''
    (TILE / 'cleanup-selected.ps1').write_text(ps, encoding='utf-8')
    return plan_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--review', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    candidate = within(args.candidate)
    review_path = args.review or candidate / 'postreview.json'
    assembly, review, sources, core, ext, assembly_path, review_path = validate(candidate, review_path)
    if args.validate_only:
        print(json.dumps({'validated': True, 'selectionPerformed': False, 'nativeCount': 16,
                          'coreMatchesExtended': True, 'candidate': str(candidate)}))
        return
    selected = TILE / 'selected'
    manifest_path = selected / 'delivery.manifest.json'
    if selected.exists():
        raise ValueError('Selected directory already exists; do not overwrite a live selection')
    selected.mkdir()
    shutil.copy2(core, selected / 'core4096.png')
    shutil.copy2(ext, selected / 'extended4326.png')
    with Image.open(core) as im:
        im.resize((1254, 1254), Image.Resampling.LANCZOS).save(selected / 'preview1254.png')
    evidence = selected / 'evidence'
    evidence.mkdir()
    copies = {}
    for name, path in [('assembly.json', assembly_path), ('postreview.json', review_path),
                       ('navigation-contract.json', TILE / 'navigation-contract.json')]:
        shutil.copy2(path, evidence / name)
        copies[name] = info(evidence / name)
    native_records = []
    for source in sources:
        path = Path(source['generationRecord']['file'])
        target = evidence / f"{source['patchId']}.png.generation.json"
        shutil.copy2(path, target)
        native_records.append(info(target))
    outputs = {key: dict(info(selected / file), pixels=size) for key, file, size in [
        ('core', 'core4096.png', [4096, 4096]), ('extended', 'extended4326.png', [4326, 4326]),
        ('preview', 'preview1254.png', [1254, 1254])]}
    for key, data in outputs.items():
        write(data['file'] + '.generation.json', {
            'schemaVersion': 1, 'createdAtUtc': now(), 'tile': 'r09_c11',
            'file': data['file'], 'sha256': data['sha256'], 'pixels': data['pixels'],
            'operation': 'downscaled preview of selected core' if key == 'preview' else 'byte-identical copy of reviewed native-pixel assembly',
            'newAIGeneration': False, 'upscale': False, 'actualModel': None, 'actualQuality': None,
            'actualModelQualityExplanation': 'Derived asset; actual per-image model/quality evidence is in sixteen preserved native generation records.',
            'sourceAssembly': copies['assembly.json'], 'sourceNativeRecords': native_records,
            'sourceOutput': assembly['outputs']['core' if key == 'preview' else key]})
    manifest = {'schemaVersion': 1, 'createdAtUtc': now(), 'appearance': 'lanxian_spring', 'tile': 'r09_c11',
                'status': 'qualified_complete_4k_candidate_pending_remaining_adjacencies_navigation_and_formal_acceptance',
                'qualifiedComplete4KCandidate': True, 'formalAccepted': False, 'navigationAccepted': False,
                'clientValidated': False, 'runtimePublished': False, 'wholeCityComplete': False,
                'geometry': {'wholeCityPixels': [65536, 65536], 'grid': [16, 16], 'corePixels': [4096, 4096],
                             'extendedPixels': [4326, 4326], 'haloPerSide': 115, 'coreInExtendedLTRB': [115, 115, 4211, 4211],
                             'wholeCityCoreLTRB': [40960, 32768, 45056, 36864],
                             'crossAppearancePairVerificationPending': True},
                'outputs': outputs, 'sourceChain': {'assembly': copies['assembly.json'], 'nativeSources': sources,
                                                   'nativeRecordsPreserved': native_records},
                'processingDeclaration': {'noUpscaleInGameImages': True, 'resamplingInGameImages': False,
                                          'coreMatchesExtended': True, 'nativeCount': 16, 'nativeSize': [1254, 1254],
                                          'assemblyParameters': assembly['parameters'], 'previewOnlyDownscaled': True},
                'qa': {'postreview': copies['postreview.json'], 'scopedPass': True,
                       'scope': review.get('scope', review.get('reviewScope')), 'remaining': review.get('remaining', [])},
                'navigationContract': copies['navigation-contract.json'],
                'retention': {'status': 'cleanup_plan_pending_parent_review', 'allTextProvenanceRetained': True,
                              'historicalPathsAreProvenanceNotRequiredLiveImages': True}}
    write(manifest_path, manifest)
    plan_path = prepare_cleanup(selected, assembly, review, manifest_path)
    print(json.dumps({'selectedManifest': str(manifest_path), 'coreSha256': outputs['core']['sha256'],
                      'extendedSha256': outputs['extended']['sha256'], 'cleanupPlan': str(plan_path),
                      'cleanupExecuted': False, 'formalAccepted': False}))


if __name__ == '__main__':
    main()
