import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916')
PROD = ROOT / 'builtin_q64_production'
OUT = PROD / 'parallel_20261005/lanxian_day/preflight'
HANDOFF = OUT.parent / 'handoff.json'
COMPLETION = PROD / 'resume_single_city_20260921/completion_20261004'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def check(p, expected=None):
    p = Path(p)
    result = {'file': str(p), 'exists': p.is_file()}
    if expected:
        result['expectedSha256'] = expected
    if p.is_file():
        data = p.read_bytes()
        result.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), lastWriteUtc=datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat())
        if expected:
            result['shaMatches'] = result['sha256'] == expected
        if p.suffix.lower() == '.png':
            with Image.open(p) as im:
                result.update(pixels=list(im.size), mode=im.mode)
    return result

handoff = read(HANDOFF)
plan = read(handoff['plan']['file'])
detail_dir = PROD / 'lanxian_day/r08_c09'
detail_plan = read(detail_dir/'plan.json')
native_inventory = []
for path in sorted((detail_dir/'native').glob('*.png')):
    record_path = path.with_suffix('.record.json')
    record = read(record_path) if record_path.is_file() else {}
    item = check(path, record.get('outputSha256'))
    item.update(record=check(record_path), usableAs='native fragment subject to placement/geometry inspection; not a complete tile', configuredModelTarget=record.get('configuredModelTarget'), configuredQualityTarget=record.get('configuredQualityTarget'), actualBackendModel=record.get('actualBackendModel'), actualQualityPreset=record.get('actualQualityPreset'))
    native_inventory.append(item)

dependencies = []
for role, historic, expected in [
    ('regional source', detail_plan['guidePreparation']['motherSource'], detail_plan['guidePreparation']['motherSha256']),
    ('guide canvas', detail_plan['guidePreparation']['mother'], None),
    ('west extended boundary', detail_plan['leftNeighborBoundary']['file'], detail_plan['leftNeighborBoundary']['sha256']),
    ('original layout source', plan['originalLayoutSource'], plan['originalLayoutSourceSha256']),
]:
    relocated = historic.replace('E:\\work\\image', 'D:\\work\\image')
    dependencies.append({'role': role, 'historicalPath': historic, 'relocatedCheck': check(relocated, expected)})
regional_record_path = detail_dir/'regional-reference/regional-v1.record.json'
regional_record = read(regional_record_path)
regional_review = read(detail_dir/'regional-reference/regional-v1.visual-review.json')

candidate_dir = COMPLETION / 'lanxian/lanxian_day'
candidates = []
for p in sorted(candidate_dir.rglob('assembly.json')):
    data = read(p)
    item = {'assembly': check(p), 'actualVisualReview': data.get('actualVisualReview'), 'formalAccepted': data.get('formalAccepted')}
    if 'candidate' in data:
        c = data['candidate']
        item['candidate'] = check(c['file'], c.get('sha256'))
    for field in ('mask','flow','tone'):
        if isinstance(data.get(field), dict) and data[field].get('file'):
            item[field] = check(data[field]['file'], data[field].get('sha256'))
    candidates.append(item)

tile_ids = [t['id'] for t in plan['tiles']]
incomplete_r08_c09 = [f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5) if not (detail_dir/f'native/r{r:02}_c{c:02}.png').is_file()]
report = {
    'auditCreatedAtUtc': datetime.now(timezone.utc).isoformat(),
    'scope': 'read-only source identity, dimensions, and availability; not visual or runtime acceptance',
    'handoff': check(HANDOFF),
    'readyForProductionAtRead': handoff['readyForProduction'],
    'plan': {**check(handoff['plan']['file'], handoff['plan']['sha256']), 'tileCount': len(tile_ids), 'uniqueTileCount': len(set(tile_ids)), 'wholeCityPixels': plan['wholeCityPixels'], 'tilePixels': plan['tilePixels'], 'historicalModelRequest': plan['requestedModel'], 'r08_c09': next(t for t in plan['tiles'] if t['id']=='r08_c09')},
    'layout': check(handoff['layout']['file'], handoff['layout']['sha256']),
    'baselineCandidates': [{**check(c['file'], c.get('sha256')), 'tile': c['tile'], 'formalAccepted': False} for c in handoff['baselineCandidates']],
    'r08_c09': {'plan': check(detail_dir/'plan.json'), 'nativeInventory': native_inventory, 'survivingNativeCount': len(native_inventory), 'missingNativeIds': incomplete_r08_c09, 'complete4KTilePresent': False, 'dependencyChecks': dependencies, 'regionalRecord': check(regional_record_path), 'regionalRecordOutputSha256': regional_record.get('outputSha256'), 'regionalVisualReviewSelectedSha256': regional_review.get('selectedRegionalSha256'), 'note': 'Historical plan status mentions sixteen pending details but actual surviving image inventory is authoritative. Missing guide/regional/extended images cannot be assumed present. Fragment counts never count as 4K tiles.'},
    'completion20261004': {'directory': str(candidate_dir), 'readOnly': True, 'candidates': candidates, 'allFileCount': sum(1 for p in candidate_dir.rglob('*') if p.is_file()), 'note': 'Parent is still writing this tree; readiness and latest candidate identity must be reread from handoff before use.'},
    'findings': [
        'All available handoff baseline tiles are complete 4096-square PNG files; this audit does not approve visual seams or geometry.',
        'r08_c09 has one surviving native fragment; the remaining 15 fragment images and a complete 4K assembled output are absent in that tile directory.',
        'Historical E: source paths must be resolved explicitly; D: relocated guide/regional/extended dependencies checked individually.',
        'Layout reference is 1254-square and remains layout/style only, never finished high-resolution art.',
        'The original production plan names GPT Image 2.0 historically; current image policy/config and per-image evidence control new work.',
        'No source image or metadata was changed, deleted, copied, or accepted during this audit.'
    ],
    'formalAccepted': 0,
    'wholeCityComplete': False,
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'source-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'report': str(OUT/'source-audit.json'), 'ready': report['readyForProductionAtRead'], 'planShaMatches': report['plan']['shaMatches'], 'layoutShaMatches': report['layout']['shaMatches'], 'baselineShaMatches': [x['shaMatches'] for x in report['baselineCandidates']], 'nativeCount': len(native_inventory), 'dependencies': dependencies, 'candidates': candidates}, ensure_ascii=False, indent=2))
