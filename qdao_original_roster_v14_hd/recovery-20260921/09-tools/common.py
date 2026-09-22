"""Small immutable-evidence helpers for character 09 only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
PACKAGE = RECOVERY.parent
IMAGE_ROOT = PACKAGE.parent
GENERATION = RECOVERY / '09-generation'
DELIVERY = RECOVERY / '09-delivery-preview'
CHARACTER = '09_bamboo_archer_girl'
DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def immutable_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, 'Existing immutable file differs: ' + str(path))
        return
    with path.open('xb') as stream:
        stream.write(data)


def immutable_json(path, value):
    immutable_bytes(path, json_bytes(value))


def inside(path, root, label):
    path = Path(path).resolve()
    require(path.is_relative_to(root.resolve()), label + ' must remain inside ' + str(root))
    return path


def claim_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError('Another export owns this direction lock: ' + str(path)) from exc
    os.write(handle, str(os.getpid()).encode('ascii'))
    os.close(handle)
    return path
