"""Mechanical test fixtures only; never creates or certifies generated artwork."""
import importlib.util
import json
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("city4k", ROOT / "pipeline.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
temporary_parent = ROOT / "qa"
temporary_parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="synthetic-fixture-", dir=temporary_parent) as temporary:
    fixture = Path(temporary).resolve()
    assert fixture.parent == temporary_parent.resolve()
    pipeline.ROOT = fixture
    pipeline.SOURCE = fixture / "layout.png"
    Image.new("RGB", (8, 8), "white").save(pipeline.SOURCE)
    for name in ("references", "generated", "prompts", "qa"):
        (fixture / name).mkdir()
    y, x = np.indices((4352, 4352), dtype=np.uint16)
    full = np.stack((x % 251, y % 241, (x + y) % 239), axis=2).astype("uint8")
    patches, records = [], []
    for index, patch_id in enumerate(pipeline.IDS):
        row, column = divmod(index, 2)
        ref = fixture / "references" / f"{patch_id}.png"
        Image.new("RGB", (1152, 1152), (10, 20, 30)).save(ref)
        prompt = fixture / "prompts" / f"{patch_id}.txt"
        prompt.write_text("Synthetic fixture only. Not artwork or real API evidence.", encoding="utf8")
        generated = fixture / "generated" / f"{patch_id}.png"
        Image.fromarray(full[row*2048:row*2048+2304, column*2048:column*2048+2304]).save(generated)
        patches.append({"id": patch_id, "layoutReference": str(ref), "referenceSha256": pipeline.digest(ref),
                        "promptFile": str(prompt), "generatedFile": str(generated)})
        records.append({"id": patch_id, "model": "gpt-image-2.5-sunburst-2026-09-08", "quality": "max",
                        "requestId": "SYNTHETIC-FIXTURE-ONLY", "nativePixels": [2304, 2304],
                        "promptSha256": pipeline.digest(prompt), "outputSha256": pipeline.digest(generated)})
    metadata = {"sourceSha256": pipeline.digest(pipeline.SOURCE),
                "targetModel": "gpt-image-2.5-sunburst-2026-09-08", "patches": patches}
    (fixture / "preparation.json").write_text(json.dumps(metadata), encoding="utf8")
    try:
        pipeline.assemble()
    except ValueError as error:
        assert "generation-records.json" in str(error)
    else:
        raise AssertionError("Missing generator evidence must reject assembly")
    (fixture / "generation-records.json").write_text(json.dumps(records), encoding="utf8")
    original_spec = pipeline.importlib.util.spec_from_file_location
    def resolve_helper(name, path, *args, **kwargs):
        if name == "city_seams":
            path = ROOT.parent / "tianyong_festival_hd_20260910/seam_helpers.py"
        return original_spec(name, path, *args, **kwargs)
    pipeline.importlib.util.spec_from_file_location = resolve_helper
    try:
        pipeline.assemble()
    finally:
        pipeline.importlib.util.spec_from_file_location = original_spec
    with Image.open(fixture / "qa/tianyong-center-candidate-4096.png") as candidate:
        assert candidate.size == (4096, 4096)
        assert np.array_equal(np.asarray(candidate), full[128:4224, 128:4224])
    report = {"scope": "isolated synthetic mechanical fixture; not generated artwork",
              "stitchWithoutResize": "passed", "pixelExactReconstruction": "passed",
              "northWestOrientation": "passed", "outputPixels": [4096, 4096],
              "missingGenerationEvidenceRejected": "passed",
              "realGeneratedArtworkCount": 0, "runtimePublished": False}
(ROOT / "qa/verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
print(json.dumps(report))
