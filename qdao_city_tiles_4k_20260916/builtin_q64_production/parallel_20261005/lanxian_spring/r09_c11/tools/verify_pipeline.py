"""Synthetic integration checks; fixtures stay under tools/.validation-fixture.

No production source is touched. Remove this fixture directory only after the
verification report is written and its resolved path has been checked.
"""
from pathlib import Path
import contextlib
import io
import json
import numpy as np
from PIL import Image

import common
import prepare_native
import assemble


def main():
    directory = Path(__file__).resolve().parent
    fixture = directory / '.validation-fixture'
    if fixture.exists():
        raise ValueError('Existing validation fixture; inspect before replacing')
    tile = fixture / 'r09_c11'
    repo = fixture / 'repo'
    (tile / 'regional').mkdir(parents=True)
    (tile / 'native').mkdir()
    (repo / 'designs/gameplay-ui').mkdir(parents=True)
    (repo / 'config').mkdir()
    Image.new('RGB', (1254, 1254), '#b8c5b6').save(tile / 'regional/shared-region1254.png')
    Image.new('RGB', (64, 64), '#cdd8df').save(repo / 'designs/gameplay-ui/04-guild.png')
    common.write(repo / 'config/image-generation.json', {'model': 'SYNTHETIC_TEST_ONLY', 'quality': 'SYNTHETIC_TEST_ONLY'})
    yy, xx = np.indices((4326, 4326), dtype=np.int32)
    full = np.stack([xx % 251, yy % 241, (xx + yy) % 239], axis=2).astype(np.uint8)
    # The entire fixture west shares the desired image's left 230 pixels in its
    # right 230 pixels, matching exact world overlap rather than preview scaling.
    west_array = full.copy()
    west_array[:, 4096:4326] = full[:, :230]
    west = fixture / 'west4326.png'
    Image.fromarray(west_array).save(west)
    for module in (common, prepare_native, assemble):
        module.TILE = tile
        module.REPO = repo
        module.WEST = west
        module.WEST_SHA = common.sha(west)

    checks = []
    try:
        prepare_native.prepare(2, 1, 'Synthetic fixture only.')
        raise AssertionError('Missing northern native was not rejected')
    except ValueError as error:
        assert 'dependency' in str(error)
        assert not (tile / 'guides').exists()
        checks.append('missing north dependency rejected before output')
    with contextlib.redirect_stdout(io.StringIO()):
        prepare_native.prepare(1, 1, 'Synthetic fixture only.')
    guide = np.asarray(Image.open(tile / 'guides/r01_c01.layout-only.png'))
    assert np.array_equal(guide[:, :230], west_array[:1254, 4096:4326])
    job = common.read(tile / 'jobs/r01_c01.json')
    assert job['tileDir'] == str(tile) and job['cell'] == 'r01_c01'
    assert job['submittedParameters']['model'] is None and job['submittedParameters']['quality'] is None
    assert len(job['references']) == 2 and job['guideDerivation']['guideOnly']
    checks.append('first-column guide uses exact pinned west 230-pixel band; compatible job keys')
    try:
        prepare_native.prepare(1, 1, 'Synthetic fixture only.')
        raise AssertionError('Existing job was overwritten')
    except ValueError as error:
        assert 'already exist' in str(error)
        checks.append('prepared input overwrite rejected')
    for row in range(4):
        for col in range(4):
            path = tile / 'native' / f'r{row + 1:02d}_c{col + 1:02d}.png'
            image = full[row * 1024:row * 1024 + 1254, col * 1024:col * 1024 + 1254]
            Image.fromarray(image).save(path)
            common.write(str(path) + '.generation.json', {'sha256': common.sha(path), 'syntheticTestFixture': True})
    # A temporary deliberate hash mismatch must be rejected, and restored only
    # in this synthetic fixture before the assembly fidelity check.
    record = tile / 'native/r02_c02.png.generation.json'
    valid = common.read(record)
    common.write(record, {**valid, 'sha256': '0' * 64})
    try:
        common.load_native(2, 2)
        raise AssertionError('Changed source was accepted')
    except ValueError as error:
        assert 'SHA differs' in str(error)
        checks.append('native source SHA mismatch rejected')
    common.write(record, valid)
    with contextlib.redirect_stdout(io.StringIO()):
        assemble.assemble('assembly_hardcut')
    selected = tile / 'assembly_hardcut'
    core = np.asarray(Image.open(selected / 'core4096.png'))
    extended = np.asarray(Image.open(selected / 'extended4326.png'))
    assert np.array_equal(extended, full)
    assert np.array_equal(core, full[115:4211, 115:4211])
    manifest = common.read(selected / 'assembly.json')
    assert len(manifest['qa']) == 41
    assert len(manifest['verification']['rawNativeOverlapMetrics']) == 24
    for item in manifest['verification']['rawNativeOverlapMetrics']:
        assert item['raw230pxOverlap']['maxAbsoluteRGB'] == [0, 0, 0]
    assert manifest['verification']['west230OverlapMetric']['maxAbsoluteRGB'] == [0, 0, 0]
    assert not manifest['qualifiedComplete4KCandidate'] and not manifest['formalAccepted']
    checks.append('16-source 4326 assembly and 4096 crop exactly replay original pixels')
    checks.append('24 native overlap metrics and 41 unscaled QA crops complete; acceptance stays false')
    try:
        assemble.assemble('assembly_hardcut')
        raise AssertionError('Existing assembly was overwritten')
    except ValueError as error:
        assert 'Refusing to overwrite' in str(error)
        checks.append('existing candidate overwrite rejected')
    report = {'status': 'passed', 'verifiedAt': common.now(), 'checks': checks,
              'syntheticFixtureOnly': True, 'productionFilesWritten': False,
              'fixtureDirectory': str(fixture), 'fixtureDeletionPending': True}
    common.write(directory / 'verification.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
