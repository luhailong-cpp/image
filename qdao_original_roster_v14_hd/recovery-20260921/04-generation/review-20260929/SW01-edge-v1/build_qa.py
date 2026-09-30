"""Build review-only composites; never replace a game sprite."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921/04-delivery-preview/revisions'
REV = BASE / 'edge-repair-20260929'
QA = REV / 'qa'
QA.mkdir(exist_ok=True)
source = BASE / 'review-set-v3/runtime/walk/SW/01.png'
native = REV / 'candidate/SW01-edge-v1.native.png'
neighbor = BASE / 'review-set-v3/runtime/walk/SW/02.png'
old = Image.open(source).convert('RGBA')
new = Image.open(native).convert('RGBA')
nxt = Image.open(neighbor).convert('RGBA').resize((512, 512), Image.Resampling.LANCZOS)
raw_display = new.resize((512, 512), Image.Resampling.LANCZOS)
normalized = Image.new('RGBA', (512, 512))
normalized.alpha_composite(new.resize((481, 481), Image.Resampling.LANCZOS), (15, 26))
norm_path = QA / 'SW01-edge-v1-whole-canvas-qa-only.png'
normalized.save(norm_path)
items = [('Original SW01', old), ('Native v1 / full canvas', raw_display), ('QA only / 481px + (15,26)', normalized), ('Existing SW02', nxt)]
for label, rgb in [('light', (242, 238, 225)), ('dark', (28, 42, 48))]:
    board = Image.new('RGB', (2048, 552), rgb)
    draw = ImageDraw.Draw(board)
    ink = (25, 35, 30) if label == 'light' else (238, 238, 220)
    for i, (title, img) in enumerate(items):
        panel = Image.new('RGBA', (512, 512), rgb + (255,))
        panel.alpha_composite(img)
        board.paste(panel.convert('RGB'), (i * 512, 40))
        draw.text((i * 512 + 10, 12), title, fill=ink)
    board.save(QA / f'SW01-v1-comparison-{label}.png')
a = np.asarray(new).astype(np.int16)
r, g, b, al = (a[:, :, i] for i in range(4))
red = (r >= 170) & (g < 110) & (b < 90)
yellow = (r >= 170) & (g >= 150) & (b < 100)
counts = {str(threshold): {'red': int((red & (al >= threshold)).sum()), 'yellow': int((yellow & (al >= threshold)).sum())} for threshold in (1, 8, 32, 64, 128, 200, 254, 255)}
meta = {
    'status': 'review_only_not_game_output',
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'native_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
    'normalization': 'Full 1254 square uniformly resized to 481 square, pasted at integer (15,26) on a 512 square. No local deformation; diagnostic trial only, not approved export settings.',
    'native_red_yellow_alpha_counts': counts,
    'warning': 'Color counts include real gold/brown materials and cannot distinguish contaminated transparency by themselves.',
    'derivedFrom': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in (source, native, neighbor)],
    'operation': 'QA compositing and full-canvas uniform resize only; native/source unchanged',
}
(QA / 'qa-derivation.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'qa': str(QA), 'counts': counts}, ensure_ascii=False))
