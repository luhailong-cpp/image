"""Run the existing local prepare/ingest with byte backups and change detection."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
import sys

HERE = Path(__file__).resolve().parent
TILE = HERE.parent
spec = importlib.util.spec_from_file_location('city_tile_existing', TILE / 'make_tile.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
history = HERE / 'byte-history' / stamp
history.mkdir(parents=True, exist_ok=False)
plan_path = TILE / 'plan.json'
initial_plan = plan_path.read_bytes()
(history / 'plan.before.json').write_bytes(initial_plan)

def checked_write(path, value):
    path = Path(path)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if path == plan_path:
        if path.read_bytes() != initial_plan:
            raise RuntimeError('Concurrent plan change; refusing overwrite')
        tmp = history / 'plan.new.json'
        tmp.write_bytes(data)
        if path.read_bytes() != initial_plan:
            raise RuntimeError('Concurrent plan change before replace')
        os.replace(tmp, path)
        (history / 'update.json').write_text(json.dumps({
            'beforeSha256': hashlib.sha256(initial_plan).hexdigest(),
            'afterSha256': hashlib.sha256(data).hexdigest(),
            'operation': sys.argv[1:],
            'atUtc': datetime.now(timezone.utc).isoformat()
        }, indent=2), encoding='utf-8')
    else:
        with path.open('xb') as stream:
            stream.write(data)

module.write = checked_write
if sys.argv[1] == 'prepare':
    module.prepare(sys.argv[2])
elif sys.argv[1] == 'ingest':
    module.ingest(*sys.argv[2:])
else:
    raise SystemExit('prepare PATCH or ingest PATCH SOURCE RECEIPT')
