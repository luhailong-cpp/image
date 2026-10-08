"""Read-only dependency report; never prepares a guide or modifies progress."""
import json
from common import TILE, load_neighbors, load_native, load_png, NATIVE


def snapshot():
    report = {'tile': 'r08_c11', 'ready': False, 'boundarySources': {},
              'regionalGuideReady': False, 'nativePresent': 0, 'nextEligibleCells': [],
              'errors': [], 'formalAccepted': False}
    try:
        _, report['boundarySources'] = load_neighbors()
    except (ValueError, OSError, KeyError) as error:
        report['errors'].append(str(error))
    try:
        load_png(TILE/'regional/shared-region1254.png', (NATIVE, NATIVE))
        report['regionalGuideReady'] = True
    except (ValueError, OSError) as error:
        report['errors'].append(str(error))
    present = set()
    for row in range(4, 0, -1):
        for col in range(1, 5):
            cell = f'r{row:02d}_c{col:02d}'
            path = TILE/'native'/f'{cell}.png'
            record = path.with_name(path.name+'.generation.json')
            if not path.exists() and not record.exists():
                continue
            try:
                load_native(row, col)
                present.add((row, col))
            except (ValueError, OSError, KeyError) as error:
                report['errors'].append(str(error))
    report['nativePresent'] = len(present)
    if not report['errors']:
        for row in range(4, 0, -1):
            for col in range(1, 5):
                if ((row, col) not in present and
                    (col == 1 or (row, col-1) in present) and
                    (row == 4 or (row+1, col) in present)):
                    cell = f'r{row:02d}_c{col:02d}'
                    report['nextEligibleCells'].append({
                        'cell': cell, 'preparedJobExists': (TILE/'jobs'/f'{cell}.json').exists()})
        report['ready'] = True
    report['allNativeRegistered'] = len(present) == 16
    return report


if __name__ == '__main__':
    print(json.dumps(snapshot(), ensure_ascii=False, indent=2))
