"""Read-only/in-memory verification of GIF palette grading against real assets."""

from __future__ import annotations

import argparse
import io
import json
import struct
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from gif_grade import gif_structure_bytes, grade_gif_bytes, inspect_gif_bytes


def _grade(colors):
    return np.rint(colors.astype(np.float32) * 0.85).astype(np.uint8)


def check_pair(original: bytes, output: bytes) -> dict:
    assert len(original) == len(output)
    assert gif_structure_bytes(original) == gif_structure_bytes(output)
    before_palettes, before_stats = inspect_gif_bytes(original)
    after_palettes, after_stats = inspect_gif_bytes(output)
    assert before_stats == after_stats
    for left, right in zip(before_palettes, after_palettes):
        for index in left.transparent_indices:
            start = left.start + index * 3
            assert original[start:start + 3] == output[start:start + 3]
    frame_results = []
    with Image.open(io.BytesIO(original)) as left, Image.open(io.BytesIO(output)) as right:
        assert left.size == right.size and left.n_frames == right.n_frames
        assert left.info.get("loop") == right.info.get("loop")
        for index in range(left.n_frames):
            left.seek(index)
            right.seek(index)
            assert left.mode == right.mode
            assert left.info.get("duration") == right.info.get("duration")
            assert left.info.get("transparency") == right.info.get("transparency")
            assert left.disposal_method == right.disposal_method
            assert left.dispose_extent == right.dispose_extent
            left_rgba = np.asarray(left.convert("RGBA"))
            right_rgba = np.asarray(right.convert("RGBA"))
            assert np.array_equal(left_rgba[..., 3], right_rgba[..., 3])
            transparent = left_rgba[..., 3] == 0
            assert np.array_equal(left_rgba[transparent, :3], right_rgba[transparent, :3])
            frame_results.append({
                "frame": index,
                "pil_mode": left.mode,
                "duration_ms": left.info.get("duration"),
                "disposal": left.disposal_method,
                "dispose_extent": list(left.dispose_extent),
                "visible_rgb_changed_pixels": int(np.count_nonzero(np.any(left_rgba[..., :3] != right_rgba[..., :3], axis=2) & ~transparent)),
                "alpha_and_hidden_rgb_unchanged": True,
            })
    return {"status": "passed", "frames": frame_results, "parser": before_stats}


def _shared_palette_fixture():
    # Three 1x1 images: two share the global table but use different transparent
    # indices; the third uses its own local table and another transparent index.
    palette = bytes([240, 230, 220, 210, 200, 190, 180, 170, 160, 150, 140, 130])
    result = bytearray(b"GIF89a" + struct.pack("<HHBBB", 1, 1, 0x81, 0, 0) + palette)
    result.extend(b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00")
    for index, local, delay in ((0, False, 5), (1, False, 8), (2, True, 11)):
        result.extend(b"\x21\xf9\x04" + struct.pack("<BHB", 9, delay, index) + b"\x00")
        result.extend(b"\x2c" + struct.pack("<HHHHB", 0, 0, 1, 1, 0x81 if local else 0))
        if local:
            result.extend(palette)
        # GIF LZW clear=4, one pixel=index, end=5, packed least-significant first.
        packed = 4 | (index << 3) | (5 << 6)
        result.extend(b"\x02\x02" + struct.pack("<H", packed) + b"\x00")
    result.extend(b"\x3b")
    return bytes(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parents[1] / "gif_audit.json")
    args = parser.parse_args()
    names = subprocess.check_output(["rg", "--files", "-g", "*.gif", "-g", "*.GIF"], cwd=args.root, text=True).splitlines()
    names = sorted(name for name in names if not name.replace("\\", "/").startswith("qdao_exposure_refinement_v8/"))
    documents = []
    for name in names:
        original = (args.root / name).read_bytes()
        output, stats = grade_gif_bytes(original, _grade)
        assert stats["modified"]
        identity, identity_stats = grade_gif_bytes(original, lambda colors: colors)
        assert identity == original and not identity_stats["modified"]
        documents.append({"path": name.replace("\\", "/"), "grade_stats": stats, "checks": check_pair(original, output)})
    fixture = _shared_palette_fixture()
    fixture_output, fixture_stats = grade_gif_bytes(fixture, _grade)
    palettes, _ = inspect_gif_bytes(fixture)
    assert palettes[0].transparent_indices == {0, 1}
    assert palettes[1].transparent_indices == {2}
    fixture_checks = check_pair(fixture, fixture_output)
    report = {
        "status": "passed",
        "real_gif_count": len(documents),
        "real_frame_count": sum(item["grade_stats"]["frame_count"] for item in documents),
        "unsupported_real_gifs": [],
        "real_assets_modified": False,
        "checks": ["all_nonpalette_bytes_identical", "same_length", "same_canvas", "same_frames", "same_lzw_and_indices", "same_delay_disposal_loop_extent", "same_pil_modes", "same_alpha_each_frame", "same_hidden_rgb_each_frame", "all_transparent_palette_rgb_protected", "identity_callback_byte_exact", "shared_global_palette_multiple_transparency_indices", "separate_local_palette_transparency"],
        "documents": documents,
        "shared_palette_fixture": {"grade_stats": fixture_stats, "checks": fixture_checks},
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "real_gif_count", "real_frame_count", "unsupported_real_gifs", "real_assets_modified")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
