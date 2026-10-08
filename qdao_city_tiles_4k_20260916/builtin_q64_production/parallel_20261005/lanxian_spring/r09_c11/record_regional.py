"""Persist the host-generated regional guide and scoped visual review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
from PIL import Image

OUT = Path(__file__).resolve().parent
REGION = OUT / 'regional'
SOURCE = Path('C:/Users/luyua/.codex/generated_images/01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1/exec-fd16e1e7-ce59-43f7-a204-541356c013a1.png')
DEST = REGION / 'shared-region1254.png'
NOW = datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p, d):
    p = Path(p)
    assert p.resolve().is_relative_to(OUT)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

request = read(OUT / 'regional-request-pending.json')
actual_receipt_path = OUT / 'regional-tool-result.json'
actual_receipt = read(actual_receipt_path)
tool_started = datetime.strptime(actual_receipt['started']['current_time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc).isoformat()
tool_completed = datetime.strptime(actual_receipt['completed']['current_time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc).isoformat()
assert len(request['references']) == 3
for ref in request['references']:
    assert sha(ref['file']) == ref['sha256']
prompt_file = Path(request['promptFile'])
assert sha(prompt_file) == request['promptSha256']
assert SOURCE.exists()
with Image.open(SOURCE) as im:
    assert im.size == (1254, 1254)
    fmt, mode = im.format, im.mode
    assert 'A' not in im.mode or im.getchannel('A').getextrema() == (255, 255)
REGION.mkdir(parents=True, exist_ok=True)
if DEST.exists():
    assert sha(DEST) == sha(SOURCE), 'Refuse to overwrite a different existing generation.'
else:
    shutil.copy2(SOURCE, DEST)
assert sha(DEST) == sha(SOURCE)
file_timestamp = datetime.fromtimestamp(SOURCE.stat().st_mtime, timezone.utc).isoformat()
prompt = prompt_file.read_text(encoding='utf-8')
frozen_prompt = REGION / 'prompt.txt'
frozen_prompt.write_text(prompt, encoding='utf-8')
receipt = {
    'schemaVersion': 1, 'recordedAtUtc': NOW,
    'tool': 'image_gen.imagegen', 'route': 'builtin',
    'returnedKeys': ['image_url', 'output_hint'],
    'toolOutputFile': SOURCE.as_posix(), 'toolOutputFileSha256': sha(SOURCE),
    'toolOutputFileLastWriteTimeUtc': file_timestamp,
    'timestampEvidence': 'Filesystem mtime of the returned host-generated file; not an exact tool start/end timestamp.',
    'actualModel': None, 'actualQuality': None,
    'actualModelQualityEvidence': 'No model or quality disclosed in returned tool keys; host managed.',
    'recordingBasis': 'Parent agent saved actual pre/post tool clock readings and output_hint in the referenced receipt; file was independently opened and hashed by recording agent.',
    'actualToolReceipt': actual_receipt_path.as_posix(), 'actualToolReceiptSha256': sha(actual_receipt_path),
    'observedToolStartUtc': tool_started, 'observedToolCompletionUtc': tool_completed,
    'clockEvidence': 'Clock readings immediately around the tool call; service-internal timings were not exposed.',
    'rawImageUrlOmitted': 'Do not persist base64 image data in text receipt; selected binary output is preserved byte-identically.',
}
write(REGION / 'tool-receipt.json', receipt)
record = {
    'schemaVersion': 1, 'file': DEST.as_posix(), 'sha256': sha(DEST),
    'generatedAt': tool_completed,
    'generatedAtEvidence': 'Post-call UTC clock reading in regional-tool-result.json; returned file mtime is recorded separately.',
    'observedToolStartUtc': tool_started, 'observedToolCompletionUtc': tool_completed,
    'recordedAtUtc': NOW, 'width': 1254, 'height': 1254, 'format': fmt, 'mode': mode,
    'tool': 'image_gen.imagegen', 'route': 'builtin',
    'configSnapshot': request['configSnapshot'],
    'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False,
        'referenced_image_paths': [r['file'] for r in request['references']]},
    'parameterAvailability': 'The built-in tool has no model or quality selector; configuration is the target only.',
    'actualModel': None, 'actualQuality': None,
    'unverifiedReason': '宿主管理，工具未披露实际模型和质量；无可核实元数据。',
    'evidence': {'toolReceipt': actual_receipt_path.as_posix(),
        'toolReceiptSha256': sha(actual_receipt_path),
        'fileVerificationReceipt': (REGION / 'tool-receipt.json').as_posix(),
        'fileVerificationReceiptSha256': sha(REGION / 'tool-receipt.json'),
        'returnedKeys': ['image_url', 'output_hint'], 'actualReturnedPath': SOURCE.as_posix()},
    'prompt': frozen_prompt.as_posix(), 'promptSha256': sha(frozen_prompt),
    'promptText': prompt, 'references': request['references'],
    'originalReturnedFile': {'file': SOURCE.as_posix(), 'sha256': sha(SOURCE), 'retainedReadOnly': True},
    'operation': 'Byte-identical copy of built-in generation into workspace; no resampling, cropping or image editing.',
    'purpose': 'Single canonical neutral day/spring structural regional guide for r09_c11',
    'nativePixels': [1254, 1254], 'productionPixelsAllowed': False,
    'futureNativeAssemblyRequired': 'Sixteen distinct1254-square native detail pieces at1024 stride; no guide enlargement in final pixels.',
    'formalAccepted': False, 'runtimePublished': False,
    'crossAppearancePairVerificationPending': True,
}
write(Path(str(DEST) + '.generation.json'), record)
review = {
    'schemaVersion': 1, 'reviewedAtUtc': NOW, 'tile': 'r09_c11',
    'image': {'file': DEST.as_posix(), 'sha256': sha(DEST), 'viewedAtOriginalPixels': True},
    'references': request['references'],
    'status': 'guide_qualified_for_native_detail_production_only',
    'guideQualified': True, 'nativeArtAccepted': False, 'finalTileAccepted': False,
    'formalAccepted': False, 'externalWestSeamAccepted': False,
    'newArtworkNavigationAccepted': False,
    'observations': [
        'The main pale arched stone bridge continues from the west and descends toward the lower-right stair/landing, matching the mapped crop camera and broad occupied bridge footprint.',
        'Both balustrades and square capped posts remain; cream deck stays open. No extra bridge, building, festival object, lantern, character or text was introduced.',
        'Turquoise river remains above/right of the bridge and below/left beneath the arch; the upper willow trunk/rock, upper leafy trunk and right clipped canopy retain their guide regions.',
        'The x230-in-4326 paste boundary was not converted into a vertical scene border. At guide scale the west entering column, foreground rails and bridge arch have plausible continuous trajectories.',
        'The lower clipped shrubs are reconstructed from soft guide envelopes. Leaf detail, paving joints and fine stone bevels are newly resolved, so the regional result must not be treated as exact native boundary pixels.',
        'The exact230-pixel west strip remains authoritative for native pieces. Regional guide-scale continuity does not replace original-pixel overlap registration or adjacent seam QA.',
    ],
    'structuralConflictObservedAtGuideScale': False,
    'limits': ['Soft original map cannot establish exact native post positions or navigation alignment.',
        'No16-piece native production or4096 tile exists from this guide yet.',
        'The reviewed west source retained a small horizontal foliage transition near extended y3187; native seam work must inspect that area.',
        'A future day counterpart must reuse the chosen canonical native structure rather than regenerate an independent layout.'],
    'nativeProductionMayStart': True,
    'beforeNativeSelection': ['Preserve the frozen native west band for each first-column piece.',
        'Review every actual1254 output and all overlaps; reject any added/moved railing, post, stair, bank or tree envelope.',
        'Keep guide upscaling confined to guidance and document provenance per native piece.'],
}
write(REGION / 'structural-review.json', review)
write(REGION / 'selection.json', {
    'tile': 'r09_c11', 'selectedAtUtc': NOW, 'guide': DEST.as_posix(), 'sha256': sha(DEST),
    'generationRecord': str(DEST) + '.generation.json',
    'structuralReview': (REGION / 'structural-review.json').as_posix(),
    'purpose': 'canonical shared neutral structural guide only',
    'guideQualified': True, 'productionPixelsAllowed': False, 'formalAccepted': False,
})
print(json.dumps({'path': DEST.as_posix(), 'sha256': sha(DEST), 'generatedAtFileTime': file_timestamp,
    'guideQualified': True, 'nativeProductionMayStart': True, 'formalAccepted': False}, ensure_ascii=False))
