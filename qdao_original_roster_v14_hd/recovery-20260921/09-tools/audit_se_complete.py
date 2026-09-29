"""Verify the SE selection and create review evidence without editing game pixels."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageSequence
from common import DELIVERY, read_json, sha, utc_now
work = DELIVERY / "work" / "SE"
out = DELIVERY / "qa-independent"
records = []
pixel_hashes = set()
for relative in [f"walk/SE/{f:02d}.png" for f in range(1, 17)] + ["idle/SE.png"]:
    path = work / "runtime" / relative
    source = read_json(work / "sources" / (relative + ".json"))
    raw = Path(source["source"]["path"])
    generation = read_json(source["source"]["generationRecord"])
    with Image.open(path) as im:
        assert im.mode == "RGBA" and im.size == (1024, 1024)
        pixels = np.array(im)
        alpha = pixels[:, :, 3]
        assert not alpha[0].any() and not alpha[-1].any() and not alpha[:, 0].any() and not alpha[:, -1].any()
        ys, xs = np.where(alpha > 8)
        top = int(ys.min()); height = int(ys.max()) - top
        axis = float(np.median(xs[ys < top + max(1, int(height * .42))]))
        assert abs(axis - 512) <= .5 and int(ys.max()) == 942
        pixel_hashes.add(hashlib.sha256(im.tobytes()).hexdigest())
    assert min(source["nativeSize"]) >= 1024
    assert sha(path) == source["outputSha256"] and sha(raw) == source["source"]["sha256"]
    assert generation["route"] == "builtin" and generation["paidApiCalls"] == 0
    assert source["operation"]["commonScale"] == .88
    assert not source["operation"]["mirrored"] and not source["operation"]["poseInterpolated"]
    assert source["operation"]["chromaProfile"] == "none"
    records.append({"slot": relative, "selectedBatch": raw.parent.name, "rawSha256": sha(raw), "outputSha256": sha(path), "nativeSize": source["nativeSize"], "sourceRecord": str(work / "sources" / (relative + ".json")), "actualModel": generation["actualModel"], "actualQuality": generation["actualQuality"]})
assert len({r["rawSha256"] for r in records}) == 17 and len(pixel_hashes) == 17
previews = []
for bg in ("dark", "light"):
    path = work / "qa" / f"walk-30ms-{bg}.gif"
    with Image.open(path) as gif:
        durations = [f.info["duration"] for f in ImageSequence.Iterator(gif)]
        assert durations == [30] * 16 and gif.info["loop"] == 0
    previews.append({"path": str(path), "sha256": sha(path), "frameCount": 16, "durationsMs": durations, "cycleMs": sum(durations), "loop": 0})
idle = Image.open(work / "runtime/idle/SE.png").convert("RGBA")
canvas = Image.new("RGB", (2048, 1024))
for offset, bg in ((0, (25, 32, 40)), (1024, (242, 239, 225))):
    comp = Image.new("RGBA", idle.size, bg + (255,)); comp.alpha_composite(idle)
    canvas.paste(comp.convert("RGB"), (offset, 0))
canvas.save(work / "qa/idle-dark-light.jpg", quality=95)
report = {"character": "09_bamboo_archer_girl", "direction": "SE", "reviewer": "qa_complete09", "checkedAt": utc_now(), "walkCount": 16, "idleCount": 1, "technicalChecks": "passed", "uniqueSourceCount": 17, "uniquePixelCount": 17, "slots": records, "previews": previews, "browser": {"url": "http://127.0.0.1:18809/work/SE/qa/se-review.html", "engine": "Codex IAB via CUA", "observed": ["384 px deep/light 16-frame playback; visible frame counter advances", "15-16-01-02 seam playback deep/light", "1024 px mode selected; both backgrounds scrolled and examined"], "timingLimit": "GIF metadata and script specify 30 ms; wall-clock browser timing not measured."}, "visualReview": "pending final idle view", "clientIntegration": "not_performed"}
(out / "SE-20260928.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("SE: 17 distinct native sources, 17 verified 1024 RGBA exports, 2 x 16-frame 30ms GIFs")
