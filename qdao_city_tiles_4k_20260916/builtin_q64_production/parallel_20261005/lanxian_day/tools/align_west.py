"""Bounded existing-geometry registration of r08_c09 against its west core.

Only the explicit input is read. No candidate/progress discovery or approval.
Registration is vertical-only; fixed world x positions are preserved. The
4096x115 true shared overlap supplies all geometric and tonal estimates.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = (ROOT / "r08_c09/registration-west").resolve()
VENDOR = Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/"
              "resume_single_city_20260921/continuation_20261004/c07-recovery/vendor")
sys.path.insert(0, str(VENDOR))
import cv2

H, E, N, REACH = 115, 4326, 4096, 435


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def safe(path):
    p = Path(path).resolve()
    if not p.is_relative_to(OUT_ROOT) or p == OUT_ROOT:
        raise ValueError(f"Output outside registration-west: {p}")
    return p


def write_json(path, value):
    p = safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_image(path, arr):
    p = safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    im = arr if isinstance(arr, Image.Image) else Image.fromarray(arr)
    im.save(p)
    return {"file": str(p), "sha256": sha(p), "pixels": list(im.size)}


def read_rgb(path, dimensions, expected):
    p = Path(path).resolve(strict=True)
    if sha(p) != expected:
        raise ValueError(f"Input checksum differs: {p}")
    with Image.open(p) as im:
        if im.mode != "RGB" or im.size != dimensions or im.format != "PNG":
            raise ValueError(f"Expected RGB PNG {dimensions}: {p}")
        return np.array(im), {"file": str(p), "sha256": expected, "pixels": list(im.size)}


def estimate_vertical_flow(fixed, moving, limit, match_start, match_end):
    """Regularized subpixel vertical flow, no scale/rotation or horizontal warp.

    Bilateral image flow is diagnostic; matching uses vertical gradients and
    local highpass intensity to avoid a brightness shift masquerading as motion.
    Dynamic programming restricts estimated per-row displacement changes to
    0.25px. Gaussian smoothing then produces a continuous monotone map.
    """
    gray_f = cv2.cvtColor(fixed, cv2.COLOR_RGB2GRAY)
    gray_m = cv2.cvtColor(moving, cv2.COLOR_RGB2GRAY)
    fb_args = dict(pyr_scale=.5, levels=3, winsize=41, iterations=8,
                   poly_n=7, poly_sigma=1.5, flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
    forward = cv2.calcOpticalFlowFarneback(gray_f, gray_m, None, **fb_args)
    backward = cv2.calcOpticalFlowFarneback(gray_m, gray_f, None, **fb_args)
    yy, xx = np.mgrid[:N, :H].astype(np.float32)
    back_sample = cv2.remap(backward, xx + forward[..., 0], yy + forward[..., 1],
                            cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    consistency = np.linalg.norm(forward + back_sample, axis=2)
    f = cv2.GaussianBlur(gray_f.astype(np.float32), (0, 0), .8)
    m = cv2.GaussianBlur(gray_m.astype(np.float32), (0, 0), .8)
    gf = cv2.Sobel(f, cv2.CV_32F, 0, 1, ksize=3, scale=1 / 8)
    gm = cv2.Sobel(m, cv2.CV_32F, 0, 1, ksize=3, scale=1 / 8)
    hf = f - cv2.GaussianBlur(f, (0, 0), 8)
    hm = m - cv2.GaussianBlur(m, (0, 0), 8)
    confidence = (consistency < 1.5) & (np.abs(gf) > 1.0)
    prior = np.zeros(N, np.float32)
    reliable = np.zeros(N, bool)
    for y in range(N):
        use = confidence[y, match_start:match_end]
        if use.sum() >= min(16, (match_end - match_start) // 2):
            prior[y] = np.median(forward[y, match_start:match_end, 1][use])
            reliable[y] = True
    shifts = np.arange(-limit, limit + .125, .25, dtype=np.float32)
    energy = cv2.blur(np.abs(gf[:, match_start:match_end]).mean(axis=1).reshape(N, 1), (1, 41)).ravel()
    denom = np.maximum(energy, .75)
    costs = np.empty((N, len(shifts)), np.float32)
    for k, shift in enumerate(shifts):
        mg = cv2.remap(gm, xx, yy + shift, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        mh = cv2.remap(hm, xx, yy + shift, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        error = .8 * np.minimum(np.abs(gf - mg), 40) + .2 * np.minimum(np.abs(hf - mh), 40)
        local = cv2.blur(error[:, match_start:match_end].mean(axis=1).reshape(N, 1), (1, 41)).ravel() / denom
        costs[:, k] = local + reliable * .002 * np.minimum((shift - prior) ** 2, 25)
    # A 0.25px/row slope limit prevents folded geometry and abrupt bends.
    backtrace = np.zeros_like(costs, np.int8)
    dp = costs[0] + .0001 * shifts ** 2
    for y in range(1, N):
        choices = np.stack([np.r_[np.inf, dp[:-1]] + .02, dp,
                            np.r_[dp[1:], np.inf] + .02])
        choice = np.argmin(choices, axis=0)
        backtrace[y] = choice - 1
        dp = costs[y] + choices[choice, np.arange(len(shifts))]
    state = int(np.argmin(dp))
    raw = np.empty(N, np.float32)
    for y in range(N - 1, -1, -1):
        raw[y] = shifts[state]
        if y:
            state += int(backtrace[y, state])
    field = cv2.GaussianBlur(raw.reshape(N, 1), (1, 0), sigmaX=0, sigmaY=5).ravel()
    field = np.clip(field, -limit, limit)
    return field, {"forward_flow": forward, "backward_flow": backward,
                   "forward_backward_error": consistency, "flow_confidence": confidence,
                   "vertical_flow_before_smoothing": raw, "vertical_flow": field,
                   "shift_candidates": shifts, "matching_cost": costs}, {
                       "method": "vertical-gradient/local-highpass subpixel matching with slope-regularized dynamic programming",
                       "flowGridStepPixels": .25, "maxRowSlopePixels": .25, "flowSmoothingSigmaRows": 5,
                       "costWindowRows": 41, "matchingOverlapColumns": [match_start, match_end],
                       "opticalFlowPrior": fb_args, "opticalFlowPriorWeight": .002,
                       "reliablePriorRows": int(reliable.sum()), "horizontalDisplacement": 0,
                       "maxForwardBackwardErrorForPriorPixels": 1.5,
                   }


def groove_measurements(west, before, after):
    # Adjacent boundary pixels on the west tile and each target core.
    w = west[:, -1].astype(float).mean(axis=1)
    fields = [before[H:H + N, H].astype(float).mean(axis=1),
              after[H:H + N, H].astype(float).mean(axis=1)]
    rows = []
    for lo, hi in [(580, 620), (640, 682), (710, 747), (1198, 1234),
                   (1456, 1496), (1766, 1804), (1908, 1944), (1998, 2044),
                   (2523, 2551), (2590, 2620), (3048, 3070), (3162, 3212),
                   (3297, 3351), (3809, 3862)]:
        wy = int(np.argmin(w[lo:hi]) + lo)
        by, ay = [int(np.argmin(f[lo:hi]) + lo) for f in fields]
        rows.append({"windowCoreY": [lo, hi], "westDarkestY": wy,
                     "beforeDarkestY": by, "afterDarkestY": ay,
                     "beforeEastMinusWestPixels": by - wy, "afterEastMinusWestPixels": ay - wy})
    return rows


def run(args):
    if not 0 < args.max_flow <= 10 or not 0 <= args.tone_limit <= 12:
        raise ValueError("Geometry bound must be <=10px and tone bound <=12/255")
    if not 0 <= args.match_start < args.match_end <= H or args.match_end - args.match_start < 8:
        raise ValueError("Matching columns must lie within true overlap, with at least8 samples")
    out = safe(OUT_ROOT / args.output_name)
    if out.exists():
        raise FileExistsError(f"Use a new output-name rather than overwrite: {out}")
    target, target_info = read_rgb(args.input, (E, E), args.input_sha)
    west, west_info = read_rgb(args.west, (N, N), args.west_sha)
    fixed = west[:, N - H:]
    moving = target[H:H + N, :H]
    vertical, raw_fields, parameters = estimate_vertical_flow(fixed, moving, args.max_flow, args.match_start, args.match_end)
    ys = np.pad(vertical, (H, H), mode="edge")
    distance = np.arange(REACH, dtype=np.float32)
    t = np.clip((distance - H) / (REACH - H), 0, 1)
    weight = .5 * (1 + np.cos(np.pi * t))
    flow_y = ys[:, None] * weight[None, :]
    yy, xx = np.mgrid[:E, :REACH].astype(np.float32)
    warped = cv2.remap(target[:, :REACH], xx, yy + flow_y, cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_REFLECT_101)
    # Estimate only slowly varying diffuse color; geometry has already moved.
    residual = fixed.astype(np.float32) - warped[H:H + N, :H].astype(np.float32)
    row_tone = np.median(residual[:, 16:110], axis=1)
    row_tone = cv2.GaussianBlur(row_tone.reshape(N, 1, 3), (1, 0), sigmaX=0, sigmaY=16).reshape(N, 3)
    row_tone = np.clip(row_tone, -args.tone_limit, args.tone_limit)
    tone = np.pad(row_tone, ((H, H), (0, 0)), mode="edge")[:, None, :] * weight[None, :, None]
    corrected = target.copy()
    corrected[:, :REACH] = np.rint(np.clip(warped.astype(np.float32) + tone, 0, 255)).astype(np.uint8)
    if not np.array_equal(corrected[:, REACH:], target[:, REACH:]):
        raise AssertionError("Pixels outside declared support changed")
    if np.max(np.abs(flow_y)) > 10.0001:
        raise AssertionError("Flow bound exceeded")
    out.mkdir(parents=True)
    mask = np.zeros((E, E), np.uint8)
    mask[:, :REACH] = np.rint(weight[None, :] * 255).astype(np.uint8)
    mask_info = save_image(out / "mask.png", mask)
    field_path = safe(out / "flow-correction.npz")
    np.savez_compressed(field_path, **raw_fields, applied_flow_y=flow_y.astype(np.float32),
                        applied_flow_x=np.zeros_like(flow_y), tone_correction=tone.astype(np.float32),
                        horizontal_weight=weight, support_box=np.array([0, 0, REACH, E]))
    core = corrected[H:H + N, H:H + N]
    outputs = {"extended": save_image(out / "extended4326.png", corrected),
               "core": save_image(out / "core4096.png", core),
               "preview": save_image(out / "preview1024.png", Image.fromarray(core).resize((1024, 1024), Image.Resampling.LANCZOS))}
    crops = []
    for part in range(4):
        y = part * 1024
        paired = np.concatenate([west[y:y + 1024, -256:], core[y:y + 1024, :256]], axis=1)
        entry = save_image(out / "qa" / f"external_west_part{part + 1}.png", paired)
        entry.update(coreYRange=[y, y + 1024], commonBoundaryX=256, resampling="none; integer QA crop/paste")
        crops.append(entry)
        edge = save_image(out / "qa" / f"edge_west_part{part + 1}.png", core[y:y + 1024, :256])
        edge.update(coreBox=[0, y, 256, y + 1024], resampling="none; integer QA crop")
        crops.append(edge)
    for label, box in {"nw": [0, 0, 512, 512], "ne": [3584, 0, 4096, 512],
                       "sw": [0, 3584, 512, 4096], "se": [3584, 3584, 4096, 4096]}.items():
        x, y, x1, y1 = box
        entry = save_image(out / "qa" / ("corner_" + label + ".png"), core[y:y1, x:x1])
        entry.update(coreBox=box, resampling="none; integer QA crop")
        crops.append(entry)
    parameters.update(maxAllowedDisplacementPixels=args.max_flow, maxAllowedIncrementalTonePerChannel=args.tone_limit,
                      fadeStartExtendedX=H, fadeZeroExtendedX=REACH,
                      appliedInterpolation="OpenCV INTER_CUBIC", borderMode="BORDER_REFLECT_101",
                      toneSmoothingSigmaRows=16, toneEstimator="median RGB residual in true115px overlap columns16:110")
    result = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "inputs": {"extended": target_info, "westCore": west_info},
              "outputs": outputs, "operation": "Bounded local vertical existing-geometry registration followed by bounded low-frequency RGB residual correction",
              "parameters": parameters, "opencvVersion": cv2.__version__, "opencvVendor": str(VENDOR),
              "scriptSha256": sha(__file__), "fullExtendedPixels": [E, E], "corePixels": [N, N],
              "nativeDetailScaleUnchanged": True, "enlargementPerformed": False,
              "subpixelResamplingPerformed": True, "notPixelIdentityToNativeSource": True,
              "subpixelResamplingSupportExtendedBox": [0, 0, REACH, E],
              "outsideSupportPixelIdentical": True, "westNeighborUnchanged": sha(args.west) == args.west_sha,
              "sourceInputUnchanged": sha(args.input) == args.input_sha,
              "actual": {"maximumAbsoluteVerticalDisplacementPixels": float(np.abs(flow_y).max()),
                         "minimumVerticalDisplacementPixels": float(flow_y.min()),
                         "maximumVerticalDisplacementPixels": float(flow_y.max()),
                         "maxVerticalFieldSlope": float(np.abs(np.diff(vertical)).max()),
                         "maximumAbsoluteIncrementalTonePerChannel": float(np.abs(tone).max()),
                         "maximumPixelDifferenceFromInput": int(np.abs(corrected.astype(np.int16) - target.astype(np.int16)).max())},
              "mask": mask_info, "flowAndCorrection": {"file": str(field_path), "sha256": sha(field_path)},
              "qaCrops": crops, "grooveMeasurements": groove_measurements(west, target, corrected),
              "previewOnlyDownsampling": "LANCZOS to1024; no preview pixels used in production output",
              "status": "candidate_pending_visual_review", "formalAccepted": False, "clientValidated": False,
              "limitations": ["Registration cannot establish missing geometry; this run is restricted to pre-existing matching west structures.",
                              "Tone bound applies to this pass only; upstream tone changes have a separate record.",
                              "Vertical gradients and darkest-row metrics support inspection; they do not establish seam acceptance."]}
    write_json(out / "registration.manifest.json", result)
    print(json.dumps({"outputDirectory": str(out), "outputs": outputs, "actual": result["actual"],
                      "grooveMeasurements": result["grooveMeasurements"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-sha", required=True)
    parser.add_argument("--west", required=True)
    parser.add_argument("--west-sha", required=True)
    parser.add_argument("--output-name", default="v2")
    parser.add_argument("--max-flow", type=float, default=10)
    parser.add_argument("--tone-limit", type=float, default=8)
    parser.add_argument("--match-start", type=int, default=96)
    parser.add_argument("--match-end", type=int, default=115)
    run(parser.parse_args())
