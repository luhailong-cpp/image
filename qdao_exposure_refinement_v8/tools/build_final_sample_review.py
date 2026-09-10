"""Render review-only comparisons from immutable backups and actual staged files."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
import audit_inventory as audit

ROOT = audit.PACKAGE
PAGES = [
    ("scene-screen-cloud", [
        "client_ui_refresh_20260908/additional/login_background.png",
        "qdao_ui_redesign_v5/05_battle_scene_2560x1080.png",
        "qdao_ui_redesign_v5/01_login_2560x1080.png",
        "qdao_ui_redesign_v5/02_server_select_2560x1080.png",
        "qdao_ui_redesign_v5/06_battle_entry_clouds_fg_2560x1080.png",
        "qdao_ui_redesign_v5/source/06_battle_entry_clouds_fg.png",
    ]),
    ("ui-and-paper", [
        "qdao_ui_redesign_v5/components/png/main_frame.png",
        "qdao_ui_redesign_v5/components/svg/primary_button_normal.svg",
        "qdao_ui_redesign_v5/hud/hud_overlay.svg",
        "designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png",
        "designs/attribute-panels/v2-painted/unity-slices/png/window_frame.png",
    ]),
    ("white-materials-and-dark-controls", [
        "q_daoist_character_pack_4096/14_short_hair_snow_summoner_girl_transparent_4096.png",
        "q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png",
        "qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png",
        "client_ui_refresh_20260908/prepared/UI/qdao_v3/icons_weapon/034_crane_feather_fan.png",
        "client_ui_refresh_20260908/prepared/UI/qdao_v3/icons_weapon/040_alchemy_furnace_golden_pills.png",
        "qdao_ui_redesign_v5/components/svg/round_badge_taiji.svg",
    ]),
]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def image_preview(path, renderer, bounds):
    if path.suffix.lower() == ".svg":
        im, _ = renderer.render(path)
    else:
        with Image.open(path) as source:
            im = source.convert("RGBA")
    im.thumbnail(bounds, Image.Resampling.LANCZOS)
    return im


def main():
    created = datetime.now(timezone.utc).isoformat()
    process = json.loads((ROOT / "processing.json").read_text("utf-8"))
    records = {row["path"]: row for row in process["records"]}
    audit.SAMPLE_MAX = 1000
    renderer = audit.SvgRenderer()
    output = {"created_utc": created, "purpose": "Review-only actual backup versus staged outputs; source assets and processing.json are untouched", "pages": []}
    label_font, title_font = audit.font(17), audit.font(25)
    try:
        for page, (label, paths) in enumerate(PAGES, 1):
            square = page == 3
            content_height = 370 if square else 295
            row_height = content_height + 62
            width, margin, gap, header = 1460, 20, 20, 74
            half = (width-2*margin-gap)//2
            canvas = Image.new("RGB", (width, header+len(paths)*row_height), "#24272b")
            draw = ImageDraw.Draw(canvas)
            draw.text((margin, 8), f"Actual staged review {page}/3  |  {label}", font=title_font, fill="#eeeeee")
            draw.text((margin, 43), "ORIGINAL BACKUP", font=label_font, fill="#c1c8cf")
            draw.text((margin+half+gap, 43), "ACTUAL STAGED OUTPUT", font=label_font, fill="#c1c8cf")
            rows = []
            for index, path in enumerate(paths):
                record = records[path]
                before, after = ROOT/record["backup"], ROOT/record["staged"]
                original_sha, staged_sha = sha(before), sha(after)
                assert original_sha == record["original_sha256"], path + " original snapshot hash mismatch"
                assert staged_sha == record["output_sha256"], path + " staged file changed since processing record"
                y = header + index*row_height
                draw.text((margin, y), audit.fit_label(draw, f"{index+1:02d} [{record['preset']}] {path}", label_font, width-40), font=label_font, fill="#edf0f2")
                for side, source in enumerate((before, after)):
                    tile = Image.new("RGB", (half, content_height), "#808080")
                    im = image_preview(source, renderer, (half,content_height))
                    tile.paste(im, ((half-im.width)//2,(content_height-im.height)//2), im.getchannel("A"))
                    im.close()
                    canvas.paste(tile, (margin+side*(half+gap),y+31))
                    tile.close()
                rows.append({"row": index+1, "path":path, "preset":record["preset"],
                             "backup":record["backup"],"staged":record["staged"],
                             "original_sha256":original_sha,"output_sha256":staged_sha})
            filename = "final-sample-review.jpg" if page == 1 else f"final-sample-review-{page:02d}.jpg"
            target = ROOT / "review" / filename
            canvas.save(target,quality=93,subsampling=0)
            output["pages"].append({"file":target.relative_to(audit.REPO).as_posix(),"size":list(canvas.size),"category":label,"rows":rows})
            canvas.close()
        audit.write_json(ROOT / "review/final-sample-review.json",output)
        print(json.dumps({"pages":len(output["pages"]),"sample_pairs":sum(len(p["rows"]) for p in output["pages"]),"files":[p["file"] for p in output["pages"]]},ensure_ascii=False,indent=2))
    finally:
        renderer.close()


if __name__ == "__main__":
    main()
