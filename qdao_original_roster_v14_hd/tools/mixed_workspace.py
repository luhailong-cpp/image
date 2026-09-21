"""Current machine paths; historical evidence remains byte-for-byte immutable."""
import os
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
