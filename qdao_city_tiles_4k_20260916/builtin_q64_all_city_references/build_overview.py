"""Rebuild the seven-reference contact sheet; does not edit source art.
Run: python build_overview.py
Requires local Pillow and Windows Microsoft YaHei fonts.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ORDER = [
    ("tianyong_festival", "天墉城 · 节庆"),
    ("penglai_day", "蓬莱仙岛 · 日景"),
    ("penglai_mid_autumn", "蓬莱仙岛 · 中秋"),
    ("donghai_day", "东海渔村 · 日景"),
    ("donghai_lantern", "东海渔村 · 元宵"),
    ("lanxian_day", "揽仙镇 · 日景"),
    ("lanxian_spring", "揽仙镇 · 春节"),
]
FONT_REG = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
PNG = ROOT / "overview-all-seven.png"
JPEG = ROOT / "overview-all-seven-preview.jpg"
MANIFEST = ROOT / "overview-manifest.json"
TITLE = "四座主城 · 七套Q版整图参考"
SUBTITLE = "原生1254×1254 · 内置GPT Image2.0请求最高可用画质 · 以下仅为缩小总览"
STATUS_TEXT = "七套整城布局参考，非64K/4K正式交付；4K局部样图1张；1792正式图块仍待制作/验收"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()

def recorded_path(record, names, base, issues):
    for name in names:
        value = record.get(name)
        if value:
            path = Path(value)
            return (path if path.is_absolute() else base / path), name
    issues.append("missing recorded path: " + "/".join(names))
    return None, None

def check_hash(record, field, actual, issues):
    expected = record.get(field)
    if not isinstance(expected, str) or not expected:
        issues.append("missing recorded hash: " + field)
        return None
    result = expected.lower() == actual
    if not result:
        issues.append("hash mismatch: " + field)
    return result

def audit_one(folder, title):
    base = ROOT / folder
    image = base / "map-native-layout-reference.png"
    prompt = base / "map.prompt.txt"
    record_path = base / "map.record.json"
    issues = []
    if not image.is_file():
        raise FileNotFoundError(image)
    record = {}
    if not record_path.is_file():
        issues.append("map.record.json missing")
    else:
        try:
            record = json.loads(record_path.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError) as exc:
            issues.append("record could not be read: " + str(exc))
    with Image.open(image) as im:
        im.load()
        dims, fmt = list(im.size), im.format
    image_hash = sha(image)
    output_hash_ok = check_hash(record, "outputSha256", image_hash, issues)
    prompt_exists = prompt.is_file()
    prompt_hash = sha(prompt) if prompt_exists else None
    prompt_hash_ok = check_hash(record, "promptSha256", prompt_hash, issues) if prompt_exists else None
    prompt_nonempty = bool(prompt.read_text(encoding="utf-8-sig").strip()) if prompt_exists else False
    if not prompt_exists:
        issues.append("map.prompt.txt missing")
    elif not prompt_nonempty:
        issues.append("map.prompt.txt empty")
    if "actualNativePixels" not in record:
        issues.append("missing actualNativePixels")
        native_size_ok = None
    else:
        native_size_ok = record["actualNativePixels"] == dims
        if not native_size_ok:
            issues.append("actualNativePixels does not match image")
    declared_output, output_key = recorded_path(record, ("outputPath", "outputFile"), base, issues)
    declared_prompt, prompt_key = recorded_path(record, ("promptPath", "promptFile"), base, issues)
    output_path_ok = declared_output.resolve() == image.resolve() if declared_output else None
    prompt_path_ok = declared_prompt.resolve() == prompt.resolve() if declared_prompt else None
    if output_path_ok is False:
        issues.append("recorded output path mismatch")
    if prompt_path_ok is False:
        issues.append("recorded prompt path mismatch")
    source, source_key = recorded_path(record, ("sourceOutputPath", "originalOutputPath"), base, issues)
    source_exists = source.is_file() if source else False
    source_hash = sha(source) if source_exists else None
    if source and not source_exists:
        issues.append("recorded generated source not found")
    source_record_hash_ok = check_hash(record, "sourceOutputSha256", source_hash, issues) if source_exists else None
    source_identity_ok = source_hash == image_hash if source_exists else None
    if source_identity_ok is False:
        issues.append("saved PNG differs from original generated source")
    if dims != [1254, 1254]:
        issues.append("actual dimensions differ from subtitle's 1254x1254")
    return {
        "id": folder, "title": title, "image": relative(image),
        "pixels": dims, "format": fmt, "imageSha256": image_hash,
        "prompt": relative(prompt), "promptExists": prompt_exists,
        "promptSha256": prompt_hash, "promptNonempty": prompt_nonempty,
        "record": relative(record_path), "recordExists": record_path.is_file(),
        "recordSha256": sha(record_path) if record_path.is_file() else None,
        "sourceOutputPath": source.as_posix() if source else None,
        "sourceOutputSha256": source_hash,
        "routeRecorded": record.get("route"), "roleRecorded": record.get("role"),
        "checks": {
            "recordedOutputHashMatches": output_hash_ok,
            "recordedPromptHashMatches": prompt_hash_ok,
            "recordedSourceHashMatches": source_record_hash_ok,
            "sourceBytesPreserved": source_identity_ok,
            "recordedNativeSizeMatches": native_size_ok,
            "recordedOutputPathMatches": output_path_ok,
            "recordedPromptPathMatches": prompt_path_ok,
        },
        "issues": issues,
    }

def font(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)

def fit_text(draw, text, max_width, size, bold=False):
    selected = font(size, bold)
    while draw.textbbox((0, 0), text, font=selected)[2] > max_width and size > 14:
        size -= 1
        selected = font(size, bold)
    return selected

def main():
    entries = [audit_one(folder, title) for folder, title in ORDER]
    issues = [{"id": entry["id"], "issues": entry["issues"]} for entry in entries if entry["issues"]]
    if not all(entry["pixels"] == [1254, 1254] for entry in entries):
        raise ValueError("Subtitle requires all references to be native 1254 square; dimensions differ.")
    canvas = Image.new("RGB", (2600, 1500), "#F1F4EE")
    draw = ImageDraw.Draw(canvas)
    ink, muted, border = "#183E33", "#52665E", "#CCD9CF"
    draw.text((40, 19), TITLE, font=font(50, True), fill=ink)
    draw.text((42, 87), SUBTITLE, font=font(27), fill=muted)
    draw.line((40, 133, 2560, 133), fill=border, width=2)
    cell_w, cell_h, gap_x, gap_y, grid_y = 612, 646, 24, 24, 148
    for index, entry in enumerate(entries):
        col, row = index % 4, index // 4
        x, y = 40 + col * (cell_w + gap_x), grid_y + row * (cell_h + gap_y)
        draw.rounded_rectangle((x, y, x+cell_w, y+cell_h), radius=15, fill="white", outline=border, width=2)
        draw.text((x+14, y+8), entry["title"], font=font(27, True), fill=ink)
        draw.text((x+cell_w-123, y+13), "布局参考", font=font(21), fill=muted)
        with Image.open(ROOT / entry["image"]) as original:
            thumb = original.convert("RGB").resize((588, 588), Image.Resampling.LANCZOS)
        canvas.paste(thumb, (x+12, y+46))
        entry["overviewImageRect"] = [x+12, y+46, x+600, y+634]
    x, y = 40 + 3*(cell_w+gap_x), grid_y + cell_h + gap_y
    draw.rounded_rectangle((x, y, x+cell_w, y+cell_h), radius=15, fill="#E6EFE6", outline="#B8CDBF", width=2)
    draw.text((x+30, y+28), "当前交付状态", font=font(34, True), fill=ink)
    draw.line((x+30, y+91, x+cell_w-30, y+91), fill="#B8CDBF", width=2)
    lines = [
        ("七套整城布局参考，", 142, 33, True, ink),
        ("非64K/4K正式交付；", 195, 32, True, ink),
        ("4K局部样图1张；", 288, 32, False, ink),
        ("1792正式图块仍待制作/验收", 347, 30, True, "#7D5234"),
        ("此页只用于整体方向与外观对照。", 448, 25, False, muted),
        ("高清分块、接缝与实机近景仍需逐项验收。", 491, 24, False, muted),
        ("七份提示词、来源记录与原PNG一致性已核验。" if not issues else "来源记录存在待核对项，详见清单。", 572, 22, False, muted),
    ]
    for text, offset, size, bold, color in lines:
        f = fit_text(draw, text, cell_w-60, size, bold)
        draw.text((x+30, y+offset), text, font=f, fill=color)
    canvas.save(PNG, format="PNG")
    preview = canvas.resize((1600, round(1500*1600/2600)), Image.Resampling.LANCZOS)
    preview.save(JPEG, format="JPEG", quality=50, subsampling=2, optimize=True)
    after = {entry["id"]: sha(ROOT / entry["image"]) for entry in entries}
    unchanged = all(after[entry["id"]] == entry["imageSha256"] for entry in entries)
    if not unchanged:
        raise ValueError("A source image changed while composing.")
    manifest = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "role": "mechanical_contact_sheet_of_layout_references_only",
        "title": TITLE, "subtitle": SUBTITLE, "statusText": STATUS_TEXT,
        "imageCount": 7, "grid": [4, 2], "nativeReferencePixels": [1254, 1254],
        "requestedRouteLabel": "Built-in GPT Image 2.0",
        "requestedQuality": "highest available through host; not a selectable max claim",
        "backendModelVerified": False, "newImageGenerationCalls": 0,
        "local4kSamples": 1, "plannedFormalTilesStillPendingProductionOrAcceptance": 1792,
        "formalDeliveryCompleted": False, "sourceImagesUnmodified": unchanged,
        "allProvenanceChecksPassed": not issues, "issues": issues,
        "script": {"file": Path(__file__).name, "sha256": sha(Path(__file__))},
        "outputs": [
            {"file": PNG.name, "pixels": [2600, 1500], "sha256": sha(PNG)},
            {"file": JPEG.name, "pixels": list(preview.size), "jpegQuality": 50, "sha256": sha(JPEG)},
        ],
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"png": str(PNG), "preview": str(JPEG), "previewBytes": JPEG.stat().st_size,
                      "manifest": str(MANIFEST), "allChecksPassed": not issues, "issues": issues},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
