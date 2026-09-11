"""Audit repository SVG embedding and exercise grading without changing assets."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image

from svg_grade import grade_svg_bytes, inspect_svg_bytes, svg_structure_bytes


def _grade_sample(data: bytes) -> bytes:
    """A visible, reversible in-memory test transform (not production grading)."""
    with Image.open(io.BytesIO(data)) as source:
        rgba = source.convert("RGBA")
        red, green, blue, alpha = rgba.split()
        rgb = [channel.point(lambda value: round(value * 0.9)) for channel in (red, green, blue)]
        output = Image.merge("RGBA", (*rgb, alpha))
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        return buffer.getvalue()


def validate_samples(root: Path) -> dict:
    samples = [
        root / "qdao_ui_redesign_v5/components/svg/list_row_normal.svg",
        root / "qdao_ui_redesign_v5/hud/hud_skin.svg",
        root / "q_daoist_login_ui_uncropped_highres_final_layers/native_q5/labels.svg",
    ]
    checked = []
    for path in samples:
        original = path.read_bytes()
        result, stats = grade_svg_bytes(original, _grade_sample)
        assert svg_structure_bytes(original) == svg_structure_bytes(result), path
        assert len(list(ElementTree.fromstring(original).iter())) == len(list(ElementTree.fromstring(result).iter())), path
        original_refs, original_stats = inspect_svg_bytes(original)
        output_refs, output_stats = inspect_svg_bytes(result)
        assert original_stats == output_stats, path
        if not original_refs:
            assert result == original and stats["callback_calls"] == 0
        for before, after in zip(original_refs, output_refs):
            with Image.open(io.BytesIO(before.data)) as left, Image.open(io.BytesIO(after.data)) as right:
                assert left.size == right.size
                assert left.convert("RGBA").getchannel("A").tobytes() == right.getchannel("A").tobytes()
        checked.append({"path": path.relative_to(root).as_posix(), **stats})

    # Use an actual asset payload in synthetic XML to cover the cases absent
    # from the current exports: xlink, duplicated data, external refs, comments,
    # quoted >, whitespace in base64, and a byte-exact preprocessed PNG index.
    references, _ = inspect_svg_bytes(samples[0].read_bytes())
    reference = references[0]
    payload = base64.b64encode(reference.data)
    fixture = (
        b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
        b'<!-- <image href="data:image/png;base64,NOT_A_PNG"/> -->'
        b'<defs><linearGradient id="unused"><stop stop-color="#ffffff"/></linearGradient></defs>'
        b'<image id="a" data-note="x > y" href="data:image/png;base64,' + payload + b'"/>'
        b'<image id="b" xlink:href="data:image/png;base64,\n' + payload + b'\n"/>'
        b'<image id="external" href="../assets/keep.png"/><text x="8" y="9">' + "保留文字 &amp; 坐标".encode() + b'</text></svg>'
    )
    result, stats = grade_svg_bytes(fixture, _grade_sample)
    assert stats["callback_calls"] == 1 and stats["duplicate_reuses"] == 1
    assert stats["embedded_png_references"] == 2 and stats["external_image_references"] == 1
    assert svg_structure_bytes(fixture) == svg_structure_bytes(result)
    output = _grade_sample(reference.data)

    def should_not_call(_):
        raise AssertionError("Exact PNG SHA index should avoid calling the grader")

    reused, reuse_stats = grade_svg_bytes(fixture, should_not_call, png_sha256_index={reference.sha256: output})
    assert reused == result
    assert reuse_stats["sha_index_reuses"] == 1 and reuse_stats["callback_calls"] == 0
    identity, _ = grade_svg_bytes(fixture, lambda value: value)
    assert identity == fixture
    return {"status": "passed", "real_samples": checked, "edge_cases": [
        "href_and_xlink_href", "duplicate_png_once", "external_path_preserved",
        "comments_ignored", "quoted_angle_bracket", "base64_whitespace",
        "vector_defs_text_and_layout_byte_exact", "png_dimensions_and_alpha_unchanged",
        "original_byte_sha_index_reuse", "identity_retains_original_svg_bytes",
    ]}


def audit(root: Path) -> dict:
    names = subprocess.check_output(["rg", "--files", "-g", "*.svg", "-g", "*.png"], cwd=root, text=True).splitlines()
    names = sorted(name for name in names if not name.replace("\\", "/").startswith("qdao_exposure_refinement_v8/"))
    svg_names = [name for name in names if name.lower().endswith(".svg")]
    png_names = [name for name in names if name.lower().endswith(".png")]
    png_index = defaultdict(list)
    for name in png_names:
        with (root / name).open("rb") as handle:
            sha = hashlib.file_digest(handle, "sha256").hexdigest()
        png_index[sha].append(name.replace("\\", "/"))
    documents = []
    all_embedded = set()
    matched_embedded = set()
    for name in svg_names:
        data = (root / name).read_bytes()
        references, stats = inspect_svg_bytes(data)
        embeddings = {}
        for reference in references:
            all_embedded.add(reference.sha256)
            matches = png_index.get(reference.sha256, [])
            if matches:
                matched_embedded.add(reference.sha256)
            embeddings[reference.sha256] = {
                "sha256": reference.sha256,
                "png_bytes": len(reference.data),
                "standalone_png_matches": matches,
            }
        documents.append({"path": name.replace("\\", "/"), "svg_bytes": len(data), **stats, "embedded_pngs": list(embeddings.values())})
    return {
        "svg_count": len(svg_names),
        "standalone_png_count_hashed": len(png_names),
        "classification_counts": dict(Counter(item["classification"] for item in documents)),
        "embedded_png_references": sum(item["embedded_png_references"] for item in documents),
        "unique_embedded_png_byte_hashes": len(all_embedded),
        "unique_embedded_pngs_matching_standalone": len(matched_embedded),
        "unique_embedded_pngs_without_exact_standalone": len(all_embedded - matched_embedded),
        "documents": documents,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parents[1] / "svg_audit.json")
    parser.add_argument("--checks-only", action="store_true")
    args = parser.parse_args()
    result = {"validation": validate_samples(args.root)}
    if not args.checks_only:
        result["audit"] = audit(args.root)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.report), "validation": result["validation"]["status"], **{key: value for key, value in result.get("audit", {}).items() if key != "documents"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
