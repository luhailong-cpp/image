"""Copy generated files byte-for-byte and record read-only PNG evidence."""
from pathlib import Path
from datetime import datetime
import hashlib
import importlib.util
import json
import re
import shutil

character = Path(__file__).resolve().parent.parent
root = character.parent.parent
prefix = character.relative_to(root).as_posix() + "/"
spec = importlib.util.spec_from_file_location("combat_audit", root / "tools/audit_combat.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
baseline = json.loads((character / "provenance/receipts/cast-E-10-v2.json").read_text(encoding="utf-8"))
references = [
    {"path": str(character / "staging/cast-E-10-v2.png"), "role": "first primary reference: approved cast E release keypose; exact identity, scale and original 1254 canvas placement"},
    {"path": str(root.parent.parent / "qdao_original_roster_v13/candidate/00_reference_topright_boy/idle/E.png"), "role": "secondary identity and strict E side profile; not scale reference"},
    {"path": str(root.parent.parent / "designs/jubaozhai-ui/02-characters.png"), "role": "approved primary hand-painted style and materials; no UI or scenery copied"},
]
for reference in references:
    reference["sha256"] = hashlib.sha256(Path(reference["path"]).read_bytes()).hexdigest()
for tool_path in sorted((character / "provenance/receipts").glob("cast-E-??-v*-tool.json")):
    meta = json.loads(tool_path.read_text(encoding="utf-8"))
    if meta.get("status") != "generated":
        continue
    stem = tool_path.name.removesuffix("-tool.json")
    receipt_path = tool_path.with_name(stem + ".json")
    if receipt_path.exists():
        continue
    source = Path(meta["sourcePath"])
    destination = character / "staging" / (stem + ".png")
    if destination.exists() and destination.read_bytes() != source.read_bytes():
        raise RuntimeError("Refusing to overwrite a different image: " + str(destination))
    if not destination.exists():
        shutil.copyfile(source, destination)
    data = audit.inspect_png(destination)
    timestamps = re.findall(rb"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", source.read_bytes())
    now = datetime.now().astimezone().isoformat()
    receipt = {
        "file": prefix + "staging/" + destination.name,
        "sha256": data["sha256"], "generatedAt": timestamps[0].decode("ascii") if timestamps else now,
        "generatedAtEvidence": "Embedded PNG provenance timestamp, signature not independently validated" if timestamps else "Observed download time; tool omitted generation time",
        "observedAt": now, "width": data["width"], "height": data["height"], "format": "PNG RGBA",
        "tool": "image_gen.imagegen", "route": "builtin", "configSnapshot": baseline["configSnapshot"],
        "officialRecheckDate": "2026-09-29", "officialRecheckEvidence": "Parent verified official sources for this batch; unchanged batch target preserved",
        "submittedParameters": {"model": None, "quality": None, "transparent_background": True, "referenced_image_paths": [item["path"].replace("\\", "/") for item in references]},
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理，工具未披露实际型号或质量，model/quality参数未开放；未把配置或提示词目标当作实际返回值。",
        "evidence": {"toolResultRecord": prefix + "provenance/receipts/" + tool_path.name, "toolOutputHint": meta["output_hint"], "sourcePath": str(source), "resultFields": meta["resultFields"], "copyOperation": "Byte-for-byte shutil.copyfile; no image editing, resampling, mirroring or alpha changes"},
        "prompt": prefix + "prompts/" + stem + ".txt", "references": references,
        "requestedOutput": {"width": 1254, "height": 1254, "format": "transparent PNG", "nativeSizeMatchesRequest": data["width"] == data["height"] == 1254, "runtimeExportPerformed": False},
        "review": {"status": "candidate_pending_sequence_review", "runtimeReady": False, "note": "Independently AI-generated single pose. Parent sequence review and final 1024 export are pending."},
        "imageValidation": data,
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": destination.name, "bbox": data["visible_bbox"], "size": [data["width"], data["height"]], "sha256": data["sha256"]}))
