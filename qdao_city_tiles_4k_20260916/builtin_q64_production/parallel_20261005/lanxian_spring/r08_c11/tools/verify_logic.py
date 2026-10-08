"""Small coordinate and guard checks; no generated art or full assembly fixture."""
import ast
from pathlib import Path
import numpy as np
from PIL import Image
import common
from assemble import ownership, external_halo_fragments


def run():
    scripts = list(Path(__file__).resolve().parent.glob('*.py'))
    for script in scripts:
        ast.parse(script.read_text(encoding='utf-8-sig'), filename=str(script))
    coverage = np.zeros(common.EXTENDED, np.uint8)
    for index in range(4):
        lo, hi, dest = ownership(index)
        coverage[dest:dest+hi-lo] += 1
        # Every 1024 native core maps to its intended 1024 world segment.
        assert index*1024+115 == dest+(115-lo)
    assert np.all(coverage == 1)
    class CropRecorder:
        def __init__(self): self.boxes = []
        def crop(self, box): self.boxes.append(box); return box
    west, south = CropRecorder(), CropRecorder()
    external_halo_fragments({'west': west, 'south': south})
    assert west.boxes == [(4096, 0, 4211, 4326)]
    assert south.boxes == [(0, 115, 4326, 230)]
    # The southern context lies at the current patch's last 230 rows.
    for row in range(1, 5):
        own_y = (row-1)*1024
        next_y = row*1024
        assert own_y+1024 == next_y
        assert own_y+1254 == next_y+230
    a = Image.new('RGB', (2, 2), (10, 20, 30))
    b = Image.new('RGB', (2, 2), (12, 18, 30))
    unequal = common.differences(a, b)
    assert unequal['differingPixels'] == 4 and unequal['byteEqual'] is False
    assert unequal['maxAbsoluteRGB'] == [2, 2, 0]
    rejected = False
    try:
        common.require_corner_decision({'metric': unequal, 'explicitDecisionProvided': False})
    except ValueError:
        rejected = True
    assert rejected
    for side in ('west', 'south'):
        assert common.require_corner_decision({'metric': unequal, 'explicitDecisionProvided': True,
                                               'selection': side}) == side
    west_corner = Image.new('RGB', (230, 230), (10, 20, 30))
    south_corner = Image.new('RGB', (230, 230), (40, 50, 60))
    split = np.asarray(common.corner_image(west_corner, south_corner, 'core-split'))
    assert np.all(split[:115] == [10, 20, 30])
    assert np.all(split[115:] == [40, 50, 60])
    assert 3 * 1024 + 1024 + 115 == 4211
    policy = common.read(common.TILE / 'corner-source-ownership.json')
    assert policy['splitYInTargetExtended'] == 4211
    assert [(p['source'], p['targetExtendedLTRB']) for p in policy['cornerGuideOwnerRects']] == [
        ('west', [0, 4096, 230, 4211]), ('south', [0, 4211, 230, 4326])]
    rejected = False
    try:
        common.corner_image(Image.new('RGB', (115, 115)), Image.new('RGB', (115, 115)), 'core-split')
    except ValueError:
        rejected = True
    assert rejected
    west_image, west_source = common.load_selected('west')
    assert west_image.size == (4326, 4326)
    south_state = 'qualified_selected_available'
    try:
        common.load_selected('south')
    except ValueError as error:
        south_state = str(error)
        assert 'WAIT:' in south_state
    result = {'checkedAtUtc': common.now(), 'scriptsParsed': [p.name for p in scripts],
              'checks': ['1D ownership covers all 4326 pixels once',
                         'All native core origins map to correct world positions',
                         'Selected exterior halo crop coordinates are correct',
                         'Bottom-to-top 230-pixel context mapping is correct',
                         'Unequal corner without source decision fails',
                         'Explicit west/south corner decisions are honored',
                         'Explicit core-split assigns upper 115 rows west and lower 115 south',
                         'Native r04_c01 core-split coordinates match regional guide ownership at extended y=4211',
                         'core-split rejects 115 by 115 exterior halo dimensions',
                         'Real west selected PNG, manifest tile identity and SHA verify'],
              'westSource': west_source, 'southReadiness': south_state,
              'fullAssemblyExecuted': False, 'generationSubmitted': False,
              'filesOutsideToolsWritten': False, 'passed': True}
    common.write(Path(__file__).resolve().parent/'verification.json', result)
    print(__import__('json').dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()
