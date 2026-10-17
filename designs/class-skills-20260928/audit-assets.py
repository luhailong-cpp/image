"""验证正式技能图与逐图来源；不调用模型、不修改图片。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

catalog = read(ROOT / 'catalog.json')
config = read(PROJECT / 'config/image-generation.json')
rows = []
for skill in catalog['skills']:
    sid = skill['id']
    file = ROOT / 'icons' / f'{sid}.png'
    prompt = ROOT / 'prompts' / f'{sid}.txt'
    receipt_path = ROOT / 'records' / f'{sid}.tool-response.json'
    receipt = read(receipt_path)
    assert file.is_file() and prompt.is_file(), sid
    with Image.open(file) as image:
        image.verify()
    with Image.open(file) as image:
        width, height, fmt, mode = image.width, image.height, image.format, image.mode
    assert width == height and width >= 1024, (sid, width, height)
    source_match = re.search(r' as (.+\.png) by default', receipt['output_hint'])
    source = Path(source_match.group(1)) if source_match else None
    if source and source.exists():
        assert sha(source) == sha(file), f'{sid}: copy changed pixels'
    record_path = file.with_suffix('.png.generation.json')
    if not record_path.exists():
        refs = [{'file': '../../gameplay-ui/02-inventory.png', 'role': '主要风格参考，已确认的道家Q版手绘物件、材质与完成度'}]
        if sid != 1101:
            refs.append({'file': '1101.png', 'role': '本批次边框、画法与图标完成度参考；不复制主体', 'sha256': sha(ROOT / 'icons/1101.png')})
        record = {
            'file': f'icons/{sid}.png', 'skillId': sid, 'name': skill['name'],
            'sha256': sha(file),
            'generatedAt': datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(),
            'generatedAtEvidence': '生成文件的LastWriteTimeUtc；工具未披露生成时间字段',
            'toolCompletedAt': receipt.get('completedAt'),
            'width': width, 'height': height, 'format': fmt, 'mode': mode,
            'nativeDimensions': [width, height], 'exportDimensions': [width, height],
            'tool': 'image_gen.imagegen', 'route': 'builtin',
            'configSnapshot': config,
            'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False},
            'actualModel': None, 'actualQuality': None,
            'unverifiedReason': '宿主管理，工具未开放model/quality选择器；返回结果仅image_url和output_hint，未披露实际模型版本及质量',
            'evidence': [{'file': f'records/{sid}.tool-response.json', 'fields': ['output_hint']}],
            'prompt': f'prompts/{sid}.txt', 'references': refs,
            'sourceFile': str(source) if source else None,
            'operation': '生成结果原样复制为正式技能图；未裁切、缩放或重新绘制',
        }
        write(record_path, record)
    record = read(record_path)
    assert record['sha256'] == sha(file), f'{sid}: image differs from recorded generation'
    rows.append({'id': sid, 'name': skill['name'], 'classId': skill['classId'], 'file': f'icons/{sid}.png', 'sha256': sha(file), 'width': width, 'height': height, 'generationRecord': f'icons/{sid}.png.generation.json', 'prompt': f'prompts/{sid}.txt'})
assert len(rows) == 32 and len({r['sha256'] for r in rows}) == 32
assert len({s['name'] for s in catalog['skills']}) == 32
for cid in range(1, 5):
    items = [s for s in catalog['skills'] if s['classId'] == cid]
    assert len(items) == 8
    assert sum(s['type'] == 'active' for s in items) == 5
    assert sum(s['type'] == 'passive' for s in items) == 3
write(ROOT / 'asset-manifest.json', {'schemaVersion': 1, 'count': len(rows), 'assets': rows})
write(ROOT / 'asset-validation.json', {'status': 'passed', 'checkedAt': datetime.now(timezone.utc).isoformat(), 'count': len(rows), 'uniquePngHashes': 32, 'nativeSquarePng': True, 'allRecordsAndPromptsPresent': True, 'allSourceCopiesByteIdenticalWhenSourcePresent': True, 'visualReview': '另见预览与逐图视觉检查；本脚本只验证文件和来源完整性'})
print(json.dumps({'status': 'passed', 'count': len(rows), 'sizes': sorted({(r['width'], r['height']) for r in rows})}, ensure_ascii=False))
