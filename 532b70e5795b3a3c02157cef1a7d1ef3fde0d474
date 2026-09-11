"""Capture and audit new/changed active artwork without modifying any source.

Compares live asset hashes with inventory.json. Complete captured bytes are
saved before visual measurement in backups/<sha256><extension>. The baseline
inventory and processing records are never written. Re-running replaces only
supplementary_inventory.json and latest review contact sheets; cached metrics
for an unchanged captured hash are reused.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

from PIL import Image, ImageDraw

import audit_inventory as audit

REPO = audit.REPO
PACKAGE = audit.PACKAGE
BASELINE = PACKAGE / "inventory.json"
OUTPUT = PACKAGE / "supplementary_inventory.json"
BACKUPS = PACKAGE / "backups"
REVIEW = PACKAGE / "review"
ELIGIBLE = {"formal", "prepared_copy", "derived", "source_or_matte"}
MEASUREMENT_KEYS = {"size", "mode", "alpha_range", "alpha_measurement", "frames", "sample_method", "metrics"}


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scan_active():
    skipped = Counter()
    files = []
    pruned = audit.INFRA | audit.REFERENCE_DIRS | {PACKAGE.name.lower()}
    for current, directories, names in os.walk(REPO):
        directories[:] = sorted(d for d in directories if d.lower() not in pruned and not (Path(current) / d).is_symlink())
        for name in sorted(names):
            path = Path(current) / name
            if path.suffix.lower() not in audit.EXTENSIONS or path.is_symlink():
                continue
            category, reason = audit.classify(path)
            if category in ELIGIBLE:
                files.append((path, category, reason))
            else:
                skipped[category] += 1
    return sorted(files, key=lambda row: row[0].relative_to(REPO).as_posix()), dict(skipped)


def stable_bytes(path):
    for attempt in range(3):
        before = path.stat()
        data = path.read_bytes()
        after = path.stat()
        if (before.st_mtime_ns, before.st_size) == (after.st_mtime_ns, after.st_size) and len(data) == after.st_size:
            return data, after, utcnow()
    raise RuntimeError("Source changed during three consecutive capture reads; retry after the producing task finishes")


def save_snapshot(data, sha, extension):
    target = BACKUPS / (sha + extension)
    if target.exists():
        if digest(target) != sha:
            raise RuntimeError("Existing content-addressed backup has mismatched bytes: " + str(target))
        return target, False
    BACKUPS.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="capture-", suffix=".tmp", dir=BACKUPS, delete=False) as temporary:
        temporary.write(data)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, target)
    return target, True


def contact_sheets(assets, groups, renderer, capture_time):
    by_path = {a["path"]: a for a in assets}
    representatives = []
    priority = {"formal": 0, "source_or_matte": 1, "derived": 2, "prepared_copy": 3}
    for group in groups:
        row = min((by_path[p] for p in group["paths"]), key=lambda a: (priority[a["classification"]], len(a["path"]), a["path"]))
        group["review_representative"] = row["path"]
        representatives.append((group, row))
    representatives.sort(key=lambda pair: pair[1]["path"])
    label_font, title_font = audit.font(12), audit.font(20)
    cw, ch, header = 236, 214, 42
    sheets = []
    for page in range(math.ceil(len(representatives) / 60)):
        portion = representatives[page*60:(page+1)*60]
        canvas = Image.new("RGB", (cw*6, header+ch*10), "#25282b")
        draw = ImageDraw.Draw(canvas)
        draw.text((10, 8), f"Latest capture {page+1:02d} | New/changed originals | {capture_time[:19]}", fill="#ededed", font=title_font)
        cells = []
        for cell, (group, row) in enumerate(portion):
            x, y = (cell%6)*cw+8, (cell//6)*ch+header
            tile = Image.new("RGB", (220,160), "#808080")
            try:
                sample, _ = audit.read_sample(REPO / row["snapshot_path"], renderer)
                sample.thumbnail((220,160), Image.Resampling.LANCZOS)
                tile.paste(sample, ((220-sample.width)//2,(160-sample.height)//2), sample.getchannel("A"))
                sample.close()
            except Exception as exc:
                ImageDraw.Draw(tile).text((5,60), "Snapshot preview unavailable", font=label_font, fill="white")
                row["contact_error"] = str(exc)
            canvas.paste(tile,(x,y))
            number = page*60+cell+1
            label = f"{number:04d} {group['id']} {Path(row['path']).name}"
            draw.text((x,y+164), audit.fit_label(draw,label,label_font),font=label_font,fill="#ededed")
            m=row.get("metrics",{})
            draw.text((x,y+181), f"{row['change_type']}  W {m.get('nearwhite_fraction',0):.1%} B {m.get('bright_fraction',0):.1%}",font=label_font,fill="#b8c3cd")
            draw.text((x,y+197),audit.fit_label(draw,row["path"].split("/")[0],label_font),font=label_font,fill="#98a7b1")
            cells.append({"number":number,"cell":cell,"row":cell//6,"column":cell%6,"group_id":group["id"],"path":row["path"],"snapshot_path":row["snapshot_path"],"all_paths":group["paths"]})
        target=REVIEW / f"latest-{page+1:02d}.jpg"
        canvas.save(target,quality=91,subsampling=0)
        canvas.close()
        sheets.append({"file":target.relative_to(REPO).as_posix(),"page":page+1,"size":[cw*6,header+ch*10],"cells":cells})
    result={"schema":"qdao.exposure.contacts.v1","snapshot_time":capture_time,"purpose":"Only new/changed originals rendered from immutable captured bytes; never production grading inputs","unique_groups_covered":len(representatives),"columns":6,"rows":10,"max_image_size":[220,160],"sheets":sheets}
    audit.write_json(REVIEW / "latest-contacts.json",result)
    return result


def processing_state():
    """Refresh read-only processing hash knowledge if its file revision changed."""
    target = PACKAGE / "processing.json"
    if not target.exists():
        return {}, None
    stat = target.stat()
    marker = (stat.st_mtime_ns, stat.st_size)
    if getattr(processing_state, "_marker", None) != marker:
        document = json.loads(target.read_text("utf-8"))
        rows = document.get("records", [])
        if isinstance(rows, dict):
            rows = list(rows.values())
        by_path = defaultdict(list)
        for row in rows:
            if row.get("path"):
                by_path[row["path"].replace("\\", "/")].append(row)
        processing_state._marker = marker
        processing_state._paths = dict(by_path)
    return processing_state._paths, marker


def known_processing_version(path, sha):
    rows, _ = processing_state()
    matches = []
    for record in rows.get(path, []):
        fields = [field for field in ("original_sha256", "output_sha256") if record.get(field) == sha]
        if fields:
            matches.append({"fields": fields,
                            "original_sha256": record.get("original_sha256"),
                            "output_sha256": record.get("output_sha256"),
                            "status": record.get("status")})
    return matches


def revision_history(previous):
    if not previous:
        return []
    history = list(previous.get("source_history", []))
    if previous.get("latest_sha") not in {r.get("latest_sha") for r in history}:
        fields = MEASUREMENT_KEYS | {"path", "latest_sha", "audit_sha", "sha256", "bytes",
                                    "snapshot_path", "snapshot_time", "extension", "change_type"}
        history.append({key: value for key, value in previous.items() if key in fields})
    return history


def retain_report_row(previous, live_sha, capture_time, status, known=None):
    row = dict(previous)
    row.update({"live_sha256": live_sha, "last_observed_time": capture_time,
                "capture_status": status, "captured_this_run": False,
                "needs_processing": status == "unchanged_previous_capture",
                "measurement_reused_without_recalculation": True})
    if known:
        row["processing_matches"] = known
        row["report_snapshot_is_current_processing_original"] = any(
            match["original_sha256"] == row["latest_sha"] for match in known)
    else:
        row.pop("processing_matches", None)
        row.pop("report_snapshot_is_current_processing_original", None)
    return row


def main():
    capture_time = utcnow()
    baseline = json.loads(BASELINE.read_text("utf-8"))
    baseline_assets = {a["path"]: a for a in baseline["assets"]}
    previous_by_path = {}
    if OUTPUT.exists():
        old = json.loads(OUTPUT.read_text("utf-8"))
        previous_by_path = {a["path"]: a for a in old.get("assets", [])}
    candidates, skipped = scan_active()
    REVIEW.mkdir(parents=True, exist_ok=True)
    records = []
    errors = []
    scanned_paths = set()
    new_backups = 0
    reused_metrics = 0
    skipped_versions = Counter()
    new_captures = []
    renderer = None
    try:
        for number, (path, category, reason) in enumerate(candidates, 1):
            rel = path.relative_to(REPO).as_posix()
            scanned_paths.add(rel)
            original = baseline_assets.get(rel)
            audit_sha = original.get("sha256") if original else None
            previous = previous_by_path.get(rel)
            try:
                current_sha = digest(path)
                known = known_processing_version(rel, current_sha)
                if known:
                    skipped_versions["known_processing_version"] += 1
                    if previous:
                        records.append(retain_report_row(previous, current_sha, capture_time,
                                       "retained_known_processing_version", known))
                        reused_metrics += 1
                    continue
                if current_sha == audit_sha:
                    skipped_versions["unchanged_audit_version"] += 1
                    if previous:
                        records.append(retain_report_row(previous, current_sha, capture_time,
                                       "retained_snapshot_live_reverted_to_audit"))
                        reused_metrics += 1
                    continue
                if previous and current_sha == previous.get("latest_sha"):
                    skipped_versions["unchanged_previous_capture"] += 1
                    records.append(retain_report_row(previous, current_sha, capture_time,
                                   "unchanged_previous_capture"))
                    reused_metrics += 1
                    continue
                data, source_stat, snapshot_time = stable_bytes(path)
                latest_sha = hashlib.sha256(data).hexdigest()
                # Refresh after the complete byte read: another task may publish concurrently.
                known = known_processing_version(rel, latest_sha)
                if known or latest_sha == audit_sha:
                    skipped_versions["known_version_during_capture"] += 1
                    if previous:
                        records.append(retain_report_row(
                            previous, latest_sha, capture_time,
                            "retained_known_processing_version" if known else "retained_snapshot_live_reverted_to_audit",
                            known))
                        reused_metrics += 1
                    del data
                    continue
                if previous and latest_sha == previous.get("latest_sha"):
                    skipped_versions["unchanged_previous_capture"] += 1
                    records.append(retain_report_row(previous, latest_sha, capture_time,
                                   "unchanged_previous_capture"))
                    reused_metrics += 1
                    del data
                    continue
                snapshot, created = save_snapshot(data, latest_sha, path.suffix.lower())
                new_backups += int(created)
                del data
                row = {"path": rel, "sha256": latest_sha, "latest_sha": latest_sha, "audit_sha": audit_sha,
                       "bytes": source_stat.st_size, "extension": path.suffix.lower(), "classification": category,
                       "classification_reason": reason, "treatment_included": True,
                       "change_type": "changed_since_audit" if original else "new_since_audit",
                       "snapshot_time": snapshot_time, "snapshot_path": snapshot.relative_to(REPO).as_posix(),
                       "source_mtime_ns": source_stat.st_mtime_ns,
                       "source_mtime_utc": datetime.fromtimestamp(source_stat.st_mtime, timezone.utc).isoformat(),
                       "measurement_input": "Complete immutable captured bytes, not live path or contact thumbnail",
                       "capture_status": "new_revision_captured", "captured_this_run": True,
                       "needs_processing": True, "live_sha256": latest_sha,
                       "last_observed_time": snapshot_time, "source_history": revision_history(previous),
                       "measurement_reused_without_recalculation": False}
                try:
                    if renderer is None:
                        renderer = audit.SvgRenderer()
                    sample, metadata = audit.read_sample(snapshot, renderer)
                    row.update(metadata)
                    row["metrics"] = audit.metrics(sample)
                    sample.close()
                except Exception as exc:
                    row["read_error"] = str(exc)
                after = path.stat()
                row["live_changed_after_capture"] = (after.st_mtime_ns, after.st_size) != (source_stat.st_mtime_ns, source_stat.st_size)
                records.append(row)
                new_captures.append({"path": rel, "latest_sha": latest_sha,
                                     "previous_latest_sha": previous.get("latest_sha") if previous else None,
                                     "audit_sha": audit_sha, "snapshot_path": row["snapshot_path"]})
            except Exception as exc:
                errors.append({"path": rel, "error": str(exc)})
                if previous:
                    row = retain_report_row(previous, None, capture_time, "retained_snapshot_capture_error")
                    row["capture_error"] = str(exc)
                    records.append(row)
            if number % 100 == 0:
                print(f"Scanned {number}/{len(candidates)}; captured {len(new_captures)} new revisions", flush=True)
        for rel, previous in previous_by_path.items():
            if rel not in scanned_paths:
                records.append(retain_report_row(previous, None, capture_time,
                               "retained_snapshot_path_missing_or_excluded"))
                reused_metrics += 1
        records.sort(key=lambda row: row["path"])
        hashes = defaultdict(list)
        for row in records:
            hashes[row["latest_sha"]].append(row["path"])
        groups = [{"id": f"L{n:04d}", "sha256": sha, "latest_sha": sha, "paths": paths, "count": len(paths)}
                  for n, (sha, paths) in enumerate(hashes.items(), 1)]
        if renderer is None and groups:
            renderer = audit.SvgRenderer()
        contacts = contact_sheets(records, groups, renderer, capture_time)
        missing = [a["path"] for a in baseline["assets"] if a.get("treatment_included") and a["path"] not in scanned_paths]
        captured = [row for row in records if row.get("captured_this_run")]
        summary = {"active_files_scanned": len(candidates), "new_or_changed_files": len(new_captures),
                   "new_captures_this_run": len(new_captures), "supplementary_report_files": len(records),
                   "by_capture_status": dict(Counter(r["capture_status"] for r in records)),
                   "skipped_versions": dict(skipped_versions),
                   "by_change_type": dict(Counter(r["change_type"] for r in records)),
                   "by_classification": dict(Counter(r["classification"] for r in records)),
                   "by_top_directory": dict(Counter(r["path"].split("/")[0] for r in records)),
                   "new_captures_by_top_directory": dict(Counter(r["path"].split("/")[0] for r in captured)),
                   "unique_byte_groups": len(groups), "new_backup_files": new_backups,
                   "reused_cached_metrics": reused_metrics,
                   "contact_sheets": len(contacts["sheets"]),
                   "contact_unique_groups_covered": contacts["unique_groups_covered"],
                   "read_errors": [{"path": r["path"], "error": r["read_error"]} for r in records if "read_error" in r],
                   "capture_errors": errors,
                   "changed_again_after_capture": [r["path"] for r in captured if r.get("live_changed_after_capture")],
                   "baseline_active_paths_now_missing_or_excluded": missing, "noneligible_files_skipped": skipped}
        manifest = {"schema": "qdao.exposure.inventory.v1", "inventory_kind": "supplementary_latest",
                    "created_utc": capture_time, "snapshot_time": capture_time, "repo": str(REPO),
                    "baseline_inventory": BASELINE.relative_to(REPO).as_posix(),
                    "audit_created_utc": baseline.get("created_utc"), "read_only_assets": True,
                    "snapshots_are_complete_original_bytes": True,
                    "statistics_policy": baseline.get("statistics_policy"),
                    "revision_policy": {
                        "known_processing_versions": "Skip a live SHA matching original_sha256 or output_sha256 for the SAME PATH in current processing records; refresh processing knowledge if that file changes.",
                        "previous_capture": "Reuse only the same path's same captured SHA; retain existing supplementary rows as report evidence without measuring them again.",
                        "latest_sha": "Latest captured original SHA, which may differ from live_sha256 after an already-known exposure output is published.",
                        "new_revision": "Capture only a SHA different from the same path's known processing versions, audit SHA and previous captured SHA.",
                        "history": "Prior captured original revisions remain in per-asset source_history and immutable backup files. processing.json is never written."},
                    "package_boundaries": {
                        "qdao_character_diversity_v9": "01-22 delivered portraits overwrite q_daoist_character_pack_4096; .work raw/reference/process files are excluded. The v9 manifest is an index, not another portrait output set.",
                        "unity_slices": "31 png/ exports are runtime sprites; sources/ are final artwork snapshots retained in source coverage. sprite-overview and unity-sprite-preview are presentation/validation views, not runtime textures; included by the original audit classification.",
                        "v8": "Entire exposure-refinement package excluded from input scan, including previous processed outputs, snapshots and review images."},
                    "summary": summary, "new_captures_this_run": new_captures,
                    "assets": records, "groups": groups,
                    "contacts": "qdao_exposure_refinement_v8/review/latest-contacts.json"}
        audit.write_json(OUTPUT, manifest)
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
        print("NEW REVISIONS", json.dumps(new_captures, ensure_ascii=False, indent=2), flush=True)
    finally:
        if renderer is not None:
            renderer.close()


if __name__ == "__main__":
    main()
