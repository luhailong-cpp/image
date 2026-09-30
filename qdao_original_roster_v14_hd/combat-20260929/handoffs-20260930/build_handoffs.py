"""Capture current combat inventory and write per-character continuation documents.

Reads image pixels for verification only. Never generates or changes an image.
All outputs stay inside this handoff directory.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
from PIL import Image

OUT = Path(__file__).resolve().parent
BATCH = OUT.parent
REPO = BATCH.parents[1]
ACTIONS = {"hit": 6, "attack": 12, "cast": 16}
DATA = json.loads((OUT / "character-details.json").read_text(encoding="utf-8"))
STAMP = datetime.now(timezone.utc)
LOCAL = STAMP.astimezone(timezone(timedelta(hours=-4))).strftime("%Y-%m-%d %H:%M EDT")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def link(label, path):
    return f"[{label}](<{Path(path).as_posix()}>)"


def numbers(values):
    values = sorted(values)
    if not values:
        return "无"
    groups = []
    start = end = values[0]
    for value in values[1:]:
        if value == end + 1:
            end = value
        else:
            groups.append(f"{start:02d}" if start == end else f"{start:02d}–{end:02d}")
            start = end = value
    groups.append(f"{start:02d}" if start == end else f"{start:02d}–{end:02d}")
    return "、".join(groups)


snapshots = []
for info in DATA:
    character = BATCH / "characters" / info["id"]
    refs = {}
    for key in ("portrait", "idleE", "idleW", "style"):
        path = Path(info[key])
        if not path.is_file():
            raise RuntimeError(f"Missing reference: {path}")
        with Image.open(path) as im:
            refs[key] = {"path": path.as_posix(), "sha256": sha(path), "size": list(im.size), "mode": im.mode}
            im.verify()
    selected_map, selections = {}, []
    for path in sorted(character.glob("*selection.json")) + sorted((character / "staging").glob("*selection.json")):
        selection = json.loads(path.read_text(encoding="utf-8-sig"))
        action, direction = selection.get("action"), selection.get("direction")
        if action not in ACTIONS or direction not in ("E", "W"):
            continue
        selections.append({"path": path.as_posix(), "sha256": sha(path), "action": action, "direction": direction})
        for frame in selection["frames"]:
            relative = Path(frame["file"])
            source = BATCH / relative if relative.parts[0] == "characters" else character / relative
            selected_map[source.resolve()] = (action, direction, frame["frame"])
    slots = {(a, d, f): [] for a, n in ACTIONS.items() for d in ("E", "W") for f in range(1, n + 1)}
    images = []
    for path in sorted((character / "staging").glob("*.png")):
        match = re.match(r"(hit|attack|cast)-([EW])-(\d{2})-", path.name)
        key = selected_map.get(path.resolve())
        if key is None and match:
            key = (match[1], match[2], int(match[3]))
        with Image.open(path) as im:
            row = {"file": path.as_posix(), "sha256": sha(path), "nativeSize": list(im.size), "mode": im.mode}
            im.verify()
        row["slot"] = list(key) if key else None
        row["slotBasis"] = "explicit_selection" if path.resolve() in selected_map else "filename_candidate_only"
        images.append(row)
        if key in slots:
            slots[key].append(row["file"])
    runtime = [p for a, d, f in slots if (p := character / "runtime" / a / d / f"{f:02d}.png").is_file()]
    covered = sum(bool(value) for value in slots.values())
    groups = []
    for a, n in ACTIONS.items():
        for d in ("E", "W"):
            present = [f for f in range(1, n + 1) if slots[a, d, f]]
            missing = [f for f in range(1, n + 1) if not slots[a, d, f]]
            groups.append({"action": a, "direction": d, "required": n, "candidateFrames": present, "missingCandidateFrames": missing})
    snapshot = {"id": info["id"], "name": info["name"], "candidatePngAttempts": len(images), "candidateSlots": covered,
                "missingCandidateSlots": 68 - covered, "runtimePngSlots": len(runtime), "references": refs,
                "selections": selections, "groups": groups, "images": images, "visualAcceptance": "not_established"}
    snapshots.append(snapshot)
    lines = [f"# {info['id'][:2]} {info['name']}：战斗动作独立新窗口交接", "",
             f"库存核对：{LOCAL}。下面是用户已授权的续作任务；只负责 `{info['id']}`，完成后不自动接下一角色。",
             "", "## 可直接复制给新窗口", "", "```text",
             f"请在 D:\\luyuan\\wuxingqitan\\image 继续完成 {info['id']}（{info['name']}）的战斗图片。",
             f"先完整读取 {OUT.as_posix()}/{info['id']}.md 和 {OUT.as_posix()}/COMMON_CONTRACT.md，按当前磁盘重新核对库存后直接续作。",
             "本角色每方向受击6帧、普通攻击12帧、施法16帧；E/W分别独立绘制，共68张1024×1024透明PNG。",
             "保留已有候选和来源，不从头重做；不镜像、复制、扭曲或插值凑帧，不覆盖移动、站立、肖像。",
             f"只写 {character.as_posix()} 内的图片、提示词、来源、选表和预览验收文件。",
             "做到本角色68帧选定、透明PNG导出、逐图来源齐全、六段按正常速度连播验收，并写明未做的客户端接入/运行验证。",
             "```", "", "## 当前库存与准确缺槽", "",
             f"已有 **{len(images)} 张 staging PNG尝试稿**，覆盖 **{covered}/68 个候选槽**；还有 **{68-covered} 个槽没有候选**。标准 runtime 路径实际有 **{len(runtime)}/68 张**。候选齐全、导出、视觉验收与客户端接入分别计算。",
             "", "| 动作/方向 | 所需 | 已有候选槽 | 没有候选的帧号 |", "|---|---:|---|---|"]
    for group in groups:
        lines.append(f"| {group['action']}/{group['direction']} | {group['required']} | {numbers(group['candidateFrames'])} | {numbers(group['missingCandidateFrames'])} |")
    lines += ["", "已有选表："]
    lines += [f"- {link(Path(s['path']).name, s['path'])}" for s in selections] or ["- 尚无完整显式选表；请核对候选后建立，不按最高版本号自动选稿。"]
    if images:
        lines += ["", "候选原图和SHA清单见本目录 `inventory-snapshot.json` 对应角色条目。`staging` 中重试稿不能重复计数；提示词及失败回执不计成图。"]
    if info["id"].startswith("00_"):
        lines += ["", "### 00续接要点", "",
                  "- hit/E 的真实顺序为01-v1、03-v3、02-v1、04-v1、05-v1、06-v1，保留既有选表。",
                  "- hit/W 的01实际使用hit-W-03-v1，之后02-v1、03-v2、04-v1、05-v1、06-v1；不要因没有hit-W-01文件误报缺槽。",
                  "- attack/E选04-v2和07-v2，其余v1。已选24槽的源图/记录SHA已核对一致。",
                  "- cast/E全部16槽已有候选但有多份重试；cast/W目前01–15有候选，10含重试，不能自动取最高版本；两方向最终选表仍需确认。",
                  "- cast/W/15已从前窗口completed工具结果原字节恢复；来源证据见本交接目录recovered-cast-W-15-tool-result.json及角色receipts/cast-W-15-v1.json。未新生图，实际模型/质量和未暴露提交参数仍记null。",
                  "- export-preview-20260930-v1只包含hit E/W及attack E的24张1024技术预览，不属于runtime成品；其固定90ms慢放不是契约速度。",
                  "- 静态序列复核点：hit/E最后一帧可能显得身体变高；hit/W 02/03后仰峰值顺序与03→04回弹偏急；attack/E09→10→11有头高上跳后回落风险。需按40/30ms连播再判定，必要时定向重画。",
                  "- 当前缺W普攻01–12与W施法16。先补缺，再统一选序、固定画布变换导出、六段验收。"]
    lines += ["", "## 必须实际附入生图的参考", ""]
    for key, title in [("portrait", "身份肖像"), ("idleE", "E朝右身份/朝向参考"), ("idleW", "W朝左身份/朝向参考"), ("style", "已确认主要风格样板")]:
        ref = refs[key]
        lines.append(f"- {link(title, ref['path'])}（当前{ref['size'][0]}×{ref['size'][1]}，{ref['mode']}）。")
    lines += ["", "参考尺寸不等于新成品尺寸；旧512仅作身份/朝向参考，不能放大充当新高清动作。实际view_image后再附图。",
              "", "## 身份与持手锁定", "", info["identity"], "", "## 动作安排建议", "", info["plan"],
              "", "上述为续作建议，不是声称已画出的动作。通用阶段与正常速度见COMMON_CONTRACT；命中和释放帧按最终实际选图记录，不能假称已经接入游戏。",
              "", "## 本角色特别注意", "", info["notes"],
              "", "## 产物位置及完成检查", "",
              f"- 候选：`{character.as_posix()}/staging/<action>-<E|W>-<两位帧号>-vN.png`。新增版本不覆盖现有版本。",
              f"- 提示词/来源：`{character.as_posix()}/prompts/` 与 `provenance/receipts/`，旧图旁generation.json也继续保留来源关系。",
              f"- 成品：`{character.as_posix()}/runtime/<hit|attack|cast>/<E|W>/<01起两位帧号>.png`。",
              "- 六组明确选表、68槽来源链、透明与重复像素检查、六段正常/慢放和深浅底视觉验收、交付清单。",
              "- hit正常40ms/帧，attack30ms/帧，cast45ms/帧；慢放必须显示倍率。",
              "- 站位/击退由代码设置，不为每个站位复制一套图；本窗口不改客户端。",
              "", "技术检查命令（只在自己的角色目录输出，不使用共享默认report）：", "", "```powershell",
              "Set-Location -LiteralPath 'D:\\luyuan\\wuxingqitan\\image'",
              f"python qdao_original_roster_v14_hd/combat-20260929/tools/audit_combat.py --characters {info['id']} --out qdao_original_roster_v14_hd/combat-20260929/characters/{info['id']}/audit-handoff --allow-incomplete",
              "```", "", "制作中allow-incomplete只改变退出码，不把缺帧或视觉问题变成通过。最终验收移除该参数，并阅读实际结果；来源/姿态/镜像/连播仍需另核。共享export_selected.py有00固定参考和90ms限制，先阅读共同契约再决定在本角色目录适配。"]
    write(info["id"] + ".md", "\n".join(lines))

scope = json.loads((BATCH.parent / "CONTINUATION_STATE_20260920_SCOPE_UPDATED.json").read_text(encoding="utf-8-sig"))
assert [r["id"] for r in DATA] == scope["active_character_ids"], "Handoff roster differs from active scope"
total = {"candidatePngAttempts": sum(r["candidatePngAttempts"] for r in snapshots), "candidateSlots": sum(r["candidateSlots"] for r in snapshots),
         "missingCandidateSlots": sum(r["missingCandidateSlots"] for r in snapshots), "runtimePngSlots": sum(r["runtimePngSlots"] for r in snapshots), "requiredSlots": 1020}
write("inventory-snapshot.json", json.dumps({"capturedAt": STAMP.isoformat(), "displayTime": LOCAL, "scope": "staging candidates and standard runtime paths; not visual acceptance", "totals": total, "characters": snapshots}, ensure_ascii=False, indent=2))
index = ["# 15人战斗动作：逐角色新窗口交接", "", f"核对时间：{LOCAL}。尚未全部完成。", "",
         f"当前{total['candidatePngAttempts']}张PNG尝试稿覆盖{total['candidateSlots']}/1020候选槽，{total['missingCandidateSlots']}槽仍无候选；标准runtime路径合计{total['runtimePngSlots']}/1020。没有任何角色凭本次核查完成68帧导出与整段验收。",
         "", "打开下面某人的文件，复制开头任务到一个新窗口；或使用[15条一键复制文本](COPY_PROMPTS.md)。一窗口一角色，先从已有候选继续。",
         "", "- [完整共同契约](COMMON_CONTRACT.md)：规格、来源记录、并行写入边界、工具限制、验收方法。",
         "- [当前文件与SHA快照](inventory-snapshot.json)：逐候选及身份/朝向/风格参考的真实尺寸和哈希。",
         "", "| 角色交接 | 已有候选槽 | 尚无候选 | runtime PNG |", "|---|---:|---:|---:|"]
for row in snapshots:
    index.append(f"| [{row['id'][:2]} {row['name']}]({row['id']}.md) | {row['candidateSlots']}/68 | {row['missingCandidateSlots']} | {row['runtimePngSlots']}/68 |")
index += ["", "00、01、14曾由聊天「制作人物回合制战斗动作图」（01a0eba1-485d-7f81-aaca-4b4c48fdc021）及其子任务制作；2026-09-30 06:23 EDT父聊天状态为interrupted/notLoaded。若以后恢复，不要同时另开同角色生产。其余角色可分窗各自只写对应combat角色目录。",
          "", "本次额外恢复了00 cast/W/15：从旧聊天已completed的原图复制到当前staging并建立追溯，未重新生图、未改像素。移动PNG未改。所有候选仍需选图和视觉验收。旧战斗README及9月29日恢复交接的库存过时，本快照只补充当前事实，不改写旧记录。"]
write("INDEX.md", "\n".join(index))
prompts = ["# 分别复制到15个新窗口的任务", "", "每个代码块只给一个窗口。详细交接和共同契约都已落在项目中；直接读文件，不需要用户再次上传图片。00/01/14先检查旧聊天及最新落盘，避免重复制作。", ""]
for info in DATA:
    prompts += [f"## {info['id'][:2]} {info['name']}", "", "```text", f"在 D:\\luyuan\\wuxingqitan\\image 继续完成 {info['id']}（{info['name']}）的受击、普通攻击、施法动作。先完整读取 {OUT.as_posix()}/{info['id']}.md 和同目录 COMMON_CONTRACT.md，核对当前库存后直接续作。只负责这个角色；按E/W独立绘制，受击6、普攻12、施法16帧/方向，共68张1024透明PNG，补齐后完成来源记录、统一导出与六段连播验收。保护移动与已有在制稿，不复制/镜像/插值凑帧，不写其他角色或共享文件，不宣称尚未做的客户端验收。", "```", ""]
write("COPY_PROMPTS.md", "\n".join(prompts))
print(json.dumps({"handoffs": len(DATA), "referencesVerified": len(DATA)*4, "totals": total, "index": str(OUT / "INDEX.md")}, ensure_ascii=False))
