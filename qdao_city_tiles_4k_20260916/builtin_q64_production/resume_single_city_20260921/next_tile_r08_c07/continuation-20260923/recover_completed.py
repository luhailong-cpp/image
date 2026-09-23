"""Recover only the two verified historical host completion events."""
from pathlib import Path
from datetime import datetime, timezone
import base64
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
TILE = HERE.parent
SESSION = Path(r'C:\Users\Administrator\.codex\archived_sessions\rollout-2026-09-21T08-30-14-01a0c3f2-0915-75f2-9d1c-88ff542fd455.jsonl')
NOW = datetime.now(timezone.utc).isoformat()
STAMP = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
ROOT = HERE / ('recovery-' + STAMP)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, data):
    with path.open('xb') as stream:
        stream.write(data)

def save_json(path, value):
    save(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

source_bytes = SESSION.read_bytes()
source_sha = sha(source_bytes)
lines = source_bytes.splitlines(keepends=True)
plan_bytes = (TILE / 'plan.json').read_bytes()
plan = json.loads(plan_bytes)
pending = []
for ident, number in [('r02_c02', 1032), ('r01_c01', 1033)]:
    event_bytes = lines[number - 1]
    event = json.loads(event_bytes)
    payload = event['payload']
    item = payload['item']
    assert event['type'] == 'event_msg'
    assert payload['type'] == 'item_completed'
    assert item['kind'] == 'image_gen.generation'
    assert item['status'] == 'completed' and item['failure'] is None
    assert payload['thread_id'] == '01a0c3f2-0915-75f2-9d1c-88ff542fd455'
    request_path = TILE / 'requests' / (ident + '.request.json')
    request_bytes = request_path.read_bytes()
    request = json.loads(request_bytes)
    assert request['prompt'] == item['revisedPrompt']
    patch = next(x for x in plan['patches'] if x['id'] == ident)
    assert patch['submittedImages'] == request['referenced_image_paths']
    assert patch.get('selectedStem', ident) == ident
    image_path = Path(item['savedPath'])
    image_bytes = image_path.read_bytes()
    assert image_bytes == base64.b64decode(item['result'])
    for suffix in ['.png', '.record.json', '.tool-response.json']:
        assert not (TILE / 'native' / (ident + suffix)).exists(), 'Refuse overwrite'
    refs = [{'path': p, 'sha256': sha(Path(p).read_bytes())} for p in request['referenced_image_paths']]
    pending.append((ident, number, event_bytes, event, request_bytes, request_path, image_path, image_bytes, refs))

ROOT.mkdir(exist_ok=False)
save(ROOT / 'plan.before-recovery.json', plan_bytes)
save_json(ROOT / 'config-target-at-original-preparation.json', plan['requestedConfigSnapshot'])
summary = {'schemaVersion': 1, 'recoveredAt': NOW, 'sourceSession': str(SESSION), 'sourceSessionSha256': source_sha,
           'sourceSessionBytes': len(source_bytes), 'evidenceType': 'exact_raw_archived_host_item_completed_events',
           'newGenerationCalls': 0, 'actualModel': None, 'actualQuality': None, 'generatedAt': None,
           'images': []}
for ident, number, event_bytes, event, request_bytes, request_path, image_path, image_bytes, refs in pending:
    event_path = ROOT / (ident + '.raw-completion-event.jsonl')
    saved_request = ROOT / (ident + '.request.json')
    save(event_path, event_bytes)
    save(saved_request, request_bytes)
    payload, item = event['payload'], event['payload']['item']
    evidence = {'sourceSession': str(SESSION), 'sourceSessionSha256': source_sha, 'sourceSessionLineOneBased': number,
                'rawCompletionEvent': str(event_path), 'rawCompletionEventSha256': sha(event_bytes),
                'request': str(request_path), 'requestSha256': sha(request_bytes), 'requestSnapshot': str(saved_request),
                'requestPromptEqualsRevisedPrompt': True, 'references': refs,
                'eventDecodedPngEqualsSavedPathBytes': True, 'sourcePng': str(image_path), 'sourcePngSha256': sha(image_bytes)}
    response_path = TILE / 'native' / (ident + '.tool-response.json')
    response = {'schemaVersion': 1, 'recoveredFrom': 'archived_host_item_completed_event', 'recoveredAt': NOW,
                'observedCompletionAt': event['timestamp'], 'hostEventTimestamp': event['timestamp'],
                'hostStartedAtMs': payload.get('started_at_ms'), 'hostCompletedAtMs': payload.get('completed_at_ms'),
                'timestampSemantics': 'Original host completion event time; recoveredAt is the later recovery observation time; server generation time undisclosed',
                'generatedAt': None, 'actualModel': None, 'actualQuality': None,
                'hostCompletion': {k: item[k] for k in ['type', 'kind', 'id', 'status', 'revisedPrompt', 'transparentBackground', 'failure', 'savedPath']},
                'imageResult': 'Exact base64 is preserved in raw completion event; decoded PNG matched savedPath bytes',
                'outputHintAvailable': False, 'evidence': evidence}
    save_json(response_path, response)
    subprocess.run([sys.executable, str(HERE / 'safe_patch.py'), 'ingest', ident, str(image_path), str(response_path)], check=True)
    copied = (TILE / 'native' / (ident + '.png')).read_bytes()
    assert copied == image_bytes
    summary['images'].append({'id': ident, 'file': str(TILE / 'native' / (ident + '.png')), 'sha256': sha(copied),
                              'record': str(TILE / 'native' / (ident + '.record.json')), 'response': str(response_path),
                              'hostEventTimestamp': event['timestamp'], 'recoveredAt': NOW, 'evidence': evidence})

summary['planBeforeSha256'] = sha(plan_bytes)
summary['planAfterSha256'] = sha((TILE / 'plan.json').read_bytes())
save_json(ROOT / 'recovery-summary.json', summary)
print(json.dumps({'recoveryDirectory': str(ROOT), 'recovered': [x['id'] for x in summary['images']], 'planSha256': summary['planAfterSha256']}))
