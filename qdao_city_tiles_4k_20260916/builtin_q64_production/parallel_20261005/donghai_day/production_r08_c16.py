"""Native-pixel generation bookkeeping for r08_c16; built-in generation is external."""
import sys
from PIL import Image
import production as p

p.T = p.ROOT / 'r08_c16'
p.ORIGIN = (61440, 28672)
p.WEST = p.ROOT / 'r08_c15/output/r08_c15.png'
_base_guide = p.guide

def checked_west():
    plan = p.loadj(p.T / 'plan.json')
    expected = plan.get('westNeighborSha256')
    if plan.get('westBindingStatus') != 'bound' or not expected:
        raise ValueError('Bind final r08_c15 SHA before generating c01.')
    if not p.WEST.is_file() or p.sha(p.WEST) != expected:
        raise ValueError('Bound west neighbor missing or changed; review source before continuation.')
    with Image.open(p.WEST) as image:
        image.load()
        if image.size != (4096, 4096):
            raise ValueError('West neighbor must contain complete 4096x4096 pixels.')
    return expected

def bind_west(expected):
    if not p.WEST.is_file() or p.sha(p.WEST) != expected:
        raise ValueError('Requested west SHA does not identify the current file.')
    with Image.open(p.WEST) as image:
        image.load()
        if image.size != (4096, 4096):
            raise ValueError('West neighbor must be 4096 square.')
    plan = p.loadj(p.T / 'plan.json')
    if plan.get('westNeighborSha256') not in (None, expected):
        raise ValueError('Refusing to replace an existing bound source identity silently.')
    plan.update(westNeighborSha256=expected, westBindingStatus='bound', westBoundAtUtc=p.now(),
                westNeighborRole='actual current west native pixel candidate; formal acceptance remains separate')
    p.savej(p.T / 'plan.json', plan)
    status()
    print('Bound west neighbor SHA256: ' + expected)

def guide(row, column):
    if not (1 <= row <= 4 and 1 <= column <= 4):
        raise ValueError('Native patch row and column must be 1..4.')
    if column == 1:
        checked_west()
    result = _base_guide(row, column)
    if column == 4:
        path = p.T / 'guides' / f'r{row:02d}_c{column:02d}.png.generation.json'
        record = p.loadj(path)
        record['mapBoundaryContext'] = {
            'mapRightExclusive': 65536, 'contextRightExclusive': 65651,
            'outOfCityRightPixels': 115,
            'finalCoreInPatchXYXY': [115, 115, 1139, 1139],
            'handling': 'Generated native continuation of existing blue open water, context only; right 115 pixels excluded from 4096 core.',
            'referencePaddingOnly': True, 'finalPixelsPaddedOrUpscaled': False}
        p.savej(path, record)
    return result

def status():
    plan = p.loadj(p.T / 'plan.json')
    state = {'tile': 'r08_c16', 'globalRect': [61440, 28672, 4096, 4096],
             'updatedAtUtc': p.now(), 'nativePatchesSaved': len(list((p.T / 'native').glob('r??_c??.png'))),
             'nativePatchesRequired': 16, 'countsAsCompleteTile': False, 'formalAccepted': False,
             'structureReferenceAvailable': (p.T / 'guides/local-structure.png').is_file(),
             'westBindingStatus': plan.get('westBindingStatus', 'pending'),
             'phase': 'native_expansion_in_progress' if list((p.T / 'native').glob('r??_c??.png')) else 'structure_preparation'}
    p.savej(p.T / 'progress.json', state)
    p.savej(p.T / 'current-work.json', state)

p.status = status
p.guide = guide

if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'prepare':
        p.prepare(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif command == 'guide':
        guide(int(sys.argv[2]), int(sys.argv[3]))
    elif command == 'record':
        p.record(sys.argv[2], sys.argv[3])
    elif command == 'bind-west':
        bind_west(sys.argv[2])
    elif command == 'status':
        status()
    else:
        raise SystemExit('Expected prepare, guide, record, bind-west, or status.')

