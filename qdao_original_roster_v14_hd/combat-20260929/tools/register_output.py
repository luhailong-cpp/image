"""Copy an unchanged built-in output and record its truthful provenance."""
import argparse
import hashlib
import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--source', required=True)
p.add_argument('--character', required=True)
p.add_argument('--label', required=True)
p.add_argument('--prompt', required=True)
p.add_argument('--references', nargs='+', required=True)
p.add_argument('--review', default='pending')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
repo = root.parents[1]
src = Path(a.source).resolve()
dst = root / 'characters' / a.character / 'staging' / (a.label + '.png')
if dst.exists():
    raise SystemExit('Refuse to overwrite existing output: ' + str(dst))
raw = src.read_bytes()
if raw[:8] != b'\x89PNG\r\n\x1a\n':
    raise SystemExit('Output is not a PNG')
width, height = struct.unpack('>II', raw[16:24])
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
record = {
    'file': dst.relative_to(root).as_posix(),
    'sha256': hashlib.sha256(raw).hexdigest(),
    'generatedAt': datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).isoformat(),
    'generatedAtEvidence': 'Local output mtime; tool did not supply generation timestamp.',
    'recordedAt': datetime.now(timezone.utc).isoformat(),
    'width': width, 'height': height, 'format': 'PNG', 'pngColorType': raw[25],
    'tool': 'image_gen.imagegen', 'route': 'builtin',
    'configSnapshot': json.loads((repo / 'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'officialRecheckDate': datetime.now(timezone.utc).date().isoformat(),
    'submittedParameters': {'model': None, 'quality': None, 'transparent_background': True,
                            'referenced_image_paths': a.references},
    'actualModel': None, 'actualQuality': None,
    'unverifiedReason': 'Host managed; tool returned image_url and output_hint, without model or quality.',
    'evidence': {'toolReturnedPath': str(src), 'returnedFields': ['image_url', 'output_hint'],
                 'workspaceCopyShaMatchesSource': hashlib.sha256(dst.read_bytes()).hexdigest() == hashlib.sha256(raw).hexdigest()},
    'prompt': a.prompt,
    'references': [{'path': ref, 'role': 'identity, pose continuity or approved painting style; exact roles in prompt'} for ref in a.references],
    'source': {'kind': 'generated', 'generated_image_path': str(src)},
    'review': {'status': a.review},
}
receipt = root / 'characters' / a.character / 'provenance/receipts' / (a.label + '.json')
receipt.parent.mkdir(parents=True, exist_ok=True)
receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'image': str(dst), 'receipt': str(receipt), 'width': width, 'height': height}, ensure_ascii=False))
