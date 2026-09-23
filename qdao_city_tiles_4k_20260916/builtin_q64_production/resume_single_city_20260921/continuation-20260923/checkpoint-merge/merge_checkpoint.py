"""Prepare a targeted five-file checkpoint; never applies without an explicit command.

prepare --selection selected.json : raw-byte backups + proposed JSON, no shared writes
apply --transaction DIR --reviewed-plan-sha256 SHA : exclusive Windows CAS commit

This writes JSON only. PNG files are read for SHA/headers; no image is changed.
"""
from __future__ import annotations

import argparse
import copy
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
SESSION = HERE.parents[1]
ART = SESSION.parents[1]
ROOT = ART.parent
TARGETS = {
    "ledger": SESSION / "current-coverage-ledger.json",
    "session": SESSION / "session-state.json",
    "batch": ART / "builtin_q64_production/current-batch.json",
    "catalog": ART / "production_catalog.json",
    "status": ART / "status.json",
}
ORDER = list(TARGETS)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
TILE_RE = re.compile(r"^r(0[1-9]|1[0-6])_c(0[1-9]|1[0-6])$")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def decode(raw):
    return json.loads(raw.decode("utf-8-sig"))


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def inside(path, base):
    path = path.resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Path outside required root {base}: {path}")
    return path


def resolve(value):
    p = Path(value)
    return inside(p if p.is_absolute() else ART / p, ART)


def relative(path):
    return inside(Path(path), ART).relative_to(ART).as_posix()


def png_pixels(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Not a PNG with IHDR")
    return list(struct.unpack(">II", data[16:24]))


def checked_ref(ref, dependencies, *, pixels=None):
    if not isinstance(ref, dict) or not ref.get("file") or not SHA_RE.fullmatch(ref.get("sha256", "")):
        raise ValueError(f"Explicit file and lowercase sha256 required: {ref}")
    p = resolve(ref["file"])
    raw = p.read_bytes()
    if digest(raw) != ref["sha256"]:
        raise ValueError(f"Current byte SHA mismatch: {p}")
    if pixels is not None and png_pixels(raw) != pixels:
        raise ValueError(f"Wrong PNG dimensions: {p}")
    dependencies[str(p)] = {"file": relative(p), "sha256": digest(raw), "bytes": len(raw)}
    return {**ref, "file": relative(p)}


def checked_historical_text_ref(ref, dependencies):
    """Only accept exact byte SHA, or exact CRLF-to-LF historical equality."""
    p = resolve(ref["file"])
    raw = p.read_bytes()
    actual = digest(raw)
    if actual == ref["sha256"]:
        return checked_ref(ref, dependencies)
    if digest(raw.replace(b"\r\n", b"\n")) != ref["sha256"]:
        raise ValueError(f"Historical record content mismatch, not just CRLF: {p}")
    current = checked_ref({**ref, "sha256": actual}, dependencies)
    current.update(historicalSha256=ref["sha256"], historicalShaVerification="exact CRLF-to-LF byte transformation")
    return current


def validate_candidate(candidate, dependencies):
    out = copy.deepcopy(candidate)
    tile = out.get("tile", "")
    if not TILE_RE.fullmatch(tile):
        raise ValueError(f"Invalid tile: {tile}")
    if out.get("pixels") != [4096, 4096]:
        raise ValueError(f"Candidate dimensions must be explicitly 4096 x 4096: {tile}")
    checked = checked_ref(out, dependencies, pixels=[4096, 4096])
    out["file"] = checked["file"]
    if not out.get("status"):
        raise ValueError(f"Explicit candidate review status required: {tile}")
    out["record"] = checked_ref(out["record"], dependencies)
    if not isinstance(out.get("qa"), dict):
        raise ValueError(f"Explicit QA evidence pointer is required even when QA is pending: {tile}")
    out["qa"] = checked_ref(out["qa"], dependencies)
    # A review is bound to this image, not merely to the tile name.
    if out["sha256"] not in resolve(out["qa"]["file"]).read_text(encoding="utf-8-sig"):
        raise ValueError(f"QA JSON does not name exact selected PNG SHA: {tile}")
    for key in ("assembly", "review"):
        if isinstance(out.get(key), dict):
            out[key] = checked_ref(out[key], dependencies)
    r, c = int(tile[1:3]), int(tile[5:7])
    out.update(appearance="tianyong_festival", pixels=[4096, 4096], accepted=False,
               formalArtAcceptancePassed=False, clientRuntimeAccepted=False,
               runtimePublished=False, role="candidate_not_production_tile",
               finalPixelRectXYWH=[(c-1)*4096, (r-1)*4096, 4096, 4096],
               worldRect={"x": 50+(c-1)*18.75, "z": 300-r*18.75,
                          "width": 18.75, "height": 18.75})
    return out


def validate_grid(ledger):
    expected_tiles = {f"r{r:02}_c{c:02}" for r in range(1, 17) for c in range(1, 17)}
    tiles = ledger["tiles"]
    if len(tiles) != 256 or {t["tile"] for t in tiles} != expected_tiles:
        raise ValueError("Ledger must contain exactly 256 unique expected coordinates")
    expected_seams = set()
    for r in range(1, 17):
        for c in range(1, 17):
            t = f"r{r:02}_c{c:02}"
            if c < 16:
                expected_seams.add(t + "|" + f"r{r:02}_c{c+1:02}")
            if r < 16:
                expected_seams.add(t + "|" + f"r{r+1:02}_c{c:02}")
    if len(ledger["seams"]) != 480 or {s["id"] for s in ledger["seams"]} != expected_seams:
        raise ValueError("Ledger must contain exactly 480 expected adjacent seams")
    expected_junctions = {f"junction_r{r:02}_c{c:02}" for r in range(1, 16) for c in range(1, 16)}
    if len(ledger["junctions"]) != 225 or {j["id"] for j in ledger["junctions"]} != expected_junctions:
        raise ValueError("Ledger must contain exactly 225 expected junctions")


def inventory_native(docs, selection, dependencies):
    """Inventory only existing source bytes linked to generation metadata.

    Old missing records never add to retained counts. New references/guides are
    excluded. Counts include physically retained rejected/superseded sources;
    they do not count as selected sources, tool calls, or complete candidates.
    """
    proposals = []
    for role, key in (("detail", "baseNativeEvidence"), ("repair", "nativeRepairEvidence")):
        for item in docs["batch"].get(key, []):
            if item.get("native") and item.get("sha256"):
                proposals.append({"file": item["native"], "sha256": item["sha256"], "kind": role,
                                  "record": {"file": item["record"], "sha256": item["recordSha256"]}})
    for key, kind in (("nativeRecords", "detail"), ("repairRecords", "repair")):
        for item in docs["session"].get(key, []):
            proposals.append({**item, "kind": kind})
    # New normal native directories have multiple historical record suffixes.
    for p in ART.rglob("*.png"):
        if p.parent.name != "native":
            continue
        for rp in (p.with_suffix(".record.json"), p.with_suffix(".generation.json"), Path(str(p)+".generation.json")):
            if rp.exists():
                rd = decode(rp.read_bytes())
                sha = rd.get("nativeSha256") or rd.get("sha256")
                if sha:
                    kind = "repair" if any("repair" in x.lower() for x in p.parts) else "detail"
                    proposals.append({"file": relative(p), "sha256": sha, "kind": kind,
                                      "record": {"file": relative(rp), "sha256": digest(rp.read_bytes())}})
                break
    # Repair batches commonly store native output outside a directory named native.
    for rp in SESSION.rglob("*.png.generation.json"):
        p = Path(str(rp)[:-len(".generation.json")])
        if not p.exists() or p.parent.name == "native":
            continue
        rd = decode(rp.read_bytes())
        sha = rd.get("nativeSha256") or rd.get("sha256")
        if sha and (rd.get("tool") == "image_gen.imagegen" or rd.get("route") in ("builtin", "builtin_image_gen")):
            proposals.append({"file": relative(p), "sha256": sha, "kind": "repair",
                              "record": {"file": relative(rp), "sha256": digest(rp.read_bytes())}})
    proposals.extend(selection.get("additionalNativeSources", []))
    by_path, missing = {}, []
    for item in proposals:
        if item.get("kind") not in ("detail", "repair"):
            raise ValueError(f"Unknown native source kind: {item.get('kind')}")
        p = resolve(item["file"])
        if not p.exists():
            missing.append({"file": relative(p), "sha256": item["sha256"]})
            continue
        key = str(p).casefold()
        if key in by_path:
            if by_path[key]["sha256"] != item["sha256"]:
                raise ValueError(f"Conflicting source SHA: {p}")
            continue
        native = checked_ref(item, dependencies)
        dims = png_pixels(p.read_bytes())
        if dims != [1254, 1254]:
            raise ValueError(f"Expected native 1254 source; explicitly extend schema for new capability: {p}")
        rec = checked_historical_text_ref(item["record"], dependencies)
        record_text = resolve(rec["file"]).read_text(encoding="utf-8-sig")
        if native["sha256"] not in record_text:
            raise ValueError(f"Generation record does not bind actual native bytes: {p}")
        by_path[key] = {"file": relative(p), "sha256": native["sha256"], "pixels": dims,
                        "record": rec, "kind": item["kind"], "physicallyRetained": True,
                        "candidateEligibilityNotAsserted": True,
                        "role": "native_source_not_production_tile", "actualModel": None,
                        "actualQuality": None, "backendModelVerified": False}
    sources = sorted(by_path.values(), key=lambda x: x["file"])
    return {"observedAtUtc": now(), "scope": "ART known generation-linked sources; reference/guide/preview PNGs excluded",
            "countMeaning": "Distinct physical retained source paths; includes rejected and superseded bytes until cleanup. Not new generations or complete tiles.",
            "physicalFileCount": len(sources), "uniqueImageShaCount": len({x["sha256"] for x in sources}),
            "detailCount": sum(x["kind"] == "detail" for x in sources),
            "repairCount": sum(x["kind"] == "repair" for x in sources),
            "missingHistoricalSourceCount": len({x["file"] for x in missing}), "sources": sources}


def merge(docs, selection, tx, dependencies):
    stamp = now()
    ledger, state = docs["ledger"], docs["session"]
    validate_grid(ledger)
    if state["activeAppearance"] != "tianyong_festival" or ledger["appearance"] != "tianyong_festival":
        raise ValueError("Wrong active appearance")
    if state.get("productionAcceptedTiles") != 0:
        raise ValueError("Unexpected existing formal acceptance; do not overwrite")
    selected = [validate_candidate(x, dependencies) for x in selection["selectedCandidates"]]
    if len({x["tile"] for x in selected}) != len(selected):
        raise ValueError("Duplicate selected tile")
    old_by_tile = {t["tile"]: copy.deepcopy(t.get("candidate")) for t in ledger["tiles"]}
    tiles = {t["tile"]: t for t in ledger["tiles"]}
    changed = set()
    for candidate in selected:
        tid = candidate["tile"]
        old = old_by_tile[tid]
        if not old or old.get("sha256") != candidate["sha256"]:
            changed.add(tid)
        t = tiles[tid]
        if old and old != candidate:
            t.setdefault("historicalCandidateSelections", []).append({"supersededAtUtc": stamp, "candidate": old})
        t.update(candidateExists=True, candidate=candidate,
                 status="selected_complete_candidate_formal_art_acceptance_pending",
                 formalArtAcceptancePassed=False, clientRuntimeAccepted=False)
    # All existing selected PNGs must still be real complete current files.
    current = {}
    for tid, t in tiles.items():
        if t.get("candidateExists"):
            checked_ref(t["candidate"], dependencies, pixels=[4096, 4096])
            current[tid] = t["candidate"]
        t["formalArtAcceptancePassed"] = False
        t["clientRuntimeAccepted"] = False
    evidence = {x["id"]: x for x in selection.get("localReviews", [])}
    if len(evidence) != len(selection.get("localReviews", [])):
        raise ValueError("Duplicate local review id")
    seen_evidence = set()
    for key, present_key in (("seams", "bothCandidatesPresent"), ("junctions", "allCandidatesPresent")):
        for item in ledger[key]:
            tids = item["tiles"]
            present = all(t in current for t in tids)
            item[present_key] = present
            item["wholeCityArtGatePassed"] = False
            exact = {t: current[t]["sha256"] for t in tids if t in current}
            touched = bool(changed.intersection(tids))
            if touched:
                historic = {k: copy.deepcopy(v) for k, v in item.items() if k in (
                    "status", "priorLocalQaReference", "currentScopedReview", "scopedReviewCandidateSha256ByTile",
                    "freshVisualReviewPerformedByThisAudit", "scopedLocalContinuityPassed")}
                if historic:
                    item.setdefault("reviewHistory", []).append({"invalidatedAtUtc": stamp, "reason": "selected candidate SHA changed", **historic})
                item["priorLocalQaReference"] = None
                item.pop("currentScopedReview", None)
                item.pop("scopedReviewCandidateSha256ByTile", None)
                item["freshVisualReviewPerformedByThisAudit"] = False
                item["scopedLocalContinuityPassed"] = False
                item["status"] = "pending_same_version_visual_review" if present else "pending_missing_neighbor"
            elif present and item.get("currentScopedReview"):
                # This is inheritance of a historical review for the unchanged full tuple.
                # It is NOT a fresh review and must remain clearly distinct from one.
                prior = {t: old_by_tile[t]["sha256"] for t in tids}
                if exact != prior:
                    raise ValueError("Unexpected changed tuple escaped invalidation")
                item.setdefault("inheritedReviewSelectionBinding", {"candidateSha256ByTile": exact,
                    "basis": "unchanged candidate tuple in raw-byte pre-transaction ledger", "sourceLedgerSha256": selection["_sourceLedgerSha256"]})
            if item["id"] in evidence:
                rev = evidence[item["id"]]
                seen_evidence.add(item["id"])
                if not present or rev["candidateSha256ByTile"] != exact:
                    raise ValueError(f"Local review candidate pair/quad does not match: {item['id']}")
                if rev["result"] not in ("passed", "failed", "pending"):
                    raise ValueError("Review result must be passed, failed or pending")
                ref = checked_ref(rev["evidence"], dependencies)
                # A source review may link a chain. Caller must provide a binding record
                # that actually names every current SHA; no synthetic pass from filenames.
                text = resolve(ref["file"]).read_text(encoding="utf-8-sig")
                if not all(sha in text for sha in exact.values()):
                    raise ValueError(f"Review evidence lacks exact SHA tuple: {item['id']}")
                item.update(currentScopedReview=ref, scopedReviewCandidateSha256ByTile=exact,
                    scopedLocalContinuityPassed=rev["result"] == "passed",
                    freshVisualReviewPerformedByThisAudit=True,
                    status=f"scoped_local_continuity_{rev['result']}_whole_city_gate_pending")
    if seen_evidence != set(evidence):
        raise ValueError(f"Unknown local review IDs: {set(evidence)-seen_evidence}")
    n = len(current)
    ledger["updatedAtUtc"] = stamp
    counts = ledger["counts"]
    counts.update(tiles=256, candidateTiles=n, missingCandidates=256-n, seams=480, junctions=225,
        seamsWithBothCandidates=sum(x["bothCandidatesPresent"] for x in ledger["seams"]),
        junctionsWithAllCandidates=sum(x["allCandidatesPresent"] for x in ledger["junctions"]),
        formalArtAcceptedTiles=0, wholeCityPassedSeams=0, wholeCityPassedJunctions=0,
        freshScopedLocalSeamsPassed=sum("passed" in x["status"] and x.get("freshVisualReviewPerformedByThisAudit", False) for x in ledger["seams"]),
        freshScopedLocalJunctionsPassed=sum("passed" in x["status"] and x.get("freshVisualReviewPerformedByThisAudit", False) for x in ledger["junctions"]))
    validate_grid(ledger)
    inventory = inventory_native(docs, selection, dependencies)
    inventory_ref = {"file": relative(tx / "retained-native-inventory.json"), "sha256": digest(encode(inventory))}
    write_new(tx / "retained-native-inventory.json", encode(inventory))
    checked_ref(inventory_ref, dependencies)
    # The legacy record arrays remain historical text. This separate inventory is
    # an exact current-byte observation and remains valid only for its timestamp.
    state["retainedNativeInventory"] = inventory_ref
    if selection.get("retentionEvidence"):
        refs = [checked_ref(r, dependencies) for r in selection["retentionEvidence"]]
        state.setdefault("currentRetentionEvidence", []).extend(r for r in refs if r not in state.get("currentRetentionEvidence", []))
        state["retentionEvidenceMeaning"] = "Current scoped deletion receipts supplement frozen prior retention records; deleted source bytes are not claimed as currently verified."
    state["retainedNativeDetailCount"] = inventory["detailCount"]
    state["retainedNativeRepairCount"] = inventory["repairCount"]
    state["allAppearanceRetainedNativeKnownCountExcludingReferences"] = inventory["physicalFileCount"]
    state["retainedNativeCountMeaning"] = inventory["countMeaning"]
    state["legacyGenerationCountersAreHistorical"] = "newNativeDetailCount/newNativeRepairCount/nativeRecords/repairRecords are historical generation records, not current retained-byte counts; see retainedNativeInventory"
    old_wip = {x["tile"]: x for x in state.get("workInProgressCandidates", [])}
    for candidate in selected:
        old_wip[candidate["tile"]] = candidate
    state["workInProgressCandidates"] = [old_wip[t] for t in sorted(old_wip)]
    state["selectedCandidateCoordinates"] = [current[t] for t in sorted(current)]
    all_candidate_ids = set()
    for variant in docs["catalog"]["variants"]:
        appearance = variant["city"] + "_" + variant["variant"]
        if appearance == "tianyong_festival":
            variant.update(candidateCoordinatesIncludingWorkInProgress=n, coordinatesWithoutAny4KCandidate=256-n,
                           productionTilesAccepted=0, runtimePublished=False,
                           currentSelectedCandidates=[current[t] for t in sorted(current)])
        else:
            for c in variant.get("currentCandidates", []):
                checked_ref(c, dependencies, pixels=[4096, 4096])
                all_candidate_ids.add((appearance, c["tile"]))
    all_count = len(all_candidate_ids) + n
    state.update(updatedAtUtc=stamp, candidateCoordinateCountIncludingWorkInProgress=n,
        coordinatesWithoutAny4KCandidate=256-n, allAppearanceCandidateCoordinateCountIncludingWorkInProgress=all_count,
        productionAcceptedTiles=0, completeCityDeliveries=0, allVisualChecksPassed=False,
        runtimePublished=False, deliveryReady=False, formalManifestProduced=False,
        coverageLedgerSha256=digest(encode(ledger)))
    if selection.get("modelCapabilityEvidence"):
        model_ref = checked_ref(selection["modelCapabilityEvidence"], dependencies)
        state["modelCapabilityEvidence"] = resolve(model_ref["file"]).relative_to(SESSION).as_posix()
        state["modelCapabilityEvidenceSha256"] = model_ref["sha256"]
    else:
        model_ref = {"file": relative(SESSION / state["modelCapabilityEvidence"])}
        model_ref["sha256"] = digest(resolve(model_ref["file"]).read_bytes())
        checked_ref(model_ref, dependencies)
    # New checkpoint evidence is distinct from old frozen handoff evidence.
    state["latestCheckpointSelection"] = {"file": relative(tx / "selection.json"),
                                           "sha256": digest((tx / "selection.json").read_bytes())}
    checked_ref(state["latestCheckpointSelection"], dependencies)
    ledger_sha, session_sha = digest(encode(ledger)), digest(encode(state))
    for key in ("batch", "catalog", "status"):
        doc = docs[key]
        doc["updatedAtUtc"] = stamp
        active = doc["activeProductionRun"]
        active.update(updatedAtUtc=stamp, sessionState=relative(TARGETS["session"]), sessionStateSha256=session_sha,
            coverageLedger=relative(TARGETS["ledger"]), coverageLedgerSha256=ledger_sha,
            modelEvidence=model_ref["file"], modelEvidenceSha256=model_ref["sha256"],
            candidateCoordinatesIncludingWorkInProgress=n, coordinatesWithoutAny4KCandidate=256-n,
            allAppearanceCandidateCoordinatesIncludingWorkInProgress=all_count,
            retainedNativeKnownCountExcludingReferences=inventory["physicalFileCount"],
            retainedNativeDetailCount=inventory["detailCount"], retainedNativeRepairCount=inventory["repairCount"],
            retainedNativeInventory=inventory_ref, formalAcceptedTileCount=0, deliveryReady=False,
            legacyGenerationCountersAreHistorical=True,
            currentWindowWorkState="continuing_single_city_art_production_incomplete",
            actualBackendModel=None, actualQuality=None, backendModelVerified=False)
        if state.get("currentRetentionEvidence"):
            active["currentRetentionEvidence"] = copy.deepcopy(state["currentRetentionEvidence"])
        doc["currentSelectedCandidateCoordinateCountAllAppearances"] = all_count
    docs["batch"].update(acceptedDeliveryTileCount=0, wholeCityCompletedCount=0, runtimePublished=False)
    docs["status"].update(status="single_city_native_detail_production_incomplete",
        scope=f"Current priority: Tianyong festival 256 tiles; {n} candidate coordinates, {256-n} missing, 0 production accepted. Other appearances retained.",
        completedCurrentDeliveryTiles=0, completedWholeCityCount=0, runtimePublished=False,
        actualModel=None, actualQualityPreset=None, backendModelVerified=False)
    docs["status"]["scopeDecision"].update(remainingCoordinatesWithoutCandidate=256-n, productionAccepted=0)
    # Root legacy source/candidate arrays remain untouched by design.
    batch_sha = digest(encode(docs["batch"]))
    for key in ("catalog", "status"):
        docs[key]["currentBatchSha256"] = batch_sha
    return docs, {"candidateTiles": n, "missingCandidates": 256-n, "allAppearances": all_count,
                  "changedCoordinates": sorted(changed), "retainedNativeSources": inventory["physicalFileCount"],
                  "retainedDetail": inventory["detailCount"], "retainedRepair": inventory["repairCount"],
                  "counts": counts, "formalAccepted": 0}


def prepare(selection_path):
    selection_path = inside(Path(selection_path), ART)
    selection_raw = selection_path.read_bytes()
    selection = decode(selection_raw)
    if selection.get("schemaVersion") != 1 or "selectedCandidates" not in selection:
        raise ValueError("Selection schemaVersion=1 and selectedCandidates array required")
    tx = HERE / ("transaction-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    tx.mkdir()
    raw = {k: p.read_bytes() for k, p in TARGETS.items()}
    for k, data in raw.items():
        write_new(tx / "before" / (k + ".json"), data)
    write_new(tx / "selection.json", selection_raw)
    selection["_sourceLedgerSha256"] = digest(raw["ledger"])
    docs = {k: decode(v) for k, v in raw.items()}
    # A stable set can still be somebody else's paused partial transaction.
    # Validate already-present current pointer hashes before merging it.
    if docs["session"].get("coverageLedgerSha256") != digest(raw["ledger"]):
        raise ValueError("Initial session -> ledger SHA chain is inconsistent; inspect existing partial transaction")
    for key in ("batch", "catalog", "status"):
        active = docs[key]["activeProductionRun"]
        if active.get("sessionStateSha256") != digest(raw["session"]):
            raise ValueError(f"Initial {key} -> session SHA chain is inconsistent; inspect existing partial transaction")
        if active.get("coverageLedgerSha256") and active["coverageLedgerSha256"] != digest(raw["ledger"]):
            raise ValueError(f"Initial {key} -> ledger SHA chain is inconsistent")
    for key in ("catalog", "status"):
        if docs[key].get("currentBatchSha256") and docs[key]["currentBatchSha256"] != digest(raw["batch"]):
            raise ValueError(f"Initial {key} -> batch SHA chain is inconsistent")
    dependencies = {str(selection_path): {"file": relative(selection_path), "sha256": digest(selection_raw), "bytes": len(selection_raw)}}
    docs, summary = merge(docs, selection, tx, dependencies)
    entries = []
    for k in ORDER:
        data = encode(docs[k])
        write_new(tx / "after" / (k + ".json"), data)
        entries.append({"key": k, "target": relative(TARGETS[k]), "beforeSha256": digest(raw[k]),
                        "afterSha256": digest(data), "beforeBytes": len(raw[k]), "afterBytes": len(data)})
    # Stop if a writer changed shared state while preparing; don't silently base
    # a transaction on inconsistent or stale five-file state.
    for k, p in TARGETS.items():
        if p.read_bytes() != raw[k]:
            raise RuntimeError(f"Concurrent shared JSON change during prepare: {p}")
    for d in dependencies.values():
        if digest(resolve(d["file"]).read_bytes()) != d["sha256"]:
            raise RuntimeError(f"Input changed during prepare: {d['file']}")
    plan = {"schemaVersion": 1, "createdAtUtc": now(), "applyOrder": ORDER, "files": entries,
            "dependencies": sorted(dependencies.values(), key=lambda x: x["file"]),
            "summary": summary, "preparedOnly": True, "sharedFilesWritten": False,
            "scriptSha256": digest(Path(__file__).read_bytes()),
            "concurrency": "All five targets plus dependencies locked at apply; SHA compared before first write. Windows deny-sharing handles retained throughout. Multi-file writes are journaled, not falsely atomic."}
    write_new(tx / "plan.json", encode(plan))
    print(json.dumps({"transaction": str(tx), "planSha256": digest(encode(plan)), "summary": summary}, ensure_ascii=False))


class WinLockedFile:
    """Deny-share Windows handle. Write-through handle avoids close/reopen CAS gap."""
    def __init__(self, path, writable):
        if os.name != "nt":
            raise RuntimeError("apply requires Windows deny-sharing file handles")
        import msvcrt
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                           wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create.restype = wintypes.HANDLE
        handle = create(str(path), 0x80000000 | (0x40000000 if writable else 0), 0, None, 3, 0x80, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            fd = msvcrt.open_osfhandle(handle, (os.O_RDWR if writable else os.O_RDONLY) | os.O_BINARY)
        except BaseException:
            kernel.CloseHandle(handle)
            raise
        self.file = os.fdopen(fd, "r+b" if writable else "rb", buffering=0)
    def read(self):
        self.file.seek(0)
        return self.file.read()
    def write(self, raw):
        self.file.seek(0)
        offset = 0
        while offset < len(raw):
            count = self.file.write(raw[offset:])
            if not count:
                raise IOError("Short/zero write on locked shared JSON")
            offset += count
        self.file.truncate()
        os.fsync(self.file.fileno())
    def close(self):
        self.file.close()


def apply(tx, reviewed_sha):
    tx = inside(Path(tx), HERE)
    plan_raw = (tx / "plan.json").read_bytes()
    if digest(plan_raw) != reviewed_sha:
        raise ValueError("Reviewed plan SHA mismatch")
    plan = decode(plan_raw)
    if plan["scriptSha256"] != digest(Path(__file__).read_bytes()):
        raise ValueError("Script changed since prepare; prepare and review again")
    if plan["applyOrder"] != ORDER or len(plan["files"]) != 5:
        raise ValueError("Unexpected target set or order")
    for row in plan["files"]:
        if resolve(row["target"]) != TARGETS[row["key"]]:
            raise ValueError("Target path is not one of the five shared JSONs")
    receipt_path = tx / "apply-receipt.json"
    journal_path = tx / "apply-journal.jsonl"
    if receipt_path.exists() or journal_path.exists():
        raise ValueError("Transaction already attempted; inspect its receipt, do not retry blindly")
    after = {}
    for row in plan["files"]:
        k = row["key"]
        before = (tx / "before" / (k + ".json")).read_bytes()
        after[k] = (tx / "after" / (k + ".json")).read_bytes()
        if digest(before) != row["beforeSha256"] or digest(after[k]) != row["afterSha256"]:
            raise ValueError("Transaction bytes have changed")
    locks, by_path, attempted, committed = [], {}, [], []
    receipt = {"startedAtUtc": now(), "planSha256": reviewed_sha, "attempted": attempted,
               "committed": committed, "status": "not_started", "automaticRollbackPerformed": False}
    def journal(event):
        with journal_path.open("ab", buffering=0) as f:
            f.write(encode({"atUtc": now(), **event}).replace(b"\n", b" ") + b"\n")
            os.fsync(f.fileno())
    try:
        # Acquire every shared target first, in a fixed order, before any write.
        for k in ORDER:
            p = TARGETS[k]
            lock = WinLockedFile(p, True)
            locks.append(lock)
            by_path[str(p).casefold()] = lock
        # Dependencies are protected against replacement/deletion until all writes finish.
        for d in plan["dependencies"]:
            p = resolve(d["file"])
            key = str(p).casefold()
            if key not in by_path:
                lock = WinLockedFile(p, False)
                locks.append(lock)
                by_path[key] = lock
            if digest(by_path[key].read()) != d["sha256"]:
                raise RuntimeError(f"Dependency CAS conflict: {p}")
        for row in plan["files"]:
            if digest(by_path[str(TARGETS[row["key"]]).casefold()].read()) != row["beforeSha256"]:
                raise RuntimeError(f"Shared JSON CAS conflict: {row['target']}")
        journal({"event": "all_inputs_locked_and_all_preconditions_passed"})
        for row in plan["files"]:
            k = row["key"]
            lock = by_path[str(TARGETS[k]).casefold()]
            attempted.append(k)
            journal({"event": "before_write", "key": k, "beforeSha256": row["beforeSha256"], "afterSha256": row["afterSha256"]})
            lock.write(after[k])
            if digest(lock.read()) != row["afterSha256"]:
                raise IOError(f"Postwrite SHA mismatch: {k}")
            committed.append(k)
            journal({"event": "write_verified", "key": k, "sha256": row["afterSha256"]})
        receipt["status"] = "complete_all_five_writes_verified"
    except BaseException as exc:
        receipt["status"] = "partial_commit_manual_recovery_required" if attempted else "aborted_before_first_write"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        try:
            receipt["finishedAtUtc"] = now()
            receipt["observedLockedTargetSha256"] = {k: digest(by_path[str(p).casefold()].read())
                for k, p in TARGETS.items() if str(p).casefold() in by_path}
            write_new(receipt_path, encode(receipt))
        finally:
            for lock in reversed(locks):
                lock.close()
    print(json.dumps(receipt, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--selection", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--transaction", required=True)
    p.add_argument("--reviewed-plan-sha256", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.selection)
    else:
        apply(args.transaction, args.reviewed_plan_sha256)


if __name__ == "__main__":
    main()
