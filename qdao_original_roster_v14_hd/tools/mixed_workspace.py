"""Current machine paths; historical evidence remains byte-for-byte immutable."""
import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parents[1]
FORMAL = WORK / "mmorpg-client"
ISOLATED = Path(os.environ.get("QDAO_ISOLATED_PROJECT", str(WORK / "tmp/qdao-original-live-candidate-20260921"))).resolve()
if not ISOLATED.is_relative_to((WORK / "tmp").resolve()):
    raise ValueError("QDAO_ISOLATED_PROJECT must be an independent project under this workspace/tmp")


def historical_formal_matches(value, formal):
    # The alias applies ONLY to the pinned historical formal baseline, never to
    # a new run, current stage, source records or arbitrary evidence paths.
    normalized = str(value).replace("\\", "/").rstrip("/").lower()
    return Path(value).resolve() == Path(formal).resolve() or normalized == "e:/work/mmorpg-client"


def active_ids():
    document = json.loads((ROOT / "CONTINUATION_STATE_20260920_SCOPE_UPDATED.json").read_text(encoding="utf-8-sig"))
    result = document["active_character_ids"]
    numbers = {int(value.split("_", 1)[0]) for value in result}
    if len(result) != 15 or len(set(result)) != 15 or numbers != set(range(11)) | {14, 15, 17, 20}:
        raise ValueError("Current scope must retain exactly00-10,14,15,17,20 without renumbering")
    return set(result)
