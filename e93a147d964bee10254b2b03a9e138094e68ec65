"""Mechanically recut 31 attribute sprites from the approved v10 painted artwork.

This script writes only the isolated v10 staging tree and its provenance file.
It does not generate art, grade artwork, or touch the client/production sprites.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from art_support import PACK, REPO, fit_art, load_art, nine_slice, save, stretch_divider

RELATIVE = Path("designs/attribute-panels/v2-painted/unity-slices")
OUT = PACK / "staged" / RELATIVE
CONTRACT = PACK / "contracts/attributes.json"
RESAMPLE = Image.Resampling.LANCZOS

# The original Unity border order remains untouched in each output manifest.
# The helper takes left, top, right, bottom and preserves the new art's real caps.
SKINS = {
    "window_frame": "frame",
    "button_primary": "jade",
    "button_secondary": "ivory",
    "button_scheme": "ivory",
    "tab_horizontal": "jade",
    "section_header": "section_header",
    "tab_vertical_normal": "tab_vertical_normal",
    "tab_vertical_selected": "tab_vertical_selected",
    "step_plate": "step_normal",
    "slider_track": "slider_track",
    "slider_fill": "slider_fill",
    "stat_field": "stat_field",
    "pet_card_normal": "card_normal",
    "pet_card_selected": "card_selected",
    "portrait_frame": "portrait_frame",
}
FITTED = {
    "title_plate": "title",
    "dropdown_arrow": "dropdown_arrow",
    "close_button": "close_button",
    "close_tassel": "tassel",
    "slider_thumb": "slider_thumb",
}
TITLE_SOURCES = {
    "title_character": "designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png",
    "title_pet": "designs/attribute-panels/v2-painted/02-pet-ui.png",
}


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def image_info(im):
    return {
        "size": list(im.size),
        "mode": im.mode,
        "alphaRange": list(im.getchannel("A").getextrema()),
        "pixelSha256": hashlib.sha256(im.tobytes()).hexdigest(),
    }


def native_glyph(im, kind):
    """Only fixed functional glyphs are drawn natively; all skins are painted art."""
    w, h = im.size
    supersample = 4
    layer = Image.new("RGBA", (w * supersample, h * supersample))
    draw = ImageDraw.Draw(layer)
    cx, cy = w * supersample / 2, h * supersample / 2
    span = min(w, h) * supersample * 0.18
    stroke = max(3, round(min(w, h) * supersample * 0.07))
    ink = (249, 235, 194, 255) if kind == "notice" else (113, 79, 34, 255)
    shine = (250, 234, 187, 220)
    if kind in ("minus", "plus"):
        def bars(color, dy):
            draw.rounded_rectangle((cx-span, cy-stroke/2+dy, cx+span, cy+stroke/2+dy), radius=stroke/2, fill=color)
            if kind == "plus":
                draw.rounded_rectangle((cx-stroke/2, cy-span+dy, cx+stroke/2, cy+span+dy), radius=stroke/2, fill=color)
        bars(shine, supersample)
        bars(ink, 0)
    elif kind == "close":
        for xa, ya, xb, yb in ((cx-span, cy-span, cx+span, cy+span), (cx-span, cy+span, cx+span, cy-span)):
            draw.line((xa, ya+supersample, xb, yb+supersample), fill=shine, width=stroke)
            draw.line((xa, ya, xb, yb), fill=ink, width=stroke)
            for x, y in ((xa, ya), (xb, yb)):
                draw.ellipse((x-stroke/2, y-stroke/2, x+stroke/2, y+stroke/2), fill=ink)
    elif kind == "notice":
        draw.rounded_rectangle((cx-stroke/2, cy-span*1.25, cx+stroke/2, cy+span*0.25), radius=stroke/2, fill=ink)
        radius = stroke * 0.57
        draw.ellipse((cx-radius, cy+span*0.8-radius, cx+radius, cy+span*0.8+radius), fill=ink)
    else:
        raise ValueError(kind)
    out = im.copy()
    out.alpha_composite(layer.resize((w, h), RESAMPLE))
    return out


def source_paint(key):
    """Embed the reviewed source crop and cap provenance used by this sprite."""
    source = load_art(key)
    index = json.loads((PACK / "artwork/index.json").read_text(encoding="utf-8-sig"))
    indexed = index["assets"][key]
    x1, y1, x2, y2 = indexed["source_box_xyxy"]
    sheet_path = PACK / indexed["source"]
    return {"artKey": key, "cleanArtSize": list(source.size),
            "cleanArtPixelSha256": hashlib.sha256(source.tobytes()).hexdigest(),
            "source": sheet_path.relative_to(REPO).as_posix(),
            "sourceSha256": indexed["source_sha256"],
            "sourceRectNativeTopLeft": [x1, y1, x2-x1, y2-y1],
            "sourceArtworkEntry": deepcopy(indexed),
            "cropProvenance": "qdao_ui_style_recut_v10/artwork/index.json"}


def title_ink(entry):
    """Preserve the latest clean, separately approved fixed calligraphy layer.

    The original TitleInk source contract is retained for traceability. Re-running
    its luminance rule on the graded screenshot reveals a faint background stroke
    above the lettering, so that lower-quality extraction is not published.
    """
    relative = RELATIVE / "png" / (entry["name"] + ".png")
    source_path = REPO / relative
    ink = Image.open(source_path).convert("RGBA")
    assert ink.size == (entry["width"], entry["height"])
    screenshot_path = REPO / TITLE_SOURCES[entry["name"]]
    return ink, {
        "source": relative.as_posix(),
        "sourceSha256": hash_file(source_path),
        "sourceNativeSize": list(ink.size),
        "sourceRectNativeTopLeft": [0, 0, ink.width, ink.height],
        "originalCalligraphyScreenshot": TITLE_SOURCES[entry["name"]],
        "originalCalligraphyScreenshotSha256": hash_file(screenshot_path),
        "originalCalligraphyScreenshotCrop": entry["sourceRectNativeTopLeft"],
        "processing": "Preserve the latest approved separate static calligraphy layer at native pixels. No resampling, recoloring, artificial pixel difference, or dynamic values.",
        "preservedArtwork": True,
        "preservationReason": "Approved static Chinese calligraphy is a separate text layer, not an old UI skin. Its current clean alpha is retained; rerunning screenshot luminance extraction would introduce a faint non-letter stroke.",
    }


def portrait(entry):
    relative = Path("designs/attribute-panels/assets") / (entry["name"].removeprefix("portrait_") + ".png")
    source_path = REPO / relative
    source = Image.open(source_path).convert("RGBA")
    x, y, w, h = entry["sourceRectNativeTopLeft"]
    # Keep the approved square head framing from the existing contract.
    box = (x, y, x + w, y + h)
    out = source.resize((entry["width"], entry["height"]), RESAMPLE, box=box)
    return out, {
        "source": relative.as_posix(),
        "sourceSha256": hash_file(source_path),
        "sourceNativeSize": list(source.size),
        "sourceRectNativeTopLeft": [x, y, w, h],
        "processing": "Square head recrop from latest approved transparent pet artwork using original crop bounds; Lanczos resample to 160x160. No painted alteration, stretched anatomy, or baked level.",
        "preservedArtwork": True,
        "preservationReason": "Approved pet identity and exposure corrections are preserved. Portrait content is separate from the newly painted UI skin; resampling does not claim a newly generated pet.",
    }


def build(entry):
    name, w, h = entry["name"], entry["width"], entry["height"]
    if name in TITLE_SOURCES:
        return title_ink(entry)
    if name.startswith("portrait_") and name != "portrait_frame":
        return portrait(entry)
    if name == "paper_tile":
        source = load_art("panel")
        sw, sh = source.size
        # Texture-only center avoids the panel's ornament and border regions.
        box = (round(sw*.36), round(sh*.38), round(sw*.64), round(sh*.62))
        im = source.crop(box).resize((w, h), RESAMPLE).convert("RGBA")
        meta = source_paint("panel")
        meta.update({"cleanArtCropXYXY": list(box), "processing": "Text-free paper texture cropped from the clean center of the new painted panel, resampled to the contracted tile size."})
    elif name == "divider":
        im = stretch_divider(w, h, vertical=True)
        meta = source_paint("divider")
        meta.update({"processing": "Rotate new horizontal painted divider 90 degrees; preserve both fixed end ornaments and the round crescent center, stretching only the unornamented rails to the original vertical canvas.",
                     "rotationDegrees": 90, "centerOrnamentPreserved": True})
    elif name in ("step_minus", "step_plus"):
        im = native_glyph(fit_art("step_normal", w, h), name.removeprefix("step_"))
        meta = source_paint("step_normal")
        meta["processing"] = "New painted blank step button with an antialiased native fixed " + name.removeprefix("step_") + " glyph; dynamic data remains separate."
    elif name == "title_plate":
        im = nine_slice("title", w, h, (92, 36, 92, 38))
        meta = source_paint("title")
        meta["processing"] = "Assemble the new title plate from fixed painted ends, separate tassels, fixed center stamps and straight jade middle. Original whole-title sprite remains non-sliced at runtime."
        meta["assemblyBordersLeftTopRightBottom"] = [92, 36, 92, 38]
    elif name == "close_button":
        im = native_glyph(fit_art("close_button", w, h), "close")
        meta = source_paint("close_button")
        meta["processing"] = "New painted blank circular close-button skin with an antialiased native fixed close cross glyph."
    elif name == "notice_icon":
        im = native_glyph(fit_art("knob", w, h), "notice")
        meta = source_paint("knob")
        meta["processing"] = "New painted blank circular knob skin with a native fixed notice exclamation glyph."
    elif name in SKINS:
        key = SKINS[name]
        l, b, r, t = entry["borderLeftBottomRightTop"]
        im = nine_slice(key, w, h, (l, t, r, b))
        meta = source_paint(key)
        meta["processing"] = "Nine-part mechanical assembly from new text-free painted art, preserving original Unity destination borders; no legacy skin pixels."
        meta["destinationBordersLeftTopRightBottom"] = [l, t, r, b]
    elif name in FITTED:
        key = FITTED[name]
        im = fit_art(key, w, h)
        meta = source_paint(key)
        meta["processing"] = "Proportional fit of complete newly painted element onto original transparent canvas; fixed ornament geometry preserved."
    else:
        raise ValueError(f"Unmapped attribute: {name}")
    im = im.convert("RGBA")
    meta["preservedArtwork"] = False
    return im, meta


def qa_font(size):
    for path in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def checker(w, h):
    im = Image.new("RGBA", (w, h), (226, 224, 209, 255))
    draw = ImageDraw.Draw(im)
    for y in range(0, h, 12):
        for x in range(0, w, 12):
            if (x//12 + y//12) % 2:
                draw.rectangle((x, y, x+11, y+11), fill=(206, 212, 202, 255))
    return im


def contact(entries, images):
    cw, ch, cols = 400, 210, 4
    out = Image.new("RGBA", (cols*cw, ((len(entries)+cols-1)//cols)*ch+58), (36, 60, 51, 255))
    draw = ImageDraw.Draw(out)
    draw.text((16, 14), "v10 PAINTED ATTRIBUTE SPRITES | 31 CONTRACTS | PIL MONTAGE", font=qa_font(21), fill="#f2e2be")
    for n, e in enumerate(entries):
        x, y = (n%cols)*cw, 58+(n//cols)*ch
        draw.text((x+12, y+6), f'{e["name"]}  {e["width"]}x{e["height"]}', font=qa_font(16), fill="#f2e2be")
        board = checker(cw-20, ch-40)
        im = images[e["name"]].copy()
        im.thumbnail((cw-34, ch-52), RESAMPLE)
        board.alpha_composite(im, ((board.width-im.width)//2, (board.height-im.height)//2))
        out.alpha_composite(board, (x+10, y+32))
    save(out, OUT / "sprite-overview.png")


def stretch_sprite(im, size, border):
    """QA: rebuild the delivered sprite with its public Unity border contract."""
    l, b, r, t = border
    w, h = size
    sx, sy = (0, l, im.width-r, im.width), (0, t, im.height-b, im.height)
    dx, dy = (0, l, w-r, w), (0, t, h-b, h)
    out = Image.new("RGBA", size)
    for iy in range(3):
        for ix in range(3):
            tw, th = dx[ix+1]-dx[ix], dy[iy+1]-dy[iy]
            if tw > 0 and th > 0:
                crop = im.crop((sx[ix], sy[iy], sx[ix+1], sy[iy+1]))
                out.alpha_composite(crop.resize((tw, th), RESAMPLE), (dx[ix],dy[iy]))
    return out


def stretch_review(entries, images):
    names = ["button_primary", "button_secondary", "button_scheme", "tab_horizontal", "stat_field", "pet_card_normal", "pet_card_selected"]
    by_name = {e["name"]:e for e in entries}
    out = Image.new("RGBA", (1460, 140+len(names)*195), (36, 60, 51, 255))
    draw = ImageDraw.Draw(out)
    draw.text((20, 18), "NINE-SLICE QA | delivered pixels + original public borders | not a Unity screenshot", font=qa_font(21), fill="#f2e2be")
    widths = (250, 420, 600)
    x_positions = (30, 340, 820)
    for i, name in enumerate(names):
        e = by_name[name]
        y = 90+i*195
        draw.text((20,y), name, font=qa_font(18), fill="#f2e2be")
        for width, x in zip(widths, x_positions):
            im = stretch_sprite(images[name], (width, e["height"]), e["borderLeftBottomRightTop"])
            out.alpha_composite(im, (x,y+35))
    save(out, OUT / "nine-slice-review.png")


def additional_reviews(entries, images):
    """Review all remaining slices and native glyphs without touching artwork."""
    by_name = {entry["name"]: entry for entry in entries}
    out = Image.new("RGBA", (1760, 1570), (36, 60, 51, 255))
    draw = ImageDraw.Draw(out)
    draw.text((20, 16), "FRAME + FIELDS | delivered PNGs, original Unity borders | Pillow QA", font=qa_font(23), fill="#f2e2be")
    frame_entry = by_name["window_frame"]
    for size, xy in (((780, 430), (25, 90)), ((900, 430), (835, 90))):
        draw.text((xy[0], xy[1]-28), f"window_frame {size[0]}x{size[1]}", font=qa_font(18), fill="#f2e2be")
        out.alpha_composite(stretch_sprite(images["window_frame"], size, frame_entry["borderLeftBottomRightTop"]), xy)
    rows = [
        ("tab_vertical_normal", (92,127), (150,210)),
        ("tab_vertical_selected", (97,127), (160,210)),
        ("section_header", (260,57), (500,57)),
        ("slider_track", (250,23), (550,23)),
        ("slider_fill", (100,23), (500,23)),
        ("step_plate", (66,65), (110,85)),
        ("portrait_frame", (160,160), (240,240)),
        ("paper_tile", (250,57), (500,80)),
    ]
    for index, (name, size1, size2) in enumerate(rows):
        x, y = (index%2)*880+25, (index//2)*240+555
        draw.text((x,y), name, font=qa_font(18), fill="#f2e2be")
        for size, offset in ((size1,0), (size2,max(size1[0]+35,230))):
            sprite = stretch_sprite(images[name], size, by_name[name]["borderLeftBottomRightTop"])
            board = checker(sprite.width,sprite.height)
            board.alpha_composite(sprite)
            out.alpha_composite(board, (x+offset,y+30))
    save(out, OUT/"frame-fields-review.png")
    # Native symbol rendering is intentionally separate from AI skin generation.
    names = ["step_minus", "step_plus", "close_button", "notice_icon", "dropdown_arrow", "slider_thumb", "close_tassel"]
    glyphs = Image.new("RGBA", (1460, 850), (36,60,51,255))
    draw = ImageDraw.Draw(glyphs)
    draw.text((20,16), "FIXED SYMBOLS + APPROVED TITLE INK | native-size and 3x QA", font=qa_font(23), fill="#f2e2be")
    for index,name in enumerate(names):
        x,y=(index%4)*365+15,(index//4)*280+65
        draw.text((x,y),name,font=qa_font(17),fill="#f2e2be")
        sprite=images[name]
        for scale,dx in ((1,0),(3,100)):
            test=sprite.resize((sprite.width*scale,sprite.height*scale),Image.Resampling.NEAREST)
            board=checker(test.width,test.height)
            board.alpha_composite(test)
            glyphs.alpha_composite(board,(x+dx,y+28))
    for index,name in enumerate(("title_character","title_pet")):
        x=20+index*720
        plate=images["title_plate"].copy()
        title=images[name]
        plate.alpha_composite(title,((plate.width-title.width)//2,(plate.height-title.height)//2))
        glyphs.alpha_composite(plate,(x,690))
        draw.text((x,660),name+" on new title plate",font=qa_font(18),fill="#f2e2be")
    save(glyphs,OUT/"fixed-glyph-title-review.png")

def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert len(contract["sprites"]) == 31
    entries, images, provenance, validation = [], {}, [], []
    for original in contract["sprites"]:
        im, meta = build(original)
        assert im.size == (original["width"],original["height"])
        destination = OUT / "png" / (original["name"] + ".png")
        save(im, destination)
        images[original["name"]] = im
        current = Image.open(REPO / RELATIVE / "png" / destination.name).convert("RGBA")
        unchanged = current.tobytes() == im.tobytes()
        if unchanged and not meta.get("preservedArtwork",False):
            raise AssertionError("Old skin unchanged: " + original["name"])
        item = deepcopy(original)
        item["legacySourceContract"] = {k: original[k] for k in ("source", "sourceRectTopLeft", "sourceRectNativeTopLeft", "processing")}
        item.update(meta)
        item["sourceRectTopLeft"] = meta.get("sourceRectNativeTopLeft")
        if "sourceRectNativeTopLeft" not in meta:
            item["sourceRectNativeTopLeft"] = None
        item["recutVersion"] = "v10"
        item["sha256"] = hash_file(destination)
        entries.append(item)
        validation.append({"name": original["name"], **image_info(im), "sha256": item["sha256"], "samePixelsAsPreviousSprite": unchanged,
                           "borderLeftBottomRightTop": original["borderLeftBottomRightTop"], "resourcePath": original["resourcePath"]})
        provenance.append({"path": (RELATIVE / "png" / destination.name).as_posix(), "family": "attributes", "name": original["name"],
                           **meta, "samePixelsAsPreviousSprite": unchanged, "outputSha256": item["sha256"],
                           "size": list(im.size), "borderLeftBottomRightTop": original["borderLeftBottomRightTop"], "resourcePath": original["resourcePath"]})
    manifest = {"tool": "Pillow mechanical recrop/resample of built-in GPT Image 2 artwork", "recutVersion": "v10",
                "styleReference": "docs/references/ui-style-20260910.png", "unityImportExecutedThisBuild": False,
                "referenceCoordinates": "New painted art uses the central artKey crop map; legacy reference rectangles are retained separately.",
                "sprites": entries}
    report = {"status": "mechanical_checks_passed_visual_review_required", "sprites":31,
              "pngSizesPassed":True, "bordersPassed":True,"resourcePathsPassed":True,
              "unityImportExecuted":False,"files":validation}
    mapping = {"schemaVersion":1,"family":"attributes","assetCount":31,"tool":"Pillow mechanical processing; no API requests",
               "styleReference":"docs/references/ui-style-20260910.png", "outputs":provenance,
               "preservedArtworkPolicy":"Static calligraphy and approved pet identity are recut without artistic alteration; old UI skins must change.",
               "limits":"No current client import or Unity rendering is claimed. The sprite contact and stretch montage are Pillow QA only."}
    OUT.mkdir(parents=True, exist_ok=True)
    for path, data in ((OUT/"manifest.json",manifest), (OUT/"file-validation.json",report), (PACK/"source-map.attributes.json",mapping)):
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    contact(entries,images)
    stretch_review(entries,images)
    additional_reviews(entries,images)
    print(json.dumps({"attributes":len(entries),"newPaintedSkinSprites":sum(not p["preservedArtwork"] for p in provenance),
                      "preservedApprovedContent":sum(p["preservedArtwork"] for p in provenance),
                      "unchangedOutputPixels":[p["name"] for p in provenance if p["samePixelsAsPreviousSprite"]]},ensure_ascii=False))


if __name__ == "__main__":
    main()
