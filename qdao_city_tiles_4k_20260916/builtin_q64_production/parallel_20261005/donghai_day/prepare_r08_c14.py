"""Prepare r08_c14 layout guidance only; no generated art or west binding."""
from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone

R = Path(__file__).resolve().parent
P = R.parents[3]
T = R / 'r08_c14'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    for name in ['guides', 'prompts', 'native', 'output', 'qa']:
        (T / name).mkdir(parents=True, exist_ok=True)
    source = P / 'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/donghai_day/map-native-layout-reference.png'
    west = R / 'r08_c13/output/r08_c13.png'
    target = T / 'guides/local-layout.png'
    if target.exists() or (T / 'plan.json').exists():
        raise SystemExit('Existing r08_c14 plan/guide retained; preparation does not overwrite.')
    with Image.open(source) as image:
        image.load()
        if image.width != image.height:
            raise ValueError('Square full-city layout required')
        box = [value * image.width / 65536 for value in (53133, 28557, 57459, 32883)]
        image.convert('RGB').transform((1254, 1254), Image.Transform.EXTENT, box, Image.Resampling.BICUBIC).save(target)
    now = datetime.now(timezone.utc).isoformat()
    plan = {
        'tile': 'r08_c14', 'globalRect': [53248, 28672, 4096, 4096],
        'worldRect': {'x': 293.75, 'z': 150, 'width': 18.75, 'height': 18.75},
        'layoutSource': str(source), 'layoutSourceSha256': sha(source), 'layoutSourceBox': box,
        'westNeighbor': str(west), 'westNeighborSha256': None,
        'westNeighborRole': 'Pending final r08_c13 current output; must bind and verify SHA before c01 generation or assembly',
        'westBindingStatus': 'pending', 'sourceGuide': str(target), 'guideSha256': sha(target),
        'preparedAtUtc': now, 'status': 'layout_reference_prepared_structure_pending',
        'referenceEnlargementOnly': True, 'finalArtUpscaled': False, 'formalAccepted': False,
        'nativeGrid': [4, 4], 'core': 1024, 'halo': 115,
        'geometryStatus': 'layout crop only; local structure and west common-edge review pending',
        'dayFestivalGeometryAligned': False, 'navigationAccepted': False,
    }
    (T / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    record = {'file': str(target), 'sha256': sha(target), 'createdAtUtc': now,
              'derivedFrom': [{'file': str(source), 'sha256': sha(source)}],
              'operation': 'reference-only enlarged layout crop', 'sourceBox': box,
              'globalBox': [53133, 28557, 57459, 32883], 'pixels': [1254, 1254],
              'allowedInFinal': False, 'countsAsHDArt': False}
    Path(str(target) + '.generation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(plan, ensure_ascii=False))

if __name__ == '__main__':
    main()
