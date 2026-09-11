"""Plan narrow metadata updates for reviewed edge repairs; never write files.

make_updates(repository, {relative_png_path: new_sha256}, repair_record) returns
only changed JSON documents. The publisher owns backups, optimistic file checks,
image/atlas QA and atomic publication. Historical generation and QA evidence is
not recursively rewritten. The v10 staging/publishing pipeline is out of scope.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


ICON_ROOT = (
    "q_daoist_login_ui_10240_redraw_clear_final_layers/"
    "q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600"
)
ICON_PATHS = (
    ICON_ROOT + "/west_eight_immortals_redrawn_100_600x600/004_golden_cudgel.png",
    ICON_ROOT + "/character_artifacts_redrawn_24_600x600/17_han_zhongli_palm_leaf_fan.png",
)
PETS = (
    ("ling_yue", "lingyue", "qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png"),
    ("hu_tuan_tuan", "hutuantuan", "qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png"),
    ("fu_xiao_hu", "fuxiaohu", "qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png"),
    ("yun_jiu_jiu", "yunjiujiu", "qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png"),
)
ATLAS = ICON_ROOT + "/fairygui_atlas/qstyle_fairygui_atlas_600.png"
CLIENT_MANIFEST = "client_ui_refresh_20260908/assets_manifest.json"


def make_updates(root, path_to_newsha, repair_record):
    """Return {repository_relative_json: updated_dict}, without filesystem writes.

    Inputs are the 32 known hero frames, six support source PNGs, four full-size
    attribute pet copies, six client prepared copies and/or the existing atlas.
    Unknown paths raise rather than silently producing incomplete metadata.
    Only supplied PNGs are considered replaced. Call before publishing files so
    each history entry captures its real on-disk before hash. A repeated plan on
    the same metadata is idempotent for the same repair_record and hash mapping.
    """
    root = Path(root).resolve()
    repair_record = deepcopy(repair_record)
    json.dumps(repair_record, ensure_ascii=False)  # Require a JSON-safe record.

    def safe(relative):
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Path escapes repository: " + str(relative))
        return path

    def read(relative):
        return json.loads(safe(relative).read_text(encoding="utf-8-sig"))

    def file_sha(relative):
        return hashlib.sha256(safe(relative).read_bytes()).hexdigest()

    requested = {}
    for supplied, digest in path_to_newsha.items():
        relative = safe(str(supplied).replace("\\", "/")).relative_to(root).as_posix()
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError("Invalid SHA-256 for " + relative)
        digest = digest.lower()
        if relative in requested and requested[relative] != digest:
            raise ValueError("Conflicting hashes for " + relative)
        if not safe(relative).is_file():
            raise FileNotFoundError(safe(relative))
        requested[relative] = digest
    if not requested:
        return {}

    hero_manifest = read("character_move_8dir/manifest.json")
    hero_paths = {
        "character_move_8dir/" + frame["file"]
        for direction in hero_manifest["directions"].values()
        for frame in direction["frames"]
    }
    client_manifest = read(CLIENT_MANIFEST)
    support_sources = {p[2] for p in PETS} | set(ICON_PATHS)
    prepared_paths = {
        "client_ui_refresh_20260908/" + row["staged"]
        for row in client_manifest["records"]
        if row.get("source") in support_sources and row.get("staged")
    }
    attribute_copies = {"designs/attribute-panels/assets/" + p[1] + ".png" for p in PETS}
    allowed = hero_paths | support_sources | prepared_paths | attribute_copies | {ATLAS}
    unknown = set(requested) - allowed
    if unknown:
        raise ValueError("Unsupported repair paths: " + ", ".join(sorted(unknown)))
    before_hashes = {path: file_sha(path) for path in requested}
    plan_id = hashlib.sha256(json.dumps(
        {"repair_record": repair_record, "outputs": requested},
        sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()

    documents, originals, edits, related = {}, {}, {}, {}

    def document(relative):
        if relative not in documents:
            originals[relative] = read(relative)
            documents[relative] = deepcopy(originals[relative])
            edits[relative], related[relative] = [], set()
        return documents[relative]

    def associate(relative, asset):
        document(relative)
        related[relative].add(asset)

    def update(relative, keys, value, asset=None):
        data = document(relative)
        for key in keys[:-1]:
            data = data[key]
        key = keys[-1]
        existed = key in data if isinstance(data, dict) else key < len(data)
        previous = deepcopy(data[key]) if existed else None
        if existed and previous == value:
            return
        data[key] = deepcopy(value)
        change = {"field": "/" + "/".join(map(str, keys)),
                  "previously_present": existed, "before": previous, "after": deepcopy(value)}
        if asset is not None:
            change["asset_path"] = asset
            related[relative].add(asset)
        edits[relative].append(change)

    def update_hash(relative, keys, asset):
        if asset in requested:
            update(relative, keys, requested[asset], asset)
            associate(relative, asset)

    # Current frame manifest hashes change. Original generation/cleanup hashes
    # in direction records remain historical; their new history supplies hashes.
    if set(requested) & hero_paths:
        rel = "character_move_8dir/manifest.json"
        for direction, entry in document(rel)["directions"].items():
            for index, frame in enumerate(entry["frames"]):
                asset = "character_move_8dir/" + frame["file"]
                if asset in requested:
                    update_hash(rel, ("directions", direction, "frames", index, "sha256"), asset)
                    associate("character_move_8dir/" + entry["qc"], asset)

    # Only transparent entries change. Opaque concepts and raw generation hashes
    # continue to describe the original accepted artwork and generation process.
    for pet_id, copy_key, asset in PETS:
        if asset not in requested:
            continue
        rel = "qdao_asset_refresh_v6/pets/records/" + pet_id + ".json"
        record = document(rel)
        if record.get("output", record.get("file")) != asset:
            raise ValueError("Unexpected pet record target: " + rel)
        update_hash(rel, ("sha256",), asset)
        rel = "qdao_asset_refresh_v6/pets/manifest.json"
        matches = [i for i, item in enumerate(document(rel)["assets"]) if item["path"] == asset]
        if len(matches) != 1:
            raise ValueError("Expected one pet manifest entry: " + asset)
        update_hash(rel, ("assets", matches[0], "sha256"), asset)
        if pet_id == "ling_yue":
            update_hash("qdao_ui_redesign_v5/pet/manifest.json", ("transparent_asset", "sha256"), asset)
        else:
            rel = "qdao_chibi_pets_v1/manifest.json"
            matches = [i for i, item in enumerate(document(rel)["pets"])
                       if item["transparent_asset"]["image"] == Path(asset).name]
            if len(matches) != 1:
                raise ValueError("Expected one transparent pet entry: " + asset)
            update_hash(rel, ("pets", matches[0], "transparent_asset", "sha256"), asset)
        associate("qdao_asset_refresh_v6/pets/validation.json", asset)

    for asset, batch in zip(ICON_PATHS, (1, 8)):
        if asset not in requested:
            continue
        for rel, array, match_key, match_value in (
            ("qdao_asset_refresh_v6/icons/manifest.json", "assets", "path", asset),
            (str(Path(asset).parent / "manifest.json").replace("\\", "/"), "items", "file", Path(asset).name),
            (f"qdao_asset_refresh_v6/icons/records/batch{batch:02d}.json", "outputs", "path", asset),
        ):
            matches = [i for i, item in enumerate(document(rel)[array]) if item[match_key] == match_value]
            if len(matches) != 1:
                raise ValueError("Expected one icon record: " + rel + ": " + asset)
            update_hash(rel, (array, matches[0], "sha256"), asset)
        associate("qdao_asset_refresh_v6/icons/validation.json", asset)

    if ATLAS in requested:
        update_hash(ICON_ROOT + "/fairygui_atlas/qstyle_fairygui_atlas_600.json", ("atlas_sha256",), ATLAS)
        update_hash("qdao_asset_refresh_v6/icons/manifest.json", ("atlas", "sha256"), ATLAS)
        update_hash("qdao_asset_refresh_v6/icons/validation.json", ("atlas_sha256",), ATLAS)
        # Parent manifest stores a path, not a SHA: preserve it. Never touch XML,
        # frame coordinates, historical atlas checks or original batch raw SHA.

    if set(requested) & (support_sources | prepared_paths):
        rel = CLIENT_MANIFEST
        for index, row in enumerate(document(rel)["records"]):
            source = row.get("source")
            if source not in support_sources:
                continue
            prepared = "client_ui_refresh_20260908/" + row["staged"] if row.get("staged") else None
            changed = source in requested or prepared in requested
            if not changed:
                continue
            update_hash(rel, ("records", index, "source_sha256"), source)
            update_hash(rel, ("records", index, "staged_sha256"), prepared)
            asset = prepared if prepared in requested else source
            update(rel, ("records", index, "status"), "pending_client_sync", asset)
            update(rel, ("records", index, "prepared_update_note"),
                   "Image-project edge repair prepared; existing client_sha256 remains the last observed client value. No client copy or import was performed by this metadata helper.", asset)
        update(rel, ("prepared_update_status",), "pending_client_sync")
        # Preserve top-level status/failures/mode/generated_at and every actual
        # client_sha256: they describe the last real client synchronization run.

    result = {}
    for rel, data in documents.items():
        previous_history = data.get("edge_rgb_repair", [])
        history = deepcopy(previous_history) if isinstance(previous_history, list) else [deepcopy(previous_history)]
        if not any(isinstance(entry, dict) and entry.get("plan_id") == plan_id for entry in history):
            history.append({
                "plan_id": plan_id,
                "repair_record": deepcopy(repair_record),
                "metadata_helper": "qdao_cutout_edge_repair_20260910/metadata_updates.py",
                "assets": [{"path": asset, "sha256_before": before_hashes[asset],
                            "sha256_after": requested[asset]} for asset in sorted(related[rel])],
                "updated_fields": edits[rel],
                "scope": "Current asset hash metadata only. Original generation, opaque concepts, prior cleanup and client observations remain historical. Image publication and new visual/atlas checks are owned by the caller; this helper performed neither.",
            })
        data["edge_rgb_repair"] = history
        if data != originals[rel]:
            result[rel] = data
    return result
