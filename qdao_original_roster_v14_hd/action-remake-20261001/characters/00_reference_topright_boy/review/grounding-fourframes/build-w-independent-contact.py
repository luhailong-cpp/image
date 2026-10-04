"""Diagnostic contact only: the final selection is preferred; otherwise explicit W plan.

No native artwork is modified and no source is chosen by version number.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
selection = ROOT / "generation/run/W/selection-middle4-side2-20261004.json"
final = selection.exists()
if final:
    data = json.loads(selection.read_text(encoding="utf-8-sig"))
    rows = data if isinstance(data, list) else data["frames"]
else:
    selection = OUT / "n-ne-w-plan-middle4-side2-20261004.json"
    rows = json.loads(selection.read_text(encoding="utf-8-sig"))["directions"]["W"]
canvas = Image.new("RGB", (1024, 1120), "#eeeae2")
legs = Image.new("RGB", (1600, 1000), "#eeeae2")
draw, detail = ImageDraw.Draw(canvas), ImageDraw.Draw(legs)
evidence = []
for index, row in enumerate(sorted(rows, key=lambda r: r["frame"])):
    src = row.get("source", row.get("plannedOutput"))
    path = ROOT / src
    with Image.open(path) as im:
        im.load()
        assert im.mode == "RGBA" and im.size == (1254, 1254)
        export = Image.new("RGBA", (1024, 1024))
        export.alpha_composite(im.resize((901, 901), Image.Resampling.LANCZOS), (41, 118))
        tile = export.resize((240, 240), Image.Resampling.LANCZOS)
        x, y = (index % 4) * 256, (index // 4) * 280
        canvas.paste(tile, (x + 8, y), tile)
        draw.text((x + 8, y + 243), f'{row["frame"]:02d} {path.name}', fill="#183a32")
        draw.text((x + 8, y + 260), "FINAL SELECTION" if final else "PLAN ONLY", fill="#183a32")
        crop = im.crop((250, 780, 1050, 1220)).resize((400, 220), Image.Resampling.LANCZOS)
        x, y = (index % 4) * 400, (index // 4) * 250
        legs.paste(crop, (x, y + 25), crop)
        detail.text((x + 4, y + 4), f'{row["frame"]:02d} {path.name}', fill="#183a32")
    evidence.append({"frame": row["frame"], "source": src, "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest()})
canvas.save(OUT / "W-independent-contact.jpg", quality=95)
legs.save(OUT / "W-independent-lower.jpg", quality=95)
(OUT / "W-independent-contact.sources.json").write_text(json.dumps({"selection": selection.relative_to(ROOT).as_posix(), "selectionSha256": hashlib.sha256(selection.read_bytes()).hexdigest(), "finalSelection": final, "frames": evidence, "operation": "Fixed W export transform for full-body display; identical native lower-body diagnostic crop only; no artwork editing", "dynamicVerified": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f'W contact created from {"final selection" if final else "explicit plan (provisional)"}; {len(evidence)} native images')
