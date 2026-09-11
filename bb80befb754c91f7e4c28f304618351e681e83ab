#!/usr/bin/env python3
"""Build the local Chinese exposure report from completed audit records.

Importing this module never reads the inventory or writes files. Running main()
reads processing.json, inventory.json, optional validation.json and optional
supplementary_inventory.json, then writes only REPORT.md and index.html in v8.
Original and delivered images are linked directly; no preview images are made.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote


PACKAGE = Path(__file__).resolve().parents[1]
PRESET_TEXT = {
    "scene": ("明亮场景", "重点收住天空、云雾与亮地面的中高光，保留暗部和原有配色。"),
    "screen": ("整屏界面", "降低登录、选服、选角等整屏视觉的亮度，照顾人物与背景的层次。"),
    "ui": ("米白面板", "控制米白底、金边和浅色条目的亮度，保留边缘与原有纹理。"),
    "ui_soft": ("界面轻调", "较轻地调整界面装饰与控件，保护可读性及按钮状态区别。"),
    "character": ("人物轻调", "轻压皮肤、白衣与白毛高光；同一套动作使用一致规则。"),
    "item": ("图标轻调", "轻压金属与浅色装饰反光，保留物件的小尺寸辨识度。"),
    "cloud": ("云层轻调", "收住明亮云气，保持透明度与原有层次。"),
    "preserve": ("原样保留", "已合适的地图、功能文字、遮罩、诊断和参考文件保持原样。"),
}
STATUS_TEXT = {
    "revised": "已修复", "preserved": "原样保留", "excluded": "归档保留",
    "prepared": "待应用", "pending": "待处理", "unverified": "待验收", "failed": "失败",
}
CLASS_TEXT = {
    "reference_or_diagnostic": "参考图、备份或诊断文件，保留原始记录。",
    "technical_preserve": "功能文字、遮罩或技术图，保留其显示含义。",
    "v8_review_sample": "本轮比较样张，不作为正式调色输入。",
    "source_or_matte": "来源图；涉及抠图键色时保护原始键色。",
    "prepared_copy": "同源准备副本，沿用对应素材规则。",
    "derived": "派生文件，沿用其来源素材的处理规则。",
    "formal": "正式素材。",
}
REPRESENTATIVES = [
    ("登录整屏", "qdao_ui_redesign_v5/01_login_2560x1080.png"),
    ("选择服务器", "qdao_ui_redesign_v5/02_server_select_2560x1080.png"),
    ("选择角色", "qdao_ui_redesign_v5/03_character_select_2560x1080.png"),
    ("明亮主城", "qdao_main_city_chibi_v1.png"),
    ("战斗场景", "qdao_ui_redesign_v5/05_battle_scene_2560x1080.png"),
    ("人物动作", "character_move_8dir/east_frame_01.png"),
    ("白色宠物", "qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox.png"),
    ("米白界面面板", "qdao_gpt_image2_refresh_v7/ui/derived/components/main_frame.png"),
    ("玉绿选中态", "qdao_gpt_image2_refresh_v7/ui/derived/components/list_row_selected.png"),
    ("物件图标", "q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/west_eight_immortals_redrawn_100_600x600/001_daoist_saber.png"),
    ("天墉城地图 · 保留原亮度", "tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png"),
]
RESTORE_COMMAND = "python qdao_exposure_refinement_v8/tools/refine_library.py restore"
ATLAS_VERSION_NOTE = "124帧图集与独立图标在本轮之前已有像素版本差异；本轮分别修正曝光且未增加不匹配像素，不宣称二者逐像素一致。"


def read_json(path: Path, optional=False):
    if optional and not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def esc(value):
    return html.escape(str(value), quote=True)


def safe_path(base: Path, value: str):
    path = (base / str(value).replace("\\", "/")).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Report link escapes the declared root: {value}")
    return path


def relative_url(path: Path, output_dir: Path):
    return quote(os.path.relpath(path, output_dir).replace("\\", "/"), safe="/")


def pretty_time(value):
    if not value:
        return "未记录"
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return str(value)


def luminance_pair(validation_row):
    """Do not mix initial sampled brightness with final full-pixel statistics."""
    if not validation_row:
        return None
    if validation_row.get("image"):
        metrics, basis = validation_row["image"], "位图可见区域"
    elif validation_row.get("gif", {}).get("frames"):
        metrics = validation_row["gif"]["frames"][0].get("image", {})
        basis = "GIF 第 1 帧；其余帧见验收记录"
    elif validation_row.get("embedded_pngs"):
        metrics = validation_row["embedded_pngs"][0]
        basis = "SVG 第 1 张内嵌 PNG；不含向量背景和文字"
    else:
        return None
    before, after = metrics.get("visible_original_mean"), metrics.get("visible_output_mean")
    if before is None or after is None:
        return None
    return {"before": float(before), "after": float(after), "basis": basis,
            "highlight_drop": metrics.get("highlight_mean_drop"),
            "shadow_drop": metrics.get("shadow_mean_drop")}


def brightness_text(pair):
    return f"{pair['before'] * 100:.1f} → {pair['after'] * 100:.1f}" if pair else "未统计"


def note_for(row):
    record = row.get("record") or {}
    if row["state"] == "failed":
        return "文件或验收检查失败；请查看 validation.json。"
    if row["state"] in {"prepared", "pending", "unverified"}:
        return {"prepared": "已生成待应用结果，正式路径尚未完成交付。",
                "pending": "已盘点，尚无处理记录。",
                "unverified": "缺少与当前处理哈希对应的通过记录。"}[row["state"]]
    if row["path"].startswith("tianyong_city_6x6/") and not record.get("changed"):
        return "地图暗部与石路层次已合适，保留原亮度。"
    if row["state"] == "excluded":
        return CLASS_TEXT.get(row["classification"], "未纳入本轮改色，保留原文件。")
    if record.get("protect_chroma"):
        return "按素材类型调色，抠图键色保持原样。"
    return PRESET_TEXT.get(row["preset"], (row["preset"], "沿用处理清单的分类规则。"))[1]


def build_model(processing, validation, inventory, supplementary=None):
    validation = validation or {"status": "missing", "records": [], "errors": [], "warnings": []}
    initial = {a["path"]: a for a in inventory.get("assets", [])}
    latest = {a["path"]: a for a in (supplementary or {}).get("assets", [])}
    records = {r["path"]: r for r in processing.get("records", [])}
    verified = {r["path"]: r for r in validation.get("records", [])}
    rows = []
    for path in sorted(set(initial) | set(latest) | set(records)):
        asset = latest.get(path, initial.get(path, {}))
        record, check = records.get(path), verified.get(path)
        matches = bool(record and check and record.get("output_sha256") and record.get("original_sha256")
                       and check.get("output_sha256") == record.get("output_sha256")
                       and check.get("original_sha256") == record.get("original_sha256"))
        if record:
            published = record.get("status", processing.get("status")) == "published"
            if record.get("status") in {"failed", "error"} or (matches and check.get("status") == "failed"):
                state = "failed"
            elif published and matches and check.get("status") == "passed":
                state = "revised" if record.get("changed") else "preserved"
            elif not published:
                state = "prepared" if record.get("output_sha256") else "pending"
            else:
                state = "unverified"
        else:
            state = "pending" if asset.get("treatment_included") else "excluded"
        row = {"path": path, "classification": asset.get("classification", (record or {}).get("classification", "unknown")),
               "state": state, "preset": (record or {}).get("preset", "preserve" if state == "excluded" else "unknown"),
               "record": record, "latest": latest.get(path), "validation": check if matches else None,
               "brightness": luminance_pair(check) if matches else None,
               "backup": (record or {}).get("backup"), "kind": (record or {}).get("kind", "")}
        row["note"] = note_for(row)
        rows.append(row)
    counts = Counter(row["state"] for row in rows)
    fresh = bool(records) and all(
        path in verified and verified[path].get("output_sha256") == record.get("output_sha256")
        and verified[path].get("original_sha256") == record.get("original_sha256")
        for path, record in records.items())
    complete = (processing.get("status") == "published" and validation.get("status") == "passed" and fresh
                and all(row["state"] in {"revised", "preserved", "excluded"} for row in rows))
    by_preset = Counter(r.get("preset", "unknown") for r in records.values())
    presets = []
    for key in [*PRESET_TEXT, *sorted(set(by_preset) - set(PRESET_TEXT))]:
        if key not in by_preset:
            continue
        title, description = PRESET_TEXT.get(key, (key, "沿用处理清单中的专用规则。"))
        cfg = processing.get("presets", {}).get(key, {})
        upper = float(cfg.get("ev", 0)) + float(cfg.get("neutral_ev", 0)) if cfg else None
        presets.append({"key": key, "title": title, "description": description,
                        "count": by_preset[key], "highlight_ev_limit": upper})
    supplementary_summary = (supplementary or {}).get("summary", {})
    return {"rows": rows, "counts": counts, "presets": presets,
            "complete": complete, "validation_fresh": fresh,
            "overall": "已完成并通过验收" if complete else "结果尚待完成或验收",
            "processing": processing, "validation": validation, "inventory": inventory,
            "supplementary": supplementary,
            "initial_scanned": inventory.get("summary", {}).get("total_visual_files", len(initial)),
            "union_scanned": len(rows), "processing_count": len(records),
            "latest_time": processing.get("latest_snapshot_time") or (supplementary or {}).get("snapshot_time"),
            "latest_new": supplementary_summary.get("by_change_type", {}).get("new_since_audit", 0),
            "latest_revised": supplementary_summary.get("by_change_type", {}).get("changed_since_audit", 0),
            "latest_characters": sum(path.startswith("q_daoist_character_pack_4096/") for path in latest),
            "generated_at": datetime.now(timezone.utc).isoformat()}


def representative_rows(model, workspace: Path, output_dir: Path):
    by_path = {row["path"]: row for row in model["rows"]}
    candidates = list(REPRESENTATIVES)
    latest_characters = [row for row in model["rows"] if row["latest"] and row["path"].startswith("q_daoist_character_pack_4096/")
                         and row["path"].lower().endswith(".png") and row["preset"] == "character"]
    if latest_characters:
        candidates.insert(5, ("同期更新人物 · latest 原图", latest_characters[0]["path"]))
    else:
        portraits = [row for row in model["rows"] if row["path"].startswith("q_daoist_character_pack_4096/")
                     and row["path"].lower().endswith(".png") and row["preset"] == "character"]
        if portraits:
            candidates.insert(5, ("职业人物", portraits[0]["path"]))
    chosen, used = [], set()
    for title, path in candidates:
        row = by_path.get(path)
        if not row or not row["backup"] or path in used:
            continue
        current = safe_path(workspace, path)
        backup = safe_path(output_dir, row["backup"])
        if not current.is_file() or not backup.is_file():
            continue
        chosen.append({**row, "title": title, "current_url": relative_url(current, output_dir),
                       "backup_url": relative_url(backup, output_dir)})
        used.add(path)
    if len(chosen) < 8:
        for row in model["rows"]:
            if len(chosen) >= 12:
                break
            if row["path"] in used or not row["backup"] or not row["path"].lower().endswith(".png"):
                continue
            current, backup = safe_path(workspace, row["path"]), safe_path(output_dir, row["backup"])
            if current.is_file() and backup.is_file() and row["record"]:
                chosen.append({**row, "title": PRESET_TEXT.get(row["preset"], ("素材对照", ""))[0],
                               "current_url": relative_url(current, output_dir), "backup_url": relative_url(backup, output_dir)})
                used.add(row["path"])
    return chosen[:12]


def scope_paragraph(model):
    return (f"初次扫描 {model['initial_scanned']:,} 个视觉文件；latest 快照新增 {model['latest_new']:,} 个路径、"
            f"更新 {model['latest_revised']:,} 个已有路径。合并去重后登记 {model['union_scanned']:,} 个路径，"
            f"其中 {model['processing_count']:,} 个进入本轮处理清单。参考、诊断和归档文件单列保留。")


def latest_paragraph(model):
    if not model["supplementary"]:
        return "本报告未发现 supplementary_inventory.json；同期新增素材未提供 latest 快照记录。"
    return (f"同期素材以 {pretty_time(model['latest_time'])} 的 latest 原始快照为准，"
            f"其中包含 {model['latest_characters']} 个更新人物路径。"
            "表内标注“latest”的文件使用该快照作为调色前基线；这是当时捕获的原字节，不代表持续跟踪其他任务之后的修改。")


def report_markdown(model, representatives):
    counts, validation = model["counts"], model["validation"]
    preserved = counts["preserved"]
    pending = counts["pending"] + counts["prepared"] + counts["unverified"]
    lines = ["# 五行奇谈 · 曝光修复交付报告", "", f"**{model['overall']}**。生成时间：{pretty_time(model['generated_at'])}。", "",
             "[打开逐文件搜索与前后对照](index.html) · [处理清单](processing.json) · [验收记录](validation.json)", "",
             "| 扫描登记 | 已修复 | 本轮保留 | 失败文件 | 待完成 |", "|---:|---:|---:|---:|---:|",
             f"| {model['union_scanned']:,} | {counts['revised']:,} | {preserved:,} | {counts['failed']:,} | {pending:,} |", "",
             f"本轮处理 {model['processing_count']:,} 个文件：修正 {counts['revised']:,} 个、原样保留 {counts['preserved']:,} 个。另有归档保留 {counts['excluded']:,} 个，不计入本轮处理量。"
             f"只有已发布且通过对应哈希验收的文件计入“已修复”。", "", scope_paragraph(model), "",
             "## 处理结果", "",
             "明亮场景重点控制天空、云雾和亮地面；人物与图标使用轻档，保留肤色、白毛、金饰与暗部层次。"
             "天墉城地图已有清晰的石路、瓦顶和树林层次，保留原亮度的原因是避免暗部继续变重。具体处理状态见逐文件表。", "",
             "| 方案 | 清单文件数 | 用途 |", "|---|---:|---|"]
    lines.extend(f"| {p['title']}（{p['key']}） | {p['count']:,} | {p['description']} |" for p in model["presets"])
    lines += ["", "这些是同源分组的固定规则；同一图像的别名共用结果。透明度、透明区域隐藏 RGB、地图切片、图集和 GIF 结构由独立验收检查。", "",
              "## 代表图前后对照", "", "HTML 页并列显示原图与正式路径，图像可点击查看原尺寸。此报告不另生成对比彩图。", "",
              "| 代表图 | 调色前原图 | 正式文件 | 亮度（0–100） |", "|---|---|---|---|"]
    lines.extend(f"| {r['title']} | [原图]({r['backup_url']}) | [正式文件]({r['current_url']}) | {brightness_text(r['brightness'])} |" for r in representatives)
    lines += ["", "亮度来自匹配当前处理哈希的验收结果，使用可见区域 alpha 加权的 sRGB 亮度均值。"
              "SVG 显示第一张内嵌 PNG、GIF 显示第一帧，完整数据见验收记录；未统计的文件不填造数值。", "",
              "## 验收与同期更新", "", f"验收状态：`{validation.get('status', 'missing')}`；"
              f"与当前处理清单的哈希对应：{'是' if model['validation_fresh'] else '否或尚未验收'}。", "",
              f"验收错误 {len(validation.get('errors', []))} 条，提示 {len(validation.get('warnings', []))} 条。"
              "图集原有差异与新增失败分开记录。", "", ATLAS_VERSION_NOTE, "", latest_paragraph(model)]
    if model["supplementary"]:
        lines += ["", "[latest 原始快照清单](supplementary_inventory.json)"]
    if validation.get("errors"):
        lines += ["", "### 待解决的验收问题", ""]
        for error in validation["errors"][:20]:
            lines.append(f"- `{error.get('check', 'unknown')}`：`{error.get('path', '')}` — {str(error.get('detail', '')).replace(chr(10), ' ')}")
        if len(validation["errors"]) > 20:
            lines.append("- 其余问题见 validation.json。")
    lines += ["", "## 原图备份与恢复", "", "原图保存在 `backups/<原图SHA-256>.<原扩展名>`，处理清单保存每个正式路径的备份对应关系。"
              "重复运行调色从原图开始，避免在已调暗的结果上继续叠加。", "",
              "在仓库根目录运行以下命令可恢复本轮记录的原图：", "", "```powershell", RESTORE_COMMAND, "```", "",
              "恢复会替换本轮正式路径；若文件已经被其他任务再次修改，恢复脚本会拒绝覆盖。", "",
              "## 范围与限制", "", "- 调色可降低已有高光，无法恢复原图中已经剪切成纯白的细节。",
              "- 数值验收补充视觉检查，不能单凭亮度占比判定白毛、纸底或发光效果是否过曝。",
              "- 本轮处理仅限此素材仓库，不推送远端，不写入客户端工程。", ""]
    return "\n".join(lines)


CSS = r"""
:root{color-scheme:light;--paper:#efeee7;--panel:#f8f7f2;--ink:#22352e;--muted:#58655d;--line:#cdd4c9;--jade:#215947;--soft:#e0ebe1;--gold:#9b7029;--danger:#933e36;--preview:#727873;font-family:Segoe UI,Microsoft YaHei,PingFang SC,system-ui,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-size:16px;line-height:1.65}a{color:var(--jade);text-underline-offset:3px}a:hover{text-decoration-thickness:2px}button,input,select{font:inherit}button,a,input,select{outline-offset:4px}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--gold)}button{cursor:pointer}header{border-top:7px solid var(--jade);padding:48px max(24px,calc((100vw - 1280px)/2)) 28px;background:var(--panel);border-bottom:1px solid var(--line)}.eyebrow{font-size:13px;font-weight:700;letter-spacing:.16em;color:var(--jade);margin:0 0 14px}.heading-line{display:flex;gap:22px;align-items:center;flex-wrap:wrap}h1{font-size:clamp(29px,4vw,46px);letter-spacing:-.045em;line-height:1.15;margin:0}h2{font-size:25px;line-height:1.35;margin:0 0 18px}h3{font-size:17px;margin:0}p{margin:12px 0}header p{max-width:980px}.muted{color:var(--muted)}.small{font-size:13px}.badge{display:inline-block;font-size:12px;line-height:1.4;padding:5px 9px;border:1px solid var(--line);border-radius:3px;white-space:nowrap;background:var(--panel)}.badge.revised,.badge.preserved{color:var(--jade);background:var(--soft);border-color:#b7cbb8}.badge.failed{background:#f2e0dc;border-color:#d3a39a;color:var(--danger)}.badge.prepared,.badge.unverified,.badge.pending{background:#eee3c8;border-color:#ccba89;color:#634917}.badge.latest{background:#e7e3f0;color:#574374}nav{display:flex;gap:20px;flex-wrap:wrap;margin-top:22px;font-size:14px}main{max-width:1328px;margin:auto;padding:30px 24px 64px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:14px}.stat{padding:20px 22px;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--jade)}.stat strong{display:block;font-size:38px;font-weight:600;line-height:1.25;font-variant-numeric:tabular-nums}.stat span{font-size:13px;color:var(--muted)}section{margin-top:44px;scroll-margin-top:20px}.section-heading{display:flex;justify-content:space-between;gap:20px;align-items:baseline;flex-wrap:wrap}.notice{padding:18px 22px;border-left:4px solid var(--gold);background:#e9e4d5}.notice p:first-child{margin-top:0}.notice p:last-child{margin-bottom:0}.preset-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.preset{background:var(--panel);padding:20px}.preset p{font-size:14px;margin:10px 0}.preset .count{font-variant-numeric:tabular-nums;color:var(--jade);font-size:13px}.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.comparison{border:1px solid var(--line);background:var(--panel);min-width:0}.comparison-heading{padding:15px 17px;border-bottom:1px solid var(--line)}.pair{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line)}figure{margin:0;min-width:0;background:var(--panel)}.image-surface{display:block;background-color:var(--preview);background-image:linear-gradient(45deg,#ffffff08 25%,transparent 25%),linear-gradient(-45deg,#ffffff08 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#ffffff08 75%),linear-gradient(-45deg,transparent 75%,#ffffff08 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.image-surface img{display:block;width:100%;height:220px;object-fit:contain}figcaption{font-size:12px;padding:8px 12px;color:var(--muted)}.comparison-footer{padding:11px 17px;font-size:12px;overflow-wrap:anywhere}.comparison-footer .metrics{display:block;font-variant-numeric:tabular-nums;margin-top:6px}.filters{display:grid;grid-template-columns:minmax(200px,1fr) 180px 180px auto;gap:12px;align-items:end;padding:18px;background:var(--panel);border:1px solid var(--line);margin:18px 0 10px}label{display:block;font-size:12px;font-weight:600;margin-bottom:5px}input,select,button{width:100%;min-height:44px;border:1px solid #acb8ac;background:var(--panel);border-radius:3px;color:var(--ink);padding:9px 11px}button{width:auto;padding:9px 18px;background:var(--soft)}.table-wrap{overflow:auto;max-height:72vh;border:1px solid var(--line);background:var(--panel)}table{border-collapse:collapse;width:100%;font-size:13px;min-width:850px}th,td{padding:13px 15px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{font-size:12px;background:#e2e8df;position:sticky;top:0;z-index:1;color:var(--ink);white-space:nowrap}th:first-child{width:40%}td .path{overflow-wrap:anywhere;word-break:break-word;line-height:1.5;display:block}td .subpath{display:block;color:var(--muted);font-size:11px;margin-top:4px;overflow-wrap:anywhere}.luma{white-space:nowrap;font-variant-numeric:tabular-nums}td:last-child{min-width:195px}.no-results td{padding:34px;text-align:center;color:var(--muted)}.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.detail{border-top:2px solid var(--line);padding-top:20px}pre{background:#243b31;color:#eff4ec;padding:18px;overflow:auto;font-size:13px;border-radius:3px}code{font-family:Consolas,monospace}.error-list{padding-left:22px;overflow-wrap:anywhere}.error-list li{margin:10px 0}footer{margin-top:40px;border-top:1px solid var(--line);padding-top:20px;font-size:12px;color:var(--muted)}[hidden]{display:none!important}.skip{position:absolute;left:20px;top:-70px;z-index:10;background:var(--panel);padding:10px}.skip:focus{top:12px}
@media(max-width:980px){.preset-grid{grid-template-columns:repeat(2,1fr)}.filters{grid-template-columns:1fr 1fr}.filters>div:first-child{grid-column:1/-1}.image-surface img{height:185px}.stats{gap:9px}.stat{padding:15px}.stat strong{font-size:30px}.details-grid{grid-template-columns:1fr}}
@media(max-width:620px){header{padding:30px 18px 22px}main{padding:20px 16px 40px}.stats{grid-template-columns:repeat(2,1fr)}.compare-grid{grid-template-columns:1fr}.preset-grid{grid-template-columns:1fr 1fr}.preset{padding:15px}.filters{grid-template-columns:1fr}.filters>div:first-child{grid-column:auto}.filters button{width:100%}.image-surface img{height:190px}nav{gap:12px 18px}.heading-line{gap:14px}h2{font-size:23px}.stat strong{font-size:32px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:white}header{padding:20px 0}main{padding:20px 0;max-width:none}.filters,nav,.skip{display:none}.table-wrap{max-height:none;overflow:visible}.comparison{break-inside:avoid}.image-surface img{height:160px}.compare-grid{grid-template-columns:1fr 1fr}th{position:static}}
"""

JAVASCRIPT = r"""
(() => {
  const search = document.getElementById('file-search');
  const state = document.getElementById('state-filter');
  const preset = document.getElementById('preset-filter');
  const rows = [...document.querySelectorAll('#file-table tbody tr[data-search]')];
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-row');
  let pending;
  function apply() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const row of rows) {
      const match = terms.every(term => row.dataset.search.includes(term)) &&
        (!state.value || row.dataset.state === state.value) &&
        (!preset.value || row.dataset.preset === preset.value);
      row.hidden = !match;
      if (match) shown += 1;
    }
    count.textContent = `显示 ${shown.toLocaleString()} / ${rows.length.toLocaleString()} 个文件`;
    empty.hidden = shown !== 0;
  }
  search.addEventListener('input', () => { clearTimeout(pending); pending = setTimeout(apply, 100); });
  state.addEventListener('change', apply);
  preset.addEventListener('change', apply);
  document.getElementById('reset-filters').addEventListener('click', () => {
    clearTimeout(pending); search.value = ''; state.value = ''; preset.value = ''; apply(); search.focus();
  });
  apply();
})();
"""


def report_html(model, representatives, workspace, output_dir):
    counts, validation = model["counts"], model["validation"]
    preserved = counts["preserved"]
    pending = counts["pending"] + counts["prepared"] + counts["unverified"]
    badge = "revised" if model["complete"] else "unverified"
    stats = [("扫描登记", model["union_scanned"], "初扫与 latest 合并后的路径数"),
             ("已修复", counts["revised"], "已发布且通过对应哈希验收"),
             ("本轮保留", preserved, "本轮处理清单内原样保留"),
             ("失败文件", counts["failed"], f"另有 {len(validation.get('errors', []))} 条验收错误")]
    stats_html = "".join(f'<div class="stat"><span>{esc(label)}</span><strong>{number:,}</strong><span>{esc(note)}</span></div>' for label, number, note in stats)
    presets_html = "".join(f'<article class="preset"><h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p><span class="count">{p["count"]:,} 个清单文件 · {esc(p["key"])}</span></article>' for p in model["presets"])
    comparisons = []
    for row in representatives:
        delivered_label = "正式文件 · 修复后" if row["state"] == "revised" else "正式文件 · 原样保留" if row["state"] == "preserved" else "当前正式文件 · 尚未完成交付"
        comparisons.append(f'''<article class="comparison"><div class="comparison-heading"><h3>{esc(row['title'])}</h3></div><div class="pair">
<figure><a class="image-surface" href="{esc(row['backup_url'])}" target="_blank" rel="noopener"><img loading="lazy" decoding="async" src="{esc(row['backup_url'])}" alt="{esc(row['title'])}调色前原图"></a><figcaption>调色前 · 原始备份</figcaption></figure>
<figure><a class="image-surface" href="{esc(row['current_url'])}" target="_blank" rel="noopener"><img loading="lazy" decoding="async" src="{esc(row['current_url'])}" alt="{esc(row['title'])}当前正式文件"></a><figcaption>{esc(delivered_label)}</figcaption></figure></div>
<div class="comparison-footer"><a href="{esc(row['current_url'])}">{esc(row['path'])}</a><span class="metrics">验收亮度：{esc(brightness_text(row['brightness']))} · {esc(PRESET_TEXT.get(row['preset'],(row['preset'],''))[0])}</span></div></article>''')
    table_rows = []
    for row in model["rows"]:
        path = safe_path(workspace, row["path"])
        link = relative_url(path, output_dir)
        parent, _, name = row["path"].rpartition("/")
        latest_badge = ' <span class="badge latest">latest</span>' if row["latest"] else ""
        preset_name = PRESET_TEXT.get(row["preset"], (row["preset"], ""))[0]
        backup = f'<a href="{esc(relative_url(safe_path(output_dir,row["backup"]), output_dir))}">原图备份</a>' if row["backup"] else '<span class="muted">未改原文件</span>'
        brightness = brightness_text(row["brightness"])
        basis = row["brightness"]["basis"] if row["brightness"] else "无匹配的验收亮度数据"
        search = f"{row['path']} {STATUS_TEXT[row['state']]} {row['preset']} {preset_name} {row['classification']} {row['note']} {'latest' if row['latest'] else ''}".lower()
        table_rows.append(f'''<tr data-search="{esc(search)}" data-state="{esc(row['state'])}" data-preset="{esc(row['preset'])}"><td><a class="path" href="{esc(link)}">{esc(name or row['path'])}</a><span class="subpath">{esc(parent)}</span>{latest_badge}</td><td><span class="badge {esc(row['state'])}">{esc(STATUS_TEXT[row['state']])}</span></td><td>{esc(preset_name)}</td><td class="luma" title="{esc(basis)}">{esc(brightness)}</td><td>{backup}</td><td>{esc(row['note'])}</td></tr>''')
    status_options = "".join(f'<option value="{esc(key)}">{esc(label)}（{counts[key]:,}）</option>' for key, label in STATUS_TEXT.items() if counts[key])
    preset_options = "".join(f'<option value="{esc(p["key"])}">{esc(p["title"])}</option>' for p in model["presets"])
    errors_html = ""
    if validation.get("errors"):
        items = "".join(f'<li><strong>{esc(e.get("check","unknown"))}</strong> · {esc(e.get("path",""))}<br>{esc(e.get("detail",""))}</li>' for e in validation["errors"][:20])
        errors_html = f'<div class="notice"><h3>待解决的验收问题</h3><ul class="error-list">{items}</ul><a href="validation.json">完整验收记录</a></div>'
    latest_link = '<a href="supplementary_inventory.json">latest 快照清单</a>' if model["supplementary"] else ""
    no_compare = '<p class="muted">可用的原图备份与正式文件不足，暂不显示代表图。</p>' if not comparisons else ""
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>五行奇谈 · 曝光修复交付报告</title><style>{CSS}</style></head>
<body><a class="skip" href="#files">跳到文件搜索</a><header><p class="eyebrow">五行奇谈 / 美术素材 / V8</p><div class="heading-line"><h1>曝光修复交付报告</h1><span class="badge {badge}">{esc(model['overall'])}</span></div><p>{esc(scope_paragraph(model))}</p><p class="muted small">报告生成：{esc(pretty_time(model['generated_at']))} · 待处理、待应用或待验收：{pending:,} 个文件</p><nav aria-label="报告导航"><a href="#comparisons">前后对照</a><a href="#files">逐文件搜索</a><a href="#method">分类方案</a><a href="#validation">验收与恢复</a><a href="REPORT.md">Markdown 报告</a></nav></header>
<main><div class="stats" aria-label="结果统计">{stats_html}</div><p class="small muted">本轮处理 {model['processing_count']:,} 个文件；归档保留 {counts['excluded']:,} 个另列。已修复仅统计完成发布、且哈希对应验收通过的文件。</p>
<section id="comparisons"><div class="section-heading"><h2>原图与正式文件</h2><p class="small muted">{len(comparisons)} 组代表图 · 相同背景 · 点击查看原尺寸</p></div><p>场景重点收住亮地面与云雾；人物、图标使用轻档。天墉城地图已有清晰暗部，保留原亮度，避免屋顶和树林继续变重。</p>{no_compare}<div class="compare-grid">{''.join(comparisons)}</div></section>
<section id="method"><h2>按用途确定调色强度</h2><div class="preset-grid">{presets_html}</div><p class="small muted">同源素材与别名共用处理结果。原图保留；透明度、键色与文件结构按各自用途保护。</p></section>
<section id="files"><div class="section-heading"><h2>逐文件记录</h2><p id="result-count" class="small muted" role="status" aria-live="polite">全部 {len(model['rows']):,} 个文件</p></div><div class="filters"><div><label for="file-search">路径或关键词</label><input id="file-search" type="search" placeholder="例如：login、天墉城、character、latest" autocomplete="off"></div><div><label for="state-filter">处理状态</label><select id="state-filter"><option value="">全部状态</option>{status_options}</select></div><div><label for="preset-filter">调色方案</label><select id="preset-filter"><option value="">全部方案</option>{preset_options}</select></div><button id="reset-filters" type="button">重置筛选</button></div><p class="small muted">亮度使用 0–100 标度，来自对应验收的可见区域 alpha 加权 sRGB 均值；SVG 取第 1 张内嵌 PNG，GIF 取第 1 帧。完整结果见验收记录。</p><div class="table-wrap" tabindex="0" aria-label="可滚动的逐文件记录"><table id="file-table"><thead><tr><th scope="col">素材路径</th><th scope="col">状态</th><th scope="col">方案</th><th scope="col">调色前 → 后</th><th scope="col">原图</th><th scope="col">说明</th></tr></thead><tbody>{''.join(table_rows)}<tr id="empty-row" class="no-results" hidden><td colspan="6">没有匹配文件，请修改关键词或重置筛选。</td></tr></tbody></table></div></section>
<section id="validation"><h2>验收、同期更新与恢复</h2>{errors_html}<div class="details-grid"><div class="detail"><h3>验收依据</h3><p>状态：<strong>{esc(validation.get('status','missing'))}</strong>。验收记录与当前处理清单哈希{'一致' if model['validation_fresh'] else '尚未完整对应'}；错误 {len(validation.get('errors',[]))} 条，提示 {len(validation.get('warnings',[]))} 条。</p><p>独立检查尺寸、模式、透明度、透明区域隐藏颜色、亮度、地图切片、图集和 GIF 帧结构。已有图集差异与新增失败分别报告。</p><p>{esc(ATLAS_VERSION_NOTE)}</p><p><a href="validation.json">查看完整验收</a> · <a href="processing.json">处理清单</a> · <a href="inventory.json">初次盘点</a></p></div><div class="detail"><h3>同期新人物与素材</h3><p>{esc(latest_paragraph(model))}</p><p>{latest_link}</p></div><div class="detail"><h3>原图恢复</h3><p>每个处理路径对应一份以原图 SHA-256 命名的完整备份。在仓库根目录执行：</p><pre><code>{esc(RESTORE_COMMAND)}</code></pre><p class="small">恢复会替换本轮结果；若目标又被其他任务修改，脚本会拒绝覆盖。调色重复运行仍从备份原图开始。</p></div><div class="detail"><h3>结果边界</h3><p>调色能降低已有高光，无法恢复已经剪切成纯白的细节。亮度统计不能替代对皮肤、白毛、纸底和发光效果的视觉判断。</p><p>本轮仅处理此素材仓库，不推送远端，不写入客户端工程。</p></div></div></section><footer>本页离线可读，搜索在浏览器本地完成。图像直接引用原始备份和正式素材路径，未重新制作比较彩图。</footer></main><script>{JAVASCRIPT}</script></body></html>'''


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args(argv)
    output_dir = args.package.resolve()
    processing = read_json(output_dir / "processing.json")
    inventory = read_json(output_dir / "inventory.json")
    validation = read_json(output_dir / "validation.json", optional=True)
    supplementary = read_json(output_dir / "supplementary_inventory.json", optional=True)
    workspace = (args.workspace or Path(processing.get("workspace_root", output_dir.parent))).resolve()
    model = build_model(processing, validation, inventory, supplementary)
    representatives = representative_rows(model, workspace, output_dir)
    markdown = report_markdown(model, representatives)
    webpage = report_html(model, representatives, workspace, output_dir)
    (output_dir / "REPORT.md").write_text(markdown, encoding="utf-8")
    (output_dir / "index.html").write_text(webpage, encoding="utf-8")
    print(json.dumps({"report": str(output_dir / "REPORT.md"), "html": str(output_dir / "index.html"),
                      "status": model["overall"], "registered_paths": model["union_scanned"],
                      "representatives": len(representatives), "states": dict(model["counts"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
