"""Real Lu Dongbin S-pose regressions; creates only temporary test evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

from process_roster import (DIRECTIONS, alignment_v3_reference, body_ground_anchor,
    normalize, normalize_direction_v3, prepare_alignment_v3, translate_alignment_v3)
from verify_delivery import verify_alignment_v3, verify_character, verify_v3_frame

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "review/lu_natural_walk_sample"


def digest(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def read_s_poses():
    sets = []
    for name in ("processing-four", "processing-inbetweens"):
        folder = SAMPLE / name
        meta = json.loads((folder / "pipeline-meta.json").read_text())
        with Image.open(folder / "raw-sheet-clean.png") as source:
            clean = source.convert("RGBA")
        poses = []
        for info in meta["frames"]:
            crop = clean.crop(info["source_box"]).crop(info["crop_bbox"])
            poses.append(crop.resize(tuple(info["output_size"]), Image.Resampling.LANCZOS))
        sets.append(poses)
    return [sets[j][i] for i in range(4) for j in range(2)]


class AlignmentV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.walk = read_s_poses()
        with Image.open(SAMPLE / "preview-idle/S.png") as image:
            cls.idle = image.convert("RGBA")
        cls.idle_crop, _ = prepare_alignment_v3(cls.idle, 1.0)
        cls.reference = alignment_v3_reference(cls.idle_crop)
        cls.prepared = [prepare_alignment_v3(f, 1.0) for f in cls.walk]

    def frame(self, index=0):
        before, record = self.prepared[index]
        image, transform = translate_alignment_v3(before, self.reference)
        return image, before, {**record, **transform}

    def test_real_s8_preserves_rgba_and_foot_depth_while_head_is_stable(self):
        tops, feet = [], []
        for index in range(8):
            image, before, record = self.frame(index)
            measured = verify_v3_frame(image, before, record, self.reference, 1.0)
            moved = record["bbox_alpha_gt_0"]
            self.assertEqual(image.crop(moved).tobytes(), before.crop(record["pretranslation_bbox"]).tobytes())
            tops.append(measured["head_anchor"][1]); feet.append(measured["lowest_alpha_y"])
        self.assertEqual(len(set(tops)), 1)
        self.assertGreater(max(feet) - min(feet), 0, "Real perspective foot variation must survive")
        print("S8 v3 head tops:", tops, "lowest alpha Y:", feet)

    def test_v2_matches_existing_real_s8_pixel_for_pixel(self):
        for index, original in enumerate(self.walk, 1):
            image, record = normalize(original, 1.0, despill_edges=True)
            with Image.open(SAMPLE / "preview-eight" / f"S-{index:02d}.png") as golden:
                self.assertEqual(image.tobytes(), golden.tobytes())
            self.assertEqual(body_ground_anchor(image), (256.0, 471))
            self.assertEqual(record["alignment_version"], 2)

    def test_wrong_translation_metadata_is_rejected(self):
        image, before, record = self.frame()
        record["translation_px"][1] += 1
        with self.assertRaises(ValueError):
            verify_v3_frame(image, before, record, self.reference, 1.0)

    def test_shifted_pixels_are_rejected_even_with_updated_output_hash(self):
        image, before, record = self.frame()
        shifted = Image.new("RGBA", (512, 512)); shifted.paste(image, (0, 1))
        record["rgba_sha256"] = digest(shifted)
        with self.assertRaises(ValueError):
            verify_v3_frame(shifted, before, record, self.reference, 1.0)

    def test_clipping_is_rejected_before_paste_and_by_inverse_verifier(self):
        image, before, record = self.frame()
        reference = deepcopy(self.reference); reference["target_head_px"][1] += 512
        with self.assertRaisesRegex(ValueError, "clip|touch"):
            translate_alignment_v3(before, reference)
        record["translation_px"][1] += 512
        with self.assertRaisesRegex(ValueError, "clip|touch"):
            verify_v3_frame(image, before, record, reference, 1.0)

    def test_visible_pixel_corruption_is_rejected_even_with_updated_output_hash(self):
        image, before, record = self.frame()
        image = image.copy()
        y, x = np.argwhere(np.asarray(image.getchannel("A")) > 128)[0]
        image.putpixel((int(x), int(y)), (0, 0, 0, 0))
        record["rgba_sha256"] = digest(image)
        with self.assertRaises(ValueError):
            verify_v3_frame(image, before, record, self.reference, 1.0)

    def test_pretranslation_metadata_and_common_scale_are_checked(self):
        for key, value in (("shared_scale", 1.01), ("pretranslation_bbox", [0, 0, 1, 1]),
                           ("pretranslation_crop_rgba_sha256", "0" * 64)):
            with self.subTest(key=key):
                image, before, record = self.frame(); record[key] = value
                with self.assertRaises(ValueError):
                    verify_v3_frame(image, before, record, self.reference, 1.0)

    def test_full_evidence_recomputes_idle_roi_and_rejects_modified_reference(self):
        # Reusing S solely as a validation fixture does not produce game art.
        with tempfile.TemporaryDirectory(prefix="qdao-v3-regression-") as temporary:
            root = Path(temporary) / "24_lu_dongbin"; root.mkdir()
            records = {"walk": {}, "idle": {}}; references = {}
            for direction in DIRECTIONS:
                frames, idle, wr, ir, ref = normalize_direction_v3(self.walk, self.idle, 1.0,
                    root / "processing/alignment-v3" / direction, root)
                records["walk"][direction] = wr; records["idle"][direction] = ir; references[direction] = ref
                (root / "idle").mkdir(exist_ok=True); idle.save(root / "idle" / f"{direction}.png")
                folder = root / "walk" / direction; folder.mkdir(parents=True)
                for index, frame in enumerate(frames, 1): frame.save(folder / f"{index:02d}.png")
            path = root / "processing/frame-transforms.json"; path.write_text(json.dumps(records))
            alignment = {"version": 3, "horizontal": "fixed_idle_head_roi_alpha_median",
                "vertical": "direction_idle_head_top", "root_px": [256, 471], "common_scale": 1.0,
                "direction_references": references, "transforms_path": "processing/frame-transforms.json",
                "transforms_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertEqual(len(verify_alignment_v3(root, alignment)), 72)
            alignment["direction_references"]["S"]["roi_height_px"] += 1
            with self.assertRaisesRegex(ValueError, "reference"):
                verify_alignment_v3(root, alignment)

    def test_existing_v2_delivery_verifies_without_rewriting(self):
        result = verify_character(ROOT / "24_lu_dongbin")
        self.assertEqual(result["alignment_version"], 2)
        self.assertEqual(result["status"], "passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
