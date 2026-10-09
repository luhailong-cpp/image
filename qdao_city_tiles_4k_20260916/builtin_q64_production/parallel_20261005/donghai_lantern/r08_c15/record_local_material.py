from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
from PIL import Image

T = Path(__file__).resolve().parent
B = T / 'repairs/local-material-finish'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def record(name, raw_path):
    assert name in ('wood-tone', 'blue-bevel', 'roof-tone')
    d = B / name; native = d / 'native.png'; assert not native.exists()
    prepared = read(d / 'prepared.json'); request = read(d / 'request.json')
    assert sha(d / 'request.json') == prepared['requestSha256']
    for ref in prepared['references']: assert sha(ref['file']) == ref['sha256']
    raw = Path(raw_path); h = sha(raw)
    with Image.open(raw) as im:
        im.load(); assert im.size == (1254, 1254) and im.mode in ('RGB', 'RGBA')
        if im.mode == 'RGBA': assert im.getchannel('A').getextrema() == (255, 255)
    shutil.copyfile(raw, native); assert sha(native) == h
    r = {'file': str(native), 'sha256': h, 'generatedAtUtc': datetime.now(timezone.utc).isoformat(),
         'tool': 'image_gen.imagegen', 'route': 'builtin', 'width': 1254, 'height': 1254,
         'configSnapshot': read(T.parent / 'batch-model-check.json')['configSnapshot'],
         'submittedParameters': {'model': None, 'quality': None, **request},
         'actualModel': None, 'actualQuality': None,
         'unverifiedReason': 'Host-managed builtin path exposes no model/quality selectors or return metadata.',
         'evidence': {'toolResultSourcePath': str(raw), 'toolResultSha256': h},
         'references': prepared['references'], 'prompt': str(d / 'prompt.txt'),
         'promptSha256': sha(d / 'prompt.txt'), 'requestFile': str(d / 'request.json'),
         'requestSha256': sha(d / 'request.json'), 'source': prepared['source'],
         'daySource': prepared['daySource'], 'cropXYXY': prepared['cropXYXY'],
         'authorizedROI': prepared['authorizedROI'], 'roiInNative': prepared['roiInNative'],
         'sourceBytesPreserved': True, 'resizedAfterGeneration': False, 'finalArtUpscaled': False,
         'role': 'local material repair native, not integrated', 'formalAccepted': False}
    Path(str(native) + '.generation.json').write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'file': str(native), 'sha256': h, 'authorizedROI': r['authorizedROI']}
if __name__ == '__main__': print(json.dumps(record(sys.argv[1], sys.argv[2]), ensure_ascii=False))
