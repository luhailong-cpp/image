"""Prepare the fifth festival conversion from the latest day leaf repair.

Run only after compose_west.py has written its complete base pair. This script
does not call image generation or alter candidate pixels; it creates a native
tone crop, a request and an exact geometry/mask integration plan for the caller.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
DAY = ROOT.parent / "donghai_day"
WORK = ROOT / "r08_c11/west-repaired/leaf-conversion"
PAIR = ROOT / "r08_c11/west-repaired/output/pair-r08_c10-c11.png"
BASE_MANIFEST = PAIR.parent / "west-integration-manifest.json"
DAY_MANIFEST = DAY / "tiles/west-leaf-repair-manifest.json"
EXPECTED_DAY_MANIFEST = "3166e405717842fcf881e62a13d74ee70590fe76ceac79d01af9f18782de2798"
SOURCE_BOX = [3469, 1543, 4723, 2797]
PAIR_RECT = [3968, 1952, 4224, 2352]
NATIVE_CROP = [499, 409, 755, 809]
GLOBAL_NATIVE = [40333, 30215, 1254, 1254]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def info(path):
    return {"file": str(Path(path).resolve()), "sha256": sha(path)}


def check(entry):
    require(Path(entry["file"]).is_file() and sha(entry["file"]) == entry["sha256"], f"Source changed: {entry['file']}")


def write_json(path, data):
    require(path.resolve().is_relative_to(WORK.resolve()), "Write outside leaf conversion branch")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def main():
    require(sha(DAY_MANIFEST) == EXPECTED_DAY_MANIFEST, "Day leaf repair contract changed; review before preparing")
    leaf, baseline = read(DAY_MANIFEST), read(BASE_MANIFEST)
    require(leaf["pairRectXYXY"] == PAIR_RECT and leaf["sourceCropXYXY"] == NATIVE_CROP, "Wrong leaf crop")
    require(leaf["registration"] is False and leaf["colorCorrection"] is False, "Unexpected day geometry field")
    pairs = [item for item in baseline["outputs"] if item["id"] == "pair-r08_c10-c11"]
    require(len(pairs) == 1 and Path(pairs[0]["file"]).resolve() == PAIR.resolve(), "Wrong base pair")
    check(pairs[0])
    for key in ("generatedEdit", "generationRecord", "combinedMask", "combinedMaskNpz"):
        check(leaf[key])
    day_record = read(leaf["generationRecord"]["file"])
    require(day_record["sha256"] == leaf["generatedEdit"]["sha256"] and
            [day_record["width"], day_record["height"]] == [1254, 1254], "Wrong day native source")
    source = read(leaf["inputRecord"]["file"])
    require(source["sourceBoxInPair"] == SOURCE_BOX, "Wrong native coordinate mapping")
    with np.load(leaf["combinedMaskNpz"]["file"], allow_pickle=False) as archive:
        require(set(archive.files) == {"alpha", "pair_rect"}, "Unknown day leaf fields")
        require(archive["pair_rect"].tolist() == PAIR_RECT, "Wrong mask coordinates")
        alpha = archive["alpha"].copy()
    with Image.open(leaf["combinedMask"]["file"]) as image:
        require(np.array_equal(np.asarray(image), alpha) and image.size == (256, 400), "Wrong day mask")
    guide = WORK / "guides/festival-same-native-window.png"
    guide.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(PAIR) as image:
        image.load()
        require(image.size == (8192, 4096), "Base pair size mismatch")
        image.crop(SOURCE_BOX).save(guide)
    write_json(Path(str(guide)+".generation.json"), {**info(guide), "pixels": [1254, 1254],
        "operation": "native unresized crop used only as festival color/lighting context",
        "pairRectXYXY": SOURCE_BOX, "globalRectXYWH": GLOBAL_NATIVE,
        "derivedFrom": [pairs[0]], "resized": False, "generatedByAI": False,
        "doesNotContainLatestDayLeafGeometry": True})
    style = Path(r"D:/work/image/designs/gameplay-ui/04-guild.png")
    tone = ROOT / "r08_c11/guides/neighbor-tone-native.png"
    refs = [
        {**leaf["generatedEdit"], "role": "PRIMARY exact latest day leaf-repaired native geometry; edit this appearance only"},
        {**info(guide), "role": "Same-coordinate festival color/light context only; do not copy its old leaf contours"},
        {**info(style), "role": "PRIMARY confirmed rounded Daoist Q painting/material/finish style; ignore UI"},
        {**info(tone), "role": "Festival rendering and palette sample only"},
    ]
    prompt = """Use case: lighting-weather. Asset: 五行奇谈 fishing-village Lantern Festival map, latest WEST-LEAF-01 exact native window, global XYWH [40333,30215,1254,1254].
Image 1 is the PRIMARY edit target and exact latest repaired DAY geometry. Image 2 is the same-coordinate FESTIVAL appearance context, but its old leaf contours near the former common edge are superseded: use its color and lighting only. Image 3 is the confirmed Daoist Q rendering style, and image 4 is a festival palette/material sample.
Convert only image 1 daylight appearance to matching clean bright Lantern Festival appearance. Precisely retain every leaf outline, leaf cluster boundary, twig, highlight/shadow SILHOUETTE, occlusion and object placement from image 1. Particularly preserve its newly repaired continuous foliage around x611–651,y517–737; never copy the old chopped leaf edge from image 2. Preserve identical camera, scale, crop and all four boundaries. Do not simplify, add, remove, reposition or redraw structure.
Match image 2 colors and local brightness gently: balanced greens, warm cream light and restrained peach/honey reflection, soft lavender shadows. Keep rounded full hand-painted Daoist Q finish and native crisp detail as image 3. No broad orange wash, added lighting blobs, new shadows, lanterns, props, particles, glow outlines, text, UI, logos, grid, border, blur, sharpening or noise.
One opaque 1254x1254 image, exact native crop. Highest available completion. Configuration target gpt-image-2.5-sunburst/max is a target only; no exposed model/quality selector is implied by this prose."""
    prompt_path = WORK / "prompt.txt"
    prompt_path.write_text(prompt+"\n", encoding="utf-8")
    request = {"prompt": prompt, "referenced_image_paths": [r["file"] for r in refs], "transparent_background": False}
    write_json(WORK / "request.json", request)
    plan = {
        "status": "prepared-for-parent-built-in-generation; not generated or integrated",
        "dayRepairManifest": info(DAY_MANIFEST), "baseManifest": info(BASE_MANIFEST), "basePair": pairs[0],
        "references": refs, "prompt": info(prompt_path), "globalNativeRectXYWH": GLOBAL_NATIVE,
        "nativePairRectXYXY": SOURCE_BOX, "outputNativeCropXYXY": NATIVE_CROP,
        "replacementPairRectXYXY": PAIR_RECT, "replacementGlobalRectXYXY": leaf["globalRectXYXY"],
        "exactDayMask": leaf["combinedMask"], "exactDayMaskNpz": leaf["combinedMaskNpz"],
        "integration": "Use generated 1254 native crop [499,409,755,809]; blend once into the festival base pair [3968,1952,4224,2352] using exact day alpha, uint32 ((base*(255-alpha)+native*alpha+127)//255). No mask optimization, flow, scaling or geometry changes.",
        "requiredInvariants": ["all base pixels outside replacement rect exactly identical", "source PNG bytes unchanged", "same day mask bytes", "one unresized native crop"],
        "requiredQA": ["full 4096 common edge at native pixel scale", "all four replacement attachment boundaries", "native replacement and surrounding context"],
        "expectedNativeDestination": str(WORK / "native/leaf.png"),
        "actualModel": None, "actualQuality": None, "submittedModel": None, "submittedQuality": None,
        "formalAccepted": False, "dayFormalAccepted": leaf["formalAccepted"],
        "dayLatestLeafVisualReview": "No later visual review verified by this preparation script",
        "script": info(__file__),
    }
    write_json(WORK / "integration-plan.json", plan)
    print(json.dumps({"request": str(WORK/"request.json"), "plan": str(WORK/"integration-plan.json"),
                      "nativeDestination": plan["expectedNativeDestination"], "sourceGeometry": refs[0]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
