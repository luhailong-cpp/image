"""Freeze the existing 158 UI PNG contracts without changing source assets."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image

PACK = Path(__file__).resolve().parents[1]
REPO = PACK.parent
EXPECTED_COUNTS = {"components": 39, "legacy": 73, "attributes": 31, "layers": 12, "hud": 3}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_png(path: Path) -> dict:
    with Image.open(path) as image:
        image.load()
        if image.format != "PNG":
            raise ValueError(f"Not a PNG: {path}")
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        return {
            "size": list(image.size),
            "mode": image.mode,
            "alpha_range": list(alpha.getextrema()) if alpha is not None else None,
            "alpha_bbox": list(alpha.getbbox()) if alpha is not None and alpha.getbbox() else None,
            "transparent_corners": (
                all(alpha.getpixel(p) == 0 for p in [(0, 0), (image.width - 1, 0),
                                                     (0, image.height - 1), (image.width - 1, image.height - 1)])
                if alpha is not None else None
            ),
            "sha256": file_sha(path),
            "pixel_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }


def relative_path(value: str, base: Path = REPO) -> str:
    path = (base / value).resolve()
    try:
        return path.relative_to(REPO.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Source outside repository: {path}") from exc


def discover_contracts():
    files = []
    manifests = []

    def source_manifest(relative: str):
        path = REPO / relative
        manifests.append({"path": relative, "sha256": file_sha(path)})
        return read_json(path)

    def add(path, family, metadata, manifest, screen_size=None, allowed_unchanged=False):
        relative = relative_path(path)
        files.append({"path": relative, "family": family, "source_manifest": manifest,
                      "metadata": metadata, "screen_size": screen_size,
                      "allowed_unchanged": allowed_unchanged})

    component_manifest = "qdao_ui_redesign_v5/components/manifest.json"
    components = source_manifest(component_manifest)
    for asset in components["assets"]:
        meta = {key: asset[key] for key in ["id", "category", "state", "nine_slice", "resize_axes",
                 "fixed_height", "minimum_size", "content_insets", "text_color", "dynamic_text_baked",
                 "selection_marker", "disabled_marker"] if key in asset}
        add("qdao_ui_redesign_v5/components/" + asset["png"], "components", meta,
            component_manifest, [asset["width"], asset["height"]])

    legacy_manifest = "exact_qdao_slices/manifest_native_q5.json"
    legacy = source_manifest(legacy_manifest)
    for asset in legacy["assets"]:
        meta = {key: asset[key] for key in ["role", "state", "symbol", "nine_slice", "resize_axes",
                 "fixed_height", "fixed_target_height", "source_grid_center_xywh", "legacy_import",
                 "dynamic_text_baked", "round_badge_baked", "status_baked", "alias_of"] if key in asset}
        logical = asset.get("legacy_import", {}).get("target_size")
        if logical is None and asset.get("role") in {"round_badge", "legacy_alias"}:
            logical = [120, 120]
        add(asset["png"], "legacy", meta, legacy_manifest, logical or [asset["width"], asset["height"]])

    attribute_manifest = "designs/attribute-panels/v2-painted/unity-slices/manifest.json"
    attributes = source_manifest(attribute_manifest)
    for asset in attributes["sprites"]:
        meta = {key: asset[key] for key in ["name", "source", "sourceRectTopLeft", "sourceRectNativeTopLeft",
                 "borderLeftBottomRightTop", "resourcePath", "containsDynamicText", "containsStaticTitle",
                 "processing"] if key in asset}
        add("designs/attribute-panels/v2-painted/unity-slices/png/" + asset["name"] + ".png",
            "attributes", meta, attribute_manifest, [asset["width"], asset["height"]])

    layer_manifest = "q_daoist_login_ui_uncropped_highres_final_layers/manifest_native_q5.json"
    layers = source_manifest(layer_manifest)
    for asset in layers["outputs"]:
        meta = {key: asset[key] for key in ["role", "dynamic_text_baked", "composition"] if key in asset}
        meta["layout"] = {key: layers[key] for key in ["hero_placement_2560", "control_placements_2560",
                           "text_placements_2560", "layer_contract"] if key in layers}
        add(asset["path"], "layers", meta, layer_manifest, [2560, 1080])

    hud_manifest = "qdao_ui_redesign_v5/hud/placement.json"
    hud = source_manifest(hud_manifest)
    for name in ["skin_png", "overlay_png", "labels_png"]:
        add("qdao_ui_redesign_v5/hud/" + hud["artifacts"][name], "hud",
            {"role": name, "layout": hud["layout"], "buttons": hud["buttons"], "text": hud["text"],
             "dynamic_text_baked": name != "skin_png"}, hud_manifest, [2560, 1080], name == "labels_png")

    paths = [item["path"] for item in files]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate paths in source manifests")
    counts = dict(Counter(item["family"] for item in files))
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"Unexpected manifest counts: {counts}; expected {EXPECTED_COUNTS}")
    return files, manifests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACK / "contracts/current_files.json")
    parser.add_argument("--refresh", action="store_true", help="Explicitly replace an existing baseline snapshot")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PACK.resolve()):
        parser.error("Output must stay inside qdao_ui_style_recut_v10")
    if output.exists() and not args.refresh:
        parser.error("Baseline exists. Use a different output or explicitly pass --refresh")
    files, manifests = discover_contracts()
    for item in files:
        item.update(inspect_png(REPO / item["path"]))
    payload = {"schema_version": 1, "captured_at_utc": datetime.now(timezone.utc).isoformat(),
               "repository": REPO.as_posix(), "scope": "158 final PNGs; excludes QA contacts, source snapshots, standard screen exports, and SVG wrappers",
               "asset_count": len(files), "family_counts": dict(Counter(item["family"] for item in files)),
               "manifest_sources": manifests, "files": files}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": output.as_posix(), "asset_count": len(files), "family_counts": payload["family_counts"]}))


if __name__ == "__main__":
    main()
