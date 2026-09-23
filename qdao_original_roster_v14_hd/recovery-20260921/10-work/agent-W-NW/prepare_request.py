"""Save exact W/NW built-in request evidence from JSON stdin, before submission."""
import sys, json, pathlib, datetime, hashlib
q = json.load(sys.stdin)
attempt = q.pop('attempt')
assert attempt.startswith(('W', 'NW')) and '/' not in attempt and '\\' not in attempt
root = pathlib.Path(__file__).resolve().parents[4]
dest = root / 'qdao_original_roster_v14_hd/recovery-20260921/10-generation' / attempt
dest.mkdir(exist_ok=False)
q['status'] = 'prepared_for_submission'
q['startedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
q['tool'] = 'image_gen__imagegen'
q['configSnapshot'] = json.loads((root / 'config/image-generation.json').read_text(encoding='utf-8-sig'))
q['submittedParameters'] = {'model': None, 'quality': None}
q['reference_bindings_at_start'] = [{'path': p, 'sha256': hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()} for p in q['actual_request']['referenced_image_paths']]
(dest / 'request.json').write_bytes(json.dumps(q, ensure_ascii=False, indent=2).encode('utf-8'))
(dest / 'prompt.txt').write_bytes(q['actual_request']['prompt'].encode('utf-8'))
print(dest)
