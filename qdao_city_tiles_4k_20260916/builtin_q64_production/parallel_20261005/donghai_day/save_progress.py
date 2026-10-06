"""Refresh current task facts without editing or accepting source artwork."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import io
import json
import re
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PATTERN = re.compile(r"r(\d{2})_c(\d{2})\Z")


def is_tile(name):
    m = PATTERN.fullmatch(name)
    return bool(m and all(1 <= int(n) <= 16 for n in m.groups()))


def rect(name):
    r, c = map(int, PATTERN.fullmatch(name).groups())
    return [(c - 1) * 4096, (r - 1) * 4096, 4096, 4096]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(name, value):
    p = ROOT / name
    temp = p.with_name(p.name + ".writing")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(p)


def link(path):
    p = Path(path)
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def inspect_image(path, size):
    # Hash and decode identical bytes despite concurrent updates to a path.
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.format != "PNG" or im.size != size:
            raise ValueError(f"Expected PNG {size}, got {im.format} {im.size}")
        if im.mode not in ("RGB", "RGBA"):
            raise ValueError(f"Unexpected pixel mode {im.mode}")
        if im.mode == "RGBA" and im.getextrema()[3] != (255, 255):
            raise ValueError("Incomplete transparent pixels cannot count as complete art")
        thumb = im.convert("RGB").resize((384, 384), Image.Resampling.LANCZOS) if size == (4096, 4096) else None
    return digest, thumb


def collect_candidates(handoff, directories):
    # Select first: do not silently downgrade an invalid current version.
    choices = {}
    for b in handoff.get("baselineCandidates", []):
        if is_tile(b["tile"]):
            choices[b["tile"]] = (Path(b["file"]), "handoff_baseline", ROOT / "handoff.json", b)
    for d in directories:
        p = d / "output" / (d.name + ".png")
        if p.exists():
            choices[d.name] = (p, "assembled_output", d / "output/assembly-manifest.json", None)
    for p in sorted((ROOT / "tiles").glob("r??_c??.png")):
        if is_tile(p.stem):
            choices[p.stem] = (p, "current_tiles", Path(str(p) + ".generation.json"), None)
    entries, thumbs, excluded = [], {}, []
    for name, (p, origin, evidence, baseline) in sorted(choices.items()):
        try:
            record = baseline or load(evidence)
            if origin == "assembled_output":
                record = record["output"]
            if Path(record["file"]).resolve() != p.resolve() or not record.get("sha256"):
                raise ValueError("Missing recorded SHA256 or mismatched evidence path")
            digest, thumb = inspect_image(p, (4096, 4096))
            if digest != record["sha256"]:
                raise ValueError("Current bytes do not match recorded SHA256")
            entries.append({"tile": name, "file": str(p), "sha256": digest, "pixels": [4096, 4096],
                            "globalRect": rect(name), "source": origin, "evidenceFile": str(evidence),
                            "evidenceSha256": sha(evidence), "completeDecode": True,
                            "recordedShaMatches": True, "formalAccepted": False})
            thumbs[name] = thumb
        except (OSError, ValueError, KeyError, TypeError) as e:
            excluded.append({"tile": name, "preferredFile": str(p), "source": origin,
                             "reason": str(e), "fallbackUsed": False})
    return entries, thumbs, excluded


def collect_work(directories, selected):
    work, reviews = [], []
    for d in directories:
        valid, invalid = [], []
        for p in sorted((d / "native").glob("r??_c??.png")):
            m = PATTERN.fullmatch(p.stem)
            if not m or not all(1 <= int(n) <= 4 for n in m.groups()):
                continue
            try:
                record = load(str(p) + ".generation.json")
                digest, _ = inspect_image(p, (1254, 1254))
                if record.get("sha256") != digest:
                    raise ValueError("Native record SHA256 mismatch")
                valid.append(p.stem)
            except (OSError, ValueError, KeyError, TypeError) as e:
                invalid.append({"file": str(p), "reason": str(e)})
        missing = [f"r{r:02d}_c{c:02d}" for r in range(1, 5) for c in range(1, 5)
                   if f"r{r:02d}_c{c:02d}" not in valid]
        files = [p for p in d.rglob("*") if p.is_file()]
        phase = ("candidate_pending_scoped_review" if d.name in selected else
                 "assembly_pending" if not missing else "native_expansion_in_progress" if valid else "structure_preparation")
        work.append({"tile": d.name, "globalRect": rect(d.name), "nativePatchesSaved": len(valid),
                     "nativePatchesRequired": 16, "nativePatchIds": valid, "missingNativePatchIds": missing,
                     "invalidNativeFiles": invalid, "hasCompletePixelCandidate": d.name in selected,
                     "phase": phase, "lastSourceChangeUnix": max((p.stat().st_mtime for p in files), default=d.stat().st_mtime),
                     "fragmentsCountAsTiles": False})
        for p in sorted(d.rglob("*review*.json")):
            if "preview" in p.name:
                continue
            try:
                data = load(p)
                candidate = data.get("candidate", {})
                bound = data.get("candidateSha256") or (candidate.get("sha256") if isinstance(candidate, dict) else None)
                current = selected.get(d.name)
                reviews.append({"tile": d.name, "file": str(p), "sha256": sha(p), "declaredStatus": data.get("status"),
                                "candidateSha256": bound,
                                "matchesCurrentTileSha": bool(bound and current and bound == current["sha256"]),
                                "scopeMustBeRead": True, "promotesFormalAcceptance": False})
            except (OSError, ValueError, TypeError):
                continue
    return work, reviews


def save_preview(entries, thumbs):
    # Separate row strips; keep absent columns empty instead of closing gaps.
    rows = {}
    for e in entries:
        r, c = map(int, PATTERN.fullmatch(e["tile"]).groups())
        rows.setdefault(r, {})[c] = e
    width = max((max(cols) - min(cols) + 1 for cols in rows.values()), default=1) * 384
    im = Image.new("RGB", (width, max(1, len(rows)) * 410), (235, 232, 220))
    draw = ImageDraw.Draw(im)
    for row_index, (r, cols) in enumerate(sorted(rows.items())):
        for c in range(min(cols), max(cols) + 1):
            x, y = (c - min(cols)) * 384, row_index * 410
            name = f"r{r:02d}_c{c:02d}"
            draw.text((x + 8, y + 7), name + (" / PREVIEW ONLY" if c in cols else " / MISSING"), fill=(38, 53, 45))
            if c in cols:
                im.paste(thumbs[name], (x, y + 26))
    p = ROOT / "current-preview.png"
    temp = p.with_name(p.name + ".writing")
    im.save(temp, format="PNG")
    temp.replace(p)
    write("current-preview.png.generation.json", {"file": str(p), "sha256": sha(p), "pixels": list(im.size),
          "operation": "downsampled candidate progress preview only", "sourceScale": 384 / 4096,
          "derivedFrom": entries, "notFinalHD": True, "rowsAreSeparateStrips": True})


def save_readme(s):
    lines = ["# 04 渔村日景地图 · 本任务制作记录", "",
             "本页由 save_progress.py 按磁盘当前事实生成。内部资产 ID：donghai_day；正式项目采用《五行奇谈》原创命名，旧 ID 不代表已确认的新旧地名映射。", "",
             f"目标65536×65536，16×16共256块，每块4096×4096。当前完整像素候选 **{s['completePixelCandidates']}/256**，基线坐标 {s['baselineCompletePixelCandidates']} 个、新增坐标 {s['newCompletePixelCandidates']} 个。正式验收 **0**；整城未完成、未客户端验收。", "",
             "当前状态见 [progress.json](progress.json)，逐坐标状态见 [tile-index.json](tile-index.json)。[当前预览](current-preview.png)仅缩小展示候选，不能用于原像素验收。", "",
             "## 当前候选与在制区域", "",
             "同一坐标仅统计一次，选择顺序为 tiles/ 当前版本 → 各图块 output/ → handoff基线。计入图均已完整解码、核实4096×4096和记录SHA；优先版本校验失败会排除并报告，不自动退回旧版。", "",
             "| 坐标 | 当前候选 | 来源 | SHA-256 |", "|---|---|---|---|"]
    for e in s["candidates"]:
        lines.append(f"| {e['tile']} | [PNG]({link(e['file'])}) | {e['source']} | {e['sha256']} |")
    lines += ["", f"当前优先在制块：**{s['activeTile'] or '无缺片在制块'}**；阶段：{s['phase']}。", ""]
    for w in s["workInProgress"]:
        lines.append(f"- {w['tile']}：已核验原生片 {w['nativePatchesSaved']}/16；{'已有完整像素候选' if w['hasCompletePixelCandidate'] else '尚无完整像素候选'}。片段、结构参考和透明进度图不计整块。")
    if s["excludedCandidates"]:
        lines += ["", "本次排除的优先候选："]
        lines += [f"- {e['tile']}：{e['reason']}" for e in s["excludedCandidates"]]
    lines += ["", "## 检查范围与来源限制", "",
              "- 完整像素候选只证明当前文件及尺寸齐全，不代表艺术、导航、最近镜头或客户端验收。",
              "- 内部缝、共边接回和修补检查分范围记录。修补后的版本不能自动继承旧SHA的全部审核；下列记录仅作索引，具体通过范围以报告绑定SHA、实际原像素证据及未变像素证明为准。",
              "- 未补齐邻接边、跨排四块交点、全城布局、日景/节庆共用结构、导航、前景遮挡和客户端最近镜头仍待核验。",
              "- [布局与导航审计](layout-audit.json)保留原导航多边形来源；独立风格母图不视为已几何对齐。道路、桥栏、台阶、建筑占地、入口及投影须保持连续。", ""]
    for e in s["reviewReferences"]:
        binding = "匹配当前图块SHA；仅报告范围有效" if e["matchesCurrentTileSha"] else "历史版本或无直接当前SHA绑定；须查范围"
        lines.append(f"- [{link(e['file'])}]({link(e['file'])})：{binding}。")
    lines += ["", "## 逐图模型、拼接与保留", "",
              "每张AI原生片、结构参考与修补片的 .generation.json 保存真实工具结果路径、SHA、原生尺寸、时间、配置快照、提示词路径及参考图角色。原生片位于各 rXX_cXX/native/；当前tiles旁的派生记录和integration manifest关联修补来源与参数。",
              "本批目标来自 [batch-model-check.json](batch-model-check.json)：gpt-image-2.5-sunburst/max。实际提交 model/quality 与返回 actualModel/actualQuality 未披露、记为 null；提示词、配置和官方公告不等于后端版本证据。仅使用宿主内置生图，未使用付费API。",
              "完整新块由16张1254×1254原生片组成，1024核心、115四边上下文。裁切、拼接、有限配准与色差匹配须看对应manifest；不把小图放大或布局裁图当高清成品，不宣称拼接图为单次原生4K。缩放仅用于布局参考及预览。",
              "production.py / expand.py负责输入与来源记录；assembly*.py及integrate*.py负责拼接或修补接入。本脚本只刷新进度、索引、README及缩小预览，不改图源、审核结论或客户端。可安全重跑：python save_progress.py。",
              "原生片、结构稿和修补片仍可能是当前依赖，不由本脚本删除。确认最终像素及引用完整后，按项目规则删除可删除原图、拒稿、回退和中间图片，不留图片备份；逐图文字、哈希及来源限制继续保留。", ""]
    p = ROOT / "README.md"
    temp = p.with_name(p.name + ".writing")
    temp.write_text("\n".join(lines), encoding="utf-8")
    temp.replace(p)


def main():
    h = load(ROOT / "handoff.json")
    directories = sorted(p for p in ROOT.iterdir() if p.is_dir() and is_tile(p.name))
    entries, thumbs, excluded = collect_candidates(h, directories)
    selected = {e["tile"]: e for e in entries}
    work, reviews = collect_work(directories, selected)
    active = max((w for w in work if not w["hasCompletePixelCandidate"]),
                 key=lambda w: w["lastSourceChangeUnix"], default=None)
    if active and any(e["tile"] == active["tile"] for e in excluded):
        active["phase"] = "candidate_validation_failed"
    actions = {
        "structure_preparation": "Prepare structure and neighbor inputs, then generate missing native patches.",
        "native_expansion_in_progress": "Continue missing native patches, then assemble and inspect required scopes.",
        "assembly_pending": "All 16 native patches are present; assemble the full tile and inspect required scopes.",
        "candidate_validation_failed": "Resolve the excluded current candidate's file, dimensions or SHA evidence before counting it.",
    }
    baseline_ids = {e["tile"] for e in h.get("baselineCandidates", [])}
    work_by_id = {w["tile"]: w for w in work}
    excluded_ids = {e["tile"] for e in excluded}
    index = []
    for r in range(1, 17):
        for c in range(1, 17):
            name = f"r{r:02d}_c{c:02d}"
            e, w = selected.get(name), work_by_id.get(name)
            status = ("complete_pixel_candidate_pending_full_acceptance" if e else
                      "current_candidate_validation_failed" if name in excluded_ids else
                      "native_fragments_in_progress" if w and w["nativePatchesSaved"] else
                      "prepared_no_complete_pixels" if w else "not_generated")
            index.append({"id": name, "globalRect": rect(name), "status": status,
                          "file": e["file"] if e else None, "sha256": e["sha256"] if e else None,
                          "source": e["source"] if e else None, "accepted": False,
                          "nativePatchesSaved": w["nativePatchesSaved"] if w else 0})
    state = {"appearance": h["appearance"], "title": h["title"], "updatedAtUtc": datetime.now(timezone.utc).isoformat(),
             "targetCityPixels": [65536, 65536], "targetTiles": 256, "completePixelCandidates": len(entries),
             "baselineCompletePixelCandidates": len(set(selected) & baseline_ids),
             "newCompletePixelCandidates": len(set(selected) - baseline_ids),
             "formalAccepted": 0, "wholeCityComplete": False, "runtimeIntegration": False,
             "activeTile": active["tile"] if active else None, "activeGlobalRect": active["globalRect"] if active else None,
             "nativePatchesSaved": active["nativePatchesSaved"] if active else 0,
             "nativePatchesRequiredForActiveTile": 16 if active else None, "fragmentsCountAsTiles": False,
             "phase": active["phase"] if active else "candidates_pending_full_acceptance",
             "workInProgress": work, "reviewReferences": reviews, "excludedCandidates": excluded,
             "wholeCityNavigationAlignment": "not verified", "nextTile": active["tile"] if active else None,
             "nextAction": f"{active['tile']}: {actions[active['phase']]}" if active else
                           "Choose the next adjacent missing tile; scoped reviews do not constitute formal acceptance.",
             "currentPreview": str(ROOT / "current-preview.png"), "tileIndex": str(ROOT / "tile-index.json"),
             "candidates": entries, "builtinOnly": True, "paidApiUsed": False, "snapshotOnly": True,
             "aggregationPolicy": "one coordinate once; current tiles > tile output > handoff baseline; invalid preferred version excluded",
             "rerunToRefresh": "python save_progress.py"}
    save_preview(entries, thumbs)
    write("tile-index.json", {"targetPixels": [65536, 65536], "grid": [16, 16],
          "targetTilePixels": [4096, 4096], "tiles": index, "notRuntimeManifest": True})
    write("progress.json", state)
    write("current-work.json", state)
    save_readme(state)
    print(json.dumps({"completePixelCandidates": len(entries), "activeTile": state["activeTile"],
                      "nativePatchesSaved": state["nativePatchesSaved"], "excludedCandidates": excluded,
                      "formalAccepted": 0, "preview": state["currentPreview"]}))


if __name__ == "__main__":
    main()

