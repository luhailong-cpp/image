from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, datetime

root = Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
out = root / 'run-axis-revision-20261004/WN-audit'
for direction, frames, name in [
    ('W', [5, 6, 7], 'W05-07-recovery-leg'),
    ('NW', [8, 9, 10, 11, 12, 13], 'NW08-13-leg-continuity'),
]:
    rows = (len(frames) + 2) // 3
    sheet = Image.new('RGB', (2700, rows * 625), (235, 234, 224))
    draw = ImageDraw.Draw(sheet)
    refs = []
    for i, number in enumerate(frames):
        p = root / f'runtime/run/{direction}/{number:02d}.png'
        im = Image.open(p).convert('RGBA')
        crop = im.crop((320, 690, 770, 970)).resize((900, 560), Image.Resampling.NEAREST)
        x, y = i % 3 * 900, i // 3 * 625
        draw.text((x + 15, y + 15), f'{direction}{number:02d} | same crop (320,690)-(770,970), 2x nearest-neighbor', fill=(20,20,20))
        sheet.paste(crop, (x, y + 50), crop)
        refs.append({'file': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'generationRecord': str(p) + '.generation.json'})
    dest = out / f'{name}.jpg'
    sheet.save(dest, quality=98)
    Path(str(dest) + '.generation.json').write_text(json.dumps({
        'file': str(dest), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'operation': 'Read-only audit crop/montage; 2x nearest-neighbor; no AI detail synthesis or sprite alteration',
        'derivedFrom': refs
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(dest)
