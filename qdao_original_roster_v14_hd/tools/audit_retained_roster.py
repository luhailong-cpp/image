"""Inventory retained IDs without approving candidates or restoring deleted art."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import mixed_workspace as workspace
from prepare_mixed_roster import DIRS, ACTION_PATHS, PNG_PATHS, sha, read


def package_metadata(directory):
    files = {}
    for name in ("manifest.json", "validation.json", "appearance.json"):
        path = directory / name
        if path.is_file():
            document = read(path)
            files[name] = {"exists": True, "sha256": sha(path), "recorded_status": document.get("status"),
                           "recorded_visual_review": document.get("visualReview", document.get("visual_review"))}
        else:
            files[name] = {"exists": False}
    return {"path": str(directory), "portrait_png_exists": (directory / "portrait.png").is_file(),
            "json_files": files, "candidate_acceptance_inferred": False}


def inventory():
    root = workspace.ROOT
    characters = []
    for character in sorted(workspace.active_ids()):
        legacy = root.parent / "qdao_original_roster_v13/candidate" / character
        candidate = root / "candidate" / character
        old = {p for p in ACTION_PATHS if (legacy / p).is_file()}
        new = {p for p in ACTION_PATHS if (candidate / p).is_file()}
        combined = old | new
        missing = set(ACTION_PATHS) - combined
        formal = []
        for version in (13, 14):
            target = workspace.FORMAL / f"Assets/Resources/World/Characters/QdaoOriginalRosterV{version}" / character
            required = set(PNG_PATHS) | {"manifest.json", "validation.json", "appearance.json"}
            absent = sorted(p for p in required if not (target / p).is_file())
            if target.is_dir():
                activation = read(target / "appearance.json") if (target / "appearance.json").is_file() else {}
                binding = not absent and activation.get("characterId") == character and activation.get("status") == "passed" and all(
                    activation.get(field) == sha(target / file) for field, file in (
                        ("manifest_sha256", "manifest.json"), ("validation_sha256", "validation.json")))
                formal.append({"version": version, "path": str(target), "required_authored_file_count": 140,
                    "metadata": package_metadata(target),
                    "missing_required_files": absent, "stored_approval_and_json_bindings_pass": bool(binding),
                    "runtime_index_exists": (target / "runtime-index.asset").is_file(),
                    "current_session_runtime_acceptance": False})
        characters.append({"character_id": character,
            "source_portrait": {"path": str(root.parent / "q_daoist_character_pack_4096" / (character + "_transparent_4096.png")),
                                "exists": (root.parent / "q_daoist_character_pack_4096" / (character + "_transparent_4096.png")).is_file()},
            "legacy_candidate_metadata": package_metadata(legacy), "hd_candidate_metadata": package_metadata(candidate),
            "legacy_walk": sum(p.startswith("walk/") for p in old), "legacy_idle": sum(p.startswith("idle/") for p in old),
            "hd_candidate_walk_pngs": sum(p.startswith("walk/") for p in new),
            "new_nonoverlapping_candidate_walk": sum(p.startswith("walk/") for p in new - old),
            "candidate_overlaps_preserved_slots_not_counted": sorted(new & old),
            "missing_walk": sum(p.startswith("walk/") for p in missing), "missing_idle": sum(p.startswith("idle/") for p in missing),
            "missing_walk_by_direction": {d: [n for n in range(1, 17) if f"walk/{d}/{n:02}.png" in missing] for d in DIRS},
            "missing_idle_directions": [d for d in DIRS if f"idle/{d}.png" in missing],
            "formal_packages": formal, "candidate_status": "inventory_only_not_art_or_runtime_approval"})
    return {"schema": "qdao-retained-roster-live-inventory-v1", "captured_utc": datetime.now(timezone.utc).isoformat(),
            "scope_file": str(root / "CONTINUATION_STATE_20260920_SCOPE_UPDATED.json"),
            "scope_sha256": sha(root / "CONTINUATION_STATE_20260920_SCOPE_UPDATED.json"),
            "active_character_count": len(characters), "characters": characters,
            "missing_walk": sum(c["missing_walk"] for c in characters), "missing_idle": sum(c["missing_idle"] for c in characters),
            "scope": "Existing expected slots and stored JSON approval bindings only. Candidate PNGs, archived raw, and prior approval do not prove current runtime/visual acceptance."}


def markdown(document):
    lines = ["# 保留15名人物：本机实际资源盘点（2026-09-21）", "",
        "来源：[逐文件状态与逐方向缺槽JSON](retained-roster-inventory-detailed.json)。本次只读取当前文件，未恢复删除人物，未生成或批准任何候选。", "",
        "00–03正式V13资源齐套，现存appearance通过标记及manifest/validation SHA绑定一致；这是既有资源通过状态，本库存未完成本轮Unity运行验收。",
        "04–06均未齐套；其余8名有原始肖像但无动作包。当前V14正式包0名。总缺1205walk + 64idle = 1269动作槽。", "",
        "M/V/A依次表示manifest.json、validation.json、appearance.json是否存在；存在不等于通过。包肖像/JSON列：00–03读取正式V13，其余读取V14候选。", "",
        "| 原ID | 旧walk/idle | 新增HD walk（不含重叠） | 缺walk/idle | 原肖像 | 包portrait | M/V/A | 接入状态 |",
        "|---|---:|---:|---:|---|---|---|---|"]
    for c in document["characters"]:
        published = c["formal_packages"]
        package = published[0]["metadata"] if published else c["hd_candidate_metadata"]
        flags = "/".join("有" if package["json_files"][p]["exists"] else "缺" for p in ("manifest.json", "validation.json", "appearance.json"))
        yes = lambda value: "有" if value else "缺"
        status = "正式V13既有通过；本轮runtime未验收" if published else "候选未齐套/未批准，不能发布"
        lines.append(f'| {c["character_id"]} | {c["legacy_walk"]}/{c["legacy_idle"]} | {c["new_nonoverlapping_candidate_walk"]} | {c["missing_walk"]}/{c["missing_idle"]} | {yes(c["source_portrait"]["exists"])} | {yes(package["portrait_png_exists"])} | {flags} | {status} |')
    lines += ["", "## 精确动作缺口", ""]
    for c in document["characters"]:
        lines.append("- **" + c["character_id"] + "**：")
        missing = [d + "=" + ",".join(f"{n:02}" for n in frames) for d, frames in c["missing_walk_by_direction"].items() if frames]
        lines.append("  walk：" + ("；".join(missing) if missing else "无缺槽") + "。idle：" + (",".join(c["missing_idle_directions"]) or "无缺槽") + "。")
        if c["candidate_overlaps_preserved_slots_not_counted"]:
            lines.append("  未计新增的旧槽重叠候选：" + ", ".join(c["candidate_overlaps_preserved_slots_not_counted"]) + "。")
    lines += ["", "## 验收缺口与发布边界", "",
        "04：NW04/06/07残边疑点尚待实际检查；NW08/10/11仅归档raw。05：NE16库存齐但独立重建、混合连播/接缝和视觉批准未完成。06：E04/06/13仅归档raw，E03紫边疑点；拒收E09第一稿不计数。这些交接状态没有被本次文件盘点提升为通过。",
        "",
        "00–03需由主任务交付本轮正式登录/选角/主城/战斗/重登与运行结果；04–06缺实际1024移动帧截图、正常/最近镜头检查和完整Unity运行；其余8名需先完成真实动作包。不存在可合法stage的本批新齐套包。",
        "",
        "正式Unity本轮导入触发旧meta序列化变化；这与旧PNG/JSON是否改变分开审计。固定历史baseline仍受SHA保护，publisher拒绝未经单独认可的旧meta变化。没有替换baseline或以新git HEAD作为保护原点。",
        "",
        "本次发布工具与测试结果另见 [发布工具接续报告](PIPELINE_REPORT.md)。"]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory()
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        destination = args.output.resolve()
        if not destination.is_relative_to((workspace.ROOT / "mixed-preparation").resolve()) or destination.exists():
            raise ValueError("Use a new report under mixed-preparation; never overwrite handoff/history")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(data)
        print(json.dumps({"output": str(destination), "characters": 15, "missing_walk": result["missing_walk"],
                          "missing_idle": result["missing_idle"]}))
    else:
        print(data)


if __name__ == "__main__":
    main()
