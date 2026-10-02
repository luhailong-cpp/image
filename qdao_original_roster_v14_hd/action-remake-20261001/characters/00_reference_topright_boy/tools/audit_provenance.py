"""Read current 00 files and refresh handoff evidence; never changes images or old records.

Only writes review/provenance-completion.json and the delimited snapshot blocks
in STATUS.md and MERGE_HANDOFF.md. Counts come from actual files on every run.
"""
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
PYTHON = "C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
SPECS = {"run": (16, ("N", "NE", "E", "SE", "S", "SW", "W", "NW"), 30),
         "hit": (6, ("E", "W"), 40), "attack": (12, ("E", "W"), 30),
         "cast": (16, ("E", "W"), 45)}
DOCUMENTS = ["manifest.json", "sources.json", "review/current-validation.json",
             "review/technical_report.json", "review/scale-audit.json", "review/scale-audit.md",
             "review/combat-reviewed.json", "review/combat-reviewed.md",
             "review/cast-selection.json", "review/cast-review.md", "review/visual-notes.json"]
SUPPLEMENT_TARGETS = {
    "generation/run/E/04-v1.png": "ecc55b1b0e7dea0d3f2077e106a229d679e7f2e71cacba773df263f0a6927a06",
    "generation/run/E/09-v3.png": "703ab6983638bbcd29488af9806644205168a508c7bd85f6bb6ea56d208e5a83"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def local(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def evidence(path):
    p = local(path)
    return {"path": p.as_posix(), "exists": p.is_file(),
            "sha256": sha(p) if p.is_file() else None}


def png(path):
    row = evidence(path)
    with Image.open(path) as im:
        row.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
    return row


def refresh_block(name, lines):
    p = ROOT / name
    if not p.is_file():
        return
    text = p.read_text(encoding="utf-8")
    replacement = "<!-- CURRENT_SNAPSHOT_START -->\n" + "\n".join(lines) + "\n<!-- CURRENT_SNAPSHOT_END -->"
    updated, count = re.subn(r"<!-- CURRENT_SNAPSHOT_START -->.*?<!-- CURRENT_SNAPSHOT_END -->",
                            lambda _: replacement, text, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one snapshot block in {name}, found {count}")
    p.write_text(updated, encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.now(ZoneInfo("America/New_York")).isoformat()
    # Read every complete document, rather than trusting a cached headline count.
    docs = {name: load(ROOT / name) for name in DOCUMENTS if name.endswith(".json")}
    document_evidence = [evidence(name) for name in DOCUMENTS]
    manifest = docs["manifest.json"]
    sources = docs["sources.json"]
    validation = docs["review/current-validation.json"]
    scale = docs["review/scale-audit.json"]
    by_file = {f["file"]: f for f in manifest["frames"]}
    actual_files = sorted((ROOT / "frames").rglob("*.png"))
    issues, inventory = [], []
    for path in actual_files:
        rel = path.relative_to(ROOT).as_posix()
        row = png(path)
        row["relativePath"] = rel
        m = by_file.get(rel)
        s = sources["frames"].get(rel.removeprefix("frames/"))
        row["manifestRecord"] = m
        row["sourcesRecord"] = s
        row["sidecar"] = evidence(str(path) + ".generation.json")
        row["shaMatchesManifest"] = bool(m and row["sha256"] == m.get("sha256"))
        row["shaMatchesSources"] = bool(s and row["sha256"] == s.get("export_sha256"))
        if not row["shaMatchesManifest"] or not row["shaMatchesSources"]:
            issues.append({"file": rel, "issue": "inventory_index_sha_mismatch"})
        if m:
            origin = m["derivedFrom"]
            row["sourceFile"] = evidence(origin["file"])
            row["sourceShaMatches"] = row["sourceFile"]["sha256"] == origin["sha256"]
            row["sourceEvidence"] = [evidence(e["path"]) for e in origin.get("evidence", [])]
            record = origin.get("generationRecord")
            if record:
                row["generationRecordEvidence"] = evidence(record)
                # Preserve the original record verbatim, including unconfirmed model/quality.
                row["originalGenerationRecord"] = load(record) if local(record).is_file() else None
            if not row["sourceShaMatches"]:
                issues.append({"file": rel, "issue": "source_missing_or_sha_mismatch"})
        inventory.append(row)
    absent_index_files = [name for name in by_file if not (ROOT / name).is_file()]
    issues.extend({"file": name, "issue": "indexed_export_missing"} for name in absent_index_files)

    generated, request_to_image = [], {}
    for path in sorted((ROOT / "generation").rglob("*.png")):
        row = png(path)
        rel = path.relative_to(ROOT).as_posix()
        row["relativePath"] = rel
        record_path = Path(str(path) + ".generation.json")
        row["generationRecord"] = evidence(record_path)
        record = load(record_path) if record_path.is_file() else {}
        row["originalRecord"] = record
        row["shaMatchesRecord"] = row["sha256"] == record.get("sha256")
        row["selectedForExports"] = [x["relativePath"] for x in inventory
                                       if x.get("sourceFile", {}).get("sha256") == row["sha256"]]
        request = record.get("evidence", {}).get("request")
        if request:
            request_to_image[local(request).as_posix()] = rel
        request_to_image[path.with_suffix(".request.json").as_posix()] = rel
        generated.append(row)

    requests = []
    for path in sorted((ROOT / "generation").rglob("*.request.json")):
        row = evidence(path)
        row["relativePath"] = path.relative_to(ROOT).as_posix()
        data = load(path)
        row["originalRequestStatus"] = data.get("status", "not_recorded")
        base = str(path).removesuffix(".request.json")
        outcomes = [Path(base + suffix) for suffix in (".receipt.json", ".tool-result.json", ".failure.json")]
        row["outcomeEvidence"] = [evidence(p) for p in outcomes if p.is_file()]
        image_path = request_to_image.get(path.as_posix())
        failure = Path(base + ".failure.json")
        row["localOutput"] = image_path
        if image_path:
            row["outcome"] = "confirmed_local_image"
        elif failure.is_file():
            raw = load(failure)
            row["outcome"] = "confirmed_failure"
            row["originalFailure"] = raw
        elif row["outcomeEvidence"]:
            row["outcome"] = "receipt_present_no_linked_local_image_review_needed"
        else:
            row["outcome"] = "unknown_no_completion_receipt"
            row["note"] = "无完成回执及关联PNG；可能未结束或历史中断，不能推断为已确认失败。"
        requests.append(row)

    config_path = REPO / "config/image-generation.json"
    config = load(config_path)
    supplements = []
    for row in generated:
        rel = row["relativePath"]
        rec = row["originalRecord"]
        if SUPPLEMENT_TARGETS.get(rel) == row["sha256"] and not rec.get("configSnapshot", {}).get("sources"):
            old = rec.get("configSnapshot", {})
            same = all(old.get(k) == config.get(k) for k in ("model", "quality", "builtin_product", "verified_on"))
            supplements.append({"image": row["path"], "imageSha256": row["sha256"],
                                "originalRecord": row["generationRecord"],
                                "reason": "同批逐图configSnapshot遗漏sources；本补充只记录已读批次配置来源，不改旧记录或实际返回。",
                                "sameBatchTargetFieldsMatch": same,
                                "supplementedSources": config.get("sources") if same else None,
                                "configEvidence": evidence(config_path),
                                "batchVerificationEvidence": evidence(ROOT.parents[1] / "README.md"),
                                "actualModel": rec.get("actualModel"), "actualQuality": rec.get("actualQuality"),
                                "interpretation": "官方网页地址证明配置核对依据，不证明本次工具实际型号或质量；本审计没有重新浏览官网。"})

    present = {p.relative_to(ROOT / "frames").as_posix() for p in actual_files}
    sequences = []
    for action, (count, directions, duration) in SPECS.items():
        for direction in directions:
            have = [n for n in range(1, count + 1) if f"{action}/{direction}/{n:02}.png" in present]
            sequences.append({"action": action, "direction": direction, "expected": count,
                              "presentIndices": have, "missingIndices": [n for n in range(1, count + 1) if n not in have],
                              "frameDurationMs": duration, "sequenceDurationMs": count * duration})
    failures = [r for r in requests if r["outcome"] == "confirmed_failure"]
    unknowns = [r for r in requests if r["outcome"] == "unknown_no_completion_receipt"]
    old_report = validation["technical"]["present"]
    report = {"schemaVersion": 1, "character": "00_reference_topright_boy", "auditedAt": now,
              "timezone": "America/New_York", "scope": "磁盘/来源文本审计，不是美术、动态或客户端验收。新增/替换后须重跑。",
              "summary": {"target": sum(n * len(ds) for n, ds, _ in SPECS.values()),
                          "actualCandidateExports": len(actual_files), "missingExportSlots": sum(len(s["missingIndices"]) for s in sequences),
                          "localGenerationPngs": len(generated), "selectedLocalGenerationPngs": sum(bool(x["selectedForExports"]) for x in generated),
                          "finalVisualApproved": manifest.get("finalVisualApproved", 0),
                          "dynamicArtApproved": validation["art"]["dynamic_art_approved"], "clientIntegrated": False,
                          "confirmedFailureRequests": len(failures), "requestsWithoutCompletionEvidence": len(unknowns)},
              "documentEvidence": document_evidence, "sequences": sequences,
              "frameInventory": inventory, "generationInventory": generated, "requestOutcomes": requests,
              "configSourcesSupplement": supplements, "indexIssues": issues,
              "validationSnapshot": {"validatedAt": validation.get("validated_at"), "presentAtValidation": old_report,
                                     "countMatchesCurrent": old_report == len(actual_files),
                                     "note": "数量相同不证明SHA相同或新在制稿已经验收；旧检查只对其绑定文件有效。"},
              "scaleAuditSnapshot": {"decision": scale.get("decision"), "images": scale.get("images"),
                                     "note": "问题与原始SHA绑定；新版本仅有PNG/来源不自动解除旧槽位问题。"},
              "historicalIncompleteRecords": [r["relativePath"] for r in inventory if r.get("manifestRecord", {}).get("configSnapshot") is None],
              "refreshRequiredAfterGeneration": ["实际PNG与来源证据清单", "manifest/sources与选择表", "技术检查及预览", "新旧SHA绑定的静态/动态美术结论", "STATUS及MERGE_HANDOFF快照"]}
    out = ROOT / "review/provenance-completion.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"核对时间：{now}（America/New_York）。本段由 tools/audit_provenance.py 实扫更新。", "",
             f"当前候选导出 **{len(actual_files)}/196**，缺 **{report['summary']['missingExportSlots']}** 槽；本批本角色 generation 实际原图 **{len(generated)}** 张。正式美术通过 **{report['summary']['finalVisualApproved']}**；客户端 **未接入、未运行**。",
             "", "| 动作/方向 | 实际导出帧号 | 缺失帧号 | 帧时长 / 完整段时长 |", "| --- | --- | --- | --- |"]
    for s in sequences:
        fmt = lambda ns: "、".join(f"{n:02}" for n in ns) or "无"
        lines.append(f"| {s['action']}/{s['direction']} | {fmt(s['presentIndices'])} | {fmt(s['missingIndices'])} | {s['frameDurationMs']} / {s['sequenceDurationMs']} ms |")
    lines.extend(["", "当前本批原图（逐图来源、完整路径及导出链见 [来源审计](review/provenance-completion.json)）：", "",
                  "| 文件 | SHA-256 | 已关联导出 |", "| --- | --- | --- |"])
    for row in generated:
        selected = "、".join(row["selectedForExports"]) or "未导出；待选帧/验收"
        lines.append(f"| [{row['relativePath']}]({row['relativePath']}) | `{row['sha256']}` | {selected} |")
    lines.extend(["", f"已确认失败请求 {len(failures)} 项（原始网络错误证据保留）；无完成证据请求 {len(unknowns)} 项（unknown，不等同于已确认失败）。", ""])
    for row in failures + unknowns:
        lines.append(f"- `{row['relativePath']}` — `{row['outcome']}`；SHA `{row['sha256']}`。")
    lines.extend(["", f"当前索引/源SHA问题 {len(issues)} 项。逐项文件、源PNG、生成记录与回执SHA均在 `review/provenance-completion.json`。",
                  f"旧 `current-validation.json` 的 {old_report} 张检查仅适用于其原始快照；新增原图、替换及当前动态美术结果须另行刷新。"])
    refresh_block("STATUS.md", lines)
    refresh_block("MERGE_HANDOFF.md", lines)
    print(json.dumps({"written": str(out), "summary": report["summary"], "indexIssues": issues}, ensure_ascii=False))


if __name__ == "__main__":
    main()
