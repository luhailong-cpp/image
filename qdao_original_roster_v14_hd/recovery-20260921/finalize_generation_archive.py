"""Bind this recovery's real builtin results without changing historic receipts."""
from pathlib import Path
import hashlib, importlib.util, json
from datetime import datetime, timezone
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location('archive_provenance', ROOT/'tools/inspect_image_provenance.py')
provenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provenance)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

rows = []
for folder in sorted((HERE/'04-generation').iterdir()):
    if not folder.is_dir():
        continue
    receipt_path, raw = folder/'generation-receipt.json', folder/'raw.png'
    if not receipt_path.is_file() or not raw.is_file():
        continue
    receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    prompt_text = receipt['actual_request']['prompt']
    prompt = folder/'prompt.txt'
    if not prompt.exists():
        prompt.write_bytes(prompt_text.encode('utf-8'))
    assert prompt.read_bytes().decode('utf-8-sig') == prompt_text, folder
    meta = folder/'provenance.json'
    if not meta.exists():
        meta.write_text(json.dumps(provenance.inspect_image(raw), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    original = Path(receipt['original_generated_file'])
    assert original.is_file() and sha(original) == sha(raw), folder
    with Image.open(raw) as im:
        size, mode = list(im.size), im.mode
    assert min(size) >= 1024, folder
    rows.append({'batch': folder.name, 'raw': str(raw), 'native_size': size, 'mode': mode,
                 'raw_sha256': sha(raw), 'prompt_sha256': sha(prompt), 'receipt_sha256': sha(receipt_path),
                 'original_generated_file_verified': True,
                 'generation_calls': receipt['generation_calls'], 'paid_api_calls': receipt['paid_api_calls'],
                 'model_actual': receipt.get('actual_model', 'host-managed-unverified'),
                 'acceptance': 'see per-batch and selected-snapshot visual review; existence is not approval'})
result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'character': '04_mountain_guardian_boy',
          'completed_builtin_results': len(rows), 'paid_api_calls': sum(r['paid_api_calls'] for r in rows),
          'source_rows': rows, 'not_a_completion_or_approval_certificate': True}
(HERE/'04-generation/archive-index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'completed_builtin_results': len(rows), 'paid_api_calls': result['paid_api_calls']}))
