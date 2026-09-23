"""Bounded seam-only candidate experiment; old neighbors and v4 remain read-only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
PRODUCTION = TOOLS.parents[1]
OLD = PRODUCTION / "tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5"
BASE = TOOLS / "sessions/tianyong_festival/r09_c09/output_resume_20260921"
V4 = TOOLS / "repairs/versions/r09_c09_repair_v4"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def load(path, box=None):
    with Image.open(path) as image:
        image.load()
        return np.asarray((image.crop(box) if box else image).convert("RGB")).copy()


def smooth(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def main():
    out = HERE / "output"
    qa = HERE / "qa"
    if out.exists() or qa.exists():
        raise ValueError("Preserve existing v5 attempt; output or qa already exists")
    source_paths = [V4 / "r09_c09.png", V4 / "repair.json", BASE / "extended-context.png", BASE / "assembly.json",
                    OLD / "quad-extended-context.png", OLD / "row10-extended-context.png",
                    OLD.parent / "assembly_v5.json"]
    old_tile_paths = [OLD / f"r{row:02d}_c{col:02d}.png" for row, cols in ((9, (7, 8)), (10, (7, 8, 9, 10))) for col in cols]
    before_hashes = {str(p): sha(p) for p in source_paths + old_tile_paths}
    original = load(BASE / "extended-context.png")
    assert original.shape == (4326, 4326, 3)
    v4 = load(V4 / "r09_c09.png")
    assert v4.shape == (4096, 4096, 3)
    original_core = original[115:4211, 115:4211]
    assert np.array_equal(original_core[:115], v4[:115]) and np.array_equal(original_core[-115:], v4[-115:])
    assert np.array_equal(original_core[:, :115], v4[:, :115]) and np.array_equal(original_core[:, -115:], v4[:, -115:])
    original[115:4211, 115:4211] = v4
    context = original.copy()
    left = load(OLD / "quad-extended-context.png", (8192, 0, 8422, 4326))
    bottom = load(OLD / "row10-extended-context.png", (8192, 0, 12518, 230))
    assert np.array_equal(left[-230:], bottom[:, :230])
    context[:, :230] = left
    context[4096:] = bottom
    x = np.arange(4326, dtype=np.float32)[None, :]
    y = np.arange(4326, dtype=np.float32)[:, None]
    mask = np.rint(255 * smooth((x - 115) / 115) * smooth((4211 - y) / 115)).astype(np.uint8)
    assert np.all(mask[:, :116] == 0) and np.all(mask[4210:] == 0)
    sys.path.insert(0, str(TOOLS / "vendor"))
    sys.dont_write_bytecode = True
    helper_path = PRODUCTION / "tools/mechanical_join.py"
    spec = importlib.util.spec_from_file_location("fixed_neighbor_join", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    result, flow, correction, registration = helper.registered_join(
        context, original, mask, edges=("left", "bottom"), max_shift=8.0,
        flow_inner=300.0, flow_full=120.0, tone_inner=330.0, tone_full=150.0, match_tone=True)
    assert np.max(np.abs(flow)) <= 8.0
    assert np.array_equal(result[mask == 0], context[mask == 0])
    final = result[115:4211, 115:4211].copy()
    assert np.array_equal(final[:3881, 215:], v4[:3881, 215:])
    assert np.array_equal(final[:, 0], left[115:4211, 115])
    assert np.array_equal(final[-1], bottom[114, 115:4211])
    changed = np.any(final != v4, axis=2)
    allowed = np.zeros((4096, 4096), dtype=bool)
    allowed[:, :215] = True
    allowed[3881:] = True
    assert not np.any(changed & ~allowed)
    out.mkdir()
    qa.mkdir()
    Image.fromarray(final).save(out / "r09_c09.png")
    Image.fromarray(result).save(out / "extended-context.png")
    Image.fromarray(mask).save(out / "mask.png")
    np.savez_compressed(out / "flow.npz", flow=flow)
    np.savez_compressed(out / "correction.npz", correction=correction)
    preview = Image.fromarray(final)
    preview.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    preview.save(qa / "overview-preview-only.png")
    qa_files = []

    def save_qa(filename, pixels, role, boxes=None):
        path = qa / filename
        Image.fromarray(pixels).save(path)
        qa_files.append({"file": str(path), "sha256": sha(path), "pixels": [pixels.shape[1], pixels.shape[0]],
                         "role": role, "resized": False, "sourceBoxes": boxes})

    def board(filename, strip, role):
        assert strip.shape == (4096, 320, 3)
        image = np.concatenate([strip[i * 1024:(i + 1) * 1024] for i in range(4)], axis=1)
        save_qa(filename, image, role, [{"segment": i, "stripYRange": [i * 1024, (i + 1) * 1024]} for i in range(4)])

    neighbor_left = load(OLD / "r09_c08.png")
    neighbor_bottom = load(OLD / "r10_c09.png")
    neighbor_corner = load(OLD / "r10_c08.png")
    for version, candidate in (("before_v4", v4), ("after_v5", final)):
        left_strip = np.concatenate((neighbor_left[:, -160:], candidate[:, :160]), axis=1)
        bottom_strip = np.concatenate((candidate[-160:], neighbor_bottom[:160]), axis=0)
        # Transpose instead of resampling: left-to-right board segments follow source x order.
        board(f"external_left_{version}_full4096_100pct.png", left_strip, "Full left boundary, four consecutive native-pixel segments")
        board(f"external_bottom_{version}_full4096_100pct.png", np.transpose(bottom_strip, (1, 0, 2)),
              "Full bottom boundary, four consecutive native-pixel segments; axes transposed")
    board("left_treatment_return_x215_100pct.png", final[:, 55:375], "Left treatment return boundary x=215")
    board("bottom_treatment_return_y3880_100pct.png", np.transpose(final[3720:4040], (1, 0, 2)),
          "Bottom treatment return boundary y=3880; axes transposed")
    fourway = np.concatenate((np.concatenate((neighbor_left[-512:, -512:], final[-512:, :512]), axis=1),
                             np.concatenate((neighbor_corner[:512, -512:], neighbor_bottom[:512, :512]), axis=1)), axis=0)
    save_qa("four_tile_junction_100pct.png", fourway, "Actual r09c08/r09c09/r10c08/r10c09 corner, no resizing")
    save_qa("treatment_return_corner_100pct.png", final[3440:4096, :720], "Return-band corner and new tile southwest corner")
    for y0 in (384, 1120):
        strip = np.concatenate((neighbor_left[:, -256:], final[:, :256]), axis=1)
        save_qa(f"left_detail_y{y0+256}_100pct.png", strip[y0:y0+512], "Native-pixel left boundary detail")
    for x0 in (1152, 1600):
        strip = np.concatenate((final[-256:], neighbor_bottom[:256]), axis=0)
        save_qa(f"bottom_detail_x{x0+256}_100pct.png", strip[:, x0:x0+512], "Native-pixel bottom boundary detail")
    assert all(sha(path) == value for path, value in before_hashes.items())
    active_flow = flow[(mask > 0) & (mask < 255)]
    report = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "fixed_neighbors_bounded_registration_candidate_pending_visual_review",
        "candidate": {"file": str(out / "r09_c09.png"), "sha256": sha(out / "r09_c09.png"), "pixels": [4096, 4096]},
        "sourceFiles": [{"file": p, "sha256": h} for p, h in before_hashes.items()],
        "script": {"file": str(Path(__file__).resolve()), "sha256": sha(__file__)},
        "helper": {"file": str(helper_path), "sha256": sha(helper_path)},
        "libraries": {"numpy": np.__version__, "opencv": helper.cv2.__version__},
        "sourcesReadOnlyAfterVerified": True, "oldSixCandidatesUnchanged": True, "v4Unchanged": True,
        "sourceOuter115PixelsUnchangedBeforeEmbedding": True, "oldCorner230OverlapIdentical": True,
        "sourceCoreEmbeddedLTRB": [115,115,4211,4211], "finalCropLTRB": [115,115,4211,4211],
        "leftSharedOldQuadLTRB": [8192,0,8422,4326], "leftSharedNewExtendedLTRB": [0,0,230,4326],
        "bottomSharedOldRow10LTRB": [8192,0,12518,230], "bottomSharedNewExtendedLTRB": [0,4096,4326,4326],
        "maskRule": "round(255*smoothstep((x-115)/115)*smoothstep((4211-y)/115))",
        "registration": registration, "activeBlendFlowP95AbsXY": np.percentile(np.abs(active_flow),95,axis=0).tolist(),
        "changedCorePixels": int(changed.sum()), "allowedChangedCoreBands": {"leftX": [0,215], "bottomY": [3881,4096]},
        "outsideAllowedCoreBandsUnchanged": True, "interiorRectLTRBUnchanged": [215,0,4096,3881],
        "firstCoreColumnMatchesOldLeftHalo": True, "lastCoreRowMatchesOldBottomHalo": True,
        "affectedCandidateCoordinates": ["r09_c09"], "nativeArtEnlarged": False,
        "resampling": "Bounded subpixel edge registration and local color matching; exact dimensions retained",
        "files": [{"file": str(p), "sha256": sha(p)} for p in sorted(out.iterdir()) if p.is_file()],
        "qa": qa_files, "visualAcceptancePassed": False, "productionAccepted": False, "runtimePublished": False,
        "remainingReview": ["full left boundary", "full bottom boundary", "four-tile junction", "treatment return edges", "new corner colour/geometry"],
    }
    with (HERE / "assembly-v5.json").open("x",encoding="utf-8") as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps({"candidate":str(out/"r09_c09.png"),"qa":str(qa),"assembly":str(HERE/"assembly-v5.json"),
                      "changedCorePixels":report["changedCorePixels"],"maxShiftXY":registration["actualMaxShiftXY"],
                      "accepted":False},indent=2))


if __name__ == "__main__":
    main()
