"""Retain builtin native output and record the actual path-reference invocation."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib, json, shutil, sys

P = Path(__file__).resolve().parent
ident, source, prompt_path, reference_path = sys.argv[1:5]
src, prompt, ref = map(Path, (source, prompt_path, reference_path))
dst = P / 'native' / f'{ident}.png'
assert not dst.exists(), dst
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
with Image.open(src) as im:
    im.load()
    assert im.size == (1254, 1254), im.size
    alpha = im.getextrema()[3] if im.mode == 'RGBA' else (255, 255)
    assert alpha == (255, 255)
plan_id = ident.split('.v')[0]
e = next(e for e in json.loads((P / 'plan.json').read_text())['entries'] if e['id'] == plan_id)
shutil.copyfile(src, dst)
guide = P / 'guides' / f'{plan_id}.png'
record = {
    'id': ident, 'route': 'builtin_image_gen', 'requestedProduct': 'ChatGPT Images 2.5',
    'backendModelVerified': False,
    'backendSelection': 'host_managed_no_model_selector_exposed',
    'actualNativePixels': [1254, 1254], 'sourceOutputPath': str(src),
    'sourceOutputSha256': sha(src), 'outputFile': str(dst), 'outputSha256': sha(dst),
    'promptFile': str(prompt), 'promptSha256': sha(prompt),
    'guidePath': str(guide), 'guideSha256': sha(guide),
    'submittedImages': [{'path': str(ref), 'sha256': sha(ref), 'pixels': [1254, 1254]}],
    'selectedTargetImageOneBased': 1,
    'toolCall': {'name': 'image_gen.imagegen', 'referenced_image_paths': [str(ref)],
                 'prompt': prompt.read_text(encoding='utf-8').strip()},
    'sourceBoxLTRB': e['box'], 'plannedRoiLTRB': e['roi'],
    'finalArtUpscaled': False, 'resizedAfterGeneration': False, 'alphaExtrema': alpha,
    'createdAtUtc': datetime.now(timezone.utc).isoformat(),
    'visualQa': {'status': 'pending_placement_and_roi_reconnection'}
}
dst.with_suffix('.record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'id': ident, 'path': str(dst), 'sha256': sha(dst)}))
