"""Append-only sidecar audit of this session's generated originals; never edits art/receipts.

Run with the bundled Python (Pillow required). Existing content-addressed records are
reused byte-for-byte; each run adds a separate index. All times are evidence-qualified.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
SESSION = OUT.parent
REPO = SESSION.parents[2]
SNAPSHOT = SESSION / "history/image-generation.before-20260921.json"
CACHE: dict[Path, bytes] = {}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw(path: Path) -> bytes:
    path = path.resolve()
    if path not in CACHE:
        before = path.stat()
        data = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError(f"Concurrent write; retry next run: {path}")
        CACHE[path] = data
    return CACHE[path]


def read(path: Path) -> dict:
    return json.loads(raw(path).decode("utf-8-sig"))


def pathof(value: str) -> Path:
    normalized = value.replace("\\", "/")
    for old in ("E:/work/image/", "E:/work/wuxingqitan/image/"):
        if normalized.lower().startswith(old.lower()):
            return (REPO / normalized[len(old):]).resolve()
    return Path(value).resolve()


def ref(path: Path, expected: str | None = None) -> dict:
    result = {"file": str(path.resolve()), "exists": path.is_file()}
    if result["exists"]:
        result["sha256"] = digest(raw(path))
    if expected:
        result["recordedSha256"] = expected
        result["matchesRecordedSha256"] = result.get("sha256") == expected
    return result


def freeze(path: Path) -> dict:
    item = ref(path)
    if item["exists"]:
        archive = OUT / "evidence" / (item["sha256"] + path.suffix.lower())
        append(archive, raw(path))
        item["immutableCopy"] = str(archive)
    return item


def append(path: Path, data: bytes) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to overwrite existing evidence: {path}")
        return False
    with path.open("xb") as output:
        output.write(data)
    return True


def encoded(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def receipt_native(receipt: dict) -> Path | None:
    response = receipt.get("response", receipt)
    match = re.search(r" as (.+?\.png) by default\.", response.get("output_hint", ""), re.S)
    return pathof(match.group(1)) if match else None


def metadata_observations(path: Path) -> dict:
    data, offset, observations = raw(path), 8, []
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        name = data[offset + 4:offset + 8].decode("ascii", errors="replace")
        if name in ("caBX", "tEXt", "iTXt"):
            payload = data[offset + 8:offset + 8 + length]
            for match in re.finditer(rb"[\x20-\x7e]{6,}", payload):
                text = match.group().decode("ascii")
                if re.search(r"gpt.image|ChatGPT|softwareAgent|OpenAI Media Service|\d{4}-\d{2}-\d{2}T", text, re.I):
                    observations.append({"chunk": name, "byteOffset": offset + 8 + match.start(), "text": text})
        offset += length + 12
    return {"method": "readable strings from metadata chunks only", "observations": observations,
            "c2paSignatureVerified": False, "establishesActualModelOrGenerationTime": False}


def discover() -> list[dict]:
    items = []
    for record_path in sorted(SESSION.glob("tools/sessions/*/*/native/*.record.json")):
        rec = read(record_path)
        items.append({"kind": "native_detail", "recordPath": record_path, "record": rec,
                      "file": pathof(rec["outputFile"]), "expected": rec.get("outputSha256"),
                      "original": pathof(rec["sourceOutputPath"]),
                      "receiptPath": pathof(rec["toolOutputReceipt"]["file"]),
                      "promptPath": pathof(rec["promptFile"]),
                      "promptSha": rec.get("promptSha256"), "refs": rec.get("submittedImages", [])})
    native_records=sorted(list(SESSION.glob("next_tile_*/native/*.record.json"))+list(SESSION.glob("next_tile_*/native/*.generation.json")))
    seen_native=set()
    for record_path in native_records:
        rec = read(record_path)
        native=pathof(rec.get("nativeFile",rec.get("file")))
        if native in seen_native:
            continue
        seen_native.add(native)
        stem = record_path.name.removesuffix(".record.json").removesuffix(".generation.json").removesuffix('.png')
        evidence=rec.get('evidence',{})
        receipt_value=evidence.get('toolResponse',evidence.get('file'))
        items.append({"kind": "native_detail", "recordPath": record_path, "record": rec,
                      "file": native, "expected": rec.get("nativeSha256",rec.get('sha256')),
                      "original": pathof(rec["toolOutputPath"]),
                      "receiptPath": pathof(receipt_value) if receipt_value else record_path.with_name(stem + ".tool-response.json"),
                      "separateRequestPath": pathof(evidence['request']) if evidence.get('request') else None,
                      "promptPath": pathof(rec["promptFile"]),
                      "promptSha": rec.get("promptSha256"), "refs": rec.get("submittedImages", rec.get('references',[]))})
    for record_path in sorted(SESSION.glob("next_tile_*/references/*.record.json")):
        rec = read(record_path)
        if not rec.get("sourceOutputPath"):
            continue
        stem = record_path.name.removesuffix(".record.json")
        items.append({"kind": "generated_style_reference_not_delivery", "recordPath": record_path, "record": rec,
                      "file": pathof(rec["outputPath"]), "expected": rec.get("outputSha256"),
                      "original": pathof(rec["sourceOutputPath"]),
                      "receiptPath": record_path.parent.parent / "native" / (stem + ".tool-response.json"),
                      "promptPath": pathof(rec["promptFile"]),
                      "promptSha": rec.get("promptSha256"), "refs": rec.get("submittedImages", [])})
    for base in [SESSION / "tools/repairs/versions", *SESSION.glob("next_tile_*/repairs/versions")]:
        for record_path in sorted(base.glob("*/repair.json")):
            rec = read(record_path)
            generation_path = (pathof(rec["generationRecord"]["file"])
                               if rec.get("generationRecord", {}).get("file") else None)
            generation = read(generation_path) if generation_path else {}
            generation_prompt = generation.get("prompt", {})
            items.append({"kind": "native_ai_repair", "recordPath": record_path, "record": rec,
                          "file": record_path.parent / "repair-native-1254.png",
                          "expected": rec["originalNativeOutput"].get("sha256"),
                          "original": pathof(rec["originalNativeOutput"]["file"]),
                          "receiptPath": record_path.parent / "request-receipt.json",
                          "promptPath": pathof(generation_prompt["file"]) if generation_prompt.get("file") else record_path.parent / "actual-prompt.txt",
                          "promptSha": generation_prompt.get("sha256", rec.get("actualPromptSha256")),
                          "refs": generation.get("references", rec.get("actualReferences", [])),
                          "generationPath": generation_path, "generation": generation})
    # Include completed tool calls awaiting a later mechanical registration. Only
    # paths explicitly disclosed by session receipts are read, never cache scans.
    known = {str(item["original"]).lower() for item in items}
    receipts = [*SESSION.glob("requests/*.request.json"),
                *SESSION.glob("next_tile_*/repairs/prepared/*/request-receipt.json"),
                *SESSION.glob("next_tile_*/repairs/external-prepared/*/request-receipt.json"),
                *SESSION.glob("tools/repairs/prepared/*/request-receipt.json")]
    for receipt_path in sorted(receipts):
        receipt = read(receipt_path)
        original = receipt_native(receipt)
        if original is None or str(original).lower() in known:
            continue
        request = receipt.get("request", {})
        if not request.get("prompt"):
            continue
        prompt_path = OUT / "prompts" / (digest(request["prompt"].encode("utf-8")) + ".txt")
        append(prompt_path, request["prompt"].encode("utf-8"))
        items.append({"kind": "generated_unregistered_candidate", "recordPath": None, "record": {},
                      "file": original, "expected": None, "original": original,
                      "receiptPath": receipt_path, "promptPath": prompt_path, "promptSha": None,
                      "refs": [{"path": value} for value in request.get("referenced_image_paths", [])]})
        known.add(str(original).lower())
    return items


def build(item: dict, snapshot: dict, snapshot_ref: dict) -> dict:
    rec, issues = item["record"], []
    image_ref = ref(item["file"], item["expected"])
    if not image_ref["exists"]:
        raise ValueError(f"Native file missing: {item['file']}")
    with Image.open(item["file"]) as image:
        image.load()
        width, height, image_format = image.width, image.height, image.format
    original_ref = ref(item["original"], item["expected"] or image_ref["sha256"])
    prompt_ref = freeze(item["promptPath"])
    prompt_ref["recordedSha256"] = item["promptSha"]
    prompt_ref["matchesRecordedSha256"] = (prompt_ref.get("sha256") == item["promptSha"]) if item["promptSha"] else None
    prompt = raw(item["promptPath"]).decode("utf-8-sig")
    transport = rec.get("promptTransport", "Exact request.prompt preserved in actual-prompt.txt")
    submitted_prompt = prompt.strip() if "leading and trailing" in transport else (prompt.rstrip("\r\n") if "trailing newline" in transport else prompt)
    receipt_ref = freeze(item["receiptPath"])
    receipt = read(item["receiptPath"]) if receipt_ref["exists"] else {}
    request = receipt.get("request")
    separate_request_ref=None
    if not request and item.get('separateRequestPath'):
        separate_request_ref=freeze(item['separateRequestPath'])
        request_record=read(item['separateRequestPath'])
        request=request_record.get('request',request_record)
    if request:
        if submitted_prompt != request.get("prompt"):
            issues.append("Retained prompt content differs from raw request.prompt")
        submitted_prompt = request.get("prompt", submitted_prompt)
        request_level = "retained_separate_request_and_response_json" if separate_request_ref else "retained_request_and_response_json"
    else:
        request_level = "existing_toolCall_record_plus_prompt_file; full_request_JSON_not_retained"
        issues.append("Full submitted request JSON not retained; prompt transport and references rely on existing generation record")
    receipt_output = receipt_native(receipt)
    if receipt_output and receipt_output != item["original"]:
        issues.append("Receipt output path differs from registered original path")
    if not receipt_ref["exists"]:
        issues.append("Tool receipt not found")
    references = []
    declared = {str(pathof(x.get("path", x.get("file")))).lower(): x for x in item["refs"]}
    reference_paths = request.get("referenced_image_paths", []) if request else rec.get("toolCall", {}).get("referenced_image_paths", [])
    if not reference_paths:
        reference_paths = [x.get("path", x.get("file")) for x in item["refs"]]
    for number, value in enumerate(reference_paths, 1):
        p = pathof(value)
        registered = declared.get(str(p).lower(), {})
        entry = ref(p, registered.get("sha256"))
        entry["submittedPath"] = value
        entry["inputNumberOneBased"] = number
        entry["shaEvidence"] = "verified_against_existing_record" if registered.get("sha256") else "observed_at_audit; historical_input_sha_not_recorded"
        entry["purpose"] = registered.get("role") or ("edit target / exact geometry context" if number == rec.get("selectedTargetImageOneBased", 1) else "additional style or continuity reference")
        entry["purposeBasis"] = "existing generation record reference role" if registered.get("role") else "existing prompt and input order; retained prompt is authoritative"
        references.append(entry)
        if not entry["exists"] or entry.get("matchesRecordedSha256") is False:
            issues.append(f"Reference unavailable or differs from recorded SHA: {value}")
        if not registered.get("sha256"):
            issues.append(f"No generation-time reference SHA in existing record: {value}")
    for checked, label in ((image_ref, "native"), (original_ref, "original tool output"), (prompt_ref, "prompt")):
        if not checked["exists"] or checked.get("matchesRecordedSha256") is False:
            issues.append(f"Missing or SHA-mismatched {label}")
    source_evidence = freeze(item["recordPath"]) if item["recordPath"] else None
    # createdAtUtc is set by the local save/assembly scripts, not by the generator.
    saved = rec.get("createdAtUtc")
    edit_before = None
    if rec.get("sourceCandidate"):
        source = rec["sourceCandidate"]
        edit_before = {"image": ref(pathof(source["file"]), source.get("sha256")),
                       "record": freeze(pathof(rec["sourceRecord"]["file"])) if rec.get("sourceRecord") else None,
                       "canvasBoxLTRB": rec.get("canvasBoxLTRB", rec.get("worldBoxLTRB")),
                       "operation": "AI-generated native repair context; later bounded mechanical assembly is recorded separately"}
    target_record = {key: rec.get(key) for key in ("requestedModel", "requestedQuality") if key in rec}
    result = {
        "schemaVersion": 1, "recordKind": "append_only_historical_generation_supplement",
        "file": image_ref["file"], "sha256": image_ref["sha256"], "width": width, "height": height,
        "format": image_format, "nativeDimensions": [width, height], "role": item["kind"],
        "generatedAt": None, "generatedAtStatus": "unknown",
        "generatedAtUnverifiedReason": "Tool receipt has no verified generation timestamp. Local registration/assembly time and unsigned C2PA strings are not substituted for generation time.",
        "recordSavedAt": saved, "recordSavedAtMeaning": "Existing record createdAtUtc: local source registration or mechanical assembly record save time, not image generation time",
        "recordSavedAtEvidence": {"file": str(item["recordPath"]), "field": "createdAtUtc"} if item["recordPath"] else None,
        "tool": "image_gen.imagegen", "route": "builtin_host_managed",
        "toolResultIdentifier": {"value": item["original"].stem, "meaning": "output filename stem from receipt; not asserted to be a tool call ID"},
        "configSnapshot": {key: snapshot.get(key) for key in ("model", "quality", "builtin_product", "verified_on", "sources")},
        "configSnapshotEvidence": snapshot_ref,
        "configSnapshotMeaning": "Pre-generation confirmed batch target from retained session history, as confirmed by session owner; not the mutable current config, not proof of actual selectors or backend",
        "existingRecordTarget": target_record,
        "userExplicitOverride": "Session request allows GPT Image 2.5 or GPT Image 2.0 route; no explicit model/quality selector was available",
        "submittedParameters": {"model": None, "quality": None},
        "submittedParametersReason": "Host imagegen schema exposes prompt/reference inputs but no model or quality selectors; target text is not a submitted selector",
        "actualModel": None, "actualQuality": None, "backendModelVerified": False,
        "unverifiedReason": "Host managed; tool receipt does not disclose model/version/quality and no signature-verified model metadata is available",
        "prompt": prompt_ref, "promptTransport": transport,
        "submittedPromptSha256Utf8": digest(submitted_prompt.encode("utf-8")),
        "references": references, "editBefore": edit_before,
        "evidence": {"existingRecord": source_evidence, "toolReceipt": receipt_ref,
                     "requestEvidenceLevel": request_level, "requestField": "request" if request else None,
                     "responseField": "response" if "response" in receipt else "root",
                     "originalToolOutput": original_ref, "preservedNative": image_ref,
                     "unsignedPngMetadataObservations": metadata_observations(item["file"])},
        "missingOrLimitedEvidence": issues,
        "artAcceptanceClaimed": False, "nativeSourceIsNotFormalDeliveryTile": True,
    }
    if separate_request_ref:
        result['evidence']['separateRequest']=separate_request_ref
    if rec.get('configSnapshot'):
        result['configSnapshot']={key:rec['configSnapshot'].get(key) for key in ('model','quality','builtin_product','verified_on','sources')}
        result['configSnapshotEvidence']={**source_evidence,'field':'configSnapshot'}
        result['configSnapshotMeaning']='Target snapshot explicitly recorded for this image; not a current-config backfill or evidence of actual model/quality selectors'
    # External repairs may have a separate per-image generation record, while
    # their mechanical repair record intentionally has no files/createdAtUtc.
    generation = item.get("generation", {})
    generation_path = item.get("generationPath")
    if generation_path:
        generation_ref = freeze(generation_path)
        generation_ref["recordedSha256"] = rec["generationRecord"].get("sha256")
        generation_ref["matchesRecordedSha256"] = generation_ref.get("sha256") == generation_ref["recordedSha256"]
        result["evidence"]["existingPerImageGenerationRecord"] = generation_ref
        if not generation_ref["matchesRecordedSha256"]:
            issues.append("Separate per-image generation record differs from repair.json recorded SHA")
        if generation.get("sha256") != image_ref["sha256"]:
            issues.append("Separate generation record does not match native output SHA")
        if [generation.get("width"), generation.get("height")] != [width, height]:
            issues.append("Separate generation record does not match actual native dimensions")
        if generation.get("configSnapshot"):
            result["configSnapshot"] = {key: generation["configSnapshot"].get(key)
                                        for key in ("model", "quality", "builtin_product", "verified_on", "sources")}
            result["configSnapshotEvidence"] = {**generation_ref, "field": "configSnapshot"}
            result["configSnapshotMeaning"] = "Target snapshot explicitly preserved by this image's generation record from its preparation; not a current-config backfill or proof of actual selectors/backend"
        result["evidence"]["existingGenerationTimestamp"] = {
            "field": "generatedAt", "value": generation.get("generatedAt"),
            "adoptedAsServerGenerationTime": False,
            "reason": "The external repair writer may copy the host receipt completion time into generatedAt; no exact server generation timestamp is disclosed"}
    completed = receipt.get("completedAtUtc",receipt.get('observedCompletionAt',rec.get('observedCompletionAt')))
    if completed is not None:
        result["observedCompletionAt"] = completed
        result["observedCompletionAtMeaning"] = "Host-side tool-result receipt completion observation; not exact server image generation time"
        result["observedCompletionAtEvidence"] = {**(receipt_ref if (receipt.get('completedAtUtc') or receipt.get('observedCompletionAt')) else source_evidence), "field": "completedAtUtc" if receipt.get('completedAtUtc') else 'observedCompletionAt'}
    return result


def main() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    snapshot = read(SNAPSHOT)
    snapshot_ref = freeze(SNAPSHOT)
    policy_refs = [freeze(REPO / name) for name in ("AGENTS.md", "docs/IMAGE_MODEL_POLICY.md", "designs/README.md")]
    entries, errors, added = [], [], 0
    items = discover()
    for item in items:
        try:
            record = build(item, snapshot, snapshot_ref)
            data = encoded(record)
            record_path = OUT / "records" / (record["sha256"] + "." + digest(data)[:16] + ".generation.json")
            added += append(record_path, data)
            entries.append({"file": record["file"], "sha256": record["sha256"], "role": record["role"],
                            "generationRecord": str(record_path), "generationRecordSha256": digest(data),
                            "actualModel": None, "actualQuality": None, "generatedAt": None,
                            "recordSavedAt": record["recordSavedAt"], "limitations": record["missingOrLimitedEvidence"]})
        except (OSError, ValueError, KeyError) as error:
            errors.append({"file": str(item["file"]), "error": str(error)})
    unchanged = []
    for path, data in CACHE.items():
        if OUT in path.parents:
            continue
        if not path.is_file() or digest(path.read_bytes()) != digest(data):
            unchanged.append(str(path))
    index = {"schemaVersion": 1, "auditedAtUtc": datetime.now(timezone.utc).isoformat(),
             "scope": str(SESSION), "nativeImages": len(entries), "newSupplementRecords": added,
             "countsByRole": dict(Counter(e["role"] for e in entries)), "entries": entries, "errors": errors,
             "requirementsEvidence": policy_refs, "scriptSha256": digest(Path(__file__).read_bytes()),
             "existingFilesModifiedByThisTool": False, "concurrentInputChangesDetected": unchanged,
             "generationTimeUnknownCount": len(entries), "actualModelQualityUnverifiedCount": len(entries),
             "noAcceptanceOrStyleApprovalInferred": True,
             "rerunPolicy": "Content-addressed supplements/evidence remain immutable; subsequent runs add timestamped indexes and new evidence versions only"}
    index_path = OUT / ("index-" + timestamp + ".json")
    append(index_path, encoded(index))
    lines = ["# 本次会话原生图来源补充索引", "", f"审计时间：{index['auditedAtUtc']}", "",
             f"覆盖 {len(entries)} 张原生输出，新增补充记录 {added} 份。JSON 索引：[{index_path.name}]({index_path.name})。", "",
             "所有实际型号、质量、提交型号／质量均为 null；配置快照只表示当批目标。生成时刻未知，已有 createdAtUtc 仅表示登记或组装记录保存时间。未验签 PNG 字符串不作为型号或时间证明。", "",
             "| 原生图片 | 用途 | 逐图记录 | 保存时间（非生成时间） |", "|---|---|---|---|"]
    for entry in entries:
        label = Path(entry["file"]).relative_to(SESSION).as_posix() if SESSION in Path(entry["file"]).parents else entry["file"]
        rp = Path(entry["generationRecord"]).relative_to(OUT).as_posix()
        lines.append(f"| {label} | {entry['role']} | [{Path(rp).name}]({rp}) | {entry['recordSavedAt'] or 'unknown'} |")
    lines.extend(["", "完整请求 JSON 未保存的旧条目，在逐图 missingOrLimitedEvidence 中列明；使用既有 toolCall、提示词文件和输入 SHA 作为有限证据，未伪造请求。", "",
                  f"读取失败：{len(errors)}；审计中检测输入并发变动：{len(unchanged)}。", ""])
    append(index_path.with_suffix(".md"), "\n".join(lines).encode("utf-8"))
    print(json.dumps({"index": str(index_path), "nativeImages": len(entries), "newSupplementRecords": added,
                      "countsByRole": index["countsByRole"], "errors": errors, "concurrentInputChanges": unchanged}, ensure_ascii=False))


if __name__ == "__main__":
    main()
