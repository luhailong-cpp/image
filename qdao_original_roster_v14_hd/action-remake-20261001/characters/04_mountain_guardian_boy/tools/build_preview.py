#!/usr/bin/env python3
"""Inspect real action frames, then build a local preview and technical manifest.

No PNG is created or modified. Only this character's directory may be written.
Numbering is one-based by default; use --index-base 0 for frame_00.png.

    python tools/build_preview.py --check
    python tools/build_preview.py
    python tools/build_preview.py --anchor-x 512 --anchor-y 860

Generation records: frame_01.generation.json is preferred. A sibling
generation.json may instead have a `frames` mapping keyed by filename or stem,
or a list whose items contain `file`, `filename`, `path`, or `output_path`.
A shared record without a matching frame entry is reported as shared/unbound.
The tool never treats a target model, quality, or output size as actual evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "run": {"label": "跑步", "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], "count": 16, "frame_ms": 30},
    "hit": {"label": "受击", "directions": ["E", "W"], "count": 6, "frame_ms": 40},
    "attack": {"label": "普攻", "directions": ["E", "W"], "count": 12, "frame_ms": 30},
    "cast": {"label": "施法", "directions": ["E", "W"], "count": 16, "frame_ms": 45},
}
COLOR_MODES = {0: "L", 2: "RGB", 3: "P", 4: "LA", 6: "RGBA"}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def safe_output(path: Path) -> Path:
    result = path.resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError(f"输出路径越过本角色目录：{result}")
    return result


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def png_info(path: Path) -> dict:
    with path.open("rb") as stream:
        header = stream.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("文件不是具有有效 IHDR 的 PNG")
    width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", header[16:29])
    info = {
        "width": width, "height": height, "bit_depth": depth,
        "color_mode": COLOR_MODES.get(color, f"unknown_{color}"),
        "alpha_channel": color in (4, 6), "alpha_extrema": None,
        "nonzero_alpha_bbox_diagnostic_only": None,
        "decoder_verified": False, "decoder_note": None,
    }
    try:
        from PIL import Image
    except ImportError:
        info["decoder_note"] = "Pillow 不可用；仅验证 PNG 文件头，未确认解码、实际透明像素或可见边界。"
        return info
    with Image.open(path) as source:
        source.load()
        info["decoder_verified"] = True
        if source.mode == "RGBA":
            alpha = source.getchannel("A")
            info["alpha_extrema"] = list(alpha.getextrema())
            bbox = alpha.getbbox()
            info["nonzero_alpha_bbox_diagnostic_only"] = list(bbox) if bbox else None
        else:
            info["decoder_note"] = f"实际解码模式为 {source.mode}；未转换或改写文件。"
    return info


def find_frame_record(payload: dict | list, frame: Path):
    entries = payload.get("frames") if isinstance(payload, dict) else payload
    if isinstance(entries, dict):
        for key in (frame.name, frame.stem, relative(frame)):
            if key in entries:
                return entries[key]
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            for key in ("file", "filename", "path", "output_path"):
                value = item.get(key)
                if isinstance(value, str) and value.replace("\\", "/").split("/")[-1] == frame.name:
                    return item
    return None


def source_info(frame: Path) -> dict:
    individual = frame.with_suffix(".generation.json")
    shared = frame.parent / "generation.json"
    record_path = individual if individual.is_file() else shared if shared.is_file() else None
    result = {
        "record_path": None, "record_sha256": None, "binding": "missing",
        "record_error": None, "declared_record": None,
        "evidence_note": "逐图原始声明仅供审阅；此工具不据配置或提示词推断实际模型、质量、原生尺寸或独立姿态。",
    }
    if record_path is None:
        return result
    result.update(record_path=relative(record_path), record_sha256=file_sha256(record_path))
    try:
        payload = json.loads(record_path.read_text(encoding="utf-8-sig"))
        if record_path == individual:
            result.update(binding="individual_sidecar", declared_record=payload)
        else:
            match = find_frame_record(payload, frame)
            if match is None:
                result.update(binding="shared_unbound", declared_record=payload)
            else:
                result.update(binding="shared_frame_entry", declared_record=match)
    except (OSError, ValueError) as error:
        result["record_error"] = str(error)
    return result


def inspect(index_base: int, anchor_x: float | None, anchor_y: float | None) -> dict:
    sequences = []
    hash_paths: dict[str, list[str]] = {}
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            frames = []
            for ordinal in range(spec["count"]):
                index = ordinal + index_base
                path = ROOT / "frames" / action / direction / f"frame_{index:02d}.png"
                frame = {
                    "ordinal": ordinal + 1, "file_index": index, "path": relative(path),
                    "exists": path.is_file(), "sha256": None, "png": None,
                    "source": None, "technical_issues": [],
                    "canvas_rgba_matches": False, "visual_review": "not_assessed_by_tool",
                    "native_single_frame_minimum_1024_verified": None,
                    "independent_pose_verified": None,
                }
                if path.is_file():
                    frame["sha256"] = file_sha256(path)
                    hash_paths.setdefault(frame["sha256"], []).append(relative(path))
                    frame["source"] = source_info(path)
                    try:
                        info = png_info(path)
                        frame["png"] = info
                        if (info["width"], info["height"]) != (1024, 1024):
                            frame["technical_issues"].append("正式画布尺寸不符 1024×1024")
                        if info["color_mode"] != "RGBA":
                            frame["technical_issues"].append("PNG 文件头不是 RGBA")
                        if info["alpha_extrema"] == [255, 255]:
                            frame["technical_issues"].append("全图不透明；须核实透明背景")
                        if info["alpha_extrema"] == [0, 0]:
                            frame["technical_issues"].append("全图透明，没有可见人物")
                        frame["canvas_rgba_matches"] = info["width"] == 1024 and info["height"] == 1024 and info["color_mode"] == "RGBA"
                    except (OSError, ValueError, SyntaxError) as error:
                        frame["technical_issues"].append(f"PNG 无法检查：{error}")
                    if frame["source"]["binding"] in ("missing", "shared_unbound"):
                        frame["technical_issues"].append("缺少可绑定此帧的逐图来源记录")
                    if frame["source"]["record_error"]:
                        frame["technical_issues"].append("来源记录 JSON 无法读取")
                frames.append(frame)
            sequences.append({
                "action": action, "label": spec["label"], "direction": direction,
                "target_count": spec["count"], "frame_ms": spec["frame_ms"],
                "duration_ms": spec["count"] * spec["frame_ms"], "frames": frames,
            })
    all_frames = [frame for sequence in sequences for frame in sequence["frames"]]
    duplicate_groups = [paths for paths in hash_paths.values() if len(paths) > 1]
    expected_paths = {frame["path"] for frame in all_frames}
    unexpected = sorted(relative(p) for p in (ROOT / "frames").rglob("*.png") if relative(p) not in expected_paths) if (ROOT / "frames").exists() else []
    return {
        "schema": "qdao-action-technical-manifest-v1", "character_id": ROOT.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "index_base": index_base,
        "canvas": {"width": 1024, "height": 1024, "required_mode": "RGBA", "display_policy": "whole_canvas_fixed_transform"},
        "root_anchor": {"x": anchor_x, "y": anchor_y, "units": "canvas_pixels", "status": "declared_for_preview" if anchor_x is not None and anchor_y is not None else "not_declared"},
        "limitations": [
            "输出尺寸不证明原生单帧输入分辨率。",
            "文件存在、SHA 不同、技术格式符合均不证明美术、姿态或动画通过。",
            "不裁剪、不缩放包围盒、不逐帧最低像素贴地、不补帧、不镜像。",
            "此工具不生成命中或施法释放标记；须在视觉审阅后另行确认。",
        ],
        "summary": {
            "target_frames": len(all_frames), "present_frames": sum(f["exists"] for f in all_frames),
            "missing_frames": sum(not f["exists"] for f in all_frames),
            "canvas_rgba_matching_frames": sum(f["canvas_rgba_matches"] for f in all_frames),
            "decoder_verified_frames": sum(bool(f["png"] and f["png"]["decoder_verified"]) for f in all_frames),
            "bound_source_records": sum(bool(f["source"] and not f["source"]["record_error"] and f["source"]["binding"] in ("individual_sidecar", "shared_frame_entry")) for f in all_frames),
            "visual_pass_count": None, "client_integration_status": "not_checked_by_tool",
        },
        "duplicate_sha_groups": duplicate_groups, "unexpected_png_files": unexpected,
        "sequences": sequences,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只输出统计和问题；不写文件")
    parser.add_argument("--index-base", type=int, choices=(0, 1), default=1)
    parser.add_argument("--anchor-x", type=float)
    parser.add_argument("--anchor-y", type=float)
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifest.technical.json")
    parser.add_argument("--preview", type=Path, default=ROOT / "preview" / "index.html")
    args = parser.parse_args()
    if (args.anchor_x is None) != (args.anchor_y is None):
        parser.error("根锚点必须同时给出 --anchor-x 与 --anchor-y；未确定时均省略。")
    report = inspect(args.index_base, args.anchor_x, args.anchor_y)
    if not args.check:
        manifest_path = safe_output(args.manifest)
        preview_path = safe_output(args.preview)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Generate browser paths from each actual output location. URLs never fetch remote assets.
        import os
        preview_report = json.loads(json.dumps(report))
        for sequence in preview_report["sequences"]:
            for frame in sequence["frames"]:
                frame["url"] = quote(os.path.relpath(ROOT / frame["path"], preview_path.parent).replace("\\", "/"), safe="/:")
        payload = json.dumps(preview_report, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        template = (ROOT / "preview" / "template.html").read_text(encoding="utf-8")
        preview_path.write_text(template.replace("__FRAME_MANIFEST_JSON__", payload), encoding="utf-8")
    result = {"summary": report["summary"], "duplicate_sha_groups": report["duplicate_sha_groups"], "unexpected_png_files": report["unexpected_png_files"]}
    if not args.check:
        result.update(manifest=str(manifest_path), preview=str(preview_path))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
