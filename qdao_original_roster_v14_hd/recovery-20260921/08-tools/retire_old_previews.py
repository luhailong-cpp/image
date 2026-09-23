"""Replace retired 08 HTML viewers with final-package links after image cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import json, os
from process import RECOVERY, write

delivery = RECOVERY / '08-delivery-preview'
final = delivery / 'revisions' / 'final-v1'
manifest = json.loads((final / 'manifest.json').read_text(encoding='utf-8'))
assert manifest['actual_walk'] == 128 and manifest['actual_idle'] == 8 and manifest['visual_approval']
audit = json.loads((final / 'file-audit-before-cleanup.json').read_text(encoding='utf-8'))
assert audit['status'] == 'passed_file_checks_only' and not audit['errors']
image_extensions = {'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.avif'}
leftovers = [p for p in delivery.rglob('*') if p.is_file() and p.suffix.lower() in image_extensions and not p.is_relative_to(final)]
assert not leftovers, 'Old images remain; do not retire their viewers before the authorized cleanup'
updated = []
for path in sorted(delivery.rglob('*.html')):
    if path.is_relative_to(final) or path == delivery / 'index.html':
        continue
    target = os.path.relpath(final / 'index.html', path.parent).replace('\\','/')
    path.write_text('<!doctype html><meta charset="utf-8"><title>08 历史预览已归档</title><h1>08 炼丹童子历史预览</h1><p>此制作快照的中间图片已按用户授权清理，文字来源记录仍保留。</p><p><a href="'+target+'">打开最终136张成品的八方向预览</a></p>', encoding='utf-8')
    updated.append(path.relative_to(delivery).as_posix())
write(final / 'retired-preview-links.json', {'updatedAt':datetime.now(timezone.utc).isoformat(), 'retired_viewers':updated, 'target':'index.html', 'historical_manifests_unchanged':True})
print(json.dumps({'retired_html':len(updated)}, ensure_ascii=False))
