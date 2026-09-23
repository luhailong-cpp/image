"""Read-only verification of selected checkpoint and retention-aware provenance.

Writes a uniquely named JSON report only. Never changes shared JSON or images.
Deleted sources are recorded as deleted_by_user_not_reverified, never as passes.
This is metadata/byte verification, not visual, layout, navigation, or runtime QA.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parent
SESSION = HERE.parents[1]
ART = SESSION.parents[1]
ROOT = ART.parent
C07 = SESSION / "next_tile_r08_c07"
TARGETS = {
    "ledger": SESSION / "current-coverage-ledger.json",
    "session": SESSION / "session-state.json",
    "batch": ART / "builtin_q64_production/current-batch.json",
    "catalog": ART / "production_catalog.json",
    "status": ART / "status.json",
}
STYLE_OLD = ROOT / "designs/guild-ui-v2/source/guild-overview.png"
STYLE_CURRENT = ROOT / "designs/gameplay-ui/04-guild.png"
STYLE_SHA = "85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6"
SHA = re.compile(r"^[0-9a-f]{64}$")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    return json.loads(raw.decode("utf-8-sig"))


def normal(value, base=ART):
    value = str(value).replace("\\", "/")
    if value.lower().startswith("e:/work/image/"):
        value = str(ROOT) + "/" + value[len("E:/work/image/"):]
    p = Path(value)
    return (p if p.is_absolute() else base / p).resolve()


def key(path):
    return str(normal(path)).casefold()


def png_dimensions(raw):
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise ValueError("Not a PNG IHDR")
    return list(struct.unpack(">II", raw[16:24]))


class Audit:
    def __init__(self):
        self.observed = {}
        self.refs = {}
        self.errors = []
        self.warnings = []
        self.deleted = {}
        self.manifests = []
        self.snapshots = {}
        self.visited = set()
        self.hashless_paths = set()
        self.summary = {}

    def read(self, path):
        path = normal(path)
        raw = path.read_bytes()
        actual = digest(raw)
        if str(path) in self.observed and self.observed[str(path)] != actual:
            raise ValueError(f"Input changed during verification: {path}")
        self.observed[str(path)] = actual
        return raw

    def expect(self, condition, message):
        if not condition:
            self.errors.append(message)
        return condition

    def ref(self, path, sha, origin, *, required_current=False, pixels=None):
        path = normal(path)
        if not isinstance(sha, str) or not SHA.fullmatch(sha.lower()):
            self.errors.append(f"Invalid SHA at {origin}: {sha}")
            return None
        sha = sha.lower()
        ident = (key(path), sha)
        if ident in self.refs:
            row = self.refs[ident]
            row["origins"].append(origin)
            if required_current and row["status"] != "current_bytes_exact":
                self.errors.append(f"Required current evidence unavailable as exact bytes: {path}")
            return row
        row = {"file": str(path), "expectedSha256": sha, "origins": [origin],
               "currentByteVerificationPassed": False, "status": "unverified"}
        self.refs[ident] = row
        # Host cache locations are historical receipts, not project dependencies.
        if not path.is_relative_to(ROOT):
            row["status"] = "historical_host_cache_not_required_or_reverified"
            if required_current:
                self.errors.append(f"Required current evidence outside project: {path}")
            return row
        if path.exists():
            raw = self.read(path)
            actual = digest(raw)
            row["actualSha256"] = actual
            if actual == sha:
                row.update(status="current_bytes_exact", currentByteVerificationPassed=True)
            elif path.suffix.lower() in (".json", ".jsonl", ".txt", ".md", ".py") and digest(raw.replace(b"\r\n", b"\n")) == sha and not required_current:
                row.update(status="historical_text_sha_reconstructed_by_exact_crlf_to_lf",
                           transformation="replace CRLF bytes with LF only; current raw SHA differs")
            else:
                snapshot = self.snapshots.get(ident)
                if snapshot and digest(self.read(snapshot)) == sha and not required_current:
                    row.update(status="historical_text_exact_snapshot_current_file_changed", exactSnapshot=str(snapshot))
                else:
                    row["status"] = "sha_mismatch"
                    self.errors.append(f"SHA mismatch: {path}; {origin}")
            if pixels is not None:
                try:
                    dims = png_dimensions(raw)
                    row["actualPixels"] = dims
                    self.expect(dims == pixels, f"PNG dimensions wrong: {path} {dims} != {pixels}")
                except ValueError as exc:
                    self.errors.append(f"{path}: {exc}")
            return row
        if not required_current and key(path) == key(STYLE_OLD) and sha == STYLE_SHA:
            raw = self.read(STYLE_CURRENT)
            if digest(raw) == sha:
                row.update(status="same_sha_current_style_alias", actualRetainedPath=str(STYLE_CURRENT), actualSha256=sha)
                return row
        proof = self.deleted.get(ident)
        if proof and not required_current:
            row.update(status="deleted_by_user_not_reverified", deletionEvidence=proof,
                       reason="Exact historical path and SHA match deletion plan plus receipt/log; original bytes unavailable")
            return row
        row["status"] = "required_current_missing" if required_current else "missing_without_exact_deletion_proof"
        self.errors.append(f"Missing evidence without permitted exact proof: {path}; {origin}")
        return row

    def pointer(self, value, origin, **kwargs):
        return self.ref(value.get("file") or value["path"], value["sha256"], origin, **kwargs)

    def load_cleanup(self, directory, modern):
        directory = normal(directory)
        receipt_path = directory / ("receipt.json" if modern else "deletion-receipt.json")
        receipt = decode(self.read(receipt_path))
        plan_path = directory / "plan.json" if modern else normal(receipt["plan"])
        plan_raw = self.read(plan_path)
        self.ref(plan_path, receipt["planSha256"], "cleanup receipt -> plan", required_current=modern)
        plan = decode(plan_raw)
        log_path = directory / "deleted-files.jsonl"
        log_raw = self.read(log_path)
        log = [decode(line) for line in log_raw.splitlines() if line.strip()]
        scope = normal(receipt["scopeRoot"])
        if modern:
            planned = {key(x["file"]): x for x in plan["items"] if x["action"] == "delete"}
            retained = [x for x in plan["items"] if x["action"] == "keep"]
        else:
            planned = {key(x["file"]): x for x in plan["delete"]}
            retained = []  # This old keep inventory predates later authorized cleanup.
        expected_count = receipt["deletedCount"] if modern else receipt["deletedFiles"]
        self.expect(len(log) == expected_count == len(planned), f"Cleanup count mismatch: {directory}")
        self.expect(sum(x["bytes"] for x in log) == receipt["deletedBytes"], f"Cleanup byte total mismatch: {directory}")
        self.expect(len({key(x["file"]) for x in log}) == len(log), f"Duplicate cleanup rows: {directory}")
        for item in log:
            p = normal(item["file"])
            expected = planned.get(key(p))
            if not self.expect(p.is_relative_to(scope) and expected is not None and expected["sha256"] == item["sha256"] and expected["bytes"] == item["bytes"], f"Cleanup row lacks exact plan match: {p}"):
                continue
            if modern:
                self.expect(not p.exists(), f"Recorded deleted file exists again: {p}")
            self.deleted[(key(p), item["sha256"])] = {"plan": str(plan_path), "planSha256": digest(plan_raw),
                "receipt": str(receipt_path), "receiptSha256": self.observed[str(receipt_path)],
                "log": str(log_path), "logSha256": digest(log_raw), "bytes": item["bytes"]}
        for item in retained:
            self.pointer(item, "current cleanup keep list", required_current=True)
        self.manifests.append({"directory": str(directory), "loggedDeleted": len(log), "retainedChecked": len(retained),
                               "status": "metadata_plan_receipt_and_log_checked_not_deleted_byte_verification"})

    def references(self, obj, loc="root"):
        """Yield explicit path/SHA pairs only, including request/response schemas."""
        if isinstance(obj, list):
            for i, value in enumerate(obj):
                yield from self.references(value, f"{loc}[{i}]")
        elif isinstance(obj, dict):
            emitted = set()
            for field in ("file", "path", "toolResponse", "snapshot", "source"):
                if isinstance(obj.get(field), str) and isinstance(obj.get("sha256"), str):
                    emitted.add((obj[field], obj["sha256"]))
                    yield obj[field], obj["sha256"], f"{loc}.{field}"
            for field, value in obj.items():
                if not isinstance(value, str) or not any(value.lower().endswith(s) for s in (".png", ".jpg", ".json", ".jsonl", ".txt", ".md", ".py", ".npy")):
                    continue
                # Examples: promptFile/promptSha256; request/requestSha256.
                stems = [field]
                for suffix in ("File", "Path"):
                    if field.endswith(suffix):
                        stems.append(field[:-len(suffix)])
                for stem in stems:
                    candidate_sha = obj.get(stem + "Sha256")
                    if isinstance(candidate_sha, str) and (value, candidate_sha) not in emitted:
                        emitted.add((value, candidate_sha))
                        yield value, candidate_sha, f"{loc}.{field}"
                        break
            if isinstance(obj.get("referenced_image_paths"), list):
                self.hashless_paths.update(key(x) for x in obj["referenced_image_paths"])
            for field, value in obj.items():
                yield from self.references(value, f"{loc}.{field}")

    def graph(self, path, *, depth=0):
        path = normal(path)
        if str(path) in self.visited or path.suffix.lower() != ".json" or not path.is_relative_to(C07):
            return
        if depth > 14:
            self.errors.append(f"Provenance traversal limit: {path}")
            return
        self.visited.add(str(path))
        obj = decode(self.read(path))
        for snapshot in obj.get("textSnapshots", []) if isinstance(obj, dict) else []:
            self.snapshots[(key(snapshot["source"]), snapshot["sha256"])] = normal(snapshot["snapshot"])
        for file, sha, field in self.references(obj):
            p = normal(file)
            row = self.ref(p, sha, f"{path.name}:{field}")
            if row and row["status"] in ("current_bytes_exact", "historical_text_sha_reconstructed_by_exact_crlf_to_lf"):
                self.graph(p, depth=depth+1)

    def topology(self, ledger):
        tiles = {x["tile"]: x for x in ledger["tiles"]}
        expected_tiles = {f"r{r:02}_c{c:02}" for r in range(1,17) for c in range(1,17)}
        self.expect(len(ledger["tiles"]) == 256 and set(tiles) == expected_tiles, "256 tile coordinate topology mismatch")
        seams, junctions = {}, {}
        for r in range(1,17):
            for c in range(1,17):
                t = f"r{r:02}_c{c:02}"
                self.expect(tiles[t]["pixelRectXYWH"] == [(c-1)*4096,(r-1)*4096,4096,4096], f"Tile pixel rect mismatch {t}")
                if c < 16:
                    other = f"r{r:02}_c{c+1:02}"
                    seams[t+"|"+other] = ([t,other], "vertical_boundary", c*4096, (r-1)*4096)
                if r < 16:
                    other = f"r{r+1:02}_c{c:02}"
                    seams[t+"|"+other] = ([t,other], "horizontal_boundary", r*4096, (c-1)*4096)
                if r < 16 and c < 16:
                    junctions[f"junction_{t}"] = ([t,f"r{r:02}_c{c+1:02}",f"r{r+1:02}_c{c:02}",f"r{r+1:02}_c{c+1:02}"],[c*4096,r*4096])
        self.expect(len(ledger["seams"]) == 480 and {x["id"] for x in ledger["seams"]} == set(seams), "480 seam topology mismatch")
        self.expect(len(ledger["junctions"]) == 225 and {x["id"] for x in ledger["junctions"]} == set(junctions), "225 junction topology mismatch")
        candidates = {t:x["candidate"] for t,x in tiles.items() if x["candidateExists"]}
        for t, item in tiles.items():
            self.expect(item["formalArtAcceptancePassed"] is False and item["clientRuntimeAccepted"] is False, f"Unexpected accepted tile: {t}")
            if t in candidates:
                self.pointer(candidates[t], f"selected tile {t}", required_current=True, pixels=[4096,4096])
                c = candidates[t]
                for field in ("record", "qa", "review", "assembly", "interiorReview"):
                    if isinstance(c.get(field), dict):
                        self.pointer(c[field], f"selected {t} {field}", required_current=False)
                    elif isinstance(c.get(field), str) and c.get(field+"Sha256"):
                        self.ref(c[field], c[field+"Sha256"], f"selected {t} {field}")
        for item in ledger["seams"]:
            expected = seams[item["id"]]
            self.expect((item["tiles"],item["axis"],item["boundaryCoordinate"],item["spanStart"]) == expected and item["spanLength"] == 4096, f"Seam geometry mismatch {item['id']}")
            self.expect(item["bothCandidatesPresent"] == all(t in candidates for t in item["tiles"]), f"Seam presence mismatch {item['id']}")
        for item in ledger["junctions"]:
            self.expect((item["tiles"],item["pixelXY"]) == junctions[item["id"]], f"Junction geometry mismatch {item['id']}")
            self.expect(item["allCandidatesPresent"] == all(t in candidates for t in item["tiles"]), f"Junction presence mismatch {item['id']}")
        for item in ledger["seams"] + ledger["junctions"]:
            self.expect(item["wholeCityArtGatePassed"] is False, f"Unexpected whole-city pass {item['id']}")
            binding = item.get("scopedReviewCandidateSha256ByTile") or item.get("inheritedReviewSelectionBinding",{}).get("candidateSha256ByTile")
            if binding:
                exact = {t:candidates[t]["sha256"] for t in item["tiles"] if t in candidates}
                self.expect(binding == exact, f"Scoped review SHA tuple mismatch {item['id']}")
        counts = ledger["counts"]
        expected = {"tiles":256,"candidateTiles":len(candidates),"missingCandidates":256-len(candidates),"seams":480,"junctions":225,
                    "seamsWithBothCandidates":sum(x["bothCandidatesPresent"] for x in ledger["seams"]),
                    "junctionsWithAllCandidates":sum(x["allCandidatesPresent"] for x in ledger["junctions"]),
                    "formalArtAcceptedTiles":0,"wholeCityPassedSeams":0,"wholeCityPassedJunctions":0}
        for field, value in expected.items():
            self.expect(counts[field] == value, f"Ledger count mismatch {field}")
        self.summary["coverage"] = expected
        return candidates

    def checkpoint(self):
        raw = {k:self.read(p) for k,p in TARGETS.items()}
        docs = {k:decode(v) for k,v in raw.items()}
        ledger, state = docs["ledger"], docs["session"]
        self.expect(state["coverageLedgerSha256"] == digest(raw["ledger"]), "session -> ledger SHA mismatch")
        candidates = self.topology(ledger)
        for field in ("productionAcceptedTiles","completeCityDeliveries"):
            self.expect(state[field] == 0, f"Unexpected formal/delivery state {field}")
        for field in ("allVisualChecksPassed","runtimePublished","deliveryReady","formalManifestProduced"):
            self.expect(state[field] is False, f"Unexpected completion claim {field}")
        self.expect(state["candidateCoordinateCountIncludingWorkInProgress"] == len(candidates), "session candidate count mismatch")
        self.expect(state["coordinatesWithoutAny4KCandidate"] == 256-len(candidates), "session missing count mismatch")
        for name in ("batch","catalog","status"):
            active = docs[name]["activeProductionRun"]
            self.expect(active["sessionStateSha256"] == digest(raw["session"]), f"{name} -> session SHA mismatch")
            self.expect(active.get("coverageLedgerSha256") == digest(raw["ledger"]), f"{name} -> ledger SHA mismatch")
            self.expect(active["formalAcceptedTileCount"] == 0 and active["deliveryReady"] is False, f"Unexpected formal state in {name}")
            self.expect(active["candidateCoordinatesIncludingWorkInProgress"] == len(candidates), f"{name} current count mismatch")
            self.expect(active["actualBackendModel"] is None and active["actualQuality"] is None and active["backendModelVerified"] is False, f"Unverifiable model claim in {name}")
            for ref in active.get("currentRetentionEvidence", []):
                self.pointer(ref, name+" currentRetentionEvidence", required_current=True)
        for name in ("catalog","status"):
            self.expect(docs[name].get("currentBatchSha256") == digest(raw["batch"]), f"{name} -> current-batch SHA mismatch")
        for field in ("acceptedDeliveryTileCount", "wholeCityCompletedCount"):
            self.expect(docs["batch"][field] == 0, f"Unexpected batch acceptance count {field}")
        for field in ("completedCurrentDeliveryTiles", "completedWholeCityCount"):
            self.expect(docs["status"][field] == 0, f"Unexpected status acceptance count {field}")
        for variant in docs["catalog"]["variants"]:
            self.expect(variant["productionTilesAccepted"] == 0 and variant["runtimePublished"] is False,
                        f"Unexpected catalog formal/runtime claim {variant['city']}_{variant['variant']}")
        for ref in state.get("currentRetentionEvidence", []):
            self.pointer(ref, "session currentRetentionEvidence", required_current=True)
        for field in ("retainedNativeInventory", "latestCheckpointSelection"):
            if state.get(field):
                self.pointer(state[field], "session "+field, required_current=True)
        if state.get("retainedNativeInventory"):
            inv = decode(self.read(normal(state["retainedNativeInventory"]["file"])))
            self.expect(inv["physicalFileCount"] == len(inv["sources"]) == state["allAppearanceRetainedNativeKnownCountExcludingReferences"], "Retained source count mismatch")
            self.expect(len({key(x["file"]) for x in inv["sources"]}) == len(inv["sources"]), "Duplicate retained source paths")
            for item in inv["sources"]:
                self.pointer(item, "inventory observation source still physically present", required_current=True, pixels=item["pixels"])
                self.pointer(item["record"], "inventory observation generation record", required_current=True)
            # Concurrent generation can legitimately add sources after the checkpoint
            # observation. Do not describe its old count as the current global count.
            known = {key(x["file"]) for x in inv["sources"]}
            snapshot_at = datetime.fromisoformat(inv["observedAtUtc"].replace("Z", "+00:00"))
            additions = []
            for p in SESSION.rglob("*.png"):
                if key(p) in known:
                    continue
                adjacent_records = (p.with_suffix(".record.json"), p.with_suffix(".generation.json"), Path(str(p)+".generation.json"))
                rp = next((x for x in adjacent_records if x.exists()), None)
                if rp is None:
                    continue
                rd_raw = self.read(rp)
                rd = decode(rd_raw)
                if rd.get("tool") != "image_gen.imagegen" and rd.get("route") not in ("builtin", "builtin_image_gen"):
                    continue
                sha = rd.get("nativeSha256") or rd.get("sha256")
                if not isinstance(sha, str) or not SHA.fullmatch(sha):
                    continue
                self.ref(p, sha, "source observed outside older inventory observation", required_current=True, pixels=[1254,1254])
                evidence_times = []
                for field in ("createdAtUtc", "recordedAtUtc", "observedCompletionAt", "observedCompletionAtUtc", "completedAtUtcObserved"):
                    value = rd.get(field)
                    if isinstance(value, str):
                        try:
                            value = value.replace(" UTC", "+00:00").replace("Z", "+00:00")
                            parsed = datetime.fromisoformat(value)
                            if parsed.tzinfo is not None:
                                evidence_times.append({"field":field,"value":rd[field],"afterSnapshot":parsed > snapshot_at})
                        except ValueError:
                            pass
                after = any(x["afterSnapshot"] for x in evidence_times)
                additions.append({"file":str(p),"sha256":sha,"record":str(rp),"recordSha256":digest(rd_raw),
                    "status":"not_in_old_observation_new_source_after_snapshot" if after else "not_in_old_observation_time_not_established",
                    "timestampEvidence":evidence_times,"partOfSharedInventoryCount":False,
                    "candidateOrAcceptanceClaim":False})
            self.summary["retainedNativeInventoryObservation"] = {"snapshotObservedAtUtc":inv["observedAtUtc"],
                "snapshotRecordedPhysicalFileCount":inv["physicalFileCount"],
                "snapshotSourcesStillPresentAndReverified":len(inv["sources"]),
                "isClaimOfGlobalCurrentNativeCount":False,"additionalSourcesObservedDuringThisReadOnlyAudit":additions,
                "additionalDiscoveryScope":"session PNGs with adjacent generation records; no image or shared counter changed"}
        selector = C07 / "latest-candidate.json"
        selected = decode(self.read(selector))
        self.expect("r08_c07" in candidates and candidates["r08_c07"]["sha256"] == selected["candidate"]["sha256"], "c07 selector is not current ledger selection")
        for field in ("candidate","record","assembly","review","interiorReview"):
            self.pointer(selected[field], "c07 latest selector "+field, required_current=True,
                         pixels=[4096,4096] if field == "candidate" else None)
        self.expect(selected["accepted"] is False and selected["formalArtAcceptancePassed"] is False and selected["clientRuntimeAccepted"] is False, "c07 selector formal flag error")
        self.expect(selected["actualModel"] is None and selected["actualQuality"] is None and selected["backendModelVerified"] is False,
                    "c07 selector asserts undisclosed backend model or quality")
        # Assembly snapshots must be registered before examining mutable source scripts.
        assembly = decode(self.read(normal(selected["assembly"]["file"])))
        for snap in assembly["textSnapshots"]:
            self.snapshots[(key(snap["source"]),snap["sha256"])] = normal(snap["snapshot"])
        self.expect(assembly["nativeSourceCount"] == 16 and len(assembly["sources"]) == 16, "c07 assembly must bind 16 native source patches")
        self.expect(assembly["method"]["upscaled"] is False and assembly["method"]["resampling"] == "none", "c07 source assembly method changed")
        self.graph(selector)
        interior = decode(self.read(normal(selected["interiorReview"]["file"])))
        self.expect(interior["candidate"]["sha256"] == selected["candidate"]["sha256"], "c07 interior review candidate mismatch")
        expected_boxes = {(c*1024,r*1024,(c+1)*1024,(r+1)*1024) for r in range(4) for c in range(4)}
        self.expect(len(interior["items"]) == 16 and {tuple(x["boxLTRB"]) for x in interior["items"]} == expected_boxes, "c07 sixteen interior review coverage mismatch")
        self.summary["selectedC07"] = {"sha256":selected["candidate"]["sha256"], "pixels":[4096,4096],
            "recordedInternalSeams":selected["internalFullSeamsReviewed"], "recordedInternalJunctions":selected["internalJunctionsReviewed"],
            "recordedInteriors":len(interior["items"]), "freshVisualReviewByThisVerifier":False,
            "formalAccepted":False, "clientRuntimeAccepted":False}
        covered_paths = {x[0] for x in self.refs}
        unbound = sorted(self.hashless_paths - covered_paths)
        self.summary["requestReferencePathsWithoutAnySourceHashBinding"] = unbound
        self.expect(not unbound, "Some actual request image paths have no traversed SHA binding")

    def finish(self):
        changed = []
        for p, sha in self.observed.items():
            if not Path(p).exists() or digest(Path(p).read_bytes()) != sha:
                changed.append(p)
        self.errors.extend(f"Input changed during read-only audit: {p}" for p in changed)
        counts = Counter(x["status"] for x in self.refs.values())
        return {"schemaVersion":1,"verifiedAtUtc":datetime.now(timezone.utc).isoformat(),
            "purpose":"selected checkpoint bytes/topology/provenance metadata verification only",
            "passedRequiredChecks":not self.errors, "errorCount":len(self.errors),"errors":self.errors,"warnings":self.warnings,
            "sourceStatusCounts":dict(counts),"deletionManifests":self.manifests,"summary":self.summary,
            "freshVisualReviewPerformed":False,"productionAccepted":False,"runtimeVerified":False,
            "deletedSourcesReverified":False,"imageFilesWrittenOrDeleted":False,"sharedFilesWritten":False,
            "observedCurrentFileSha256":self.observed,"references":list(self.refs.values()),
            "scriptSha256":digest(Path(__file__).read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", default=str(HERE / "verification"))
    args = parser.parse_args()
    a = Audit()
    try:
        a.load_cleanup(ART / "cleanup-current-assets", False)
        a.load_cleanup(C07 / "continuation-20260923/cleanup-selected-c07", True)
        a.checkpoint()
    except Exception as exc:
        a.errors.append(f"Audit could not complete: {type(exc).__name__}: {exc}")
    report = a.finish()
    directory = normal(args.output_directory)
    if not directory.is_relative_to(HERE):
        raise ValueError("Report directory must be beneath verifier directory")
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / ("selected-checkpoint-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"report":str(output),"sha256":digest(output.read_bytes()),"passedRequiredChecks":report["passedRequiredChecks"],
                      "errorCount":report["errorCount"],"errors":report["errors"],"sourceStatusCounts":report["sourceStatusCounts"],"summary":report["summary"]}, ensure_ascii=False))
    raise SystemExit(0 if report["passedRequiredChecks"] else 1)


if __name__ == "__main__":
    main()
