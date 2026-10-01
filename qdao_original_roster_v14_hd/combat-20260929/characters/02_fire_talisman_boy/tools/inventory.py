"""Snapshot only this character's inputs. Never changes existing assets."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"hit": 6, "attack": 12, "cast": 16}
PATTERN = re.compile(r"(hit|attack|cast)-([EW])-(\d{2})-v\d+\.png$")


def main():
    paths = set()
    for folder in ("staging", "runtime", "selection", "selections", "provenance/receipts"):
        base = ROOT / folder
        if base.exists():
            paths.update(path for path in base.rglob("*") if path.is_file())
    paths.update(ROOT.glob("*selection*.json"))
    rows, covered, runtimes = [], set(), set()
    for path in sorted(paths):
        raw = path.read_bytes()
        row = {"file": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
               "sha256": hashlib.sha256(raw).hexdigest(),
               "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        if raw.startswith(b"\x89PNG\r\n\x1a\n"):
            row["nativeCanvas"] = list(struct.unpack(">II", raw[16:24]))
            row["pngColorType"] = raw[25]
            match = PATTERN.fullmatch(path.name)
            if path.parent.name == "staging" and match:
                action, direction, number = match.groups()
                if 1 <= int(number) <= COUNTS[action]:
                    covered.add((action, direction, int(number)))
            parts = path.relative_to(ROOT).parts
            if len(parts) == 4 and parts[0] == "runtime":
                if parts[1] in COUNTS and parts[2] in ("E", "W") and path.stem.isdigit():
                    runtimes.add((parts[1], parts[2], int(path.stem)))
        rows.append(row)
    expected = [(a, d, n) for a, count in COUNTS.items() for d in ("E", "W") for n in range(1, count + 1)]
    snapshot = {"schemaVersion": 1, "character": ROOT.name,
                "capturedAt": datetime.now(timezone.utc).isoformat(),
                "scope": "staging/runtime/selection/selections/root selection JSON/provenance receipts",
                "summary": {"candidateSlots": len(covered), "expected": 68,
                            "runtimeSlots": len(set(expected) & runtimes), "files": len(rows)},
                "missingCandidateSlots": [f"{a}/{d}/{n:02d}" for a, d, n in expected if (a,d,n) not in covered],
                "missingRuntimeSlots": [f"{a}/{d}/{n:02d}" for a, d, n in expected if (a,d,n) not in runtimes],
                "files": rows,
                "visualApproval": "not_reviewed", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
    folder = ROOT / "inventory"
    folder.mkdir(exist_ok=True)
    stem = "initial-20260930"
    out = folder / (stem + ".json")
    version = 2
    while out.exists():
        out = folder / f"{stem}-v{version}.json"
        version += 1
    with out.open("x", encoding="utf-8") as stream:
        json.dump(snapshot, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(out), **snapshot["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
