"""Isolated gate tests only. Procedural PNG/XML fixtures never enter Unity, approval or publication."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location('v14_publisher_under_test', Path(__file__).with_name('publish_original_roster_v14.py'))
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.sandbox_root = (publisher.WORK / 'tmp').resolve()
        self.temporary = tempfile.TemporaryDirectory(prefix='v14-publisher-gate-unit-', dir=self.sandbox_root)
        self.root = Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(self.sandbox_root)
        self.project = self.root / 'unit-project'
        self.project.mkdir()
        self.capture = self.root / 'captures'
        self.capture.mkdir()
        self.actor_id = '03_lotus_healer_girl'
        self.plan = {'characterId': self.actor_id, 'outputs': {path: 'a' * 64 for path in publisher.EXPECTED_OUTPUTS}}
        self.camera = {'minimum': 5.0, 'default': 27.0}

    def tearDown(self):
        # Only delete this test-owned, verified temporary directory.
        assert self.root.resolve().is_relative_to(self.sandbox_root) and self.root.name.startswith('v14-publisher-gate-unit-')
        self.temporary.cleanup()

    def save_json(self, path, value):
        path.write_text(json.dumps(value), encoding='utf-8')

    def xml(self, platform):
        required = (publisher.HD_REQUIRED_METHODS[platform], publisher.identity.REQUIRED_METHODS[platform])
        total = sum(sum(methods.values()) for _, methods in required)
        root = ET.Element('test-run', result='Passed', passed=str(total), total=str(total), failed='0', skipped='0',
                          inconclusive='0', **{'start-time': '2026-01-01 00:00:01Z', 'end-time': '2026-01-01 00:00:03Z'})
        for class_name, methods in required:
            for method, count in methods.items():
                for index in range(count):
                    ET.SubElement(root, 'test-case', classname=class_name, methodname=method,
                                  fullname=class_name + '.' + method + '(' + str(index) + ')', result='Passed')
        path = self.root / (platform.lower() + '.xml')
        ET.ElementTree(root).write(path, encoding='utf-8')
        return path, root

    def launch(self):
        path, _ = self.xml('PlayMode')
        rows = {rel: {'path': rel, 'sha256': 'a' * 64} for rel in publisher.CURRENT_INPUT_BINDING_PATHS}
        snapshot_path = self.root / 'unit-input.json'
        self.save_json(snapshot_path, {'project': str(self.project), 'shared_writable_links': False, 'files': list(rows.values())})
        log = path.with_suffix('.log'); log.write_text('Unit fixture, not an actual Unity run.\n', encoding='utf-8')
        arguments = ['-projectPath', str(self.project), '-testPlatform', 'PlayMode', '-testFilter', publisher.EXPECTED_FILTERS['PlayMode'],
                     '-testResults', str(path), '-logFile', str(log)]
        launch = {'platform': 'PlayMode', 'filter': publisher.EXPECTED_FILTERS['PlayMode'], 'project': str(self.project),
                  'input_snapshot': str(snapshot_path), 'input_snapshot_sha256': publisher.sha(snapshot_path),
                  'arguments': arguments, 'started_utc': '2026-01-01T00:00:00Z', 'capture_directory': str(self.capture)}
        completion = {'exit_code': 0, 'xml_exists': True, 'log': str(log), 'finished_utc': '2026-01-01T00:00:04Z'}
        launch_path = path.with_name(path.stem + '-launch.json'); completion_path = path.with_name(path.stem + '-completion.json')
        self.save_json(launch_path, launch); self.save_json(completion_path, completion)
        report = {'projectPath': str(self.project), 'generatedUtc': '2026-01-01T00:00:02Z'}
        return path, report, rows, publisher.sha(snapshot_path), launch_path, completion_path

    def test_missing_identity_case_cannot_hide_inside_passed_hd_results(self):
        for platform in ("EditMode", "PlayMode"):
            path, result = self.xml(platform)
            classname, _ = publisher.identity.REQUIRED_METHODS[platform]
            victim = next(case for case in result if case.get("classname") == classname)
            result.remove(victim)
            result.set("total", str(len(result))); result.set("passed", str(len(result)))
            ET.ElementTree(result).write(path, encoding="utf-8")
            with self.subTest(platform=platform), self.assertRaisesRegex(ValueError, "Incomplete identity"):
                publisher.check_results(path, hd_platform=platform)

    def test_missing_identity_source_binding_rejects_launch(self):
        path, report, rows, digest, _, _ = self.launch()
        del rows[publisher.identity.SOURCES[0]]
        with self.assertRaises(ValueError):
            publisher.check_launch_binding(path, report, rows, [], digest, platform="PlayMode")

    def inventory_rows(self):
        prefix = publisher.FAMILY + '/' + self.actor_id + '/'
        relative = dict(self.plan['outputs'])
        relative.update({path + '.meta': 'b' * 64 for path in publisher.EXPECTED_OUTPUTS})
        relative.update({'runtime-index.asset': 'c' * 64, 'runtime-index.asset.meta': 'd' * 64,
                         'walk.meta': 'e' * 64, 'idle.meta': 'e' * 64})
        relative.update({'walk/' + direction + '.meta': 'f' * 64 for direction in publisher.DIRECTIONS})
        return {prefix + path: {'sha256': digest} for path, digest in relative.items()}

    def view_actor(self, view_name='normalView'):
        suffix = '-nearest-zoom' if view_name == 'nearestView' else ''
        path = self.capture / ('tianyong-' + self.actor_id + suffix + '.png')
        # Procedural gate fixture, deliberately confined to this temporary test folder.
        Image.effect_noise((1920, 1080), 60).convert('RGB').save(path)
        zoom = self.camera['minimum'] if view_name == 'nearestView' else self.camera['default']
        world = 512 / 52; height = world * 1080 / (2 * zoom)
        bottom = 540 - height * .08; top = bottom + height
        actor = {'actualCharacterId': self.actor_id, 'actualFrameWorldHeight': world, 'actualFrameHeight': 1024}
        actor[view_name] = {'imagePath': str(path), 'imageSha256': publisher.sha(path), 'renderWidth': 1920, 'renderHeight': 1080,
            'configuredZoomMin': 5.0, 'configuredZoomDefault': 27.0, 'requestedZoom': zoom, 'actualOrthographicSize': zoom,
            'frameLeftPixels': 960 - height / 2, 'frameRightPixels': 960 + height / 2, 'frameBottomPixels': bottom, 'frameTopPixels': top,
            'projectedFrameHeightPixels': height, 'screenPixelsPerTexturePixel': height / 1024,
            'actorFeetScreenPixels': {'x': 960, 'y': 540, 'z': 110}, 'fullFrameInsideCapture': top <= 1080}
        return actor

    def review_fixture(self):
        actor = self.view_actor('nearestView')
        observed = publisher.check_runtime_view(actor, 'nearestView', self.capture, self.camera)
        report = {'generatedUtc': '2026-01-01T00:00:02Z'}
        report_path = self.root / 'unit-runtime.json'; snapshot_path = self.root / 'unit-snapshot.json'
        self.save_json(report_path, report); self.save_json(snapshot_path, {'scope': 'unit fixture only'})
        review = {'schema': 'qdao-original-v14-hd/runtime-visual-review-v1', 'status': 'passed', 'reviewer': 'UNIT FIXTURE ONLY',
            'runtime_report_sha256': publisher.sha(report_path), 'input_snapshot_sha256': publisher.sha(snapshot_path),
            'reviewed_utc': '2026-01-01T00:00:05Z', 'views': [{'character_id': self.actor_id, 'view': 'nearestView', 'status': 'passed',
                'image_sha256': observed['imageSha256'], 'notes': 'Synthetic unit data, never an actual artwork approval.',
                'clipping_reviewed': True, 'full_frame_inside_capture': False}]}
        path = self.root / 'unit-visual-review.json'; self.save_json(path, review)
        return path, report_path, snapshot_path, report, {(self.actor_id, 'nearestView'): observed}

    def test_all_hd_methods_and_parameter_cases_are_required(self):
        for platform, (_, methods) in publisher.HD_REQUIRED_METHODS.items():
            for parameter_case in (False, True):
                with self.subTest(platform=platform, parameter_case=parameter_case):
                    path, root = self.xml(platform)
                    publisher.check_results(path, hd_platform=platform)
                    victim = next(case for case in root if (methods[case.get('methodname')] > 1) == parameter_case)
                    root.remove(victim); root.set('passed', str(len(root))); root.set('total', str(len(root)))
                    ET.ElementTree(root).write(path, encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, 'Incomplete HD'):
                        publisher.check_results(path, hd_platform=platform)

    def test_aggregate_passed_cannot_hide_skips_inconclusive_or_duplicate_cases(self):
        for reason in ('skipped', 'inconclusive', 'duplicate', 'failed_case'):
            with self.subTest(reason=reason):
                path, root = self.xml('PlayMode')
                if reason in ('skipped', 'inconclusive'): root.set(reason, '1')
                elif reason == 'duplicate': list(root)[-1].set('fullname', list(root)[0].get('fullname'))
                else: list(root)[-1].set('result', 'Failed')
                ET.ElementTree(root).write(path, encoding='utf-8')
                with self.assertRaises(ValueError): publisher.check_results(path, hd_platform='PlayMode')

    def test_launch_requires_exit_zero_xml_and_retained_log(self):
        for invalid in ('nonzero', 'missing_xml_flag', 'missing_log'):
            with self.subTest(invalid=invalid):
                path, report, rows, digest, _, completion_path = self.launch()
                completion = publisher.read(completion_path)
                if invalid == 'nonzero': completion['exit_code'] = 1
                elif invalid == 'missing_xml_flag': completion['xml_exists'] = False
                else: path.with_suffix('.log').unlink()
                self.save_json(completion_path, completion)
                with self.assertRaisesRegex(ValueError, 'exit0'):
                    publisher.check_launch_binding(path, report, rows, [], digest, platform='PlayMode')

    def test_launch_rejects_filtered_or_wrong_platform_runs_and_wrong_snapshot(self):
        for invalid in ('filter', 'platform', 'snapshot'):
            with self.subTest(invalid=invalid):
                path, report, rows, digest, launch_path, _ = self.launch()
                publisher.check_launch_binding(path, report, rows, [], digest, platform='PlayMode')
                launch = publisher.read(launch_path)
                if invalid == 'filter': launch['filter'] = 'OnlyOldThreeMethods'
                elif invalid == 'platform': launch['platform'] = 'EditMode'
                else: launch['input_snapshot_sha256'] = 'f' * 64
                self.save_json(launch_path, launch)
                with self.assertRaises(ValueError): publisher.check_launch_binding(path, report, rows, [], digest, platform='PlayMode')

    def test_launch_timestamps_must_enclose_xml(self):
        path, report, rows, digest, _, completion_path = self.launch()
        completion = publisher.read(completion_path); completion['finished_utc'] = '2025-01-01T00:00:00Z'
        self.save_json(completion_path, completion)
        with self.assertRaisesRegex(ValueError, 'timestamps'): publisher.check_launch_binding(path, report, rows, [], digest, platform='PlayMode')

    def test_exact140_inventory_accepts_only_real_root_derived_index_and_valid_metas(self):
        rows = self.inventory_rows(); publisher.check_runtime_inventory(rows, self.plan, require_index=True)
        prefix = publisher.FAMILY + '/' + self.actor_id + '/'
        for extra in ('walk_E.png', 'review/strips/walk_N.png', 'nested/runtime-index.asset', 'orphan.png.meta'):
            with self.subTest(extra=extra):
                changed = dict(rows); changed[prefix + extra] = {'sha256': 'a' * 64}
                with self.assertRaisesRegex(ValueError, 'exactly140'): publisher.check_runtime_inventory(changed, self.plan, require_index=True)

    def test_inventory_rejects_missing_authored_index_or_guid_meta_and_changed_bytes(self):
        rows = self.inventory_rows(); prefix = publisher.FAMILY + '/' + self.actor_id + '/'
        for missing in ('walk/N/16.png', 'runtime-index.asset', 'runtime-index.asset.meta', 'walk/N/16.png.meta'):
            with self.subTest(missing=missing):
                changed = dict(rows); del changed[prefix + missing]
                with self.assertRaises(ValueError): publisher.check_runtime_inventory(changed, self.plan, require_index=True)
        rows[prefix + 'portrait.png'] = {'sha256': 'f' * 64}
        with self.assertRaisesRegex(ValueError, 'bytes differ'): publisher.check_runtime_inventory(rows, self.plan, require_index=True)

    def test_existing_target_cannot_hide_a_nested_runtime_index(self):
        target = self.project / publisher.FAMILY / self.actor_id
        plan = copy.deepcopy(self.plan)
        for rel in plan['outputs']:
            path = target / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(b'unit inventory fixture')
            plan['outputs'][rel] = publisher.sha(path)
        self.assertEqual(publisher.target_state(self.project, plan)[1], 'already_identical')
        extra = target / 'nested/runtime-index.asset'; extra.parent.mkdir(); extra.write_text('unapproved extra', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'exactly140'): publisher.target_state(self.project, plan)

    def test_default_nonempty_view_object_is_not_a_screenshot(self):
        actor = {'actualCharacterId': self.actor_id, 'nearestView': {'imagePath': '', 'renderWidth': 0, 'renderHeight': 0}}
        self.assertTrue(actor['nearestView'])
        with self.assertRaisesRegex(ValueError, 'path is missing'): publisher.check_runtime_view(actor, 'nearestView', self.capture, self.camera)

    def test_saved_png_hash_is_verified_and_missing_file_is_rejected(self):
        actor = self.view_actor(); view = actor['normalView']; path = Path(view['imagePath'])
        publisher.check_runtime_view(actor, 'normalView', self.capture, self.camera)
        with path.open('ab') as stream: stream.write(b'changed after observation')
        with self.assertRaisesRegex(ValueError, 'SHA'): publisher.check_runtime_view(actor, 'normalView', self.capture, self.camera)
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'missing'): publisher.check_runtime_view(actor, 'normalView', self.capture, self.camera)

    def test_png_dimensions_are_decoded_even_when_sha_and_claimed_size_match(self):
        actor = self.view_actor(); view = actor['normalView']; path = Path(view['imagePath'])
        Image.effect_noise((2000, 1080), 60).convert('RGB').save(path); view['imageSha256'] = publisher.sha(path)
        with self.assertRaisesRegex(ValueError, '1920x1080'): publisher.check_runtime_view(actor, 'normalView', self.capture, self.camera)

    def test_nearest_view_accepts_honest_clipping_but_rejects_false_flags_and_wrong_zoom(self):
        actor = self.view_actor('nearestView'); view = actor['nearestView']
        self.assertFalse(publisher.check_runtime_view(actor, 'nearestView', self.capture, self.camera)['fullFrameInsideCapture'])
        view['fullFrameInsideCapture'] = True
        with self.assertRaisesRegex(ValueError, 'clipping'): publisher.check_runtime_view(actor, 'nearestView', self.capture, self.camera)
        view['fullFrameInsideCapture'] = False; view['actualOrthographicSize'] = 27
        with self.assertRaisesRegex(ValueError, 'camera zoom'): publisher.check_runtime_view(actor, 'nearestView', self.capture, self.camera)

    def test_nonfinite_projection_and_wrong_minimum_configuration_are_rejected(self):
        actor = self.view_actor()
        for key, value in [('frameTopPixels', float('nan')), ('configuredZoomMin', 6), ('screenPixelsPerTexturePixel', float('inf'))]:
            with self.subTest(key=key):
                changed = copy.deepcopy(actor); changed['normalView'][key] = value
                with self.assertRaises(ValueError): publisher.check_runtime_view(changed, 'normalView', self.capture, self.camera)

    def test_runtime_visual_review_binds_report_input_view_hash_and_clipping(self):
        args = self.review_fixture(); publisher.check_runtime_visual_review(*args)
        path = args[0]; baseline = publisher.read(path)
        for key in ('runtime_report_sha256', 'input_snapshot_sha256'):
            with self.subTest(key=key):
                changed = copy.deepcopy(baseline); changed[key] = 'f' * 64; self.save_json(path, changed)
                with self.assertRaisesRegex(ValueError, 'another report/input'): publisher.check_runtime_visual_review(*args)
        for key, value in [('image_sha256', 'f' * 64), ('clipping_reviewed', False), ('full_frame_inside_capture', True), ('notes', '')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(baseline); changed['views'][0][key] = value; self.save_json(path, changed)
                with self.assertRaisesRegex(ValueError, 'exact visual/clipping review'): publisher.check_runtime_visual_review(*args)

    def test_runtime_visual_review_rejects_missing_duplicate_and_predated_records(self):
        args = self.review_fixture(); path = args[0]; baseline = publisher.read(path)
        for invalid in ('missing', 'duplicate', 'predated'):
            with self.subTest(invalid=invalid):
                changed = copy.deepcopy(baseline)
                if invalid == 'missing': changed['views'] = []
                elif invalid == 'duplicate': changed['views'].append(copy.deepcopy(changed['views'][0]))
                else: changed['reviewed_utc'] = '2025-01-01T00:00:00Z'
                self.save_json(path, changed)
                with self.assertRaises(ValueError): publisher.check_runtime_visual_review(*args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
