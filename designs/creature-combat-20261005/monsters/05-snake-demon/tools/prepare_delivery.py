#!/usr/bin/env python3
"""Validate snake combat frames and build honest, offline review artifacts.

Requires Pillow only. Does not generate, transform, delete, or modify runtime art
or its provenance. --check-only never writes files. Run without that switch only
when the production owner is ready to assemble the delivery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path(__file__).with_name("preview.template.html")
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
LABELS = {"hit": "受击", "attack": "普攻", "cast": "施法"}
DIRECTIONS = {"E": "敌方斜前 · 朝右下", "W": "我方真斜后 · 朝左上"}
EXPECTED_SIZE = (1024, 1024)
PIVOT = [0.5, 0.08]
ANCHOR_TOP_LEFT = [512, 942]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_output(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Output escapes this character directory: {path}")
    return path


def resolve_ref(value: str, record_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    beside = record_path.parent / path
    return beside if beside.exists() else ROOT / path


def provenance(image_path: Path, digest: str) -> tuple[dict, list[str], list[str]]:
    """Validate current record and retained provenance without inventing metadata."""
    candidates = [Path(str(image_path) + ".generation.json"), image_path.with_suffix(".generation.json")]
    record_path = next((p for p in candidates if p.is_file()), candidates[0])
    summary = {"record": rel(record_path), "present": record_path.is_file(),
               "actualModel": None, "actualQuality": None, "targetModel": None,
               "targetQuality": None, "chain": []}
    errors: list[str] = []
    warnings: list[str] = []
    if not record_path.is_file():
        return summary, ["missing_generation_record"], warnings

    visited: set[Path] = set()

    def visit(path: Path, expected_sha: str | None = None) -> dict | None:
        resolved = path.resolve()
        if resolved in visited:
            return None
        visited.add(resolved)
        try:
            data = load_json(path)
            if not isinstance(data, dict):
                raise ValueError("record root must be an object")
        except (OSError, ValueError) as exc:
            errors.append(f"unreadable_generation_record:{rel(path)}:{exc}")
            return None
        summary["chain"].append(rel(path))
        recorded_sha = data.get("sha256", data.get("outputSha256"))
        if not isinstance(recorded_sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", recorded_sha):
            errors.append(f"invalid_record_sha256:{rel(path)}")
        elif expected_sha and recorded_sha.lower() != expected_sha.lower():
            errors.append(f"record_sha256_mismatch:{rel(path)}")

        if data.get("derivedFrom"):
            if not data.get("operation"):
                errors.append(f"missing_derivation_operation:{rel(path)}")
            sources = data["derivedFrom"]
            if isinstance(sources, dict):
                sources = [sources]
            if not isinstance(sources, list) or not sources:
                errors.append(f"invalid_derivedFrom:{rel(path)}")
                return data
            for source in sources:
                if not isinstance(source, dict):
                    errors.append(f"invalid_derivation_source:{rel(path)}")
                    continue
                source_hash = source.get("sha256", source.get("sourceSha256"))
                source_record = source.get("generationRecord", source.get("record", source.get("generation")))
                if not source_hash or not re.fullmatch(r"[a-fA-F0-9]{64}", str(source_hash)):
                    errors.append(f"invalid_source_sha256:{rel(path)}")
                if not source.get("file", source.get("path")):
                    errors.append(f"missing_source_file_identity:{rel(path)}")
                if not isinstance(source_record, str):
                    errors.append(f"missing_source_record_reference:{rel(path)}")
                    continue
                source_path = resolve_ref(source_record, path)
                if source_path.is_file():
                    visit(source_path, source_hash)
                else:
                    errors.append(f"missing_retained_source_record:{source_record}")
            return data

        # Unknown model / quality is valid only when explicitly recorded as unknown.
        required = ["file", "generatedAt", "width", "height", "format", "tool", "route",
                    "configSnapshot", "submittedParameters", "actualModel", "actualQuality",
                    "evidence", "prompt", "references"]
        for key in required:
            if key not in data:
                errors.append(f"missing_provenance_field:{rel(path)}:{key}")
        if "generatedAt" in data:
            try:
                stamp = datetime.fromisoformat(str(data["generatedAt"]).replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    errors.append(f"generation_time_missing_timezone:{rel(path)}")
            except ValueError:
                errors.append(f"invalid_generation_time:{rel(path)}")
        config = data.get("configSnapshot")
        if not isinstance(config, dict):
            errors.append(f"invalid_config_snapshot:{rel(path)}")
            config = {}
        for key in ["model", "quality", "builtin_product", "verified_on", "sources"]:
            if key not in config:
                errors.append(f"missing_config_snapshot_field:{rel(path)}:{key}")
        submitted = data.get("submittedParameters")
        if not isinstance(submitted, dict) or not all(k in submitted for k in ["model", "quality"]):
            errors.append(f"missing_submitted_model_quality_fields:{rel(path)}")
        if (data.get("actualModel") is None or data.get("actualQuality") is None) and not data.get("unverifiedReason"):
            errors.append(f"missing_unverified_reason:{rel(path)}")
        if not data.get("evidence"):
            errors.append(f"empty_tool_evidence:{rel(path)}")
        prompt = data.get("prompt")
        if isinstance(prompt, str) and not resolve_ref(prompt, path).is_file():
            errors.append(f"missing_prompt_file:{prompt}")
        if not isinstance(data.get("references"), list) or not data.get("references"):
            errors.append(f"missing_creation_references:{rel(path)}")
        # Historical source pixels may legitimately have been removed after export.
        # The retained record and hash remain mandatory; do not demand a backup image.
        for key, value in [("actualModel", data.get("actualModel")), ("actualQuality", data.get("actualQuality")),
                           ("targetModel", config.get("model")), ("targetQuality", config.get("quality"))]:
            if summary[key] is None:
                summary[key] = value
        summary["unverifiedReason"] = data.get("unverifiedReason")
        return data

    visit(record_path, digest)
    return summary, errors, warnings


def inspect_frame(path: Path, action: str, direction: str, index: int, review: dict) -> dict:
    entry = {"file": rel(path), "action": action, "direction": direction, "frame": index,
             "width": None, "height": None, "durationMs": ACTIONS[action][1],
             "pivot": PIVOT, "anchorTopLeftPx": ANCHOR_TOP_LEFT,
             "event": None, "present": path.is_file(), "sha256": None, "pixelSha256": None,
             "visualStatus": review.get("frames", {}).get(rel(path), {}).get("status", "pending"),
             "visualReview": review.get("frames", {}).get(rel(path), {}), "errors": [], "warnings": []}
    if not path.is_file():
        entry["errors"].append("missing_frame")
        return entry
    entry["sha256"] = sha(path)
    try:
        with Image.open(path) as im:
            im.load()
            entry.update(width=im.width, height=im.height, format=im.format, mode=im.mode)
            if im.format != "PNG":
                entry["errors"].append("not_png")
            if im.mode != "RGBA":
                entry["errors"].append("not_native_rgba")
            if im.size != EXPECTED_SIZE:
                entry["errors"].append("wrong_dimensions")
            rgba = im.convert("RGBA")
            entry["pixelSha256"] = hashlib.sha256(rgba.tobytes()).hexdigest()
            alpha = rgba.getchannel("A")
            histogram = alpha.histogram()
            bbox = alpha.getbbox()
            edge_pixels = (sum(1 for a in alpha.crop((0, 0, im.width, 1)).getdata() if a)
                           + sum(1 for a in alpha.crop((0, im.height - 1, im.width, im.height)).getdata() if a)
                           + sum(1 for a in alpha.crop((0, 1, 1, im.height - 1)).getdata() if a)
                           + sum(1 for a in alpha.crop((im.width - 1, 1, im.width, im.height - 1)).getdata() if a))
            entry["alpha"] = {"min": alpha.getextrema()[0], "max": alpha.getextrema()[1],
                              "transparentPixels": histogram[0], "opaquePixels": histogram[255],
                              "partialPixels": sum(histogram[1:255]), "visibleBounds": list(bbox) if bbox else None,
                              "nonTransparentEdgePixels": edge_pixels}
            if not bbox:
                entry["errors"].append("empty_visible_image")
            if histogram[0] == 0:
                entry["errors"].append("no_fully_transparent_pixels")
            if edge_pixels:
                entry["errors"].append("visible_pixels_touch_canvas_boundary")
            if bbox:
                entry["alpha"]["marginPx"] = [bbox[0], bbox[1], im.width - bbox[2], im.height - bbox[3]]
                if min(entry["alpha"]["marginPx"]) < 8:
                    entry["warnings"].append("visible_subject_within_8px_of_boundary")
    except (OSError, ValueError) as exc:
        entry["errors"].append(f"unreadable_png:{exc}")
    source, errors, warnings = provenance(path, entry["sha256"])
    entry["source"] = source
    entry["errors"].extend(errors)
    entry["warnings"].extend(warnings)
    entry["event"] = review.get("frames", {}).get(rel(path), {}).get("event")
    return entry


def build_manifest(review: dict) -> dict:
    frames = [inspect_frame(ROOT / "runtime" / action / direction / f"{i:02}.png", action, direction, i, review)
              for action, (count, _) in ACTIONS.items() for direction in DIRECTIONS for i in range(1, count + 1)]
    duplicates = []
    for key in ["sha256", "pixelSha256"]:
        buckets: dict[str, list[dict]] = defaultdict(list)
        for frame in frames:
            if frame[key]:
                buckets[frame[key]].append(frame)
        for digest, same in buckets.items():
            if len(same) > 1:
                duplicates.append({"kind": key, "hash": digest, "files": [f["file"] for f in same]})
                for frame in same:
                    frame["errors"].append(f"duplicate_{key}")
    expected = {f["file"] for f in frames}
    extra = sorted(rel(p) for p in (ROOT / "runtime").rglob("*.png") if rel(p) not in expected) if (ROOT / "runtime").exists() else []
    groups = []
    for action, (count, duration) in ACTIONS.items():
        for direction in DIRECTIONS:
            subset = [f for f in frames if f["action"] == action and f["direction"] == direction]
            key = f"{action}/{direction}"
            group_review = review.get("groups", {}).get(key, {})
            groups.append({"id": key, "action": action, "actionLabel": LABELS[action], "direction": direction,
                           "directionLabel": DIRECTIONS[direction], "expectedFrames": count,
                           "presentFrames": sum(f["present"] for f in subset), "durationMs": duration,
                           "totalDurationMs": count * duration, "frames": [f["file"] for f in subset],
                           "visualStatus": group_review.get("visualStatus", "pending"),
                           "normalPlaybackStatus": group_review.get("normalPlaybackStatus", "pending"),
                           "slowPlaybackStatus": group_review.get("slowPlaybackStatus", "pending"),
                           "adjacencyStatus": group_review.get("adjacencyStatus", "pending"), "review": group_review})
    errors = [{"file": f["file"], "issues": f["errors"]} for f in frames if f["errors"]]
    warnings = [{"file": f["file"], "issues": f["warnings"]} for f in frames if f["warnings"]]
    return {"schemaVersion": 1, "character": {"slug": "05-snake-demon", "name": "蛇妖"},
            "assembledAtUTC": datetime.now(timezone.utc).isoformat(),
            "scope": ["hit", "attack", "cast"], "dimensions": [1024, 1024], "expectedFrames": 68,
            "presentFrames": sum(f["present"] for f in frames), "pivot": PIVOT, "anchorTopLeftPx": ANCHOR_TOP_LEFT,
            "coordinateSystem": "unmodified 1024x1024 export canvas; anchor uses top-left pixels; pivot uses bottom-left normalized coordinates",
            "technicalStatus": "failed" if errors or extra else "passed",
            "clientAcceptanceStatus": review.get("clientAcceptanceStatus", "not_tested"),
            "reviewEvidence": review, "groups": groups, "frames": frames,
            "validation": {"errors": errors, "warnings": warnings, "extraRuntimePngs": extra, "duplicates": duplicates,
                           "limitations": ["Technical checks do not prove anatomical continuity, independent AI poses, direction correctness, or art quality.",
                                           "No game client integration or acceptance is performed by this script.",
                                           "Native vs exported image dimensions and true model version must come from generation evidence."]}}


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    canvas = Image.new("RGB", size, "#d3d7df")
    draw = ImageDraw.Draw(canvas)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if ((x // cell) + (y // cell)) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill="#edf0f5")
    return canvas


def contact_sheet(group: dict, frames: dict[str, dict], thumb: int) -> tuple[Path, dict]:
    cols = min(4, group["expectedFrames"])
    rows = (group["expectedFrames"] + cols - 1) // cols
    header, label_h, pad = 48, 34, 10
    sheet = Image.new("RGB", (cols * (thumb + pad) + pad, rows * (thumb + label_h + pad) + header + pad), "#111827")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    draw.text((pad, 14), f"Snake demon | {group['id']} | {group['durationMs']} ms/frame | QA ONLY", fill="white", font=font)
    sources = []
    for i, name in enumerate(group["frames"]):
        x = pad + (i % cols) * (thumb + pad)
        y = header + pad + (i // cols) * (thumb + label_h + pad)
        cell = checkerboard((thumb, thumb))
        frame = frames[name]
        if frame["present"]:
            try:
                with Image.open(ROOT / name) as image:
                    rgba = image.convert("RGBA")
                    rgba.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
                    cell.paste(rgba, ((thumb - rgba.width) // 2, (thumb - rgba.height) // 2), rgba)
                sources.append({"file": name, "sha256": frame["sha256"], "generationRecord": frame.get("source", {}).get("record")})
            except (OSError, ValueError):
                ImageDraw.Draw(cell).text((12, 12), "UNREADABLE", fill="#b91c1c", font=font)
        else:
            ImageDraw.Draw(cell).text((12, 12), "MISSING", fill="#b91c1c", font=font)
        sheet.paste(cell, (x, y))
        color = "#fca5a5" if frame["errors"] else "#a7f3d0"
        draw.text((x, y + thumb + 5), f"{i + 1:02} | {len(frame['errors'])} error(s)", fill=color, font=font)
    path = safe_output(f"qa/contact-{group['action']}-{group['direction']}.jpg")
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=94, subsampling=0)
    record = {"file": rel(path), "sha256": sha(path), "createdAtUTC": datetime.now(timezone.utc).isoformat(),
              "usage": "QA contact sheet only; not a generated pose or runtime asset", "derivedFrom": sources,
              "operation": f"uniform whole-canvas thumbnail to {thumb}px; composite over QA checkerboard; add labels; no frame alignment or pose modification"}
    write_json(Path(str(path) + ".generation.json"), record)
    return path, record


def assemble(manifest: dict, thumb: int) -> None:
    write_json(safe_output("manifest.json"), manifest)
    report = {k: manifest[k] for k in ["assembledAtUTC", "expectedFrames", "presentFrames", "technicalStatus", "clientAcceptanceStatus", "validation"]}
    write_json(safe_output("qa/technical-report.json"), report)
    frame_map = {f["file"]: f for f in manifest["frames"]}
    contacts = []
    for group in manifest["groups"]:
        path, _ = contact_sheet(group, frame_map, thumb)
        contacts.append(rel(path))
    payload = json.dumps({"manifest": manifest, "contacts": contacts}, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DELIVERY_DATA__*/null", payload)
    path = safe_output("preview/index.html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    lines = ["# 蛇妖逐帧来源索引", "", f"正式帧 {manifest['presentFrames']}/68；技术状态：{manifest['technicalStatus']}。",
             "", "型号与质量仅逐图引用来源证据；未知值保持未确认。技术检查不替代美术、动态或客户端验收。", "",
             "| 帧 | 来源记录 | 配置目标 | 实际型号 / 质量 | 技术问题 |", "|---|---|---|---|---|"]
    for frame in manifest["frames"]:
        src = frame.get("source", {})
        target = f"{src.get('targetModel') or '未记录'} / {src.get('targetQuality') or '未记录'}"
        actual = f"{src.get('actualModel') or '未确认'} / {src.get('actualQuality') or '未确认'}"
        record = f"[{src['record']}]({src['record']})" if src.get("present") else "缺失"
        lines.append(f"| [{frame['file']}]({frame['file']}) | {record} | {target} | {actual} | {', '.join(frame['errors']) or '无'} |")
    safe_output("provenance-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="inspect and print JSON summary; write nothing")
    parser.add_argument("--review", type=Path, help="optional manually documented review JSON; never inferred by this tool")
    parser.add_argument("--contact-size", type=int, default=256, choices=range(128, 513), metavar="128..512")
    args = parser.parse_args()
    review = load_json(args.review) if args.review else {}
    if not isinstance(review, dict):
        parser.error("--review must contain a JSON object")
    manifest = build_manifest(review)
    if not args.check_only:
        assemble(manifest, args.contact_size)
    summary = {"root": str(ROOT), "writesPerformed": not args.check_only,
               "expectedFrames": 68, "presentFrames": manifest["presentFrames"],
               "technicalStatus": manifest["technicalStatus"], "framesWithErrors": len(manifest["validation"]["errors"]),
               "missingFrames": [f["file"] for f in manifest["frames"] if not f["present"]],
               "extraRuntimePngs": manifest["validation"]["extraRuntimePngs"],
               "duplicateSets": len(manifest["validation"]["duplicates"]),
               "clientAcceptanceStatus": manifest["clientAcceptanceStatus"]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if manifest["technicalStatus"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
