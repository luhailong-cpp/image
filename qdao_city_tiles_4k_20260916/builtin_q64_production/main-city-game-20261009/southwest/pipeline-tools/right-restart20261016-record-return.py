import base64, hashlib, json, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

B = Path(__file__).resolve().parent.parent
payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')) if Path(sys.argv[1]).is_file() else json.loads(base64.b64decode(sys.argv[1]))
tile, patch, attempt = payload['tile'], payload['patch'], payload['attempt']
assert re.fullmatch(r'r(?:09|1[0-6])_c0[78]', tile)
assert re.fullmatch(r'p0[1-4]_0[1-4]', patch)
assert re.fullmatch(r'[A-Za-z0-9_-]+', attempt)
t = B / tile
w = t / 'pipeline'
request = Path(payload['request'])
req = json.loads(request.read_text(encoding='utf-8-sig'))
assert req['tile'] == tile and req['coordinates']['id'] == patch
hint = payload['outputHint']
paths = re.findall(r'[A-Za-z]:[\\/][^:\r\n]*?\.png', hint)
existing = [Path(p) for p in paths if Path(p).is_file()]
assert existing, 'No actual native PNG located in returned output_hint'
src = existing[-1]
digest = hashlib.sha256(src.read_bytes()).hexdigest()
dest = w / 'returned-originals' / f'{patch}.{attempt}.png'
receipt = w / 'receipts' / f'{patch}.{attempt}.receipt.json'
assert not dest.exists() and not receipt.exists()
dest.parent.mkdir(parents=True, exist_ok=True)
receipt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest() == digest
with Image.open(dest) as im:
 im.load()
 size, fmt, mode = list(im.size), im.format, im.mode
 opaque = mode != 'RGBA' or im.getextrema()[3] == (255,255)
record = {**payload, 'sourceOutputPath': str(src), 'sourceOutputSha256': digest,
 'savedUnmodifiedOriginal': str(dest), 'savedUnmodifiedOriginalSha256': digest,
 'nativePixels': size, 'format': fmt, 'mode': mode, 'opaque': opaque,
 'tool': 'image_gen.imagegen', 'status': 'returned_image',
 'recordedAtUtc': datetime.now(timezone.utc).isoformat(),
 'actualModel': None, 'actualQuality': None, 'paidApiUsed': False,
 'resizedAfterGeneration': False, 'internalAccepted': False, 'formalAccepted': False,
 'visualDisposition': 'pending_actual_visual_inspection',
 'requestSha256': hashlib.sha256(request.read_bytes()).hexdigest()}
receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':str(dest),'receipt':str(receipt),'sha256':digest,'size':size},ensure_ascii=False))
