"""Read-only PNG/provenance/grid checks. Writes new technical reports only.

No art, navigation, runtime, or formal-publishing approval is performed here.
Relative candidate/source paths are explicitly rooted at ART, while session
state pointers are rooted at SESSION. Historical E:/work/image is read-mapped.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent
SESSION = TOOLS.parent
ART = SESSION.parents[1]
REPO = ART.parent
OBSERVED: dict[Path, str] = {}
ERRORS: list[str] = []
NOTES: list[str] = []
RETIRED: list[dict] = []
_retired_path = ART/'cleanup-current-assets/deleted-files.jsonl'
_retired_receipt = ART/'cleanup-current-assets/deletion-receipt.json'
RETIRED_SHA = {}
if _retired_receipt.exists() and _retired_path.exists():
    _receipt = json.loads(_retired_receipt.read_text(encoding='utf-8-sig'))
    if _receipt.get('status') == 'completed':
        RETIRED_SHA = {Path(x['file']).resolve(): x['sha256'] for x in
                       (json.loads(line) for line in _retired_path.read_text(encoding='utf-8-sig').splitlines())}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        ERRORS.append(message)


def resolve(value: str, base: Path = ART) -> Path:
    text = value.replace("\\", "/")
    for prefix in ("E:/work/image/", "E:/work/wuxingqitan/image/"):
        if text.lower().startswith(prefix.lower()):
            return (REPO / text[len(prefix):]).resolve()
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def read_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    actual = sha(data)
    if path in OBSERVED and OBSERVED[path] != actual:
        ERRORS.append(f"STALE_FAIL input changed between reads: {path}")
    OBSERVED.setdefault(path, actual)
    return data


def read_json(path: Path) -> dict:
    return json.loads(read_bytes(path).decode("utf-8-sig"))


def pointer(value: str | dict, *, base: Path = ART, expected: str | None = None,
            pixels: list[int] | None = None, label: str = "file", allow_retired: bool = False) -> dict:
    if isinstance(value, dict):
        expected = value.get("sha256", expected)
        value = value.get("file", value.get("path"))
    if not value:
        ERRORS.append(f"Missing explicit {label} pointer")
        return {"status": "missing_pointer", "label": label}
    path = resolve(value, base)
    result = {"declaredPath": value, "resolvedPath": str(path), "expectedSha256": expected,
              "status": "checked", "label": label}
    if allow_retired and not path.exists() and path in RETIRED_SHA:
        if expected:
            require(expected == RETIRED_SHA[path], f"Retired-source SHA does not match pre-deletion record: {path}")
        result.update(status="deleted_by_user_not_reverified", preDeletionSha256=RETIRED_SHA[path],
                      currentBytesVerified=False, reason="User explicitly removed obsolete originals/rollback images")
        RETIRED.append(result)
        return result
    try:
        data = read_bytes(path)
        result["sha256"] = sha(data)
        result["shaMatches"] = expected == result["sha256"] if expected else None
        if expected:
            require(result["shaMatches"], f"SHA mismatch {label}: {path}")
        else:
            result["shaEvidence"] = "observed now; input provided no SHA"
        if pixels is not None:
            with Image.open(io.BytesIO(data)) as image:
                image.load()  # Force complete decode, never just inspect header.
                result.update(format=image.format, pixels=list(image.size), mode=image.mode,
                              fullPngDecode=True)
                require(image.format == "PNG", f"Not PNG {label}: {path}")
                require(list(image.size) == pixels, f"Pixel dimensions differ {label}: {path}")
    except (OSError, ValueError) as error:
        result.update(status="error", error=str(error))
        ERRORS.append(f"Cannot verify {label}: {path}: {error}")
    return result


def tile_id(row: int, column: int) -> str:
    return f"r{row:02d}_c{column:02d}"


def geometry(row: int, column: int) -> tuple[list[int], dict]:
    return ([(column - 1) * 4096, (row - 1) * 4096, 4096, 4096],
            {"x": 50 + (column - 1) * 18.75, "z": 300 - row * 18.75,
             "width": 18.75, "height": 18.75})


def check_world(actual: dict | None, expected: dict, label: str) -> None:
    require(isinstance(actual, dict), f"Missing world rect: {label}")
    if isinstance(actual, dict):
        require(all(isinstance(actual.get(k), (int, float)) and abs(actual[k] - v) < 1e-8
                    for k, v in expected.items()), f"World rectangle mismatch: {label}")


def expected_topology() -> tuple[dict, dict, dict]:
    tiles, seams, junctions = {}, {}, {}
    for row in range(1, 17):
        for column in range(1, 17):
            name = tile_id(row, column)
            rect, world = geometry(row, column)
            tiles[name] = {"pixelRectXYWH": rect, "worldRect": world}
            if column < 16:
                ids = [name, tile_id(row, column + 1)]
                seams["|".join(ids)] = {"axis": "vertical_boundary", "tiles": ids,
                    "boundaryCoordinate": column * 4096, "spanStart": (row - 1) * 4096, "spanLength": 4096}
            if row < 16:
                ids = [name, tile_id(row + 1, column)]
                seams["|".join(ids)] = {"axis": "horizontal_boundary", "tiles": ids,
                    "boundaryCoordinate": row * 4096, "spanStart": (column - 1) * 4096, "spanLength": 4096}
            if row < 16 and column < 16:
                junctions[f"junction_{name}"] = {"pixelXY": [column * 4096, row * 4096],
                    "tiles": [name, tile_id(row, column + 1), tile_id(row + 1, column), tile_id(row + 1, column + 1)]}
    return tiles, seams, junctions


def check_key_set(items: list, key: str, expected: dict, label: str) -> dict:
    counter = Counter(item.get(key) for item in items)
    require(set(counter) == set(expected), f"{label}: missing or unexpected coordinates/IDs")
    require(all(count == 1 for count in counter.values()), f"{label}: duplicate IDs")
    require(len(items) == len(expected), f"{label}: wrong item count")
    return {item.get(key): item for item in items}


def provenance_links(record: dict, record_path: Path) -> list[dict]:
    links = []
    for field, sha_field in (("promptFile", "promptSha256"), ("sourceOutputPath", "sourceOutputSha256"),
                             ("toolOutputPath", "toolOutputSha256")):
        if record.get(field):
            links.append(pointer(record[field], expected=record.get(sha_field), label=field, allow_retired=True))
    for field in ("originalNativeOutput", "sourceCandidate", "sourceRecord", "prepared", "toolOutputReceipt", "originalPlan",
                  "generationRecord", "prompt", "evidence"):
        if isinstance(record.get(field), dict) and record[field].get("file"):
            links.append(pointer(record[field], label=field, allow_retired=True))
    for field in ("submittedImages", "actualReferences", "references"):
        for entry in record.get(field, []):
            links.append(pointer(entry, label=field, allow_retired=True))
    # Repair records explicitly enumerate their local raw input/prompt/receipt files.
    for name in ("actual-prompt.txt", "request-receipt.json", "repair-native-1254.png"):
        if name in record.get("files", {}):
            links.append(pointer(record["files"][name], base=record_path.parent, label=name, allow_retired=True))
    return links


def inspect_native(entry: dict) -> dict:
    output = pointer(entry, pixels=entry.get("pixels", [1254, 1254]), label="native image")
    record_result = pointer(entry.get("record"), label="native record")
    result = {"image": output, "record": record_result, "role": entry.get("role")}
    if record_result.get("status") == "checked":
        path = Path(record_result["resolvedPath"])
        record = read_json(path)
        recorded_output_sha = (record.get("outputSha256") or record.get("nativeSha256")
                               or record.get("originalNativeOutput", {}).get("sha256"))
        if recorded_output_sha is None and record.get("file") and record.get("sha256"):
            require(resolve(record["file"]) == resolve(entry["file"]),
                    f"Native record points to a different image: {path}")
            recorded_output_sha = record["sha256"]
        require(recorded_output_sha == entry.get("sha256"), f"Native record does not bind image SHA: {path}")
        result["explicitProvenanceLinks"] = provenance_links(record, path)
        if record.get("generationRecord", {}).get("file"):
            generation_path = resolve(record["generationRecord"]["file"])
            generation = read_json(generation_path)
            require(generation.get("sha256") == entry.get("sha256"), f"Separate generation record does not bind native SHA: {generation_path}")
            require([generation.get("width"), generation.get("height")] == entry.get("pixels"),
                    f"Separate generation record dimensions differ: {generation_path}")
            result["explicitGenerationRecordLinks"] = provenance_links(generation, generation_path)
    return result


def verify(state: dict, ledger: dict) -> dict:
    expected_tiles, expected_seams, expected_junctions = expected_topology()
    require(state.get("target") == {"mapPixels": [65536, 65536], "rows": 16, "columns": 16,
                                   "tilePixels": [4096, 4096], "tileCount": 256}, "Session target differs from required 64K grid")
    require(ledger.get("cityPixels") == [65536, 65536] and ledger.get("tilePixels") == [4096, 4096], "Ledger target pixels differ")
    require(ledger.get("appearance") == state.get("activeAppearance") == "tianyong_festival", "Appearance mismatch")
    tiles = check_key_set(ledger.get("tiles", []), "tile", expected_tiles, "tiles")
    seams = check_key_set(ledger.get("seams", []), "id", expected_seams, "seams")
    junctions = check_key_set(ledger.get("junctions", []), "id", expected_junctions, "junctions")
    present, candidates = set(), []
    for name, entry in tiles.items():
        if name not in expected_tiles:
            continue
        expected = expected_tiles[name]
        require(entry.get("pixelRectXYWH") == expected["pixelRectXYWH"], f"Tile pixel rect mismatch: {name}")
        candidate = entry.get("candidate")
        require(bool(candidate) == entry.get("candidateExists"), f"Candidate presence flag mismatch: {name}")
        if candidate:
            present.add(name)
            require(candidate.get("tile") == name, f"Candidate coordinate mismatch: {name}")
            require(candidate.get("pixels") == [4096, 4096], f"Candidate declared dimensions: {name}")
            require(candidate.get("finalPixelRectXYWH") == expected["pixelRectXYWH"], f"Candidate global rect: {name}")
            check_world(candidate.get("worldRect"), expected["worldRect"], name)
            checked = {"tile": name, "image": pointer(candidate, pixels=[4096, 4096], label=name), "explicitLinks": []}
            for key, sha_key in (("assembly", "assemblySha256"), ("qa", "qaSha256")):
                if candidate.get(key):
                    checked["explicitLinks"].append(pointer(candidate[key], expected=candidate.get(sha_key), label=f"{name} {key}"))
            for key in ("record", "review"):
                if candidate.get(key):
                    checked["explicitLinks"].append(pointer(candidate[key], label=f"{name} {key}"))
            candidates.append(checked)
    for group, expected_group, flag in ((seams, expected_seams, "bothCandidatesPresent"),
                                         (junctions, expected_junctions, "allCandidatesPresent")):
        for name, entry in group.items():
            if name not in expected_group:
                continue
            expected = expected_group[name]
            for key, value in expected.items():
                require(entry.get(key) == value, f"Topology field mismatch {name}: {key}")
            require(entry.get(flag) == all(t in present for t in expected["tiles"]), f"Candidate completeness flag mismatch: {name}")
    # All 256 world rectangles are checked against the actual production plan via
    # the explicit fileEvidence pointer in the session's layout source audit.
    layout_pointer = state.get("layoutSourceAudit")
    plan_result = {"status": "not_checked_no_pointer"}
    if layout_pointer:
        audit_path = resolve(layout_pointer, SESSION)
        audit = read_json(audit_path)
        plan_links = [entry for entry in audit.get("fileEvidence", [])
                      if "/q64_production_plans/" in entry.get("file", "").replace("\\", "/")
                      and Path(entry["file"]).name == state["activeAppearance"] + ".json"]
        require(len(plan_links) == 1, "Layout audit does not provide one unique explicit production-plan pointer")
        if len(plan_links) == 1:
            plan_result = pointer(plan_links[0], label="production plan via layout audit")
            plan = read_json(Path(plan_result["resolvedPath"]))
            plan_tiles = check_key_set(plan.get("tiles", []), "id", expected_tiles, "production plan tiles")
            check_world(plan.get("worldRect"), {"x": 50, "z": 0, "width": 300, "height": 300}, "whole-city production plan")
            for name, entry in plan_tiles.items():
                if name in expected_tiles:
                    require(entry.get("finalPixelRect") == expected_tiles[name]["pixelRectXYWH"], f"Plan global pixel rect: {name}")
                    check_world(entry.get("worldRect"), expected_tiles[name]["worldRect"], f"plan {name}")
                    runtime = {**expected_tiles[name]["worldRect"]}
                    runtime["y"] = runtime.pop("z")
                    check_world(entry.get("runtimeWorldRect"), runtime, f"plan runtime {name}")
            plan_result["worldRectanglesChecked"] = len(plan_tiles)
    else:
        ERRORS.append("No session layoutSourceAudit pointer; cannot assert all 256 world rectangles checked against a source")
    native_entries = [*state.get("nativeRecords", []), *state.get("repairRecords", [])]
    native_names = [entry.get("file") for entry in native_entries]
    require(len(native_names) == len(set(native_names)), "Duplicate native image entries")
    expected_native = sum(state.get(key, 0) for key in ("newNativeDetailCount", "newReferenceCount", "newNativeRepairCount"))
    require(len(native_entries) == expected_native, "Native entries do not match declared detail/reference/repair count")
    native = [inspect_native(entry) for entry in native_entries]
    for candidate in state.get("workInProgressCandidates", []):
        named = tiles.get(candidate.get("tile"), {}).get("candidate")
        require(named is not None and all(named.get(k) == candidate.get(k) for k in ("file", "sha256", "record", "worldRect", "finalPixelRectXYWH")),
                f"Session/ledger WIP pointer mismatch: {candidate.get('tile')}")
    counts = {"tiles": len(tiles), "candidateTiles": len(present), "missingCandidates": 256 - len(present),
              "seams": len(seams), "seamsWithBothCandidates": sum(all(t in present for t in e["tiles"]) for e in expected_seams.values()),
              "junctions": len(junctions), "junctionsWithAllCandidates": sum(all(t in present for t in e["tiles"]) for e in expected_junctions.values())}
    for key, value in counts.items():
        require(ledger.get("counts", {}).get(key) == value, f"Ledger summary count mismatch: {key}")
    require(state.get("candidateCoordinateCountIncludingWorkInProgress") == len(present), "Session candidate count mismatch")
    require(state.get("coordinatesWithoutAny4KCandidate") == 256 - len(present), "Session missing candidate count mismatch")
    return {"counts": counts, "candidates": candidates, "nativeSourceCount": len(native), "nativeSources": native,
            "productionPlan": plan_result, "expected256Geometry": expected_tiles,
            "topologyMeaning": "Unique ledger bookkeeping only; 480 edges and 225 corners are not visually reviewed by this checker"}


def final_changes() -> list[dict]:
    changed = []
    for path, before in OBSERVED.items():
        try:
            with path.open("rb") as stream:
                after = hashlib.file_digest(stream, "sha256").hexdigest()
        except OSError:
            after = None
        if after != before:
            changed.append({"file": str(path), "beforeSha256": before, "afterSha256": after})
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=TOOLS / "checkpoint_reports")
    args = parser.parse_args()
    report_dir = args.report_dir.resolve()
    if SESSION not in report_dir.parents:
        parser.error("Reports must remain in an independent directory under this SESSION")
    started = datetime.now(timezone.utc)
    data = {}
    try:
        if RETIRED_SHA:
            retired_receipt = read_json(_retired_receipt)
            read_bytes(_retired_path)
            require(retired_receipt.get('status') == 'completed', 'Cleanup receipt is not complete')
            require(retired_receipt.get('deletedFiles') == len(RETIRED_SHA), 'Cleanup log count differs from receipt')
        state_path = SESSION / "session-state.json"
        state = read_json(state_path)
        ledger_path = resolve(state.get("coverageLedger", "current-coverage-ledger.json"), SESSION)
        require(ledger_path == SESSION / "current-coverage-ledger.json", "Unexpected coverageLedger pointer")
        ledger = read_json(ledger_path)
        require(state.get("coverageLedgerSha256") == OBSERVED[ledger_path], "Session coverageLedgerSha256 mismatch")
        data = verify(state, ledger)
    except (OSError, ValueError, KeyError, TypeError) as error:
        ERRORS.append(f"Incomplete technical check: {type(error).__name__}: {error}")
    changes = final_changes()
    if changes:
        ERRORS.append("STALE_FAIL: one or more inputs changed during verification; rerun after writer completes")
    status = "STALE_FAIL" if changes or any("STALE_FAIL" in error for error in ERRORS) else ("TECHNICAL_FAIL" if ERRORS else ("CURRENT_ASSETS_CONSISTENT_WITH_RETIRED_SOURCES" if RETIRED else "TECHNICAL_CONSISTENT"))
    report = {"schemaVersion": 1, "startedAtUtc": started.isoformat(), "finishedAtUtc": datetime.now(timezone.utc).isoformat(),
              "status": status, "scope": "Read-only file, provenance-pointer and grid consistency check; no visual review or publishing",
              "inputFilesBefore": [{"file": str(p), "sha256": h} for p, h in OBSERVED.items()],
              "inputChangesDuringCheck": changes, "inputCount": len(OBSERVED), "errors": ERRORS,
              "results": data, "scriptSha256": sha(Path(__file__).read_bytes()),
              "retiredSourceReferencesNotReverified": RETIRED,
              "artAcceptance": "not_performed", "navigationAcceptance": "not_performed", "runtimeAcceptance": "not_performed",
              "limitations": ["World-coordinate formulas do not establish semantic geometry alignment",
                              "Source checks follow explicit current pointers only; they do not invent missing provenance or certify every historical ancestor",
                              "Results bind input SHA at this check only; rerun after selected candidate pointers change"]}
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / ("checkpoint-" + started.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with report_path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(report, out, ensure_ascii=False, indent=2)
        out.write("\n")
    counts = data.get("counts", {})
    lines = ["# 主城检查点技术报告", "", f"状态：`{status}`；时间：{report['finishedAtUtc']}", "",
             f"[完整 JSON 报告]({report_path.name})。输入文件 {len(OBSERVED)} 个，期间变更 {len(changes)} 个，错误 {len(ERRORS)} 项。", "",
             f"当前候选 {counts.get('candidateTiles', 'unknown')} 张；原生来源 {data.get('nativeSourceCount', 'unknown')} 张。每张读取全部 PNG 像素并核对尺寸、SHA；源记录及已有明确指针同时核对。", "",
             f"坐标 {counts.get('tiles', 'unknown')}；唯一邻边 {counts.get('seams', 'unknown')}；四块交点 {counts.get('junctions', 'unknown')}。这些数字表示台账完整性，不表示视觉验收通过。", "",
             "输入在读前后变更时结果为 STALE_FAIL。每次报告使用新时间戳文件，旧报告不覆盖。", "",
             "本检查没有美术、布局语义、导航或客户端实机验收，也没有执行正式发布。", ""]
    lines.extend(["错误：", "", *["- " + error for error in ERRORS]] if ERRORS else [])
    if RETIRED:
        lines.extend(["", f"按用户授权已删除的历史来源引用 {len(RETIRED)} 项：仅核对删除前记录 SHA，当前字节无法复验；逐项 status=deleted_by_user_not_reverified，未把删除项标为通过。", ""])
    with report_path.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as out:
        out.write("\n".join(lines) + "\n")
    print(json.dumps({"report": str(report_path), "status": status, "counts": counts,
                      "nativeSourceCount": data.get("nativeSourceCount"), "inputCount": len(OBSERVED), "retiredSourceReferencesNotReverified": len(RETIRED), "errors": ERRORS}, ensure_ascii=False))
    return 2 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
