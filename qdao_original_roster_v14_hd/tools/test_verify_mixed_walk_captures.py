"""Small walk-evidence binding tests; shared real PNG checks are tested separately."""
import copy
import unittest
from unittest.mock import patch

import verify_mixed_walk_captures as check


class NativeWalkBindingTests(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 64
        self.rows = {}
        self.manifest = {"files": []}
        self.actor = {"actualCharacterId": check.CHARACTER, "actualIsMixedResolution": True,
                      "controllerMoveSpeed": 9, "walkFrameCaptures": []}
        for number, direction in enumerate(("SW", "NW")):
            relative = "walk/" + direction + "/02.png"
            resource = check.gate.RESOURCE_FAMILY + "/" + check.CHARACTER + "/" + relative[:-4]
            self.rows["Assets/Resources/" + resource + ".png"] = {"sha256": self.sha}
            self.manifest["files"].append({"path": relative, "source_kind": "native-hd", "width": 1024,
                "height": 1024, "pixels_per_unit": 104, "sha256": self.sha})
            self.actor["walkFrameCaptures"].append({"characterId": check.CHARACTER, "direction": direction,
                "frameNumber": 2, "resourcePath": resource, "resourcePngSha256": self.sha,
                "inputSnapshotSha256": self.sha, "textureWidth": 1024, "textureHeight": 1024,
                "pixelsPerUnit": 104, "frameWorldHeight": 512 / 52,
                "normalizedPivot": {"x": .5, "y": .08}, "billboardScale": {"x": 1, "y": 1, "z": 1},
                "locomotionState": "Run", "realMotorEnabled": True, "matchesExpectedResource": True,
                "pathDistance": .45, "movementSeconds": .05,
                "routeStart": {"x": 0, "y": 0, "z": 0}, "captureFeet": {"x": .45, "y": 0, "z": 0},
                "simulationFrame": 100 + number * 35, "generatedUtc": "2026-09-19T10:00:01Z",
                "normalView": {"fixture": "normal"}, "nearestView": {"fixture": "near"}})

    def invoke(self):
        with patch.object(check.gate, "check_runtime_view", return_value={"imageSha256": self.sha}) as shared_view:
            result = check.check_frames(self.actor, self.rows, self.manifest, self.sha, None,
                {"minimum": 5, "default": 27}, "2026-09-19T10:00:00Z", "2026-09-19T10:00:02Z")
            self.assertEqual(shared_view.call_count, 4)
            for args in shared_view.call_args_list:
                self.assertEqual(args.args[0]["actualFrameHeight"], 1024)
                self.assertIn("-walk-", args.args[0]["actualCharacterId"])
            return result

    def reject(self, change):
        change()
        with self.assertRaises(ValueError):
            self.invoke()

    def test_two_native_frames_produce_four_bound_views(self):
        views = self.invoke()
        self.assertEqual([(v["direction"], v["view"]) for v in views],
                         [(d, v) for d in ("SW", "NW") for v in ("normalView", "nearestView")])

    def test_missing_duplicate_or_wrong_frame_is_rejected(self):
        for captures in ([], [copy.deepcopy(self.actor["walkFrameCaptures"][0])] * 2):
            with self.subTest(captures=captures):
                self.actor["walkFrameCaptures"] = captures
                with self.assertRaises(ValueError): self.invoke()

    def test_idle_cannot_stand_in_for_walking(self):
        self.reject(lambda: self.actor["walkFrameCaptures"][0].update(locomotionState="Idle"))

    def test_stale_input_or_resource_sha_is_rejected(self):
        for field in ("inputSnapshotSha256", "resourcePngSha256", "resourcePath"):
            with self.subTest(field=field):
                original = self.actor["walkFrameCaptures"][0][field]
                self.reject(lambda: self.actor["walkFrameCaptures"][0].update({field: "stale"}))
                self.actor["walkFrameCaptures"][0][field] = original

    def test_preserved_geometry_cannot_claim_native_detail(self):
        self.reject(lambda: self.manifest["files"][0].update(source_kind="preserved-v13"))

    def test_observed_512_or_wrong_ppu_pivot_world_scale_is_rejected(self):
        for field, value in (("textureWidth", 512), ("pixelsPerUnit", 52), ("frameWorldHeight", 5),
                             ("normalizedPivot", {"x": .5, "y": .5}), ("billboardScale", {"x": 2, "y": 2, "z": 2})):
            with self.subTest(field=field):
                original = self.actor["walkFrameCaptures"][0][field]
                self.reject(lambda: self.actor["walkFrameCaptures"][0].update({field: value}))
                self.actor["walkFrameCaptures"][0][field] = original

    def test_warp_or_stationary_frame_is_rejected(self):
        for end in ({"x": 0, "y": 0, "z": 0}, {"x": 20, "y": 0, "z": 0}):
            self.reject(lambda: self.actor["walkFrameCaptures"][0].update(captureFeet=end))

    def test_unbound_or_reused_simulation_time_is_rejected(self):
        self.reject(lambda: self.actor["walkFrameCaptures"][1].update(simulationFrame=100))

    def test_outside_launch_time_is_rejected(self):
        self.reject(lambda: self.actor["walkFrameCaptures"][0].update(generatedUtc="2026-09-18T10:00:01Z"))

    def test_shared_png_projection_gate_failure_is_preserved(self):
        with patch.object(check.gate, "check_runtime_view", side_effect=ValueError("PNG SHA changed")):
            with self.assertRaisesRegex(ValueError, "PNG SHA changed"):
                check.check_frames(self.actor, self.rows, self.manifest, self.sha, None,
                    {"minimum": 5, "default": 27}, "2026-09-19T10:00:00Z", "2026-09-19T10:00:02Z")


if __name__ == "__main__":
    unittest.main()
