"""Read-only checks of expected static exports and their evidence chains."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    manifest = read(ROOT / "manifest.json")
    errors, pending, checked, source_records = [], [], [], {}
    for pet in manifest["pets"]:
        expected = {"idle_E", "idle_W", "fullbody_1024", "portrait_512"}
        missing = sorted(expected - set(pet.get("outputs", {})))
        if missing:
            pending.append({"slug": pet["slug"], "missingOutputs": missing})
        for key, item in pet.get("outputs", {}).items():
            path = ROOT / item["file"]
            try:
                meta = read(ROOT / item["record"])
                actual_sha = digest(path)
                if actual_sha != meta["sha256"] or actual_sha != item["sha256"]:
                    raise ValueError("Export hash mismatch")
                with Image.open(path) as im:
                    im.load()
                    expected_size = (512, 512) if key == "portrait_512" else (1024, 1024)
                    if im.mode != "RGBA" or im.size != expected_size:
                        raise ValueError("Unexpected image mode or dimensions")
                    alpha = im.getchannel("A")
                    if alpha.getextrema()[0] != 0 or alpha.getbbox() is None:
                        raise ValueError("Missing true transparency or empty image")
                    if key.startswith("idle_"):
                        x0, y0, x1, y1 = alpha.getbbox()
                        if min(x0, y0) <= 0 or x1 >= im.width or y1 >= im.height:
                            raise ValueError("Runtime alpha touches the frame edge")
                        if meta["runtimePivotBottomOrigin"] != [0.5, 0.08]:
                            raise ValueError("Unexpected foot pivot")
                        if meta["sharedScale"] != pet["sharedScale"]:
                            raise ValueError("E/W shared-scale contract differs")
                if meta.get("upscaled") is True or meta.get("scale", 1) > 1 or meta.get("sharedScale", 1) > 1:
                    raise ValueError("Upsampling detected")
                for source in meta["derivedFrom"]:
                    source_path = ROOT / source["file"]
                    generation_path = ROOT / source["generationRecord"]
                    generation = read(generation_path)
                    if digest(source_path) != source["sha256"] or source["sha256"] != generation["sha256"]:
                        raise ValueError("Source generation chain hash mismatch")
                    if min(generation["width"], generation["height"]) < 1024:
                        raise ValueError("Native source below minimum resolution")
                    if not isinstance(generation.get("generatedAt"), str):
                        raise ValueError("Generation timestamp is unavailable or malformed")
                    archive = ROOT / generation["immutableNativeArchive"]
                    if digest(archive) != generation["sha256"]:
                        raise ValueError("Preserved native archive differs from its generation record")
                    if not generation.get("prompt") or not generation.get("references"):
                        raise ValueError("Generation prompt or reference evidence missing")
                    if not generation.get("toolSource"):
                        raise ValueError("Tool result-file source missing")
                    source_records[source["file"]] = {"file": source["file"], "sha256": source["sha256"], "nativeSize": [generation["width"], generation["height"]], "actualModel": generation["actualModel"], "actualQuality": generation["actualQuality"], "generationRecord": source["generationRecord"]}
                checked.append({"file": item["file"], "sha256": actual_sha, "checks": "passed"})
            except Exception as error:
                errors.append({"file": item["file"], "error": str(error)})
    for filename in ("previews/E-roster.png", "previews/EW-roster.png"):
        path = ROOT / filename
        if not path.exists():
            continue
        meta = read(Path(str(path) + ".derived.json"))
        if digest(path) != meta["sha256"]:
            errors.append({"file": filename, "error": "Overview hash mismatch"})
        for source in meta["derivedFrom"]:
            if digest(ROOT / source["file"]) != source["sha256"]:
                errors.append({"file": filename, "error": "Overview has stale source artwork"})
    if args.require_complete and pending:
        errors.append({"file": "manifest.json", "error": "Incomplete expected static asset set"})
    previous = read(ROOT / "records/technical-validation.json") if (ROOT / "records/technical-validation.json").exists() else {}
    report = {"schemaVersion": 1, "status": "passed" if not errors else "failed", "allExpectedStaticExportsPresent": not pending, "expectedPetCount": 14, "checkedOutputCount": len(checked), "checkedSourceCount": len(source_records), "outputs": checked, "sources": list(source_records.values()), "pending": pending, "errors": errors, "visualApproval": False, "clientIntegrated": False, "animation": False, "scope": "PNG dimensions, alpha, clipping, no-upscale, paired shared scale, hashes, generation and derived evidence; does not grant visual or engine acceptance", "deterministicSnowFoxRebuild": previous.get("deterministicSnowFoxRebuild")}
    target = ROOT / "records/technical-validation.json"
    raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if not target.exists() or target.read_bytes() != raw:
        target.write_bytes(raw)
    print(json.dumps({k: v for k, v in report.items() if k not in ("outputs", "sources")}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
