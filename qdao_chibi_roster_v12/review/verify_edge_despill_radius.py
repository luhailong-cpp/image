"""Regression on frozen real S/NW frames; never modifies candidate/formal art."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path(__file__).resolve().parent / "edge-despill-qc"
sys.path.insert(0, str(ROOT))
import edge_despill
import process_roster


def digest(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def distance_squared(mask, limit=12):
    """Independent padded-window distance to alpha <= 8, sufficient for this audit."""
    h, w = mask.shape
    background = np.pad(~mask, limit, constant_values=True)
    result = np.full((h, w), (limit + 1) ** 2, dtype=np.int16)
    for dy in range(-limit, limit + 1):
        for dx in range(-limit, limit + 1):
            dd = dx * dx + dy * dy
            if dd <= limit * limit:
                nearby = background[limit + dy:limit + dy + h, limit + dx:limit + dx + w]
                result[nearby] = np.minimum(result[nearby], dd)
    return result


def masks(image):
    a = np.asarray(image)
    r, g, b = a[:, :, :3].astype(np.int16).transpose(2, 0, 1)
    visible = a[:, :, 3] > 8
    magenta = (r - g >= 12) & (b - g >= 12) & (b * 5 >= r * 4) & visible
    red = (r - g >= 30) & (r * 10 > b * 13)
    return a, visible, magenta, red


def render(crop, translation):
    result = Image.new("RGBA", (512, 512))
    result.paste(crop, tuple(translation))
    return result


def backdrop(image, color=(38, 55, 55, 255)):
    result = Image.new("RGBA", image.size, color)
    result.alpha_composite(image)
    return result.convert("RGB")


def main():
    baseline = json.loads((EVIDENCE / "baseline-before.json").read_text(encoding="utf-8"))
    report = {"status": "running", "baseline_edge_despill_sha256": baseline["edge_despill_before_sha256"],
              "current_edge_despill_sha256": process_roster.sha(ROOT / "edge_despill.py"),
              "current_processor_sha256": process_roster.sha(ROOT / "process_roster.py"),
              "baseline_file_sha256": process_roster.sha(EVIDENCE / "baseline-before.json"), "cases": []}
    comparisons = []
    for case in baseline["cases"]:
        image_path = EVIDENCE / case["input"]
        assert process_roster.sha(image_path) == case["input_png_sha256"]
        image = Image.open(image_path).convert("RGBA")
        assert digest(image) == case["input_rgba_sha256"]
        direct, direct_stats = edge_despill.despill(image)
        default_v2, _ = process_roster.normalize(image, 1, True)
        default_v3, _ = process_roster.prepare_alignment_v3(image, 1, True)
        assert digest(direct) == case["expected_default_direct_rgba_sha256"], case["id"]
        assert digest(default_v2) == case["expected_default_v2_rgba_sha256"], case["id"]
        assert digest(default_v3) == case["expected_default_v3_rgba_sha256"], case["id"]
        assert direct_stats["radius_px"] == 2 and direct_stats["reference_radius_px"] == 6
        assert np.array_equal(np.asarray(direct), np.asarray(edge_despill.despill(image, 2, 6)[0]))
        before = render(default_v3, case["translation_px"])
        assert digest(before) == case["existing_candidate_rgba_sha256"]
        # Candidate paths are observations only; this script never writes them.
        changed_external_since_baseline = process_roster.sha(Path(case["existing_candidate_path"])) != case["existing_candidate_png_sha256"]
        cleaned, record = process_roster.prepare_alignment_v3(image, 1, True, 4)
        stats = record["edge_despill"]
        assert stats["radius_px"] == 4 and stats["reference_radius_px"] == 12
        after = render(cleaned, case["translation_px"])
        original = render(process_roster.prepare_alignment_v3(image, 1, False)[0], case["translation_px"])
        raw, fg, _, red = masks(original)
        a, _, remaining, _ = masks(after)
        b, _, previous_remaining, _ = masks(before)
        depth = distance_squared(fg)
        changed = np.any(a[:, :, :3] != raw[:, :, :3], axis=2)
        delta = np.any(a != b, axis=2)
        assert np.array_equal(raw[:, :, 3], a[:, :, 3]), case["id"]
        assert np.array_equal(raw[:, :, 1], a[:, :, 1]), case["id"]
        assert not np.any(changed & ((depth > 16) | ~fg)), case["id"]
        assert not np.any(changed & red), case["id"]
        assert np.all(a[:, :, [0, 2]] <= raw[:, :, [0, 2]]), case["id"]
        assert not np.any(delta & ((depth > 16) | ~fg)), case["id"]
        assert stats["maximum_distance_to_alpha_le_8_px"] <= 4
        assert stats["maximum_clean_reference_distance_px"] <= 12
        changed_deep = delta & (depth > 4)
        extra_coordinates = []
        for y, x in zip(*np.where(delta & previous_remaining)):
            if len(extra_coordinates) >= 12:
                break
            extra_coordinates.append({"xy": [int(x), int(y)], "before_rgba": b[y, x].tolist(),
                                      "after_rgba": a[y, x].tolist(), "distance_px": round(float(depth[y, x]) ** .5, 5)})
        summary = {"id": case["id"], "default_direct_v2_v3_exactly_match_frozen_baseline": True,
                   "candidate_changed_externally_since_baseline": changed_external_since_baseline,
                   "radius4_stats": stats, "delta_vs_radius2_pixels": int(delta.sum()),
                   "newly_changed_beyond_2px": int(changed_deep.sum()),
                   "magenta_before": int(previous_remaining.sum()), "magenta_after": int(remaining.sum()),
                   "magenta_inside4_before": int((previous_remaining & (depth <= 16)).sum()),
                   "magenta_inside4_after": int((remaining & (depth <= 16)).sum()),
                   "alpha_green_geometry_red_protection_passed": True,
                   "examples_final512_coordinates": extra_coordinates,
                   "before_rgba_sha256": digest(before), "after_rgba_sha256": digest(after)}
        report["cases"].append(summary)
        if case["id"] in ("NW-idle-00", "NW-walk-01", "S-idle-00"):
            before.save(EVIDENCE / (case["id"] + "-radius2.png"))
            after.save(EVIDENCE / (case["id"] + "-radius4.png"))
            if case["id"] == "NW-idle-00":
                assert summary["newly_changed_beyond_2px"] > 0
                assert summary["magenta_after"] < summary["magenta_before"]
                assert summary["magenta_inside4_after"] < summary["magenta_inside4_before"]
            comparisons.append((case["id"], before, after))
    # Exercise opt-in parsing at the CLI boundary, without starting an export.
    help_run = subprocess.run([sys.executable, str(ROOT / "process_roster.py"), "--help"], capture_output=True, text=True)
    assert help_run.returncode == 0 and "--despill-radius {2,4}" in help_run.stdout
    invalid = subprocess.run([sys.executable, str(ROOT / "process_roster.py"), "--despill-radius", "3"], capture_output=True, text=True)
    assert invalid.returncode == 2 and "invalid choice" in invalid.stderr
    report.update(status="passed", real_frame_cases=len(report["cases"]),
                  default_pixel_comparisons=len(report["cases"]) * 3,
                  cli_help_and_invalid_radius_passed=True,
                  candidate_or_formal_outputs_written=False)
    (EVIDENCE / "regression-result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    board = Image.new("RGB", (1080, len(comparisons) * 630), (22, 34, 34))
    draw = ImageDraw.Draw(board)
    for row, (name, before, after) in enumerate(comparisons):
        y = row * 630
        draw.text((20, y + 10), name + " / old radius 2, reference 6", fill="white")
        draw.text((560, y + 10), name + " / opt-in radius 4, reference 12", fill="white")
        for col, img in enumerate([before, after]):
            board.paste(backdrop(img).resize((330, 330)), (col * 540 + 105, y + 32))
            crop = backdrop(img).crop((165, 70, 345, 265)).resize((240, 260), Image.Resampling.NEAREST)
            board.paste(crop, (col * 540 + 150, y + 365))
    board.save(EVIDENCE / "comparison-dark.png")
    print(json.dumps({"status": report["status"], "default_exact_comparisons": report["default_pixel_comparisons"],
                      "cases": [{k: c[k] for k in ["id", "delta_vs_radius2_pixels", "newly_changed_beyond_2px", "magenta_before", "magenta_after"]} for c in report["cases"]],
                      "report": str(EVIDENCE / "regression-result.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
