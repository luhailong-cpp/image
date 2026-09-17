#!/usr/bin/env python3
"""Native left/right full-span stair repair, hard minimum-error seams only."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
QA = ROOT / "qa"
REPAIR = ROOT / "repairs" / "south_stairs_fullspan"
BASE = OUT / "tianyong_plaza_4k_candidate.png"
DEST = OUT / "tianyong_plaza_4k_candidate_v3b.png"
REPORT = OUT / "south_stairs_v3b_assembly.json"
HELPER = ROOT.parents[1] / "tianyong_festival_hd_20260910" / "seam_helpers.py"
BAND = 96
TOP_BAND = 20
OVERLAP = 230
SOURCE_UNION = [909, 2842, 3187, 4096]
UNION = [909, 3358, 3187, 4096]
SOURCE_CROP = [0, 516, 2278, 1254]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rgb(path):
    with Image.open(path) as image:
        image.load()
        if image.format != "PNG":
            raise ValueError(f"Not a PNG: {path}")
        if image.mode == "RGBA" and image.getextrema()[3] != (255,255):
            raise ValueError(f"Unexpected transparent ground image: {path}")
        return np.asarray(image.convert("RGB")).copy()


def save(array, path):
    Image.fromarray(array).save(path, format="PNG", optimize=True)


def source_size(record):
    for key in ("actualNativePixels", "nativeSize"):
        if key in record:
            return record[key]
    for wk,hk in (("nativeWidth","nativeHeight"),("actualWidth","actualHeight"),("width","height")):
        if wk in record and hk in record:
            return [record[wk],record[hk]]
    raise ValueError("No actual native dimensions in record")


def prepare_inputs():
    original = data(OUT / "assembly.json")
    if sha(BASE) != original["output"]["sha256"]:
        raise ValueError("Must compose onto unchanged first candidate, never v2")
    plan = data(REPAIR / "plan.json")
    expected_patches = {"left":[909,2842,2163,4096], "right":[1933,2842,3187,4096]}
    if plan["union"] != SOURCE_UNION or plan["patches"] != expected_patches or plan["overlap"] != OVERLAP:
        raise ValueError("Unexpected full-span coordinate plan")
    pixels, sources = {}, []
    for side in ("left","right"):
        native = REPAIR / (side+".png")
        record_file = REPAIR / (side+".record.json")
        prompt = REPAIR / (side+".prompt.txt")
        guide = REPAIR / (side+".layout-only.png")
        for path in (native,record_file,prompt,guide):
            if not path.is_file():
                raise ValueError(f"Full-span generation incomplete: {path}")
        record = data(record_file)
        if source_size(record) != [1254,1254] or record.get("backendModelVerified") is not False:
            raise ValueError(f"Unexpected actual native dimensions/model assertion: {side}")
        expected_guide_hash = record.get("guideSha256",record.get("referenceSha256"))
        for path,value in ((native,record["outputSha256"]),(prompt,record["promptSha256"]),(guide,expected_guide_hash)):
            if not isinstance(value,str) or sha(path) != value.lower():
                raise ValueError(f"Source hash mismatch: {path}")
        raw = Path(record["sourceOutputPath"])
        if not raw.is_file() or sha(raw) != sha(native):
            raise ValueError(f"Native file must equal generator output: {side}")
        if record.get("resizedAfterGeneration") is True or record.get("finalArtUpscaled") is True:
            raise ValueError("Resized generated art is not allowed")
        image = rgb(native)
        if image.shape != (1254,1254,3):
            raise ValueError(f"Native image shape mismatch: {side}")
        if not prompt.read_text(encoding="utf-8-sig").strip():
            raise ValueError(f"Empty prompt: {side}")
        pixels[side] = image
        sources.append({"side":side,"nativeFile":str(native),"nativeSha256":sha(native),"nativeSize":[1254,1254],
                        "recordFile":str(record_file),"recordSha256":sha(record_file),
                        "promptFile":str(prompt),"promptSha256":sha(prompt),"guideFile":str(guide),
                        "guideSha256":sha(guide),"sourceOutputPath":str(raw),"sourceOutputSha256":sha(raw),
                        "route":record.get("route"),"backendModelVerified":False,
                        "crop":expected_patches[side],"generatedBytesPreserved":True})
    return pixels,sources


def seam_fn():
    spec = importlib.util.spec_from_file_location("city_v3b_minimum_seam",HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._minimum_vertical_seam


def stats(line):
    return {"min":int(line.min()),"max":int(line.max()),"mean":float(line.mean())}


def check():
    _,sources = prepare_inputs()
    report = data(REPORT)
    if report["nativeSources"] != sources:
        raise ValueError("Current repair provenance differs from assembly")
    for path,expected in ((BASE,report["base"]["sha256"]),(DEST,report["output"]["sha256"]),
                          (Path(__file__),report["script"]["sha256"]),(HELPER,report["seamHelper"]["sha256"])):
        if sha(path) != expected:
            raise ValueError(f"Artifact hash mismatch: {path}")
    if rgb(DEST).shape != (4096,4096,3):
        raise ValueError("Final output must remain 4096 square")
    for item in report["qa"]:
        if sha(Path(item["file"])) != item["sha256"]:
            raise ValueError("QA artifact hash mismatch")
    return {"passed":True,"status":report["status"],"output":str(DEST),"qaFiles":len(report["qa"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(check(),ensure_ascii=False,indent=2))
        return
    pixels,sources = prepare_inputs()
    if DEST.exists() or REPORT.exists():
        raise ValueError("v3b already exists; use --check rather than overwriting its audit record")
    minimum = seam_fn()
    left,right = pixels["left"],pixels["right"]
    seam = minimum(left[:,-OVERLAP:],right[:,:OVERLAP])
    inner_mask = np.arange(OVERLAP)[None,:] >= seam[:,None]
    overlap = np.where(inner_mask[...,None],right[:,:OVERLAP],left[:,-OVERLAP:])
    repair = np.concatenate((left[:,:-OVERLAP],overlap,right[:,OVERLAP:]),axis=1)
    if repair.shape != (1254,2278,3):
        raise AssertionError("Native joined union shape is wrong")
    if not np.array_equal(repair, rgb(QA / "v3_fullspan_native_join_2278x1254.png")):
        raise AssertionError("Joined source differs from the reviewed full-span v3 native join")
    repair = repair[516:1254].copy()
    if repair.shape != (738,2278,3):
        raise AssertionError("Cropped native repair must remain 2278x738 without resampling")
    base = rgb(BASE)
    x0,y0,x1,y1 = UNION
    old = base[y0:y1,x0:x1]
    height,width = old.shape[:2]
    edge_left = minimum(old[:,:BAND],repair[:,:BAND])
    edge_right = minimum(old[:,-BAND:],repair[:,-BAND:]) + width - BAND
    edge_top = minimum(np.transpose(old[:TOP_BAND],(1,0,2)),np.transpose(repair[:TOP_BAND],(1,0,2)))
    edge_bottom = minimum(np.transpose(old[-BAND:],(1,0,2)),np.transpose(repair[-BAND:],(1,0,2))) + height - BAND
    xx=np.arange(width)[None,:]
    yy=np.arange(height)[:,None]
    mask=(xx>=edge_left[:,None])&(xx<edge_right[:,None])&(yy>=edge_top[None,:])&(yy<edge_bottom[None,:])
    combined=np.where(mask[...,None],repair,old)
    result=base.copy()
    result[y0:y1,x0:x1]=combined
    outside=np.ones((4096,4096),dtype=bool)
    outside[y0:y1,x0:x1]=False
    if not np.array_equal(result[outside],base[outside]):
        raise AssertionError("Pixels outside repair union changed")
    if not np.all(np.all(combined==old,axis=2)|np.all(combined==repair,axis=2)):
        raise AssertionError("Composition contains samples not present in sources")
    save(result,DEST)
    qa=[]
    joined=QA/"v3b_cropped_native_join_2278x738.png"
    save(repair,joined)
    qa.append({"file":str(joined),"kind":"native_join_no_resize","size":[2278,738],"sourceCrop":SOURCE_CROP,"sha256":sha(joined)})
    overview_path=QA/"v3b_overview_1024.png"
    Image.fromarray(result).resize((1024,1024),Image.Resampling.LANCZOS).save(overview_path,optimize=True)
    qa.append({"file":str(overview_path),"kind":"downsampled_preview_only","size":[1024,1024],"sha256":sha(overview_path)})
    crops={
        "v3b_south_stairs_left_seam_100pct":[459,3196,1359,4096],
        "v3b_south_stairs_right_seam_100pct":[2737,3196,3637,4096],
        "v3b_south_stairs_internal_seam_100pct":[1598,3196,2498,4096],
        "v3b_south_stairs_top_seam_100pct":[1598,2810,2498,3710],
        "v3b_south_stairs_fullwidth_100pct":[650,2842,3450,4096],
    }
    for name,rect in crops.items():
        a,b,c,d=rect
        path=QA/(name+".png")
        save(result[b:d,a:c],path)
        qa.append({"file":str(path),"kind":"native_pixel_crop","crop":rect,"size":[c-a,d-b],"resized":False,"sha256":sha(path)})
    full_preview=QA/"v3b_south_stairs_fullwidth_overview_1400.png"
    Image.fromarray(result[2842:4096,650:3450]).resize((1400,627),Image.Resampling.LANCZOS).save(full_preview,optimize=True)
    qa.append({"file":str(full_preview),"kind":"downsampled_preview_only","sourceCrop":[650,2842,3450,4096],
               "size":[1400,627],"sha256":sha(full_preview)})
    report={
        "schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),
        "status":"candidate_pending_visual_QA_not_published","published":False,
        "base":{"file":str(BASE),"sha256":sha(BASE),"version":"original_v1"},
        "script":{"file":str(Path(__file__)),"sha256":sha(Path(__file__))},
        "seamHelper":{"file":str(HELPER),"sha256":sha(HELPER),"function":"_minimum_vertical_seam"},
        "plan":{"file":str(REPAIR/"plan.json"),"sha256":sha(REPAIR/"plan.json"),"sourceUnion":SOURCE_UNION,"actualCompositeRect":UNION,"joinedSourceCrop":SOURCE_CROP},
        "nativeSources":sources,
        "composition":{"method":"native left/right minimum-error hard seam, then four hard border seams into original candidate",
                       "internalOverlapPixels":OVERLAP,"joinedNativeSize":[2278,1254],"joinedSourceCrop":SOURCE_CROP,"croppedNativeSize":[2278,738],"actualCompositeRect":UNION,"borderSearchBandPixels":BAND,"topBorderSearchBandPixels":TOP_BAND,
                       "featherPixels":0,"sourceResampling":False,"sourceStretching":False,"blur":False,
                       "colorMatching":False,"sharpening":False,"guidePixelsCompositedIntoFinal":False,
                       "outsideUnionPixelsPreserved":True,"allPixelsAboveY3358MatchOriginal":bool(np.array_equal(result[:3358],base[:3358])),"outputPixelsAreUnmodifiedSourceSamples":True,
                       "selectedRepairPixelCount":int(mask.sum()),
                       "seams":{"internal_overlap_x":stats(seam),"left_x":stats(edge_left),"right_x":stats(edge_right),
                                "top_y":stats(edge_top),"bottom_y":stats(edge_bottom)}},
        "finalArtUpscaled":False,
        "output":{"file":str(DEST),"width":4096,"height":4096,"sha256":sha(DEST)},
        "qa":qa,
        "visualQa":{"status":"pending","concern":"Restricted crop preserves original pixels above y3358; top seam search is only y3358..3378, before the regenerated upper stair edge. Compare directly with v3a before acceptance."}
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(check(),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
